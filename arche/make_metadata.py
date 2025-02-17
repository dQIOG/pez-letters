import glob
import os
import shutil
from tqdm import tqdm
from acdh_cidoc_pyutils import extract_begin_end
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext
from rdflib import Namespace, URIRef, RDF, Graph, Literal, XSD

to_ingest = "to_ingest"
arche_ttl_name = "arche.ttl"
arche_md_save = os.path.join(to_ingest, arche_ttl_name)
shutil.rmtree(to_ingest, ignore_errors=True)
os.makedirs(to_ingest, exist_ok=True)
g = Graph().parse("arche/arche_constants.ttl")
g_repo_objects = Graph().parse("arche/repo_objects_constants.ttl")
TOP_COL_URI = URIRef("https://id.acdh.oeaw.ac.at/pez-briefe")
APP_URL = "https://pez-briefe.acdh.oeaw.ac.at/"

ACDH = Namespace("https://vocabs.acdh.oeaw.ac.at/schema#")
COLS = [ACDH["TopCollection"], ACDH["Collection"], ACDH["Resource"]]
COL_URIS = set()


files = sorted(glob.glob("data/editions/*.xml"))
# files = files[:20]
for i, x in enumerate(tqdm(files, total=len(files)), start=1):
    doc = TeiReader(x)
    cur_col_id = os.path.split(x)[-1].replace(".xml", "")
    cur_doc_id = f"{cur_col_id}.xml"

    # TEI/XML Document
    cur_doc_uri = URIRef(f"{TOP_COL_URI}/{cur_doc_id}")
    g.add((cur_doc_uri, RDF.type, ACDH["Resource"]))
    g.add((cur_doc_uri, ACDH["isPartOf"], URIRef(f"{TOP_COL_URI}/editions")))
    g.add(
        (
            cur_doc_uri,
            ACDH["hasLanguage"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/iso6393/deu"),
        )
    )
    g.add(
        (
            cur_doc_uri,
            ACDH["hasLanguage"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/iso6393/lat"),
        )
    )

    # title
    title = extract_fulltext(doc.any_xpath(".//tei:titleStmt/tei:title[1]")[0])
    letter_nr = doc.any_xpath("./@n")[0]

    try:
        inferred = doc.any_xpath("//tei:gap[@reason='inferred letter']")[0]
        final_title = f"{letter_nr} {title}"
    except IndexError:
        final_title = f"[{letter_nr}] {title}"
    g.add(
        (
            cur_doc_uri,
            ACDH["hasTitle"],
            Literal(f"{final_title}", lang="de"),
        )
    )
    g.add(
        (
            cur_doc_uri,
            ACDH["hasCategory"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/text/tei"),
        )
    )

    # start/end date
    try:
        start, end = extract_begin_end(
            doc.any_xpath(".//tei:correspAction[@type='sent']/tei:date")[0]
        )
    except IndexError:
        start, end = False, False
    if start:
        g.add(
            (
                cur_doc_uri,
                ACDH["hasCoverageStartDate"],
                Literal(start, datatype=XSD.date),
            )
        )
    if end:
        g.add(
            (
                cur_doc_uri,
                ACDH["hasCoverageEndDate"],
                Literal(start, datatype=XSD.date),
            )  # noqa: 501
        )

    # hasExtent
    nr_of_pages = len(doc.any_xpath(".//tei:pb"))
    if nr_of_pages > 1:
        g.add(
            (
                cur_doc_uri,
                ACDH["hasExtent"],
                Literal(f"{nr_of_pages} Seiten", lang="de"),
            )
        )
    else:
        g.add((cur_doc_uri, ACDH["hasExtent"], Literal("1 Seite", lang="de")))

    # hasNextItem
    try:
        next_doc = TeiReader(files[i])
        next_id = next_doc.any_xpath(".//@xml:id")[0]
        g.add(
            (cur_doc_uri, ACDH["hasNextItem"], URIRef(f"{TOP_COL_URI}/{next_id}.xml"))
        )
    except IndexError:
        pass

    # hasSchema
    g.add(
        (cur_doc_uri, ACDH["hasSchema"], Literal("https://id.acdh.oeaw.ac.at/pez-briefe/pez-letters.rng"))
    )

    _, tail = os.path.split(x)
    new_name = os.path.join(to_ingest, tail)
    shutil.copy(x, new_name)

# indices
files = sorted(glob.glob("data/indices/*.xml"))

for x in tqdm(files):
    doc = TeiReader(x)
    cur_col_id = os.path.split(x)[-1].replace(".xml", "")
    # cur_doc_id = f"register-{cur_col_id}.xml"
    cur_doc_id = f"{cur_col_id}.xml"
    cur_doc_uri = URIRef(f"{TOP_COL_URI}/{cur_doc_id}")
    g.add((cur_doc_uri, RDF.type, ACDH["Resource"]))
    g.add((cur_doc_uri, ACDH["isPartOf"], URIRef(f"{TOP_COL_URI}/indices")))
    title = extract_fulltext(doc.any_xpath(".//tei:titleStmt/tei:title[1]")[0])
    g.add(
        (
            cur_doc_uri,
            ACDH["hasTitle"],
            Literal(f"{title}", lang="de"),
        )
    )
    g.add(
        (
            cur_doc_uri,
            ACDH["hasCategory"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/text/tei"),
        )
    )
    _, tail = os.path.split(x)
    new_name = os.path.join(to_ingest, cur_doc_id)
    shutil.copy(x, new_name)

for x in COLS:
    for s in g.subjects(None, x):
        COL_URIS.add(s)

for x in COL_URIS:
    for p, o in g_repo_objects.predicate_objects():
        g.add((x, p, o))

print("adding triples from 'other_things.ttl'")
g.parse("arche/other_things.ttl")

print("writing graph to file")
g.serialize(arche_md_save)

print("resolving relativ imports schema locaiton")

files = glob.glob("to_ingest/pez-*.xml")

for x in tqdm(files, total=len(files)):
    with open(x, "r") as f:
        content = f.read()
    old_value = '<?xml-model href="../../odd/pez-letters.rng"'
    new_value = f'<?xml-model href="{TOP_COL_URI}/pez-letters.rng"'
    content = content.replace(old_value, new_value)

    old_value = 'replacementPattern="../indices/'
    new_value = f'replacementPattern="{TOP_COL_URI}/'
    content = content.replace(old_value, new_value)
    with open(x, "w") as f:
        f.write(content)

files = glob.glob("./data/editions/pez-*.xml")
print(f"done, check {arche_md_save}")
