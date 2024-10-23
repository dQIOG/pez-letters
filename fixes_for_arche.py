import glob
import tqdm
import csv
from acdh_tei_pyutils.tei import TeiReader

data = [["file", "error"]]
files = glob.glob("./data/*/*.xml")
for x in tqdm.tqdm(files, total=len(files)):
    try:
        doc = TeiReader(x)
    except Exception as e:
        data.append([x, e])
        continue
    doc.tree_to_file(x)

with open("parsing_errors.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)
