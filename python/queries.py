"""
Query Executor
Wrapper for executing common queries against the Twit's Treats database.
"""

from typing import List, Optional
from datetime import datetime
from .db_connection import OracleConnection
from .models import (
    Customer, Staff, MenuItem, MenuItemPortion, Payment, 
    Order, OrderItem, Delivery, Event, OrderSummary, CustomerLifetimeValue
)


class QueryExecutor:
    """Executes common database queries."""
    
    def __init__(self, db_connection: OracleConnection):
        """
        Initialize the query executor.
        
        Args:
            db_connection: Active OracleConnection instance
        """
        self.db = db_connection
    
    # Customer Queries
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        query = "SELECT * FROM CUSTOMERS WHERE CUSTOMER_ID = :id"
        results = self.db.execute_query_dict(query, {"id": customer_id})
        if results:
            row = results[0]
            return Customer(
                customer_id=row['CUSTOMER_ID'],
                first_name=row['FIRST_NAME'],
                last_name=row['LAST_NAME'],
                phone_no=row['PHONE_NO'],
                email=row.get('EMAIL'),
                social_handle=row.get('SOCIAL_HANDLE'),
                created_at=row.get('CREATED_AT')
            )
        return None
    
    def get_all_customers(self) -> List[Customer]:
        """Get all customers."""
        query = "SELECT * FROM CUSTOMERS ORDER BY CUSTOMER_ID"
        results = self.db.execute_query_dict(query)
        return [
            Customer(
                customer_id=row['CUSTOMER_ID'],
                first_name=row['FIRST_NAME'],
                last_name=row['LAST_NAME'],
                phone_no=row['PHONE_NO'],
                email=row.get('EMAIL'),
                social_handle=row.get('SOCIAL_HANDLE')
            )
            for row in results
        ]
    
    def get_customer_orders(self, customer_id: int) -> List[OrderSummary]:
        """Get all orders for a customer."""
        query = """
            SELECT * FROM VW_ORDER_SUMMARY 
            WHERE CUSTOMER_ID = :cid 
            ORDER BY ORDER_DATE DESC
        """
        results = self.db.execute_query_dict(query, {"cid": customer_id})
        return [
            OrderSummary(
                order_id=row['ORDER_ID'],
                order_date=row['ORDER_DATE'],
                customer_name=row['CUSTOMER_NAME'],
                phone_no=row['PHONE_NO'],
                order_amount=row['ORDER_AMOUNT'],
                discount=row['DISCOUNT'],
                order_channel=row.get('ORDER_CHANNEL'),
                special_instructions=row.get('SPECIAL_INSTRUCTIONS'),
                payment_status=row['PAYMENT_STATUS'],
                payment_method=row['PAYMENT_METHOD'],
                amount_paid=row['AMOUNT_PAID'],
                delivery_type=row.get('DELIVERY_TYPE'),
                delivery_status=row.get('DELIVERY_STATUS'),
                delivery_price=row.get('DELIVERY_PRICE'),
                item_count=row['ITEM_COUNT']
            )
            for row in results
        ]
    
    # Order Queries
    
    def get_order_by_id(self, order_id: int) -> Optional[OrderSummary]:
        """Get an order by ID."""
        query = "SELECT * FROM VW_ORDER_SUMMARY WHERE ORDER_ID = :id"
        results = self.db.execute_query_dict(query, {"id": order_id})
        if results:
            row = results[0]
            return OrderSummary(
                order_id=row['ORDER_ID'],
                order_date=row['ORDER_DATE'],
                customer_name=row['CUSTOMER_NAME'],
                phone_no=row['PHONE_NO'],
                order_amount=row['ORDER_AMOUNT'],
                discount=row['DISCOUNT'],
                order_channel=row.get('ORDER_CHANNEL'),
                special_instructions=row.get('SPECIAL_INSTRUCTIONS'),
                payment_status=row['PAYMENT_STATUS'],
                payment_method=row['PAYMENT_METHOD'],
                amount_paid=row['AMOUNT_PAID'],
                delivery_type=row.get('DELIVERY_TYPE'),
                delivery_status=row.get('DELIVERY_STATUS'),
                delivery_price=row.get('DELIVERY_PRICE'),
                item_count=row['ITEM_COUNT']
            )
        return None
    
    def get_pending_orders(self) -> List[OrderSummary]:
        """Get all pending (unpaid) orders."""
        query = """
            SELECT * FROM VW_ORDER_SUMMARY 
            WHERE PAYMENT_STATUS != 'COMPLETED' 
            ORDER BY ORDER_DATE DESC
        """
        results = self.db.execute_query_dict(query)
        return [
            OrderSummary(
                order_id=row['ORDER_ID'],
                order_date=row['ORDER_DATE'],
                customer_name=row['CUSTOMER_NAME'],
                phone_no=row['PHONE_NO'],
                order_amount=row['ORDER_AMOUNT'],
                discount=row['DISCOUNT'],
                order_channel=row.get('ORDER_CHANNEL'),
                special_instructions=row.get('SPECIAL_INSTRUCTIONS'),
                payment_status=row['PAYMENT_STATUS'],
                payment_method=row['PAYMENT_METHOD'],
                amount_paid=row['AMOUNT_PAID'],
                delivery_type=row.get('DELIVERY_TYPE'),
                delivery_status=row.get('DELIVERY_STATUS'),
                delivery_price=row.get('DELIVERY_PRICE'),
                item_count=row['ITEM_COUNT']
            )
            for row in results
        ]
    
    # Menu Queries
    
    def get_menu_by_category(self, category: str) -> List[MenuItem]:
        """Get all menu items in a category."""
        query = "SELECT DISTINCT * FROM MENU_ITEMS WHERE CATEGORY = :cat ORDER BY ITEM_NAME"
        results = self.db.execute_query_dict(query, {"cat": category})
        return [
            MenuItem(
                menu_item_id=row['MENU_ITEM_ID'],
                item_name=row['ITEM_NAME'],
                category=row['CATEGORY'],
                item_description=row.get('ITEM_DESCRIPTION'),
                is_available=row.get('IS_AVAILABLE', True)
            )
            for row in results
        ]
    
    def get_menu_with_prices(self, category: Optional[str] = None) -> List[dict]:
        """Get full menu with all portion sizes and prices."""
        if category:
            query = """
                SELECT * FROM VW_MENU_WITH_PRICES 
                WHERE CATEGORY = :cat 
                ORDER BY ITEM_NAME, PRICE
            """
            results = self.db.execute_query_dict(query, {"cat": category})
        else:
            query = "SELECT * FROM VW_MENU_WITH_PRICES ORDER BY CATEGORY, ITEM_NAME, PRICE"
            results = self.db.execute_query_dict(query)
        return results
    
    # Delivery Queries
    
    def get_active_deliveries(self) -> List[dict]:
        """Get all active (on-going) deliveries."""
        query = "SELECT * FROM VW_ACTIVE_DELIVERIES ORDER BY DELIVERY_DATE DESC"
        return self.db.execute_query_dict(query)
    
    def get_delivery_by_id(self, delivery_id: int) -> Optional[dict]:
        """Get a specific delivery."""
        query = """
            SELECT * FROM DELIVERIES 
            WHERE DELIVERY_ID = :id
        """
        results = self.db.execute_query_dict(query, {"id": delivery_id})
        return results[0] if results else None
    
    # Revenue Queries
    
    def get_revenue_by_category(self) -> List[dict]:
        """Get revenue breakdown by menu category."""
        query = "SELECT * FROM VW_REVENUE_BY_CATEGORY"
        return self.db.execute_query_dict(query)
    
    def get_revenue_by_channel(self) -> List[dict]:
        """Get revenue breakdown by order channel."""
        query = """
            SELECT
                ORDER_CHANNEL,
                COUNT(ORDER_ID) as total_orders,
                SUM(AMOUNT_PAID) as total_revenue,
                ROUND(AVG(AMOUNT_PAID), 2) as avg_order_value
            FROM ORDERS o
            JOIN PAYMENTS p ON o.PAYMENT_ID = p.PAYMENT_ID
            GROUP BY ORDER_CHANNEL
            ORDER BY total_revenue DESC
        """
        return self.db.execute_query_dict(query)
    
    def get_monthly_revenue(self, year: Optional[int] = None) -> List[dict]:
        """Get monthly revenue trend."""
        if year:
            query = """
                SELECT
                    TO_CHAR(o.ORDER_DATE, 'YYYY-MM') as order_month,
                    COUNT(o.ORDER_ID) as orders_placed,
                    SUM(p.AMOUNT_PAID) as monthly_revenue
                FROM ORDERS o
                JOIN PAYMENTS p ON o.PAYMENT_ID = p.PAYMENT_ID
                WHERE EXTRACT(YEAR FROM o.ORDER_DATE) = :year
                GROUP BY TO_CHAR(o.ORDER_DATE, 'YYYY-MM')
                ORDER BY order_month
            """
            return self.db.execute_query_dict(query, {"year": year})
        else:
            query = """
                SELECT
                    TO_CHAR(o.ORDER_DATE, 'YYYY-MM') as order_month,
                    COUNT(o.ORDER_ID) as orders_placed,
                    SUM(p.AMOUNT_PAID) as monthly_revenue
                FROM ORDERS o
                JOIN PAYMENTS p ON o.PAYMENT_ID = p.PAYMENT_ID
                GROUP BY TO_CHAR(o.ORDER_DATE, 'YYYY-MM')
                ORDER BY order_month DESC
            """
            return self.db.execute_query_dict(query)
    
    # Customer Lifetime Value
    
    def get_top_customers(self, limit: int = 10) -> List[dict]:
        """Get top customers by lifetime value."""
        query = f"""
            SELECT
                c.CUSTOMER_ID,
                c.FIRST_NAME || ' ' || c.LAST_NAME as full_name,
                c.PHONE_NO,
                COUNT(o.ORDER_ID) as total_orders,
                SUM(p.AMOUNT_PAID) as lifetime_value
            FROM CUSTOMERS c
            LEFT JOIN ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
            LEFT JOIN PAYMENTS p ON o.PAYMENT_ID = p.PAYMENT_ID
            GROUP BY c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME, c.PHONE_NO
            ORDER BY lifetime_value DESC
            FETCH FIRST {limit} ROWS ONLY
        """
        return self.db.execute_query_dict(query)
    
    # Best Sellers
    
    def get_best_selling_items(self, limit: int = 5) -> List[dict]:
        """Get top selling menu items."""
        query = f"""
            SELECT
                mi.ITEM_NAME,
                mi.CATEGORY,
                COUNT(oi.ORDER_ITEM_ID) as times_ordered,
                SUM(oi.ITEM_SUBTOTAL) as total_revenue,
                ROUND(AVG(oi.ITEM_PRICE), 2) as avg_selling_price
            FROM ORDER_ITEMS oi
            JOIN MENU_ITEMS mi ON oi.MENU_ITEM_ID = mi.MENU_ITEM_ID
            GROUP BY mi.ITEM_NAME, mi.CATEGORY
            ORDER BY times_ordered DESC
            FETCH FIRST {limit} ROWS ONLY
        """
        return self.db.execute_query_dict(query)