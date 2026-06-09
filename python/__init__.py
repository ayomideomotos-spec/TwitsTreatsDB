"""
TwitsTreatsDB Python Package
A Python interface for interacting with the Twit's Treats Oracle database.
"""

__version__ = "1.0.0"
__author__ = "Ayomide Omotoso"

from .db_connection import OracleConnection
from .models import Customer, Staff, MenuItem, Payment, Order
from .queries import QueryExecutor

__all__ = [
    'OracleConnection',
    'Customer',
    'Staff',
    'MenuItem',
    'Payment',
    'Order',
    'QueryExecutor'
]