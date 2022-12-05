from io import StringIO
from datetime import datetime
import csv
from os.path import join
import time

from bs4 import BeautifulSoup as bs
import requests


page = 0
url_tmpl = "https://www.ifrc.org/appeals?page={page}"
rows = []
headers = [
    "Name",
    "Location",
    "Appeal code",
    "Disaster type",
    "Appeal type",
    "Orig. type",
    "Date",
    "URL",
]


def extract_row(tr):
    row = [x.text.strip() for x in tr.find_all("td")]
    row[6] = str(datetime.strptime(row[6], "%d/%m/%Y").date())
    row.append(tr.find("td").find("a").get("href"))
    return dict(zip(*(headers, row)))


csv_url = "https://codeforiati.org/ifrc-appeals-codelist/ifrc-appeals.csv"
r = requests.get(csv_url)
existing_rows = list(csv.DictReader(StringIO(r.text)))

done = False
while not done:
    r = requests.get(url_tmpl.format(page=page))
    soup = bs(r.text, features="html.parser")
    tbody = soup.tbody
    if not tbody:
        # table is empty so stop
        break
    for tr in tbody.find_all("tr"):
        row = extract_row(tr)
        if row in existing_rows:
            # we’ve already seen this row, so stop
            done = True
            break
        rows.append(row)
    time.sleep(0.5)
    page += 1


rows += existing_rows
with open(join("output", "ifrc-appeals.csv"), "w") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
