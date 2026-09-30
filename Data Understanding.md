# Data Understanding

## Dataset Overview

The project uses five operational datasets covering different areas of Bean there Done That's business operations.

| Dataset | Rows | Columns |
|---|---:|---:|
| Raw Material Inventory | 72 | 10 |
| Finished Product Inventory | 36 | 8 |
| Roasting | 36 | 15 |
| E-commerce Sales | 240,352 | 9 |
| B2B Orders | 273 | 8 |

### Raw Material Inventory

Contains information about raw materials, suppliers, monthly stock levels, scrapped materials, unit prices, stock value and purchases.

### Finished Product Inventory

Contains monthly information about finished coffee products, stock levels, scrapped products, reason codes, unit prices and stock value.

The products are:

- Dark Roast
- Medium Roast
- Light Roast

### Roasting

Contains information about the roasting machines, production activity, batch quantities, production times and quality failures.

The machines are:

- Probat P60
- Probat Px120

### E-commerce Sales

Contains sales information including product, bag type, quantity, sales value, order date, delivery date, delivery fee, shipping costs and destination province.

### B2B Orders

Contains information about B2B customers, cities, products, quantities, sales value, delivery dates and shipping costs.

---

## Data Quality

An initial data quality check was performed using Python.

### Missing Values

Missing values were found only in the `Reasoncode` fields:

- Raw Material Inventory: 68 missing values
- Finished Product Inventory: 30 missing values

The other fields contain no missing values.

The missing reason codes are not automatically treated as errors because a missing reason code may indicate that no reason for scrapping was recorded.

### Duplicate Records

No duplicate rows were found in:

- Raw Material Inventory
- Finished Product Inventory
- Roasting
- B2B Orders

The e-commerce dataset contains 119,101 exact duplicate rows. The duplicates are present throughout the year rather than being concentrated in a single month. Since the dataset does not contain a unique order ID, it is not possible to determine whether identical records represent duplicated data or separate transactions. Therefore, the records are retained for the initial analysis and the limitation is considered when interpreting the results.

---

## Data Types

The datasets contain:

- Categorical variables such as product, supplier, machine, customer and province.
- Numerical variables such as quantity, stock level, sales value, stock value and production measures.
- Date variables in the e-commerce and B2B datasets.

The date fields in the E-commerce Sales dataset were converted to datetime format in Python to allow delivery-time calculations and time-based analysis.

---

## Initial KPI Analysis

The first analysis produced the following descriptive results:

| Area | KPI | Result |
|---|---|---:|
| E-commerce | Sales records | 240,352 |
| E-commerce | Quantity sold | 1,208,471 |
| E-commerce | Sales value | €17,561,219.89 |
| E-commerce | Average delivery time | 1.59 days |
| B2B | Sales records | 273 |
| B2B | Quantity sold | 16,280 |
| B2B | Sales value | €421,652 |
| Production | Total batches | 11,838 |
| Production | Production output | 795,671.2 kg |
| Production | Rejected batches | 224 |
| Production | Rejection rate | 1.89% |
| Inventory | Raw material stock value | €8,331,132.20 |
| Inventory | Finished product stock value | €15,243,531.20 |
| Inventory | Raw material scrapped | 20,040 |
| Inventory | Finished product scrapped | 48,000 |

> **Note:** The e-commerce and B2B datasets do not contain an explicit order ID. Therefore, the number of rows is currently reported as **sales records** rather than unique orders.
