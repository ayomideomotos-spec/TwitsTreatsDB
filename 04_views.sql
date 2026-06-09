/*
=======================================================================
  Twit's Treats — Reusable Views
  Views abstract complex queries into simple, queryable "virtual tables"
  that the business can rely on for daily reporting.
=======================================================================
*/

-- -----------------------------------------------------------------------
-- V1: VW_ORDER_SUMMARY
--     One row per order with customer name, payment status, item count,
--     and delivery info — the go-to view for order management.
-- -----------------------------------------------------------------------
CREATE OR REPLACE VIEW VW_ORDER_SUMMARY AS
SELECT
    o.ORDER_ID,
    o.ORDER_DATE,
    c.FIRST_NAME || ' ' || c.LAST_NAME        AS customer_name,
    c.PHONE_NO,
    o.ORDER_AMOUNT,
    o.DISCOUNT,
    o.ORDER_CHANNEL,
    o.SPECIAL_INSTRUCTIONS,
    p.PAYMENT_STATUS,
    p.PAYMENT_METHOD,
    p.AMOUNT_PAID,
    d.DELIVERY_TYPE,
    d.DELIVERY_STATUS,
    d.DELIVERY_PRICE,
    COUNT(oi.ORDER_ITEM_ID)                    AS item_count
FROM ORDERS o
JOIN CUSTOMERS   c  ON o.CUSTOMER_ID  = c.CUSTOMER_ID
JOIN PAYMENTS    p  ON o.PAYMENT_ID   = p.PAYMENT_ID
LEFT JOIN DELIVERIES d ON d.PAYMENT_ID = o.PAYMENT_ID
LEFT JOIN ORDER_ITEMS oi ON oi.ORDER_ID = o.ORDER_ID
GROUP BY
    o.ORDER_ID, o.ORDER_DATE, c.FIRST_NAME, c.LAST_NAME, c.PHONE_NO,
    o.ORDER_AMOUNT, o.DISCOUNT, o.ORDER_CHANNEL, o.SPECIAL_INSTRUCTIONS,
    p.PAYMENT_STATUS, p.PAYMENT_METHOD, p.AMOUNT_PAID,
    d.DELIVERY_TYPE, d.DELIVERY_STATUS, d.DELIVERY_PRICE;


-- -----------------------------------------------------------------------
-- V2: VW_MENU_WITH_PRICES
--     Full menu catalogue: every item with all available portion sizes
--     and prices. Used for customer-facing price lists.
-- -----------------------------------------------------------------------
CREATE OR REPLACE VIEW VW_MENU_WITH_PRICES AS
SELECT
    mi.MENU_ITEM_ID,
    mi.ITEM_NAME,
    mi.CATEGORY,
    mi.ITEM_DESCRIPTION,
    mi.IS_AVAILABLE,
    mp.PORTION_PACKAGE,
    mp.PORTION_SIZE,
    mp.PRICE
FROM MENU_ITEMS mi
JOIN MENU_ITEM_PORTIONS mp ON mi.MENU_ITEM_ID = mp.MENU_ITEM_ID
ORDER BY mi.CATEGORY, mi.ITEM_NAME, mp.PRICE;


-- -----------------------------------------------------------------------
-- V3: VW_ACTIVE_DELIVERIES
--     Snapshot of all deliveries currently ON-GOING with assigned driver.
-- -----------------------------------------------------------------------
CREATE OR REPLACE VIEW VW_ACTIVE_DELIVERIES AS
SELECT
    d.DELIVERY_ID,
    d.DELIVERY_TYPE,
    d.DELIVERY_DATE,
    d.DELIVERY_ADDRESS,
    d.DELIVERY_PRICE,
    s.FIRST_NAME || ' ' || s.LAST_NAME   AS driver_name,
    s.STAFF_ROLE,
    c.FIRST_NAME || ' ' || c.LAST_NAME   AS customer_name,
    c.PHONE_NO                           AS customer_phone
FROM DELIVERIES d
LEFT JOIN STAFFS   s ON d.STAFF_ID   = s.STAFF_ID
JOIN  PAYMENTS     p ON d.PAYMENT_ID = p.PAYMENT_ID
JOIN  ORDERS       o ON o.PAYMENT_ID = p.PAYMENT_ID
JOIN  CUSTOMERS    c ON o.CUSTOMER_ID = c.CUSTOMER_ID
WHERE d.DELIVERY_STATUS = 'ON-GOING';


-- -----------------------------------------------------------------------
-- V4: VW_REVENUE_BY_CATEGORY
--     Total revenue grouped by menu category (Rice, Protein, Soup, etc.)
--     to understand which food types drive the most sales.
-- -----------------------------------------------------------------------
CREATE OR REPLACE VIEW VW_REVENUE_BY_CATEGORY AS
SELECT
    mi.CATEGORY,
    COUNT(oi.ORDER_ITEM_ID)     AS total_items_sold,
    SUM(oi.ITEM_SUBTOTAL)       AS category_revenue,
    ROUND(AVG(oi.ITEM_PRICE),2) AS avg_item_price
FROM ORDER_ITEMS oi
JOIN MENU_ITEMS mi ON oi.MENU_ITEM_ID = mi.MENU_ITEM_ID
GROUP BY mi.CATEGORY
ORDER BY category_revenue DESC;


-- -----------------------------------------------------------------------
-- V5: VW_UPCOMING_EVENTS
--     All future catering events with quoted cost and customer contact.
-- -----------------------------------------------------------------------
CREATE OR REPLACE VIEW VW_UPCOMING_EVENTS AS
SELECT
    e.EVENT_ID,
    e.EVENT_TYPE,
    e.EVENT_DATE,
    e.EVENT_LOCATION,
    e.GUEST_COUNT,
    e.QUOTED_COST,
    e.NOTES,
    c.FIRST_NAME || ' ' || c.LAST_NAME  AS customer_name,
    c.PHONE_NO,
    c.EMAIL
FROM EVENTS e
JOIN ORDERS    o ON e.ORDER_ID    = o.ORDER_ID
JOIN CUSTOMERS c ON o.CUSTOMER_ID = c.CUSTOMER_ID
WHERE e.EVENT_DATE >= SYSDATE
ORDER BY e.EVENT_DATE;
