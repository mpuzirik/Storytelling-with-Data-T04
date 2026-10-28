# Data Understanding

## Dataset Overview

The project uses five operational datasets covering different areas of Bean There Done That's business operations during 2023.

| Dataset | Rows | Columns |
|---|---:|---:|
| Raw Material Inventory | 72 | 10 |
| Finished Product Inventory | 36 | 8 |
| Roasting | 36 | 15 |
| E-commerce Sales | 240,352 | 9 |
| B2B Orders | 273 | 8 |

### Raw Material Inventory

Contains information about raw materials, suppliers, monthly stock levels, scrapped materials, unit prices, stock value and purchases.

Raw materials include coffee beans and packaging materials, which are measured using different units.

### Finished Product Inventory

Contains monthly information about finished coffee products, stock levels, scrapped products, reason codes, unit prices and stock value.

The products are:

- Dark Roast
- Medium Roast
- Light Roast

Finished product stock and scrapping are measured in kilograms.

### Roasting

Contains information about roasting machines, production activity, batch quantities, production times and quality failures.

The machines are:

- Probat P60
- Probat Px120

The dataset allows us to calculate estimated production output, total batches, rejected batches and rejection rates.

### E-commerce Sales

Contains sales information including product, bag type, quantity, sales value, order date, delivery date, delivery fee, shipping costs and destination province.

The dataset contains sales records without unique order IDs.

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

The missing reason codes are not automatically treated as errors because the field may only be relevant when scrapping occurs.

### Duplicate Records

No exact duplicate rows were found in:

- Raw Material Inventory
- Finished Product Inventory
- Roasting
- B2B Orders

The e-commerce dataset contains 
