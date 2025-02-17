import glob
import os

from acdh_tei_pyutils.tei import TeiReader

for x in glob.glob("./data/editions/*.xml"):
    doc = TeiReader(x)
    path, _ = os.path.split(x)
    xmlid = doc.any_xpath(".//@xml:id")[0]
    new_name = f"{xmlid.replace("-", "_")}.xml"
    new_path = os.path.join(path, new_name)
    os.rename(x, new_path)
