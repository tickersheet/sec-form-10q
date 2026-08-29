import json
import urllib.request

CIK = "0000320193"
TICKER = "AAPL"

URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

# Identify ourselves to the SEC
request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "TickerSheet sec-financial-data tickersheet@gmail.com"
    }
)

with urllib.request.urlopen(request) as response:
    data = json.load(response)

print(f"Company: {data['entityName']}")
print(f"Facts found: {len(data['facts'])}")

# Look at the US-GAAP facts
us_gaap = data["facts"]["us-gaap"]

print(f"US-GAAP concepts: {len(us_gaap)}")

# Look for Revenue
if "Revenues" in us_gaap:
    revenue = us_gaap["Revenues"]

    print("\nRevenue:")
    print(json.dumps(revenue, indent=2)[:5000])
