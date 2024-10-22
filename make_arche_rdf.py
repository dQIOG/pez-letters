import glob
import os
import shutil
from tqdm import tqdm
from acdh_cidoc_pyutils import extract_begin_end
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext
from rdflib import Namespace, URIRef, RDF, Graph, Literal, XSD

to_ingest = "to_ingest"
os.makedirs(to_ingest, exist_ok=True)
g = Graph().parse("arche_seed_files/arche_constants.ttl")
g_repo_objects = Graph().parse("arche_seed_files/repo_objects_constants.ttl")
TOP_COL_URI = URIRef("https://id.acdh.oeaw.ac.at/pez-briefe")
APP_URL = "https://pez-briefe.acdh.oeaw.ac.at/"

ACDH = Namespace("https://vocabs.acdh.oeaw.ac.at/schema#")
COLS = [ACDH["TopCollection"], ACDH["Collection"], ACDH["Resource"]]
COL_URIS = set()


files = sorted(glob.glob("data/editions/*.xml"))
files = files[:20]
for x in tqdm(files):
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
            ACDH["hasLicense"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archelicenses/cc-by-4-0"),
        )
    )

    # title
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
            (cur_doc_uri, ACDH["hasCoverageEndDate"], Literal(start, datatype=XSD.date))  # noqa: 501
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
        g.add(
            (cur_doc_uri, ACDH["hasExtent"], Literal("1 Seite", lang="de"))
        )

for x in COLS:
    for s in g.subjects(None, x):
        COL_URIS.add(s)

for x in COL_URIS:
    for p, o in g_repo_objects.predicate_objects():
        g.add((x, p, o))

print("writing graph to file")
g.serialize("to_ingest/arche.ttl")

files_to_ingest = glob.glob("./data/*/*.xml")
print(f"copying {len(files_to_ingest)} into {to_ingest}")
for x in files_to_ingest:
    _, tail = os.path.split(x)
    new_name = os.path.join(to_ingest, tail)
    shutil.copy(x, new_name)
