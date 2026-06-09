"""
Oracle Database Connection Handler
Manages connections to the Twit's Treats Oracle database.
"""

import cx_Oracle
from typing import Optional, Any
from .config import (
    ORACLE_HOST, ORACLE_PORT, ORACLE_SID, ORACLE_USER, ORACLE_PASSWORD,
    CONNECTION_POOL_MIN, CONNECTION_POOL_MAX, CONNECTION_POOL_INCREMENT
)


class OracleConnection:
    """Handles Oracle database connections with connection pooling."""
    
    _pool = None
    
    def __init__(self):
        """Initialize Oracle connection."""
        self.connection = None
        self._init_pool()
        self.connection = self._get_connection()
    
    @staticmethod
    def _init_pool():
        """Initialize connection pool (one-time setup)."""
        if OracleConnection._pool is None:
            dsn = cx_Oracle.makedsn(ORACLE_HOST, ORACLE_PORT, ORACLE_SID)
            OracleConnection._pool = cx_Oracle.SessionPool(
                user=ORACLE_USER,
                password=ORACLE_PASSWORD,
                dsn=dsn,
                min=CONNECTION_POOL_MIN,
                max=CONNECTION_POOL_MAX,
                increment=CONNECTION_POOL_INCREMENT
            )
    
    @staticmethod
    def _get_connection():
        """Get a connection from the pool."""
        return OracleConnection._pool.acquire()
    
    def execute_query(self, query: str, params: Optional[dict] = None) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Dictionary of query parameters
        
        Returns:
            List of tuples containing query results
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def execute_query_dict(self, query: str, params: Optional[dict] = None) -> list:
        """
        Execute a SELECT query and return results as dictionaries.
        
        Args:
            query: SQL query string
            params: Dictionary of query parameters
        
        Returns:
            List of dictionaries containing query results
        """
        cursor = self.connection.cursor()
        cursor.rowfactory = lambda *args: dict(
            zip([d[0] for d in cursor.description], args)
        )
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def execute_update(self, query: str, params: Optional[dict] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Dictionary of query parameters
        
        Returns:
            Number of rows affected
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def call_procedure(self, proc_name: str, params: dict) -> Any:
        """
        Call a stored procedure.
        
        Args:
            proc_name: Name of the stored procedure
            params: Dictionary of procedure parameters
        
        Returns:
            Result from the stored procedure
        """
        cursor = self.connection.cursor()
        try:
            result = cursor.callfunc(proc_name, cx_Oracle.STRING, [params.values()])
            self.connection.commit()
            return result
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def test_connection(self) -> bool:
        """Test if the database connection is active."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.close()
            return True
        except Exception:
            return False
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()