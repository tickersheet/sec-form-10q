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
print("\n--- Investment-related concepts ---")

for tag, concept in us_gaap.items():

    label = concept.get("label") or ""

    if any(word in tag.lower() for word in [
        "investment",
        "marketable",
        "securities"
    ]) or any(word in label.lower() for word in [
        "investment",
        "marketable",
        "securities"
    ]):

        print(f"{tag} → {label}")
# Financial metrics to extract
# ---------------------------------------------------------
# Financial metrics
# ---------------------------------------------------------

metrics = {

    # =========================
    # INCOME STATEMENT
    # =========================

    "Revenue": {
        "statement": "Income Statement",
        "tags": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet"
        ]
    },

    "Cost of Revenue": {
        "statement": "Income Statement",
        "tags": [
            "CostOfGoodsAndServicesSold",
            "CostOfRevenue"
        ]
    },

    "Gross Profit": {
        "statement": "Income Statement",
        "tags": [
            "GrossProfit"
        ]
    },

    "R&D": {
        "statement": "Income Statement",
        "tags": [
            "ResearchAndDevelopmentExpense"
        ]
    },

    "SG&A": {
        "statement": "Income Statement",
        "tags": [
            "SellingGeneralAndAdministrativeExpense"
        ]
    },

    "Operating Income": {
        "statement": "Income Statement",
        "tags": [
            "OperatingIncomeLoss"
        ]
    },

    "Interest Expense": {
        "statement": "Income Statement",
        "tags": [
            "InterestExpenseNonOperating",
            "InterestExpenseDebt"
        ]
    },

    "Pre-Tax Income": {
        "statement": "Income Statement",
        "tags": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
        ]
    },

    "Income Tax": {
        "statement": "Income Statement",
        "tags": [
            "IncomeTaxExpenseBenefit"
        ]
    },

    "Net Income": {
        "statement": "Income Statement",
        "tags": [
            "NetIncomeLoss",
            "ProfitLoss"
        ]
    },


    # =========================
    # BALANCE SHEET
    # =========================

    "Cash & Equivalents": {
        "statement": "Balance Sheet",
        "tags": [
            "CashAndCashEquivalentsAtCarryingValue"
        ]
    },

    "Short-Term Investments": {
    "statement": "Balance Sheet",
    "tags": [
        "MarketableSecuritiesCurrent",
        "AvailableForSaleSecuritiesCurrent"
    ]
},

    "Accounts Receivable": {
        "statement": "Balance Sheet",
        "tags": [
            "AccountsReceivableNetCurrent"
        ]
    },

    "Inventory": {
        "statement": "Balance Sheet",
        "tags": [
            "InventoryNet"
        ]
    },

    "Current Assets": {
        "statement": "Balance Sheet",
        "tags": [
            "AssetsCurrent"
        ]
    },

    "PP&E": {
        "statement": "Balance Sheet",
        "tags": [
            "PropertyPlantAndEquipmentNet"
        ]
    },

    "Goodwill": {
        "statement": "Balance Sheet",
        "tags": [
            "Goodwill"
        ]
    },

    "Intangible Assets": {
        "statement": "Balance Sheet",
        "tags": [
            "FiniteLivedIntangibleAssetsNet",
            "FiniteLivedIntangibleAssetsNetExcludingGoodwill"
        ]
    },

    "Total Assets": {
        "statement": "Balance Sheet",
        "tags": [
            "Assets"
        ]
    },

    "Accounts Payable": {
        "statement": "Balance Sheet",
        "tags": [
            "AccountsPayableCurrent"
        ]
    },

    "Current Liabilities": {
        "statement": "Balance Sheet",
        "tags": [
            "LiabilitiesCurrent"
        ]
    },

    "Long-Term Debt": {
        "statement": "Balance Sheet",
        "tags": [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent"
        ]
    },

    "Total Liabilities": {
        "statement": "Balance Sheet",
        "tags": [
            "Liabilities"
        ]
    },

    "Stockholders Equity": {
        "statement": "Balance Sheet",
        "tags": [
            "StockholdersEquity"
        ]
    },


    # =========================
    # CASH FLOW
    # =========================

    "Operating Cash Flow": {
        "statement": "Cash Flow",
        "tags": [
            "NetCashProvidedByUsedInOperatingActivities"
        ]
    },

    "Capital Expenditures": {
        "statement": "Cash Flow",
        "tags": [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets"
        ]
    },

    "Investing Cash Flow": {
        "statement": "Cash Flow",
        "tags": [
            "NetCashProvidedByUsedInInvestingActivities"
        ]
    },

    "Financing Cash Flow": {
        "statement": "Cash Flow",
        "tags": [
            "NetCashProvidedByUsedInFinancingActivities"
        ]
    },


    # =========================
    # PER SHARE
    # =========================

    "Basic EPS": {
        "statement": "Per Share",
        "tags": [
            "EarningsPerShareBasic"
        ]
    },

    "Diluted EPS": {
        "statement": "Per Share",
        "tags": [
            "EarningsPerShareDiluted"
        ]
    },

    "Basic Shares": {
        "statement": "Per Share",
        "tags": [
            "WeightedAverageNumberOfSharesOutstandingBasic"
        ]
    },

    "Diluted Shares": {
        "statement": "Per Share",
        "tags": [
            "WeightedAverageNumberOfDilutedSharesOutstanding"
        ]
    },

    "Dividends": {
        "statement": "Per Share",
        "tags": [
            "CommonStockDividendsPerShareDeclared"
        ]
    }
}

rows = []

for metric_name, metric_info in metrics.items():

    statement = metric_info["statement"]

    # Find the first available XBRL tag
    selected_tag = None

    for tag in metric_info["tags"]:

        if tag in us_gaap:
            selected_tag = tag
            break

    if selected_tag is None:
        print(f"Not found: {metric_name}")
        continue

    concept = us_gaap[selected_tag]
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

            # Determine period type
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
                statement,
                metric_name,
                selected_tag,
                fy,
                fp,
                period_type,
                start or "",
                end or "",
                filed,
                form,
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
    "Statement",
    "Metric",
    "XBRL Tag",
    "Filing Fiscal Year",
    "Filing Fiscal Period",
    "Period Type",
    "Start Date",
    "End Date",
    "Filing Date",
    "Form",
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
