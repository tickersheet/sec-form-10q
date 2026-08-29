import json
import urllib.request

CIK = "0000320193"
TICKER = "AAPL"

URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "TickerSheet sec-financial-data tickersheet@gmail.com"
    }
)

with urllib.request.urlopen(request) as response:
    data = json.load(response)

print(f"Company: {data['entityName']}")
print(f"Taxonomies found: {list(data['facts'].keys())}")

us_gaap = data["facts"]["us-gaap"]

print(f"US-GAAP concepts: {len(us_gaap)}")

print("\n--- Revenue-related concepts ---")

for tag, concept in us_gaap.items():

    label = concept.get("label") or ""
    description = concept.get("description") or ""

    text = (
        tag
        + " "
        + label
        + " "
        + description
    ).lower()

    if "revenue" in text:

        print(
            f"{tag} → {label}"
        )
