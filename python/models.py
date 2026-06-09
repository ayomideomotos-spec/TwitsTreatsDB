"""
Data Models for Twit's Treats
ORM-style data classes representing database entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    """Customer entity."""
    customer_id: int
    first_name: str
    last_name: str
    phone_no: str
    email: Optional[str] = None
    social_handle: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Staff:
    """Staff member entity."""
    staff_id: int
    first_name: str
    last_name: str
    staff_role: str
    pay_rate: float
    contact_info: Optional[str] = None


@dataclass
class MenuItem:
    """Menu item entity."""
    menu_item_id: int
    item_name: str
    category: str
    item_description: Optional[str] = None
    is_available: bool = True


@dataclass
class MenuItemPortion:
    """Menu item portion entity."""
    portion_id: int
    menu_item_id: int
    portion_package: str
    portion_size: str
    price: float


@dataclass
class Payment:
    """Payment entity."""
    payment_id: int
    payment_status: str
    payment_method: str
    amount_paid: float
    payment_date: Optional[datetime] = None


@dataclass
class Order:
    """Order entity."""
    order_id: int
    order_date: datetime
    customer_id: int
    payment_id: int
    order_amount: float
    discount: float = 0.0
    order_channel: Optional[str] = None
    special_instructions: Optional[str] = None


@dataclass
class OrderItem:
    """Order line item entity."""
    order_item_id: int
    order_id: int
    menu_item_id: Optional[int] = None
    item_quantity: Optional[int] = None
    item_price: Optional[float] = None
    item_subtotal: Optional[float] = None
    item_name: Optional[str] = None


@dataclass
class Delivery:
    """Delivery entity."""
    delivery_id: int
    payment_id: int
    staff_id: Optional[int] = None
    delivery_type: Optional[str] = None
    delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    delivery_price: float = 0.0
    delivery_status: str = "ON-GOING"


@dataclass
class Event:
    """Catering event entity."""
    event_id: int
    order_id: int
    event_type: str
    event_date: datetime
    event_location: str
    guest_count: int
    quoted_cost: float
    notes: Optional[str] = None


# Summary/View Models

@dataclass
class OrderSummary:
    """Summary view of an order with all related information."""
    order_id: int
    order_date: datetime
    customer_name: str
    phone_no: str
    order_amount: float
    discount: float
    order_channel: Optional[str]
    special_instructions: Optional[str]
    payment_status: str
    payment_method: str
    amount_paid: float
    delivery_type: Optional[str]
    delivery_status: Optional[str]
    delivery_price: Optional[float]
    item_count: int


@dataclass
class CustomerLifetimeValue:
    """Customer lifetime value metrics."""
    customer_id: int
    full_name: str
    phone_no: str
    total_orders: int
    lifetime_value: float
    first_order: Optional[datetime]
    last_order: Optional[datetime]