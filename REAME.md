# FirstByte 2026 — NorthByte Airlines Case Study

**Organizer:** Bolt UBC  
**Challenge:** Airline profitability analysis and business recommendations

## Overview

FirstByte 2026 is a data analytics case competition. Teams act as external consultants to **NorthByte Airlines**, a fictional Canadian domestic airline serving **20 airports**. Using two fiscal years of operational data (**September 2024–August 2026**), the goal is to explain declining profitability and propose practical, evidence-backed improvements.

## The Problem

NorthByte achieved record revenue, but operating costs grew even faster. It lost approximately **$40 million on flights in FY2025–26**, before airport gate lease costs. Leadership needs to understand **where losses occur, what causes them, and where to invest or cut back**—without compromising safety, fair treatment of customers, or connections to regional communities.

## Datasets

| File                | What it records                                                                           | Main analytical use                                           |
| ------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `transactions.xlsx` | Customer ticket sales, add-ons, fees, refunds, booking channels, loyalty tiers and routes | Net revenue, customer segments, ancillary revenue and refunds |
| `costs.xlsx`        | Flight-level fuel, crew, maintenance and food costs                                       | Operating costs and route-level profitability                 |
| `gates.xlsx`        | Airport gates, assigned routes and annual lease costs                                     | Gate utilization, fixed overhead and lease-cost forecasting   |

**Data considerations:** Route IDs are inconsistent across sources; transactions use **purchase dates**, while costs use **flight dates**. Gate leases run January–January instead of September–August, and **2026–2027 gate records are missing**. Gate cost is repeated for each route using a gate, so avoid double-counting it. Document assumptions when allocating and forecasting costs.

## Questions to Answer

1. **Financial trends:** How did revenue, costs and profit change between FY2024–25 and FY2025–26? When did performance deteriorate, and why?
2. **Network profitability:** Which routes, airports or network segments are profitable or loss-making? Are profitable operations subsidizing others?
3. **Loss drivers:** How much of the decline is explained by fuel and crew costs, refunds and the NorthByte Rewards program? Which matter most?
4. **Revenue composition:** How do ancillary sales, refunds and connecting passengers affect earnings?
5. **Gate leases:** How did gate costs change between lease years, and what should NorthByte expect to pay in 2026–2027?
6. **Recommendations:** What short- and long-term actions should NorthByte take, and how will they affect customers, employees and communities?

## Expected Deliverable

Submit a **PDF slide deck** with analysis, alternatives and justified recommendations by **October 15, 2026 at 11:59 PM**. Shortlisted teams present on **October 17** (10-minute presentation, 5-minute Q&A).

**Judging:** Data analysis **35%** · Business recommendations **35%** · Presentation **30%**.

## Reference Materials

- `FirstByte 2026 Case Package.pdf` — business context, guiding questions, requirements and judging
- `FirstByte 2026 Data Dictionary.pdf` — field definitions and dataset structure

## Analysis Answers

The completed [final analysis report](outputs/final_report.md) answers all six questions with supporting charts, exact-value tables and limitations. All amounts are CAD. **“Profit” below is a pre-gate activity-period proxy: purchase/refund-date receipts minus flight-date expenses, not matched-flight accrual operating profit.** Fiscal years run September–August.

1. **Financial trends:** Net revenue rose **5.15%**, from **$180.42m to $189.71m**, but flight expenses rose **23.52%**, from **$192.99m to $238.38m**. The proxy worsened from **−$12.57m to −$48.67m**, a **$36.10m decline**. It first turned negative in **March 2025** and stayed negative thereafter. Added flying and higher average expense/mix explain the cost arithmetic; these records do not isolate inflation or expansion's causal effect. The brief's February onset and approximate $40m loss differ from the measured results. [Answer 1 notebook](notebooks/01_financial_trends.ipynb), [annual evidence](outputs/tables/01_annual_financials.csv), [monthly evidence](outputs/tables/01_monthly_financials.csv).

2. **Network profitability:** **26 of 54 directions** are positive in FY2025–26. Their **$12.37m surplus** covers only **20.3% of $61.04m in gross route losses**, versus 54.2% previously. Toronto→Calgary leads at **+$1.49m**; Montreal↔Vancouver loses **$19.72m**. Montreal↔Vancouver, Halifax↔Toronto, Montreal↔Toronto and Ottawa↔Toronto explain **71.2% of deterioration**. Calgary leads the eight positive departure portfolios; all four broad network segments are negative. Review individual corridors before broad cuts: route losses are not closure savings. [Answer 2 notebook](notebooks/02_network_profitability.ipynb), [route pools](outputs/tables/02_cross_subsidy_pools.csv), [airport evidence](outputs/tables/02_departure_airport_profitability.csv).

3. **Loss drivers:** Higher fuel, crew and refunds contribute **$16.12m, $15.05m and $1.14m**, together **$32.31m / 89.51% of the net decline**. Maintenance adds another **$13.00m**, partly offset by sales growth. Flight counts rise **20.33%**, so total fuel/crew growth cannot be equated with price or wage inflation. **Rewards cost is unknown**: FY2 **$19.74m of Points + Cash ticket amounts are recorded receipts, not program expense**. [Answer 3 notebook](notebooks/03_loss_drivers.ipynb), [exact bridge](outputs/tables/03_decline_bridge.csv), [Rewards evidence](outputs/tables/03_rewards_payment.csv).

4. **Revenue composition:** FY2 ancillaries add **$3.96m / 2.00% of gross receipts**, while refunds remove **$7.82m / 3.96%**. Inferred connection-compatible bookings supply **$13.08m / 6.90% of net receipts**; route continuity does not prove actual connections or incremental profit. Direct channels supply **62.07% of net receipts**. A hypothetical combined 10% ancillary/refund improvement is only **$1.18m / 2.42% of the pre-gate deficit**, before costs. [Answer 4 notebook](notebooks/04_revenue_analysis.ipynb), [receipt bridge](outputs/tables/04_revenue_bridge.csv), [booking proxy](outputs/tables/04_connecting_booking_proxy.csv).

5. **Gate leases:** Actual calendar-2024/2025 leases rise **2.21%, from $9.664m to $9.878m**. For the missing **2026–2027 lease year (calendar 2026)**, repeating gate-specific increases forecasts **$10.096m**; flat rates imply **$9.878m**. These are scenarios, not a confidence interval. Halifax A3 and Ottawa A2 carry **$441,444.87 forecast annual exposure**, not assured savings. Each lease is counted once and airport totals are allocated across departing flights only. FY2 gates are estimated at **$10.023m**, giving a conditional **−$58.689m after-gate proxy**. [Answer 5 notebook](notebooks/05_gate_costs.ipynb), [forecast scenarios](outputs/tables/05_forecast_scenarios.csv), [fiscal allocation](outputs/tables/05_fiscal_allocation_summary.csv).

6. **Recommendations:** Start with the four deteriorating corridors, safe fuel/crew productivity and maintenance purchasing/planning reviews. In the first 90 days, pilot disruption prevention, feasible gate sharing and transparent optional ancillaries while building matched-flight records. Over months 3–18, scale only proven net-positive changes and reassess network/Rewards economics. Protect valid refunds, required maintenance, accrued benefits, safe workloads and workable regional/northern connections; consult employees and communities before permanent changes. A hypothetical **3% fuel/crew improvement yields $4.74m before costs but still leaves $43.93m negative**. Scenarios overlap and cannot be summed into promised savings. [Answer 6 notebook](notebooks/06_recommendations.ipynb), [action register](outputs/tables/06_prioritized_actions.csv), [financial sensitivities](outputs/tables/06_financial_sensitivities.csv), [stakeholder effects](outputs/tables/06_stakeholder_tradeoffs.csv).

**Scope and validation:** The requested day-first assumption applies only to 7,902 ambiguous dates; 759 outside-period transactions totaling $499,209.97 net are separately excluded, and all 57 duplicate-resolved records remain. All six notebooks were independently rerun successfully; consequential figures were recomputed and reconciled across questions. [Full assumptions and limitations](outputs/final_report.md#assumptions-and-limitations), [independent checks](outputs/tables/07_validation.csv), [financial reconciliation](outputs/tables/07_financial_reconciliation.csv).
