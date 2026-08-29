import json
import urllib.request

CIK = "0000320193"

URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "TickerSheet sec-financial-data tickersheet@gmail.com"
    }
)

with urllib.request.urlopen(request) as response:
    data = json.load(response)

us_gaap = data["facts"]["us-gaap"]

tag = "RevenueFromContractWithCustomerExcludingAssessedTax"

concept = us_gaap[tag]

print("APPLE REVENUE — Q3 2026 FILING")
print("=" * 60)

for unit, values in concept["units"].items():

    for item in values:

        if item.get("accn") == "0000320193-26-000020":

            print(item)
