## 🏗️ TwitsTreatsDB Schema Overview

This document provides a detailed breakdown of the database schema design for Twit's Treats.

---

## Table Definitions

### 1. CUSTOMERS
Stores customer information including contact details and preferences.

| Column | Type | Constraints | Description |
|---|---|---|---|
| CUSTOMER_ID | NUMBER(5) | PK, FK | Primary key; auto-increment |
| FIRST_NAME | VARCHAR2(30) | NOT NULL | Customer's first name |
| LAST_NAME | VARCHAR2(30) | NOT NULL | Customer's last name |
| PHONE_NO | VARCHAR2(20) | NOT NULL, UNIQUE | Primary contact number |
| EMAIL | VARCHAR2(50) | UNIQUE | Email address |
| SOCIAL_HANDLE | VARCHAR2(50) | UNIQUE | Instagram/WhatsApp handle |

### 2. STAFFS
Tracks staff members and their job information.

| Column | Type | Constraints | Description |
|---|---|---|---|
| STAFF_ID | NUMBER(5) | PK | Primary key; auto-increment |
| FIRST_NAME | VARCHAR2(30) | NOT NULL | Staff first name |
| LAST_NAME | VARCHAR2(30) | NOT NULL | Staff last name |
| STAFF_ROLE | VARCHAR2(30) | NOT NULL | Role (e.g., "Driver", "Cook") |
| PAY_RATE | NUMBER(6,2) | NOT NULL | Hourly/daily rate in NGN |
| CONTACT_INFO | VARCHAR2(20) | | Emergency contact number |

### 3. MENU_ITEMS
Core menu catalogue for available dishes.

| Column | Type | Constraints | Description |
|---|---|---|---|
| MENU_ITEM_ID | NUMBER(5) | PK | Primary key; auto-increment |
| ITEM_NAME | VARCHAR2(60) | NOT NULL | Dish name (e.g., "Jollof Rice") |
| CATEGORY | VARCHAR2(30) | NOT NULL | Food category (Rice, Protein, Soup) |
| ITEM_DESCRIPTION | VARCHAR2(200) | | Dish description/ingredients |
| IS_AVAILABLE | CHAR(1) | DEFAULT 'Y' | 'Y' = available, 'N' = unavailable |

### 4. MENU_ITEM_PORTIONS
Pricing tiers for each menu item based on portion size.

| Column | Type | Constraints | Description |
|---|---|---|---|
| PORTION_ID | NUMBER(5) | PK | Primary key; auto-increment |
| MENU_ITEM_ID | NUMBER(5) | FK → MENU_ITEMS | Which item this portion is for |
| PORTION_PACKAGE | VARCHAR2(20) | NOT NULL | Package type (e.g., "Tray", "Bowl") |
| PORTION_SIZE | VARCHAR2(10) | NOT NULL | Size designation (S, M, L, 2L, 4L) |
| PRICE | NUMBER(6,2) | NOT NULL | Price in NGN |

**Example:**
- Menu Item: "Jollof Rice"
  - Portion 1: Tray + Large = ₦2,500
  - Portion 2: Tray + Medium = ₦2,000
  - Portion 3: Bowl + 2L = ₦1,500

### 5. PAYMENTS
Captures all payment transactions for orders.

| Column | Type | Constraints | Description |
|---|---|---|---|
| PAYMENT_ID | NUMBER(5) | PK | Primary key; auto-increment |
| PAYMENT_STATUS | VARCHAR2(15) | NOT NULL | 'COMPLETED' or 'FAILED' |
| PAYMENT_METHOD | VARCHAR2(20) | NOT NULL | 'Cash', 'Transfer', 'POS' |
| AMOUNT_PAID | NUMBER(8,2) | NOT NULL | Amount in NGN |
| PAYMENT_DATE | DATE | DEFAULT SYSDATE | When payment was made |

### 6. ORDERS
Master table for customer orders.

| Column | Type | Constraints | Description |
|---|---|---|---|
| ORDER_ID | NUMBER(5) | PK | Primary key; auto-increment |
| ORDER_DATE | DATE | DEFAULT SYSDATE | When order was placed |
| ORDER_AMOUNT | NUMBER(8,2) | NOT NULL | Total order value (before discount) |
| CUSTOMER_ID | NUMBER(5) | FK → CUSTOMERS | Customer who placed order |
| PAYMENT_ID | NUMBER(5) | FK → PAYMENTS | Associated payment record |
| DISCOUNT | NUMBER(5,2) | DEFAULT 0 | Discount percentage applied |
| ORDER_CHANNEL | VARCHAR2(20) | | How order was placed (Instagram, WhatsApp) |
| SPECIAL_INSTRUCTIONS | VARCHAR2(200) | | Customer notes/requests |

**Design Note:** ORDER_AMOUNT is stored separately (not calculated on-the-fly) to maintain historical accuracy even if menu prices change later.

### 7. ORDER_ITEMS
Line items within each order — the details of what was ordered.

| Column | Type | Constraints | Description |
|---|---|---|---|
| ORDER_ITEM_ID | NUMBER(5) | PK | Primary key; auto-increment |
| ORDER_ID | NUMBER(5) | FK → ORDERS | Which order this item belongs to |
| MENU_ITEM_ID | NUMBER(5) | FK → MENU_ITEMS | Standard menu item (nullable for custom items) |
| ITEM_QUANTITY | NUMBER(3) | | How many units ordered |
| ITEM_PRICE | NUMBER(6,2) | | Unit price at time of order (optional for custom) |
| ITEM_SUBTOTAL | NUMBER(8,2) | | Quantity × Price |
| ITEM_NAME | VARCHAR2(60) | | Item name (nullable for off-menu custom dishes) |

**Design Note:** ITEM_NAME and ITEM_PRICE are optional to support custom off-menu requests (e.g., "Chef's Special Mix").

### 8. DELIVERIES
Tracks delivery/pick-up logistics for orders.

| Column | Type | Constraints | Description |
|---|---|---|---|
| DELIVERY_ID | NUMBER(5) | PK | Primary key; auto-increment |
| PAYMENT_ID | NUMBER(5) | FK → PAYMENTS | Associated payment (one payment can include delivery fee) |
| STAFF_ID | NUMBER(5) | FK → STAFFS | Driver assigned (nullable = self-pickup) |
| DELIVERY_TYPE | VARCHAR2(20) | | 'HOME DELIVERY' or 'PICK-UP' |
| DELIVERY_DATE | DATE | | Scheduled delivery date |
| DELIVERY_ADDRESS | VARCHAR2(100) | | Delivery location |
| DELIVERY_PRICE | NUMBER(6,2) | | Delivery fee in NGN |
| DELIVERY_STATUS | VARCHAR2(15) | DEFAULT 'ON-GOING' | 'ON-GOING' or 'DELIVERED' |

**Design Note:** DELIVERIES links to PAYMENTS (not ORDERS) because the payment record captures both food cost and delivery fee together.

### 9. EVENTS
Special catering event records.

| Column | Type | Constraints | Description |
|---|---|---|---|
| EVENT_ID | NUMBER(5) | PK | Primary key; auto-increment |
| ORDER_ID | NUMBER(5) | FK → ORDERS | Associated order for the event |
| EVENT_TYPE | VARCHAR2(30) | NOT NULL | 'Wedding', 'Conference', 'Birthday', etc. |
| EVENT_DATE | DATE | NOT NULL | When event occurs |
| EVENT_LOCATION | VARCHAR2(100) | NOT NULL | Event venue |
| GUEST_COUNT | NUMBER(4) | NOT NULL | Expected number of guests |
| QUOTED_COST | NUMBER(8,2) | NOT NULL | Quoted price for catering |
| NOTES | VARCHAR2(500) | | Special requirements/preferences |

---

## Relationships & Foreign Keys

```
CUSTOMERS (1) ──── (N) ORDERS
    │                    │
    │              PAYMENTS (1)
    │                    │
    │              DELIVERIES (1)
    │                    │
    └──────────────── STAFFS (N)

MENU_ITEMS (1) ──── (N) MENU_ITEM_PORTIONS
    │
    └──── (N) ORDER_ITEMS ──── (1) ORDERS

ORDERS (1) ──── (N) EVENTS
```

---

## Indexes

Recommended indexes for performance optimization:

```sql
-- Primary Key Indexes (automatic)
CREATE UNIQUE INDEX PK_CUSTOMERS ON CUSTOMERS(CUSTOMER_ID);
CREATE UNIQUE INDEX PK_ORDERS ON ORDERS(ORDER_ID);
-- etc.

-- Foreign Key Indexes (automatic)
-- Recommended additional indexes for common queries:
CREATE INDEX IDX_ORDERS_CUSTOMER_ID ON ORDERS(CUSTOMER_ID);
CREATE INDEX IDX_ORDERS_PAYMENT_ID ON ORDERS(PAYMENT_ID);
CREATE INDEX IDX_ORDERS_ORDER_DATE ON ORDERS(ORDER_DATE);
CREATE INDEX IDX_ORDER_ITEMS_MENU_ID ON ORDER_ITEMS(MENU_ITEM_ID);
CREATE INDEX IDX_DELIVERIES_STAFF_ID ON DELIVERIES(STAFF_ID);
CREATE INDEX IDX_DELIVERIES_STATUS ON DELIVERIES(DELIVERY_STATUS);
```

---

## Sample Data Relationships

### Order Workflow Example

**Customer Places Order:**
1. Customer Amaka (ID=1) places order on Instagram
2. Order (ID=101) created with ORDER_AMOUNT=5,500
3. Payment (ID=51) created with AMOUNT_PAID=5,500, PAYMENT_METHOD='Transfer'
4. Order items added:
   - Jollof Rice (Large) × 2 @ ₦2,500 = ₦5,000
   - Delivery fee: ₦500
5. Delivery (ID=28) scheduled for next day with staff member Tunde (STAFF_ID=3)

**Result in Database:**
```
CUSTOMERS:   ID=1  | Amaka
ORDERS:      ID=101| Customer=1, Payment=51, Amount=5500, Channel='Instagram'
PAYMENTS:    ID=51 | Status='COMPLETED', Method='Transfer', Amount=5500
ORDER_ITEMS: ID=1  | Order=101, MenuItem=5, Quantity=2, Subtotal=5000
DELIVERIES:  ID=28 | Payment=51, Staff=3, Address='123 Lekki', Price=500
```

---

## Data Integrity Constraints

### Unique Constraints
- `CUSTOMERS.PHONE_NO` — No duplicate phone numbers
- `CUSTOMERS.EMAIL` — No duplicate emails
- `CUSTOMERS.SOCIAL_HANDLE` — No duplicate social handles

### NOT NULL Constraints
- Essential fields like FIRST_NAME, ORDER_AMOUNT, PAYMENT_STATUS are required

### Check Constraints
- DISCOUNT must be ≥ 0 and ≤ 100
- PAYMENT_STATUS must be in ('COMPLETED', 'FAILED')
- DELIVERY_STATUS must be in ('ON-GOING', 'DELIVERED')

---

## Views for Reporting

The `04_views.sql` file creates 5 key views:

1. **VW_ORDER_SUMMARY** — One-row view per order with all related details
2. **VW_MENU_WITH_PRICES** — Full menu with all portion options and prices
3. **VW_ACTIVE_DELIVERIES** — Currently on-going deliveries with driver info
4. **VW_REVENUE_BY_CATEGORY** — Revenue breakdown by food category
5. **VW_UPCOMING_EVENTS** — Future catering events

---

## Stored Procedures

Three key procedures in `05_stored_procedures.sql`:

1. **SP_PLACE_ORDER** — Atomic insert of payment + order (with rollback on error)
2. **SP_UPDATE_DELIVERY_STATUS** — Safe status update with validation
3. **SP_CUSTOMER_ORDER_REPORT** — Generate order history report for a customer

---

## Normalization Assessment

✅ **1NF (First Normal Form)**
- All attributes are atomic (no repeating groups)
- Each cell contains a single value

✅ **2NF (Second Normal Form)**
- 1NF requirements met
- Every non-key attribute depends on the **entire primary key**, not just part of it
- Example: In ORDER_ITEMS, ITEM_PRICE depends on the full key (ORDER_ITEM_ID), not just ORDER_ID

✅ **3NF (Third Normal Form)**
- 2NF requirements met
- No **transitive dependencies** (non-key attributes don't depend on other non-key attributes)
- Example: Menu pricing lives in MENU_ITEM_PORTIONS, not duplicated in ORDER_ITEMS

---

## Performance Considerations

- **ORDERS table** may grow large → index on ORDER_DATE
- **PAYMENTS table** heavily queried for reporting → index on PAYMENT_STATUS, PAYMENT_DATE
- **ORDER_ITEMS table** joined frequently → index on MENU_ITEM_ID, ORDER_ID
- Consider partitioning ORDERS, PAYMENTS by date in production

---