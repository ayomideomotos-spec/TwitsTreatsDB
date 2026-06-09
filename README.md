# 🍲 Twit's Treats — Relational Database System

A fully normalized, production-ready Oracle SQL database designed for a Nigerian home-based catering and meal-delivery business. Built as a capstone project for **COSC 3606: Database and Data Management** at Nipissing University (Fall 2025).

---

## 📌 Project Overview

**Twit's Treats** is a home-based Nigerian food service that handles everyday meal orders, home deliveries, customer pick-ups, and large-scale event catering. This database centralizes all business operations — from customer management and menu pricing to payments, deliveries, and event scheduling — into a single, consistent relational system.

### Business Goals Addressed
- Eliminate manual order tracking on paper/WhatsApp
- Enforce referential integrity across all order, payment, and delivery records
- Support flexible pricing through per-item portion configurations
- Track catering events with guest counts and quoted costs
- Enable reporting on revenue, delivery performance, and customer lifetime value

---

## 🗂️ Repository Structure

```
twits-treats-db/
│
├── sql/
│   ├── schema/
│   │   ├── TwitsTreatsSchema.sql     # DDL: all 9 tables + seed data
│   │   └── 02_sequences.sql          # Oracle sequences for auto-increment IDs
│   │
│   ├── queries/
│   │   ├── 03_analytical_queries.sql # 12 advanced SELECT queries
│   │   └── 04_views.sql              # 5 reusable reporting views
│   │
│   └── procedures/
│       └── 05_stored_procedures.sql  # 3 PL/SQL stored procedures
│
└── docs/
    └── COSC_3606_Final_Project.pdf   # Original project report with ERD
```

---

## 🏗️ Schema Design — 9 Tables

| Table | Description |
|---|---|
| `CUSTOMERS` | Customer contact info with unique phone/email/social constraints |
| `STAFFS` | Per-job staff records with pay rate and role |
| `MENU_ITEMS` | Menu catalogue with availability flag |
| `MENU_ITEM_PORTIONS` | Per-item pricing by package and size (S/M/L, Bowl 2L/4L) |
| `PAYMENTS` | Payment records with status (COMPLETED / FAILED) |
| `ORDERS` | Orders linked to customers and payments |
| `ORDER_ITEMS` | Line items per order (supports off-menu custom items) |
| `DELIVERIES` | Delivery/pick-up records linked to staff and payment |
| `EVENTS` | Catering event details linked to orders |

### Entity Relationship Summary

```
CUSTOMERS ──< ORDERS >── PAYMENTS ──< DELIVERIES >── STAFFS
                │                         │
           ORDER_ITEMS              (delivery type)
                │
           MENU_ITEMS ──< MENU_ITEM_PORTIONS
                │
             EVENTS
```

### Normalization
The schema satisfies **1NF through 3NF**:
- All attributes are atomic (1NF)
- Every non-key attribute depends on the entire primary key (2NF)
- No transitive dependencies — portion pricing lives in `MENU_ITEM_PORTIONS`, not repeated in `ORDER_ITEMS` (3NF)

---

## 🔍 Analytical Queries (03_analytical_queries.sql)

12 queries demonstrating real reporting scenarios:

| # | Query | Techniques Used |
|---|---|---|
| Q1 | Revenue by order channel | GROUP BY, SUM, CASE |
| Q2 | Top 5 best-selling menu items | ORDER BY, FETCH FIRST |
| Q3 | Customer lifetime value | LEFT JOIN, MIN/MAX |
| Q4 | Delivery performance report | CASE aggregation |
| Q5 | Staff workload analysis | LEFT JOIN, COUNT |
| Q6 | Payment method breakdown | Window function: SUM OVER |
| Q7 | Monthly revenue trend | TO_CHAR date grouping |
| Q8 | Menu item price range | MIN, MAX, AVG per group |
| Q9 | Multi-item orders | HAVING COUNT > 1 |
| Q10 | Customer spend ranking | RANK(), NTILE() window functions |
| Q11 | Event catering overview | 4-table JOIN |
| Q12 | Failed payments report | Filtered JOIN |

---

## 👁️ Views (04_views.sql)

| View | Purpose |
|---|---|
| `VW_ORDER_SUMMARY` | All order info in one row — customer, payment, delivery |
| `VW_MENU_WITH_PRICES` | Full price list including all portion options |
| `VW_ACTIVE_DELIVERIES` | Live delivery snapshot with driver and customer contact |
| `VW_REVENUE_BY_CATEGORY` | Revenue breakdown by food category |
| `VW_UPCOMING_EVENTS` | Future catering bookings with customer details |

---

## ⚙️ Stored Procedures (05_stored_procedures.sql)

| Procedure | Purpose |
|---|---|
| `SP_PLACE_ORDER` | Atomically inserts payment + order; rolls back on failure |
| `SP_UPDATE_DELIVERY_STATUS` | Validates and updates a delivery status |
| `SP_CUSTOMER_ORDER_REPORT` | Cursor-based order history report with DBMS_OUTPUT |

---

## 🗃️ Seed Data Summary

| Table | Rows |
|---|---|
| CUSTOMERS | 15 |
| STAFFS | 8 |
| MENU_ITEMS | 29 |
| MENU_ITEM_PORTIONS | 65 |
| PAYMENTS | 12 |
| ORDERS | 12 |
| ORDER_ITEMS | 15 |
| DELIVERIES | 10 |
| EVENTS | 5 |

---

## 🚀 How to Run

This project targets **Oracle Database** (tested on Oracle APEX / Oracle 19c+).

1. Run `TwitsTreatsSchema.sql` — creates all tables and inserts seed data
2. Run `02_sequences.sql` — creates sequences for new inserts
3. Run `04_views.sql` — creates all reporting views
4. Run `05_stored_procedures.sql` — compiles all PL/SQL procedures
5. Run any query from `03_analytical_queries.sql` to explore the data

> For the stored procedures, enable server output first:
> ```sql
> SET SERVEROUTPUT ON;
> ```

---

## 💡 Key Design Decisions

**Why is `DELIVERIES` linked to `PAYMENTS` instead of `ORDERS`?**
In Twit's Treats, one payment can cover both the order amount and the delivery fee. Linking deliveries directly to the payment record avoids a circular dependency between `ORDERS` and `DELIVERIES`, and it mirrors how the business actually processes transactions.

**Why does `ORDER_ITEMS` have `ITEM_NAME` and `ITEM_PRICE` as optional columns?**
Customers can request custom dishes not on the standard menu. These columns capture off-menu orders without polluting `MENU_ITEMS` with temporary or one-time items.

**Why `MENU_ITEM_PORTIONS` as a separate table?**
The same dish (e.g. Jollof Rice) has different prices at different tray sizes. Storing pricing in a separate portions table eliminates update anomalies — changing the small-tray price requires updating one row, not every occurrence in `ORDER_ITEMS`.

---

Download files.zip to access all project files at once.

--
## 👤 Author

**Ayomide Omotoso**  
B.Sc. Computer Science — Nipissing University (2025)  
Certified SQL Developer | AWS DEA-C01 (In Progress)  
[LinkedIn](https://linkedin.com/in/ayomide-omotoso-965b28280)
