/*
=======================================================================
  Twit's Treats — Advanced Analytical Queries
  Demonstrates: JOINs, GROUP BY, HAVING, subqueries, CASE, RANK(),
                window functions, aggregation, and business reporting.
=======================================================================
*/

-- -----------------------------------------------------------------------
-- Q1: REVENUE SUMMARY BY ORDER CHANNEL
--     How much total revenue does each channel (Instagram, WhatsApp, etc.)
--     generate, and how many orders come through each?
-- -----------------------------------------------------------------------
SELECT
    o.ORDER_CHANNEL,
    COUNT(o.ORDER_ID)                          AS total_orders,
    SUM(p.AMOUNT_PAID)                         AS total_revenue,
    ROUND(AVG(p.AMOUNT_PAID), 2)               AS avg_order_value,
    SUM(CASE WHEN p.PAYMENT_STATUS = 'COMPLETED' THEN p.AMOUNT_PAID ELSE 0 END)
                                               AS confirmed_revenue
FROM ORDERS o
JOIN PAYMENTS p ON o.PAYMENT_ID = p.PAYMENT_ID
GROUP BY o.ORDER_CHANNEL
ORDER BY total_revenue DESC;


-- -----------------------------------------------------------------------
-- Q2: TOP 5 BEST-SELLING MENU ITEMS
--     Ranked by total times ordered (frequency), not revenue.
-- -----------------------------------------------------------------------
SELECT
    mi.ITEM_NAME,
    mi.CATEGORY,
    COUNT(oi.ORDER_ITEM_ID)     AS times_ordered,
    SUM(oi.ITEM_SUBTOTAL)       AS total_revenue,
    ROUND(AVG(oi.ITEM_PRICE),2) AS avg_selling_price
FROM ORDER_ITEMS oi
JOIN MENU_ITEMS mi ON oi.MENU_ITEM_ID = mi.MENU_ITEM_ID
GROUP BY mi.ITEM_NAME, mi.CATEGORY
ORDER BY times_ordered DESC
FETCH FIRST 5 ROWS ONLY;


-- -----------------------------------------------------------------------
-- Q3: CUSTOMER ORDER HISTORY WITH LIFETIME VALUE
--     Full name, number of orders, and total spend per customer.
-- -----------------------------------------------------------------------
SELECT
    c.CUSTOMER_ID,
    c.FIRST_NAME || ' ' || c.LAST_NAME         AS full_name,
    c.PHONE_NO,
    COUNT(o.ORDER_ID)                           AS total_orders,
    SUM(p.AMOUNT_PAID)                          AS lifetime_value,
    MIN(o.ORDER_DATE)                           AS first_order,
    MAX(o.ORDER_DATE)                           AS last_order
FROM CUSTOMERS c
LEFT JOIN ORDERS o   ON c.CUSTOMER_ID  = o.CUSTOMER_ID
LEFT JOIN PAYMENTS p ON o.PAYMENT_ID   = p.PAYMENT_ID
GROUP BY c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME, c.PHONE_NO
ORDER BY lifetime_value DESC NULLS LAST;


-- -----------------------------------------------------------------------
-- Q4: DELIVERY PERFORMANCE REPORT
--     Count of DELIVERED vs ON-GOING per delivery type,
--     and average delivery price per type.
-- -----------------------------------------------------------------------
SELECT
    DELIVERY_TYPE,
    COUNT(*)                                                   AS total_deliveries,
    SUM(CASE WHEN DELIVERY_STATUS = 'DELIVERED'  THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN DELIVERY_STATUS = 'ON-GOING'   THEN 1 ELSE 0 END) AS on_going,
    ROUND(AVG(DELIVERY_PRICE), 2)                              AS avg_delivery_price,
    SUM(DELIVERY_PRICE)                                        AS total_delivery_revenue
FROM DELIVERIES
GROUP BY DELIVERY_TYPE
ORDER BY total_deliveries DESC;


-- -----------------------------------------------------------------------
-- Q5: STAFF DELIVERY WORKLOAD
--     How many deliveries has each staff member completed?
--     Includes staff with zero deliveries (LEFT JOIN).
-- -----------------------------------------------------------------------
SELECT
    s.STAFF_ID,
    s.FIRST_NAME || ' ' || s.LAST_NAME   AS staff_name,
    s.STAFF_ROLE,
    s.PAY_RATE,
    COUNT(d.DELIVERY_ID)                 AS deliveries_assigned,
    SUM(d.DELIVERY_PRICE)                AS total_delivery_value_handled
FROM STAFFS s
LEFT JOIN DELIVERIES d ON s.STAFF_ID = d.STAFF_ID
GROUP BY s.STAFF_ID, s.FIRST_NAME, s.LAST_NAME, s.STAFF_ROLE, s.PAY_RATE
ORDER BY deliveries_assigned DESC;


-- -----------------------------------------------------------------------
-- Q6: PAYMENT METHOD BREAKDOWN
--     What percentage of revenue comes from each payment method?
-- -----------------------------------------------------------------------
SELECT
    PAYMENT_METHOD,
    COUNT(*)                                                      AS transactions,
    SUM(AMOUNT_PAID)                                              AS total_collected,
    ROUND(
        SUM(AMOUNT_PAID) * 100.0 /
        SUM(SUM(AMOUNT_PAID)) OVER (), 2
    )                                                             AS pct_of_revenue
FROM PAYMENTS
WHERE PAYMENT_STATUS = 'COMPLETED'
GROUP BY PAYMENT_METHOD
ORDER BY total_collected DESC;


-- -----------------------------------------------------------------------
-- Q7: MONTHLY REVENUE TREND
--     Total revenue grouped by month (useful for seasonal analysis).
-- -----------------------------------------------------------------------
SELECT
    TO_CHAR(o.ORDER_DATE, 'YYYY-MM')   AS order_month,
    COUNT(o.ORDER_ID)                  AS orders_placed,
    SUM(p.AMOUNT_PAID)                 AS monthly_revenue
FROM ORDERS o
JOIN PAYMENTS p ON o.PAYMENT_ID = p.PAYMENT_ID
WHERE p.PAYMENT_STATUS = 'COMPLETED'
GROUP BY TO_CHAR(o.ORDER_DATE, 'YYYY-MM')
ORDER BY order_month;


-- -----------------------------------------------------------------------
-- Q8: MENU ITEM PRICE RANGE (MIN / MAX / AVG PER ITEM)
--     Useful for identifying pricing tiers across portion sizes.
-- -----------------------------------------------------------------------
SELECT
    mi.ITEM_NAME,
    mi.CATEGORY,
    COUNT(mp.PORTION_ID)          AS portion_options,
    MIN(mp.PRICE)                 AS min_price,
    MAX(mp.PRICE)                 AS max_price,
    ROUND(AVG(mp.PRICE), 2)       AS avg_price
FROM MENU_ITEMS mi
JOIN MENU_ITEM_PORTIONS mp ON mi.MENU_ITEM_ID = mp.MENU_ITEM_ID
GROUP BY mi.ITEM_NAME, mi.CATEGORY
ORDER BY mi.CATEGORY, avg_price DESC;


-- -----------------------------------------------------------------------
-- Q9: ORDERS WITH MULTIPLE ITEMS (complex orders)
--     Find every order that contained more than one item, with item count
--     and the customer who placed it.
-- -----------------------------------------------------------------------
SELECT
    o.ORDER_ID,
    c.FIRST_NAME || ' ' || c.LAST_NAME    AS customer_name,
    o.ORDER_DATE,
    COUNT(oi.ORDER_ITEM_ID)               AS item_count,
    SUM(oi.ITEM_SUBTOTAL)                 AS items_total,
    o.ORDER_AMOUNT                        AS order_total
FROM ORDERS o
JOIN CUSTOMERS   c  ON o.CUSTOMER_ID     = c.CUSTOMER_ID
JOIN ORDER_ITEMS oi ON o.ORDER_ID        = oi.ORDER_ID
GROUP BY o.ORDER_ID, c.FIRST_NAME, c.LAST_NAME, o.ORDER_DATE, o.ORDER_AMOUNT
HAVING COUNT(oi.ORDER_ITEM_ID) > 1
ORDER BY item_count DESC;


-- -----------------------------------------------------------------------
-- Q10: RANK CUSTOMERS BY SPEND USING WINDOW FUNCTION
--      RANK() lets us assign positions without filtering rows.
-- -----------------------------------------------------------------------
SELECT
    CUSTOMER_ID,
    full_name,
    lifetime_value,
    RANK() OVER (ORDER BY lifetime_value DESC)      AS spend_rank,
    NTILE(3) OVER (ORDER BY lifetime_value DESC)    AS tier   -- 1=high, 2=mid, 3=low
FROM (
    SELECT
        c.CUSTOMER_ID,
        c.FIRST_NAME || ' ' || c.LAST_NAME   AS full_name,
        SUM(p.AMOUNT_PAID)                    AS lifetime_value
    FROM CUSTOMERS c
    JOIN ORDERS   o ON c.CUSTOMER_ID = o.CUSTOMER_ID
    JOIN PAYMENTS p ON o.PAYMENT_ID  = p.PAYMENT_ID
    WHERE p.PAYMENT_STATUS = 'COMPLETED'
    GROUP BY c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME
)
ORDER BY spend_rank;


-- -----------------------------------------------------------------------
-- Q11: EVENT CATERING OVERVIEW
--      All events with linked order details and quoted vs actual payment.
-- -----------------------------------------------------------------------
SELECT
    e.EVENT_ID,
    e.EVENT_TYPE,
    e.EVENT_DATE,
    e.EVENT_LOCATION,
    e.GUEST_COUNT,
    e.QUOTED_COST,
    p.AMOUNT_PAID        AS actual_amount_paid,
    p.PAYMENT_STATUS,
    p.PAYMENT_METHOD,
    c.FIRST_NAME || ' ' || c.LAST_NAME  AS customer_name
FROM EVENTS e
JOIN ORDERS    o ON e.ORDER_ID    = o.ORDER_ID
JOIN PAYMENTS  p ON o.PAYMENT_ID  = p.PAYMENT_ID
JOIN CUSTOMERS c ON o.CUSTOMER_ID = c.CUSTOMER_ID
ORDER BY e.EVENT_DATE;


-- -----------------------------------------------------------------------
-- Q12: FAILED PAYMENTS REPORT
--      Identify all failed transactions and the orders they belong to.
-- -----------------------------------------------------------------------
SELECT
    p.PAYMENT_ID,
    p.PAYMENT_DATE,
    p.PAYMENT_METHOD,
    p.AMOUNT_PAID,
    o.ORDER_ID,
    c.FIRST_NAME || ' ' || c.LAST_NAME   AS customer_name,
    c.PHONE_NO
FROM PAYMENTS p
JOIN ORDERS    o ON p.PAYMENT_ID  = o.PAYMENT_ID
JOIN CUSTOMERS c ON o.CUSTOMER_ID = c.CUSTOMER_ID
WHERE p.PAYMENT_STATUS = 'FAILED'
ORDER BY p.PAYMENT_DATE;
