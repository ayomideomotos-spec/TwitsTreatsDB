/*
=======================================================================
  Twit's Treats — Stored Procedures
  Encapsulates repeatable business logic in reusable, safe procedures.
  Demonstrates: PL/SQL, exception handling, parameters, cursors.
=======================================================================
*/


-- -----------------------------------------------------------------------
-- SP1: SP_PLACE_ORDER
--      Inserts a new payment + order in one atomic transaction.
--      Rolls back both if either insert fails.
--
--      Parameters:
--        p_customer_id       Customer placing the order
--        p_order_amount      Total order value
--        p_discount          Discount applied (0 if none)
--        p_channel           e.g. 'Instagram', 'WhatsApp'
--        p_instructions      Special instructions (can be NULL)
--        p_pay_method        e.g. 'Cash', 'Transfer', 'POS'
--        p_amount_paid       Amount customer paid
--        p_new_order_id  OUT The generated ORDER_ID returned to caller
-- -----------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE SP_PLACE_ORDER (
    p_customer_id    IN  ORDERS.CUSTOMER_ID%TYPE,
    p_order_amount   IN  ORDERS.ORDER_AMOUNT%TYPE,
    p_discount       IN  ORDERS.DISCOUNT%TYPE       DEFAULT 0,
    p_channel        IN  ORDERS.ORDER_CHANNEL%TYPE  DEFAULT NULL,
    p_instructions   IN  ORDERS.SPECIAL_INSTRUCTIONS%TYPE DEFAULT NULL,
    p_pay_method     IN  PAYMENTS.PAYMENT_METHOD%TYPE,
    p_amount_paid    IN  PAYMENTS.AMOUNT_PAID%TYPE,
    p_new_order_id   OUT ORDERS.ORDER_ID%TYPE
) AS
    v_payment_id  PAYMENTS.PAYMENT_ID%TYPE;
    v_order_id    ORDERS.ORDER_ID%TYPE;
BEGIN
    -- 1. Generate IDs using sequences
    v_payment_id := SEQ_PAYMENTS.NEXTVAL;
    v_order_id   := SEQ_ORDERS.NEXTVAL;

    -- 2. Insert payment record (COMPLETED assumed on placement)
    INSERT INTO PAYMENTS (PAYMENT_ID, PAYMENT_STATUS, PAYMENT_METHOD,
                          AMOUNT_PAID, PAYMENT_DATE)
    VALUES (v_payment_id, 'COMPLETED', p_pay_method,
            p_amount_paid, SYSDATE);

    -- 3. Insert order linked to customer and payment
    INSERT INTO ORDERS (ORDER_ID, ORDER_DATE, ORDER_AMOUNT, CUSTOMER_ID,
                        DISCOUNT, ORDER_CHANNEL, SPECIAL_INSTRUCTIONS, PAYMENT_ID)
    VALUES (v_order_id, SYSDATE, p_order_amount, p_customer_id,
            p_discount, p_channel, p_instructions, v_payment_id);

    -- 4. Return the new order ID
    p_new_order_id := v_order_id;

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Order ' || v_order_id || ' placed successfully.');

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('SP_PLACE_ORDER failed: ' || SQLERRM);
        RAISE;
END SP_PLACE_ORDER;
/


-- -----------------------------------------------------------------------
-- SP2: SP_UPDATE_DELIVERY_STATUS
--      Marks a delivery as DELIVERED and optionally logs completion time.
--
--      Parameters:
--        p_delivery_id   The delivery to update
--        p_new_status    'DELIVERED' or 'ON-GOING'
-- -----------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE SP_UPDATE_DELIVERY_STATUS (
    p_delivery_id  IN DELIVERIES.DELIVERY_ID%TYPE,
    p_new_status   IN DELIVERIES.DELIVERY_STATUS%TYPE
) AS
    v_count  NUMBER;
BEGIN
    -- Validate the delivery exists
    SELECT COUNT(*) INTO v_count
    FROM DELIVERIES
    WHERE DELIVERY_ID = p_delivery_id;

    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20001,
            'Delivery ID ' || p_delivery_id || ' not found.');
    END IF;

    UPDATE DELIVERIES
    SET    DELIVERY_STATUS = UPPER(p_new_status)
    WHERE  DELIVERY_ID     = p_delivery_id;

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Delivery ' || p_delivery_id
        || ' updated to ' || UPPER(p_new_status));

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('SP_UPDATE_DELIVERY_STATUS failed: ' || SQLERRM);
        RAISE;
END SP_UPDATE_DELIVERY_STATUS;
/


-- -----------------------------------------------------------------------
-- SP3: SP_CUSTOMER_ORDER_REPORT
--      Prints a summary of all orders for a given customer using a cursor.
--      Demonstrates: explicit cursors, loops, DBMS_OUTPUT.
--
--      Parameters:
--        p_customer_id   Customer to report on
-- -----------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE SP_CUSTOMER_ORDER_REPORT (
    p_customer_id IN CUSTOMERS.CUSTOMER_ID%TYPE
) AS
    -- Explicit cursor joins orders, payments, and delivery info
    CURSOR c_orders IS
        SELECT
            o.ORDER_ID,
            o.ORDER_DATE,
            o.ORDER_AMOUNT,
            p.PAYMENT_STATUS,
            p.PAYMENT_METHOD,
            NVL(d.DELIVERY_TYPE,   'N/A') AS delivery_type,
            NVL(d.DELIVERY_STATUS, 'N/A') AS delivery_status
        FROM ORDERS o
        JOIN PAYMENTS  p ON o.PAYMENT_ID  = p.PAYMENT_ID
        LEFT JOIN DELIVERIES d ON d.PAYMENT_ID = o.PAYMENT_ID
        WHERE o.CUSTOMER_ID = p_customer_id
        ORDER BY o.ORDER_DATE;

    v_cust_name  VARCHAR2(61);
    v_row        c_orders%ROWTYPE;
BEGIN
    -- Fetch customer name
    SELECT FIRST_NAME || ' ' || LAST_NAME
    INTO   v_cust_name
    FROM   CUSTOMERS
    WHERE  CUSTOMER_ID = p_customer_id;

    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('Order History for: ' || v_cust_name);
    DBMS_OUTPUT.PUT_LINE('========================================');

    OPEN c_orders;
    LOOP
        FETCH c_orders INTO v_row;
        EXIT WHEN c_orders%NOTFOUND;

        DBMS_OUTPUT.PUT_LINE(
            'Order #' || v_row.ORDER_ID
            || ' | Date: ' || TO_CHAR(v_row.ORDER_DATE, 'YYYY-MM-DD')
            || ' | Amount: $' || v_row.ORDER_AMOUNT
            || ' | Payment: ' || v_row.PAYMENT_STATUS
            || ' (' || v_row.PAYMENT_METHOD || ')'
            || ' | Delivery: ' || v_row.DELIVERY_TYPE
            || ' [' || v_row.DELIVERY_STATUS || ']'
        );
    END LOOP;
    CLOSE c_orders;

    DBMS_OUTPUT.PUT_LINE('Total orders: ' || c_orders%ROWCOUNT);

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Customer ID ' || p_customer_id || ' not found.');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END SP_CUSTOMER_ORDER_REPORT;
/


-- -----------------------------------------------------------------------
-- Example calls (run in SQL*Plus / Oracle APEX with DBMS_OUTPUT enabled)
-- -----------------------------------------------------------------------
/*
SET SERVEROUTPUT ON;

-- Place a new order for customer 1
DECLARE
    v_new_order_id NUMBER;
BEGIN
    SP_PLACE_ORDER(
        p_customer_id  => 1,
        p_order_amount => 130,
        p_discount     => 0,
        p_channel      => 'Instagram',
        p_instructions => 'Extra sauce please',
        p_pay_method   => 'Transfer',
        p_amount_paid  => 130,
        p_new_order_id => v_new_order_id
    );
    DBMS_OUTPUT.PUT_LINE('New Order ID: ' || v_new_order_id);
END;
/

-- Mark delivery 8 as complete
EXEC SP_UPDATE_DELIVERY_STATUS(8, 'DELIVERED');

-- Print order history for customer 2
EXEC SP_CUSTOMER_ORDER_REPORT(2);
*/