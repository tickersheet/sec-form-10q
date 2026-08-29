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

# Metrics we want
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

rows = []

for tag, metric_name in metrics.items():

    if tag not in us_gaap:
        print(f"Not found: {tag}")
        continue

    concept = us_gaap[tag]
    units = concept.get("units", {})

    for unit, values in units.items():

        for item in values:

            form = item.get("form")

            if form not in ["10-Q", "10-K"]:
                continue

            fy = item.get("fy")
            fp = item.get("fp")
            start = item.get("start")
            end = item.get("end")
            filed = item.get("filed")

            # Determine period type
            period_type = ""

            if start and end:

                from datetime import date

                start_date = date.fromisoformat(start)
                end_date = date.fromisoformat(end)

                days = (end_date - start_date).days

                if days <= 110:
                    period_type = "Quarter"

                elif days <= 200:
                    period_type = "YTD"

                elif days <= 400:
                    period_type = "Annual"

            else:
                # Balance sheet facts have no start date
                period_type = "Instant"

            rows.append([
                TICKER,
                fy,
                fp,
                period_type,
                start or "",
                end or "",
                filed,
                form,
                metric_name,
                item.get("val"),
                unit,
                item.get("accn"),
                item.get("frame", "")
            ])


# Create data folder
os.makedirs("data", exist_ok=True)

output_file = "data/AAPL.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Ticker",
        "Fiscal Year",
        "Fiscal Period",
        "Period Type",
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
