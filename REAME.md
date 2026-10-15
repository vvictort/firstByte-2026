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