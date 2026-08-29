import json
import urllib.request
import csv
import os

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

us_gaap = data["facts"]["us-gaap"]

rows = []

# Concepts we want to start with
metrics = {
    "RevenueFromContractWithCustomerExcludingAssessedTax": "Revenue",
    "CostOfGoodsAndServicesSold": "Cost of Revenue",
    "GrossProfit": "Gross Profit",
    "OperatingIncomeLoss": "Operating Income",
    "NetIncomeLoss": "Net Income",
    "Assets": "Total Assets",
    "Liabilities": "Total Liabilities",
    "StockholdersEquity": "Stockholders Equity",
    "CashAndCashEquivalentsAtCarryingValue": "Cash & Equivalents",
}

for tag, metric_name in metrics.items():

    if tag not in us_gaap:
        print(f"Not found: {tag}")
        continue

    concept = us_gaap[tag]
    units = concept.get("units", {})

    for unit, values in units.items():

        for item in values:

            # Only use 10-Q and 10-K filings
            if item.get("form") not in ["10-Q", "10-K"]:
                continue

            # We only want Apple's current filing
            rows.append([
                TICKER,
                item.get("fy"),
                item.get("fp"),
                item.get("start", ""),
                item.get("end", ""),
                item.get("filed"),
                item.get("form"),
                metric_name,
                item.get("val"),
                unit,
                item.get("accn"),
                item.get("frame", "")
            ])

# Create data directory
os.makedirs("data", exist_ok=True)

output_file = "data/AAPL.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Ticker",
        "Fiscal Year",
        "Fiscal Period",
        "Start Date",
        "End Date",
        "Filing Date",
        "Form",
        "Metric",
        "Value",
        "Unit",
        "Accession",
        "Frame"
    ])

    writer.writerows(rows)

print(f"\nCreated {output_file}")
print(f"Rows written: {len(rows)}")
