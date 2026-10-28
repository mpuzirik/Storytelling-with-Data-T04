"""Bean There Done That - reproducible KPI analysis for the T04 assessment.

Run from the folder containing 'Bean there done that data.xlsx':
    python bean_there_done_that_analysis.py

Required: pandas, matplotlib, openpyxl
Outputs: analysis_outputs/figures/*.png, analysis_outputs/tables/*.csv,
         analysis_outputs/analysis_summary.md

Important: e-commerce records have no unique order ID; identical rows might
represent separate transactions. The all-rows analysis is the starting point,
and a deduplicated scenario is shown ONLY as a sensitivity check.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 1. Load the five datasets
# ------------------------------------------------------------------
BASE = Path(__file__).resolve().parent
WORKBOOK = BASE / "Bean there done that data.xlsx"
OUT = BASE / "analysis_outputs"
FIGURES = OUT / "figures"
TABLES = OUT / "tables"
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

if not WORKBOOK.exists():
    raise FileNotFoundError(f"Put the Excel workbook beside this script: {WORKBOOK}")

SHEETS = {
    "raw": "Inventory (raw material)",
    "finished": "Inventory (finished product)",
    "roasting": "Roasting",
    "ecommerce": "E-com sales orders by product",
    "b2b": "B2B orders",
}
data = pd.read_excel(WORKBOOK, sheet_name=list(SHEETS.values()))
raw, finished, roasting, ecommerce, b2b = [data[s].copy() for s in SHEETS.values()]

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def ordered_months(df, month_col="Month"):
    """Aggregate-ready frame with months ordered January to December."""
    result = df.copy()
    result[month_col] = pd.Categorical(
        result[month_col], categories=MONTHS, ordered=True
    )
    return result


def export_table(df, filename):
    df.to_csv(TABLES / filename, index=False, encoding="utf-8-sig")


def save_plot(name, title, xlabel="", ylabel=""):
    plt.title(title, pad=13)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=40, ha="right")
    plt.grid(axis="y", alpha=0.15)
    plt.tight_layout()
    plt.savefig(FIGURES / name, dpi=160, bbox_inches="tight")
    plt.close()


print("DATASET OVERVIEW")
for key, sheet in SHEETS.items():
    df = data[sheet]
    print(f"{key}: {len(df):,} rows, {len(df.columns)} columns; "
          f"missing cells: {df.isna().sum().sum():,}; "
          f"exact duplicate rows: {df.duplicated().sum():,}")

# ------------------------------------------------------------------
# 2. E-commerce sales, product demand, duplicates and delivery
# ------------------------------------------------------------------
ecommerce["Order date"] = pd.to_datetime(ecommerce["Order date"], errors="coerce")
ecommerce["Delivery date"] = pd.to_datetime(ecommerce["Delivery date"], errors="coerce")
ecommerce["Delivery days"] = (
    ecommerce["Delivery date"] - ecommerce["Order date"]
).dt.days

if ecommerce["Order date"].isna().any():
    raise ValueError("Some e-commerce order dates could not be read.")

invalid_delivery = ecommerce["Delivery days"].isna() | (ecommerce["Delivery days"] < 0)
if invalid_delivery.any():
    print(f"WARNING: {invalid_delivery.sum():,} invalid delivery intervals excluded.")

ecom_valid = ecommerce.loc[~invalid_delivery].copy()
ecommerce["Month"] = ecommerce["Order date"].dt.month
# Remove exact duplicates on ORIGINAL source columns, before adding derived columns.
ecommerce_unique = ecommerce.drop_duplicates(
    subset=["Product", "Bag type", "Quantity", "Value", "Order date",
            "Delivery date", "Delivery fee", "Shipping costs", "Ship to (province)"]
).copy()
ecommerce_unique["Month"] = ecommerce_unique["Order date"].dt.month

monthly_sales = ecommerce.groupby("Month", as_index=False).agg(
    sales_records=("Value", "size"), quantity_bags=("Quantity", "sum"),
    sales_eur=("Value", "sum"), shipping_cost_eur=("Shipping costs", "sum"),
    customer_delivery_fees_eur=("Delivery fee", "sum"),
)
monthly_sales["Month name"] = monthly_sales["Month"].map(
    dict(enumerate(MONTHS, start=1))
)
monthly_unique = ecommerce_unique.groupby("Month", as_index=False).agg(
    sensitivity_sales_eur=("Value", "sum"),
    sensitivity_records=("Value", "size"),
)
monthly_sales = monthly_sales.merge(monthly_unique, on="Month", how="left")
export_table(monthly_sales, "ecommerce_monthly.csv")

product_sales = ecommerce.groupby("Product", as_index=False).agg(
    sales_eur=("Value", "sum"), quantity_bags=("Quantity", "sum")
).sort_values("sales_eur", ascending=False)
export_table(product_sales, "ecommerce_by_product.csv")

bag_sales = ecommerce.groupby(["Product", "Bag type"], as_index=False).agg(
    quantity_bags=("Quantity", "sum"), sales_eur=("Value", "sum")
)
# Excel does not explicitly label bag type codes 1 and 2. Don't assume sizes here.
export_table(bag_sales, "ecommerce_by_product_and_bag_type.csv")

monthly_delivery = ecom_valid.groupby(ecom_valid["Order date"].dt.month).agg(
    avg_calendar_days=("Delivery days", "mean"),
    records=("Delivery days", "size"),
    pct_within_1_calendar_day=("Delivery days", lambda x: 100 * x.le(1).mean()),
).rename_axis("Month").reset_index()
monthly_delivery["Month name"] = monthly_delivery["Month"].map(
    dict(enumerate(MONTHS, start=1))
)
export_table(monthly_delivery, "ecommerce_delivery_monthly.csv")

# ------------------------------------------------------------------
# 3. Roasting: batches, output and quality by machine/month
# ------------------------------------------------------------------
# 'Number of batches per day' is the reported daily average, so multiply
# by workdays and round to the nearest whole batch.
roasting["Batches"] = (
    roasting["Workdays"] * roasting["Number of batches per day"]
).round().astype(int)
roasting["Output kg"] = roasting["Batches"] * roasting["Final weight /pbatch"]
roasting["Rejected batches"] = roasting["Total rejected batches p/month"]
roasting["Rejection rate %"] = (
    100 * roasting["Rejected batches"] / roasting["Batches"].replace(0, float("nan"))
)

machine_kpis = roasting.groupby("Machine", as_index=False).agg(
    batches=("Batches", "sum"), rejected_batches=("Rejected batches", "sum"),
    production_kg=("Output kg", "sum")
)
machine_kpis["rejection_rate_pct"] = (
    100 * machine_kpis["rejected_batches"] / machine_kpis["batches"]
)
export_table(machine_kpis, "roasting_by_machine.csv")

monthly_roasting = ordered_months(roasting).groupby(
    "Month", observed=True, as_index=False
).agg(production_kg=("Output kg", "sum"),
      batches=("Batches", "sum"), rejected_batches=("Rejected batches", "sum"))
monthly_roasting["rejection_rate_pct"] = (
    100 * monthly_roasting["rejected_batches"] / monthly_roasting["batches"]
)
export_table(monthly_roasting, "roasting_monthly.csv")

# The data does not state scheduled machine hours or how cooling/packing overlap
# with roasting, so genuine machine-capacity utilization CANNOT be confirmed.

# ------------------------------------------------------------------
# 4. Inventory: monthly snapshots and scrap by physical UNIT
# ------------------------------------------------------------------
# Stock value is a monthly snapshot. Summing all 12 months would overstate
# stock held at one point in time. Scrap is stored as NEGATIVE adjustments.
raw = ordered_months(raw)
finished = ordered_months(finished)
raw["Scrapped amount"] = raw["Scrapped"].abs()
finished["Scrapped amount"] = finished["Scrapped"].abs()

raw_monthly = raw.groupby("Month", observed=True, as_index=False).agg(
    inventory_value_eur=("Stock value", "sum")
)
finished_monthly = finished.groupby("Month", observed=True, as_index=False).agg(
    inventory_value_eur=("Stock value", "sum"),
    stock_kg=("Stock level", "sum"), scrapped_kg=("Scrapped amount", "sum")
)
raw_by_unit = raw.groupby(["Month", "Unit"], observed=True, as_index=False).agg(
    stock_amount=("Stock level", "sum"), scrapped_amount=("Scrapped amount", "sum"),
    purchased_amount=("Purchased", "sum")
)
raw_scrap_by_item = raw.groupby(["Product", "Unit"], as_index=False).agg(
    scrapped_amount=("Scrapped amount", "sum")
)
finished_by_product = finished.groupby("Product", as_index=False).agg(
    scrapped_kg=("Scrapped amount", "sum")
)
export_table(raw_monthly, "raw_inventory_monthly_value.csv")
export_table(raw_by_unit, "raw_inventory_by_unit_monthly.csv")
export_table(raw_scrap_by_item, "raw_scrap_by_item.csv")
export_table(finished_monthly, "finished_inventory_monthly.csv")
export_table(finished_by_product, "finished_scrap_by_product.csv")

# ------------------------------------------------------------------
# 5. B2B: delivery-month-based sales, products and customers
# ------------------------------------------------------------------
b2b["Delivery date"] = pd.to_datetime(b2b["Delivery date"], errors="coerce")
if b2b["Delivery date"].isna().any():
    raise ValueError("Some B2B delivery dates could not be read.")
b2b["Delivery month"] = b2b["Delivery date"].dt.month
b2b_monthly = b2b.groupby("Delivery month", as_index=False).agg(
    sales_records=("Value", "size"), sales_eur=("Value", "sum"),
    quantity_bags=("Quantity", "sum"), shipping_cost_eur=("Shipping costs", "sum")
)
b2b_monthly["Month name"] = b2b_monthly["Delivery month"].map(
    dict(enumerate(MONTHS, start=1))
)
b2b_customers = b2b.groupby("Customer", as_index=False).agg(
    sales_eur=("Value", "sum"), quantity_bags=("Quantity", "sum")
).sort_values("sales_eur", ascending=False)
export_table(b2b_monthly, "b2b_monthly_by_delivery_date.csv")
export_table(b2b_customers, "b2b_by_customer.csv")

# Illustrative growth scenario: proportional output requirement, not a capacity test.
# It does NOT establish that the roasting machines have enough free hours.
base_output_kg = roasting["Output kg"].sum()
growth_scenarios = pd.DataFrame({"illustrative_growth_pct": [0, 10, 20]})
growth_scenarios["required_output_kg_if_proportional"] = (
    base_output_kg * (1 + growth_scenarios["illustrative_growth_pct"] / 100)
)
growth_scenarios["additional_output_kg"] = (
    growth_scenarios["required_output_kg_if_proportional"] - base_output_kg
)
export_table(growth_scenarios, "illustrative_growth_output_scenarios.csv")

# ------------------------------------------------------------------
# 6. KPI summary: all figures are calculated, not typed by hand
# ------------------------------------------------------------------
total_batches = int(roasting["Batches"].sum())
rejected_batches = int(roasting["Rejected batches"].sum())
raw_december_eur = raw.loc[raw["Month"] == "December", "Stock value"].sum()
finished_december_eur = finished.loc[
    finished["Month"] == "December", "Stock value"
].sum()
raw_scrap_units = raw.groupby("Unit")["Scrapped amount"].sum().to_dict()

kpis = [
    ("E-commerce", "Sales records (not confirmed unique orders)", len(ecommerce), "records"),
    ("E-commerce", "Recorded sales", ecommerce["Value"].sum(), "EUR"),
    ("E-commerce", "Quantity sold", ecommerce["Quantity"].sum(), "bags"),
    ("E-commerce", "Exact duplicate rows", ecommerce.duplicated(subset=[
        "Product", "Bag type", "Quantity", "Value", "Order date",
        "Delivery date", "Delivery fee", "Shipping costs", "Ship to (province)"
    ]).sum(), "rows"),
    ("E-commerce", "Deduplicated sensitivity scenario sales", ecommerce_unique["Value"].sum(), "EUR"),
    ("E-commerce", "Average delivery time", ecom_valid["Delivery days"].mean(), "calendar days"),
    ("E-commerce", "Shipping costs", ecommerce["Shipping costs"].sum(), "EUR"),
    ("E-commerce", "Customer delivery fees", ecommerce["Delivery fee"].sum(), "EUR"),
    ("B2B", "Sales records (not confirmed unique orders)", len(b2b), "records"),
    ("B2B", "Sales", b2b["Value"].sum(), "EUR"),
    ("B2B", "Quantity sold", b2b["Quantity"].sum(), "bags"),
    ("B2B", "Shipping costs", b2b["Shipping costs"].sum(), "EUR"),
    ("Production", "Batches", total_batches, "batches"),
    ("Production", "Estimated production output", roasting["Output kg"].sum(), "kg (includes rejected batches)"),
    ("Production", "Rejected batches", rejected_batches, "batches"),
    ("Production", "Batch rejection rate", 100 * rejected_batches / total_batches, "%"),
    ("Inventory", "Raw-material December stock value", raw_december_eur, "EUR (snapshot)"),
    ("Inventory", "Finished-product December stock value", finished_december_eur, "EUR (snapshot)"),
    ("Inventory", "Finished-product December stock", finished.loc[
        finished["Month"] == "December", "Stock level"].sum(), "kg"),
    ("Waste", "Raw material scrapped (mass)", raw_scrap_units.get("Kg", 0), "kg"),
    ("Waste", "Raw material scrapped (packaging)", raw_scrap_units.get("Piece", 0), "pieces"),
    ("Waste", "Finished product scrapped", finished["Scrapped amount"].sum(), "kg"),
]
kpi_table = pd.DataFrame(kpis, columns=["Area", "KPI", "Value", "Unit / caveat"])
export_table(kpi_table, "kpi_summary.csv")

print("\nKEY KPIs")
print(kpi_table.to_string(index=False, formatters={"Value": "{:,.2f}".format}))
print("\nREJECTION BY MACHINE")
print(machine_kpis.to_string(index=False))

# ------------------------------------------------------------------
# 7. Presentation-oriented charts (PNG), with restrained design
# ------------------------------------------------------------------
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.figsize": (9, 4.6)})

plt.figure()
plt.plot(monthly_sales["Month name"], monthly_sales["sales_eur"] / 1e6,
         marker="o", label="All sales records")
plt.plot(monthly_sales["Month name"],
         monthly_sales["sensitivity_sales_eur"] / 1e6,
         marker="o", linestyle="--", label="Exact duplicates removed (sensitivity only)")
plt.legend(frameon=False)
save_plot("01_ecommerce_sales_sensitivity.png",
          "Monthly recorded e-commerce sales: duplicate treatment matters", "", "Sales value (€ million)")

plt.figure()
plt.bar(product_sales["Product"], product_sales["sales_eur"] / 1e6)
save_plot("02_ecommerce_sales_by_product.png",
          "E-commerce sales value by product", "", "Sales value (€ million)")

plt.figure()
plt.plot(monthly_roasting["Month"].astype(str),
         monthly_roasting["production_kg"] / 1000, marker="o")
save_plot("03_roasting_output_by_month.png",
          "Roasting output changes across the year", "", "Produced coffee (tonnes, incl. rejected)")

plt.figure()
plt.bar(machine_kpis["Machine"], machine_kpis["rejection_rate_pct"])
for i, value in enumerate(machine_kpis["rejection_rate_pct"]):
    plt.text(i, value + 0.05, f"{value:.2f}%", ha="center")
plt.ylim(0, machine_kpis["rejection_rate_pct"].max() * 1.25)
save_plot("04_rejection_rate_by_machine.png",
          "Recorded batch rejection rates differ by roaster", "", "Rejected batches (%)")

plt.figure()
plt.plot(finished_monthly["Month"].astype(str),
         finished_monthly["inventory_value_eur"] / 1e6, marker="o")
save_plot("05_finished_inventory_value_monthly.png",
          "Finished-product inventory value is a monthly snapshot", "", "Stock value (€ million)")

plt.figure()
plt.bar(finished_monthly["Month"].astype(str),
        finished_monthly["scrapped_kg"] / 1000)
save_plot("06_finished_product_scrapping.png",
          "Finished-product scrapping is recorded in June-August", "", "Scrapped finished coffee (tonnes)")

plt.figure()
plt.plot(monthly_delivery["Month name"],
         monthly_delivery["avg_calendar_days"], marker="o")
save_plot("07_ecommerce_delivery_days.png",
          "Average e-commerce delivery time rises in December", "", "Average calendar days")

plt.figure()
plt.plot(raw_monthly["Month"].astype(str),
         raw_monthly["inventory_value_eur"] / 1e6, marker="o")
save_plot("08_raw_inventory_value_monthly.png",
          "Raw-material inventory value varies by month", "", "Stock value (€ million)")

plt.figure()
plt.plot(b2b_monthly["Month name"], b2b_monthly["sales_eur"] / 1000,
         marker="o")
save_plot("09_b2b_sales_by_delivery_month.png",
          "B2B sales by recorded delivery month", "", "Sales value (€ thousand)")

# ------------------------------------------------------------------
# 8. Short evidence-based findings for the final CEO presentation
# ------------------------------------------------------------------
max_delivery = monthly_delivery.loc[monthly_delivery["avg_calendar_days"].idxmax()]
max_scrap = finished_monthly.loc[finished_monthly["scrapped_kg"].idxmax()]
summary = f"""# Bean There Done That - verified analysis summary

## Recorded operational results
- E-commerce: {len(ecommerce):,} sales records and EUR {ecommerce['Value'].sum():,.2f} recorded sales.
- E-commerce quantity: {ecommerce['Quantity'].sum():,} bags (the bag-type codes are not explicitly defined in the Excel sheet).
- Exact duplicate e-commerce rows: {len(ecommerce) - len(ecommerce_unique):,}. It is UNKNOWN whether they are errors or repeat transactions because no order ID exists.
- Sensitivity scenario if all exact duplicates are removed: EUR {ecommerce_unique['Value'].sum():,.2f}. **Not an independently verified revenue figure.**
- B2B: {len(b2b):,} records, EUR {b2b['Value'].sum():,.2f} sales.
- Production: {roasting['Output kg'].sum():,.1f} kg gross calculated output, based on reported batch-average final weight (before excluding rejected batches).
- Batch rejection: {rejected_batches:,} of {total_batches:,}, or {100 * rejected_batches / total_batches:.2f}%.
- Finished-product scrapping: {finished['Scrapped amount'].sum():,.0f} kg (the Excel sheet encodes scrap as negative inventory adjustments).
- Raw-material scrap: {raw_scrap_units.get('Kg', 0):,.0f} kg of beans and {raw_scrap_units.get('Piece', 0):,.0f} packaging pieces. Do NOT add kg and pieces together.
- December stock value: EUR {raw_december_eur:,.2f} of raw materials and EUR {finished_december_eur:,.2f} of finished products. Values are month-end snapshots, not sums across the year.
- Average e-commerce delivery: {ecom_valid['Delivery days'].mean():.2f} calendar days; worst monthly average: {max_delivery['Month name']} ({max_delivery['avg_calendar_days']:.2f} days).

## Initial observations and possible management actions
1. Investigate why the Probat Px120 has a higher recorded batch rejection percentage. The files do not establish the reason or whether operating conditions are comparable.
2. Investigate finished-product scrapping, especially the period June-August; largest monthly amount is {max_scrap['Month']} ({max_scrap['scrapped_kg']:,.0f} kg). Reason code EXP appears on the scrap rows and indicates expiration under the dataset's convention.
3. Resolve or document the uncertain e-commerce transaction identity before trusting total sales values or growth projections.
4. Review delivery performance in December and assess the holiday/weekend delivery promise separately from simple calendar-day averages.
5. Check production utilization only after confirming scheduled shift hours, machine availability and whether process times overlap. This workbook alone does not prove available spare capacity.
6. A higher sales period alone does not prove that it caused delivery delays.

## Interpretation safeguards
- Counts of sales rows are *not* counts of unique orders.
- E-commerce monthly trends refer to **order dates**, while B2B sales trends use **delivery dates** (no B2B order date provided).
- E-commerce delivery time uses calendar days, not an adjusted business-day SLA.
- Inventory stock values are monthly snapshots; summing them across 12 months is not an end-of-year inventory value.
- Gross roasting output includes the nominal weight of batches later rejected; it is not confirmed saleable output.
- Without work schedule/capacity assumptions, growth readiness cannot be proved by production numbers alone.
- The illustrative 10% and 20% growth scenarios assume proportional production demand; they are neither forecasts nor proven feasible capacity.
"""
(OUT / "analysis_summary.md").write_text(summary, encoding="utf-8")

print("\nFINISHED. Review these outputs:")
print(f"  {TABLES / 'kpi_summary.csv'}")
print(f"  {OUT / 'analysis_summary.md'}")
print(f"  {FIGURES}  (9 PNG charts)")
