"""
Business Analytics - Simple Base Project
-----------------------------------------
What it does:
  1. Loads sales data from a CSV (or generates sample data if none is given)
  2. Cleans the data
  3. Calculates key business KPIs
  4. Analyses sales by month, region, product and category
  5. Saves charts (PNG), a summary CSV and a text report to ./output

Usage:
  python business_analytics.py                 # uses generated sample data
  python business_analytics.py my_sales.csv    # uses your own CSV

Your CSV should have these columns:
  Date, Region, Category, Product, Quantity, UnitPrice, UnitCost
Install requirements:
  pip install pandas numpy matplotlib
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # works without a display
import matplotlib.pyplot as plt

OUTPUT_DIR = "output"


# ---------------------------------------------------------------------------
# 1. DATA
# ---------------------------------------------------------------------------
def generate_sample_data(n=1500, seed=42):
    """Create a realistic sample sales dataset."""
    rng = np.random.default_rng(seed)
    products = {
        "Laptop": ("Electronics", 55000, 42000),
        "Smartphone": ("Electronics", 25000, 19000),
        "Headphones": ("Electronics", 3000, 1800),
        "Office Chair": ("Furniture", 7000, 4500),
        "Desk": ("Furniture", 12000, 8000),
        "Notebook": ("Stationery", 120, 60),
        "Pen Pack": ("Stationery", 250, 120),
    }
    regions = ["North", "South", "East", "West"]
    names = list(products)

    dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(
        rng.integers(0, 365, n), unit="D"
    )
    chosen = rng.choice(names, n)
    df = pd.DataFrame(
        {
            "Date": dates,
            "Region": rng.choice(regions, n, p=[0.25, 0.30, 0.20, 0.25]),
            "Category": [products[p][0] for p in chosen],
            "Product": chosen,
            "Quantity": rng.integers(1, 10, n),
            "UnitPrice": [products[p][1] for p in chosen],
            "UnitCost": [products[p][2] for p in chosen],
        }
    )
    return df.sort_values("Date").reset_index(drop=True)


def load_data(path=None):
    if path and os.path.exists(path):
        print(f"Loading data from {path}")
        return pd.read_csv(path)
    print("No CSV provided - using generated sample data.")
    return generate_sample_data()


def clean_data(df):
    """Basic cleaning + derived columns."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date", "Quantity", "UnitPrice", "UnitCost"])
    df = df.drop_duplicates()
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["Cost"] = df["Quantity"] * df["UnitCost"]
    df["Profit"] = df["Revenue"] - df["Cost"]
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df


# ---------------------------------------------------------------------------
# 2. ANALYSIS
# ---------------------------------------------------------------------------
def calculate_kpis(df):
    revenue = df["Revenue"].sum()
    profit = df["Profit"].sum()
    return {
        "Total Revenue": revenue,
        "Total Cost": df["Cost"].sum(),
        "Total Profit": profit,
        "Profit Margin (%)": profit / revenue * 100 if revenue else 0,
        "Total Orders": len(df),
        "Units Sold": int(df["Quantity"].sum()),
        "Average Order Value": revenue / len(df) if len(df) else 0,
    }


def group_summary(df, column):
    out = (
        df.groupby(column)
        .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Units=("Quantity", "sum"))
        .sort_values("Revenue", ascending=False)
    )
    out["Margin (%)"] = out["Profit"] / out["Revenue"] * 100
    return out


def monthly_summary(df):
    m = df.groupby("Month").agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    m["Growth (%)"] = m["Revenue"].pct_change() * 100
    return m


# ---------------------------------------------------------------------------
# 3. CHARTS
# ---------------------------------------------------------------------------
def make_charts(monthly, by_region, by_product, by_category):
    # Monthly trend
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly.index, monthly["Revenue"], marker="o", label="Revenue")
    ax.plot(monthly.index, monthly["Profit"], marker="s", label="Profit")
    ax.set_title("Monthly Revenue & Profit")
    ax.set_ylabel("Amount")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/monthly_trend.png", dpi=150)
    plt.close(fig)

    # Revenue by region
    fig, ax = plt.subplots(figsize=(7, 5))
    by_region["Revenue"].plot(kind="bar", ax=ax, color="#4C78A8")
    ax.set_title("Revenue by Region")
    ax.set_ylabel("Revenue")
    plt.xticks(rotation=0)
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/revenue_by_region.png", dpi=150)
    plt.close(fig)

    # Top products
    fig, ax = plt.subplots(figsize=(8, 5))
    by_product["Profit"].sort_values().plot(kind="barh", ax=ax, color="#54A24B")
    ax.set_title("Profit by Product")
    ax.set_xlabel("Profit")
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/profit_by_product.png", dpi=150)
    plt.close(fig)

    # Category share
    fig, ax = plt.subplots(figsize=(6, 6))
    by_category["Revenue"].plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    ax.set_title("Revenue Share by Category")
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/category_share.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. REPORT
# ---------------------------------------------------------------------------
def write_report(kpis, monthly, by_region, by_product, by_category):
    best_month = monthly["Revenue"].idxmax()
    worst_month = monthly["Revenue"].idxmin()
    lines = ["BUSINESS ANALYTICS REPORT", "=" * 40, "", "KEY METRICS"]
    for k, v in kpis.items():
        lines.append(f"  {k:<22}: {v:,.2f}")
    lines += [
        "",
        "INSIGHTS",
        f"  Best month        : {best_month} ({monthly.loc[best_month, 'Revenue']:,.0f})",
        f"  Weakest month     : {worst_month} ({monthly.loc[worst_month, 'Revenue']:,.0f})",
        f"  Top region        : {by_region.index[0]}",
        f"  Top product       : {by_product.index[0]}",
        f"  Top category      : {by_category.index[0]}",
        f"  Most profitable   : {by_product['Profit'].idxmax()}",
        f"  Highest margin    : {by_product['Margin (%)'].idxmax()}",
        "",
        "REVENUE BY REGION",
        by_region.round(2).to_string(),
        "",
        "REVENUE BY PRODUCT",
        by_product.round(2).to_string(),
    ]
    report = "\n".join(lines)
    with open(f"{OUTPUT_DIR}/report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    return report


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = sys.argv[1] if len(sys.argv) > 1 else None

    df = clean_data(load_data(path))
    df.to_csv(f"{OUTPUT_DIR}/cleaned_data.csv", index=False)

    kpis = calculate_kpis(df)
    monthly = monthly_summary(df)
    by_region = group_summary(df, "Region")
    by_product = group_summary(df, "Product")
    by_category = group_summary(df, "Category")

    monthly.to_csv(f"{OUTPUT_DIR}/monthly_summary.csv")
    by_region.to_csv(f"{OUTPUT_DIR}/region_summary.csv")
    by_product.to_csv(f"{OUTPUT_DIR}/product_summary.csv")

    make_charts(monthly, by_region, by_product, by_category)
    print(write_report(kpis, monthly, by_region, by_product, by_category))
    print(f"\nDone! Files saved in the '{OUTPUT_DIR}/' folder.")


if __name__ == "__main__":
    main()
