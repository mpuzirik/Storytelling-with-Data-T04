# Bean There Done That - Storytelling with Data

## Project Overview

This project analyses the operational performance of Bean There Done That, a small Dutch coffee roaster.

The company wants to understand whether its current operations can support further growth and which operational improvements may be needed before expanding.

The project follows the CRISP-DM approach and focuses on data understanding, KPI analysis, data visualization and storytelling.

## Main Business Question

Is Bean There Done That operationally ready to grow next year, and which operational improvements are needed before expanding?

## Areas of Analysis

The analysis covers:

- Sourcing
- Production
- Warehouse operations
- E-commerce sales
- B2B sales
- Delivery performance

## Project Structure

| File | Purpose |
|---|---|
| `Business Understanding.md` | Business context, objective and research questions |
| `Data Understanding.md` | Dataset structure, data quality and initial data analysis |
| `KPI framework.md` | Selected KPIs and their business purpose |
| `bean_there_done_that_analysis.py` | Python analysis, KPI calculations and visualization generation |
| `Bean there done that data.xlsx` | Operational datasets used for the analysis |
| `Week 4 Storytelling.md` | Audience, Big Idea, storyboard, visual strategy and findings |
| `analysis_outputs/` | Generated KPI tables, charts and analysis summary |

## Data

The project uses five datasets:

1. Raw Material Inventory
2. Finished Product Inventory
3. Roasting
4. E-commerce Sales
5. B2B Orders

The datasets cover operational activities during 2023.

## Initial Analysis

The analysis identified several key operational figures:

- E-commerce recorded sales value: €17,561,219.89
- E-commerce quantity sold: 1,208,471 bags
- E-commerce sales records: 240,352
- Exact duplicate e-commerce rows: 119,101
- Average e-commerce delivery time: 1.59 calendar days
- B2B sales value: €421,652
- Production output: 795,671.2 kg, including estimated output from rejected batches
- Total production batches: 11,838
- Rejected batches: 224
- Production rejection rate: 1.89%
- Raw material December stock value: €823,886.30
- Finished product December stock value: €866,200.72
- Finished product December stock: 35,460 kg
- Raw material scrapped: 5,040 kg of beans and 15,000 packaging pieces
- Finished product scrapped: 48,000 kg

## Data Limitations

The e-commerce dataset contains 119,101 exact duplicate rows. Since no unique order ID is available, it is not possible to confirm whether these are errors or separate transactions.

Removing exact duplicates produces a sensitivity scenario of €9,071,629.64 in e-commerce sales value. This is not confirmed revenue.

Inventory stock values represent monthly snapshots and should not be added together to represent the stock value at one point in time.

Production output includes the estimated weight of rejected batches and therefore does not represent confirmed saleable output.

Delivery time is calculated using calendar days rather than business days.

The available data does not establish the company's full production capacity or available spare capacity.

## Initial Findings

The analysis identified several areas requiring further investigation:

- Production quality differences between the two roasting machines
- Finished product scrapping, particularly between June and August
- E-commerce sales data reliability
- Delivery performance during periods of higher recorded sales
- Production capacity and readiness for additional demand

These findings will be used to develop recommendations for management. Further validation is required before making a final conclusion about the company's readiness for growth.

## Final Assessment

The final assessment will use the results of the analysis to create a visual and oral presentation for the CEO and management.

The presentation will explain the current operational situation, highlight important findings, identify potential growth roadblocks and recommend actions to prepare the company for future expansion.
