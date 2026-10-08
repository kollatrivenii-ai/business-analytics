# Business Analytics Project

A simple base project in Python that analyses sales data: cleaning, KPIs,
monthly/region/product/category analysis, charts and a text report.

## Setup
    pip install -r requirements.txt

## Run
    python business_analytics.py                 # uses generated sample data
    python business_analytics.py my_sales.csv    # uses your own CSV

## CSV format
Columns: Date, Region, Category, Product, Quantity, UnitPrice, UnitCost
(see sample_sales_data.csv)

## Output (saved in ./output)
- monthly_trend.png, revenue_by_region.png, profit_by_product.png, category_share.png
- cleaned_data.csv, monthly_summary.csv, region_summary.csv, product_summary.csv
- report.txt
