from datetime import datetime
import csv
from os.path import join
import time

from bs4 import BeautifulSoup as bs
import requests


page = 0
url = "https://www.ifrc.org/appeals?page={page}"
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


def extract_row(inp):
    row = [x.text.strip() for x in inp.find_all("td")]
    row[6] = str(datetime.strptime(row[6], "%d/%m/%Y").date())
    row.append(inp.find("td").find("a").get("href"))
    return dict(zip(*(headers, row)))


while True:
    r = requests.get(url.format(page=page))
    soup = bs(r.text, features="html.parser")
    tbody = soup.tbody
    if not tbody:
        break
    for row in tbody.find_all("tr"):
        rows.append(extract_row(row))
    time.sleep(0.5)
    page += 1


with open(join("output", "ifrc-appeals.csv"), "w") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
