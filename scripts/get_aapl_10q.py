import json
import urllib.request
import csv
import os
from datetime import date

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

# Financial metrics to extract
metrics = {
    "RevenueFromContractWithCustomerExcludingAssessedTax": "Revenue",
    "CostOfGoodsAndServicesSold": "Cost of Revenue",
    "GrossProfit": "Gross Profit",
    "ResearchAndDevelopmentExpense": "R&D",
    "SellingGeneralAndAdministrativeExpense": "SG&A",
    "OperatingIncomeLoss": "Operating Income",
    "InterestExpenseNonOperating": "Interest Expense",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "Pre-Tax Income",
    "IncomeTaxExpenseBenefit": "Income Tax",
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
            accession = item.get("accn")
            frame = item.get("frame", "")
            value = item.get("val")

            # Determine whether this is an instant or duration fact
            if not start or not end:

                period_type = "Instant"

            else:

                start_date = date.fromisoformat(start)
                end_date = date.fromisoformat(end)

                days = (end_date - start_date).days

                if days <= 110:
                    period_type = "Quarter"

                elif days <= 200:
                    period_type = "YTD"

                else:
                    period_type = "Annual"

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
                tag,
                value,
                unit,
                accession,
                frame
            ])


# ---------------------------------------------------------
# Remove exact duplicate rows
# ---------------------------------------------------------

unique_rows = []
seen = set()

for row in rows:

    key = tuple(row)

    if key not in seen:
        seen.add(key)
        unique_rows.append(row)

rows = unique_rows


# ---------------------------------------------------------
# Sort the data
# ---------------------------------------------------------

rows.sort(
    key=lambda x: (
        x[1] or 0,       # Fiscal year
        x[2] or "",      # Fiscal period
        x[5] or "",      # End date
        x[8] or ""       # Metric
    )
)


# ---------------------------------------------------------
# Write CSV
# ---------------------------------------------------------

os.makedirs("data", exist_ok=True)

output_file = f"data/{TICKER}.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Ticker",
        "Filing Fiscal Year",
        "Filing Fiscal Period",
        "Period Type",
        "Start Date",
        "End Date",
        "Filing Date",
        "Form",
        "Metric",
        "XBRL Tag",
        "Value",
        "Unit",
        "Accession",
        "Frame"
    ])

    writer.writerows(rows)


print()
print("=" * 60)
print(f"Created {output_file}")
print(f"Rows written: {len(rows)}")
print("=" * 60)
