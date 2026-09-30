import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# ============================================================
# 1. LOAD DATA
# ============================================================

file_path = "Bean there done that data.xlsx"

excel_file = pd.ExcelFile(file_path)

print("Available datasets:")
print(excel_file.sheet_names)


# ============================================================
# 2. LOAD DATASETS
# ============================================================

raw_inventory = pd.read_excel(
    file_path,
    sheet_name="Inventory (raw material)"
)

finished_inventory = pd.read_excel(
    file_path,
    sheet_name="Inventory (finished product)"
)

roasting = pd.read_excel(
    file_path,
    sheet_name="Roasting"
)

ecommerce = pd.read_excel(
    file_path,
    sheet_name="E-com sales orders by product"
)

b2b = pd.read_excel(
    file_path,
    sheet_name="B2B orders"
)


# ============================================================
# 3. DATASET OVERVIEW
# ============================================================

datasets = {
    "Raw Material Inventory": raw_inventory,
    "Finished Product Inventory": finished_inventory,
    "Roasting": roasting,
    "E-commerce Sales": ecommerce,
    "B2B Orders": b2b
}

print("\nDATASET OVERVIEW")
print("================")

for name, data in datasets.items():
    print(f"\n{name}")
    print(f"Rows: {data.shape[0]}")
    print(f"Columns: {data.shape[1]}")


# ============================================================
# 4. MISSING VALUES
# ============================================================

print("\n\nMISSING VALUES")
print("==============")

for name, data in datasets.items():
    print(f"\n{name}")
    print(data.isna().sum())


# ============================================================
# 5. DUPLICATES
# ============================================================

print("\n\nDUPLICATES")
print("==========")

for name, data in datasets.items():
    print(f"{name}: {data.duplicated().sum()} duplicate rows")


# ============================================================
# 6. DATA TYPES
# ============================================================

print("\n\nDATA TYPES")
print("==========")

for name, data in datasets.items():
    print(f"\n{name}")
    print(data.dtypes)


# ============================================================
# 7. DESCRIPTIVE STATISTICS
# ============================================================

print("\n\nDESCRIPTIVE STATISTICS")
print("======================")

for name, data in datasets.items():
    print(f"\n{name}")
    print(data.describe(include="all"))
