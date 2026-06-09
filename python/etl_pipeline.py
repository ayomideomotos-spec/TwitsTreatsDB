"""
ETL Pipeline for TwitsTreatsDB
Extract data from Oracle, transform it, and export to multiple formats.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from .db_connection import OracleConnection
from .queries import QueryExecutor


class ETLPipeline:
    """Main ETL orchestrator."""
    
    def __init__(self, db_connection: OracleConnection):
        """Initialize ETL pipeline."""
        self.db = db_connection
        self.executor = QueryExecutor(db_connection)
        self.export_dir = "data_exports"
        self._create_export_dir()
    
    def _create_export_dir(self):
        """Create export directory if it doesn't exist."""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    # ===== EXTRACT PHASE =====
    
    def extract_customers(self) -> pd.DataFrame:
        """Extract all customers."""
        query = "SELECT * FROM CUSTOMERS ORDER BY CUSTOMER_ID"
        results = self.db.execute_query_dict(query)
        return pd.DataFrame(results)
    
    def extract_orders_summary(self) -> pd.DataFrame:
        """Extract order summary view."""
        query = "SELECT * FROM VW_ORDER_SUMMARY ORDER BY ORDER_DATE DESC"
        results = self.db.execute_query_dict(query)
        return pd.DataFrame(results)
    
    def extract_revenue_by_category(self) -> pd.DataFrame:
        """Extract revenue by category."""
        return pd.DataFrame(self.executor.get_revenue_by_category())
    
    def extract_revenue_by_channel(self) -> pd.DataFrame:
        """Extract revenue by channel."""
        return pd.DataFrame(self.executor.get_revenue_by_channel())
    
    def extract_top_customers(self, limit: int = 50) -> pd.DataFrame:
        """Extract top customers by lifetime value."""
        return pd.DataFrame(self.executor.get_top_customers(limit=limit))
    
    def extract_best_selling_items(self, limit: int = 20) -> pd.DataFrame:
        """Extract best selling items."""
        return pd.DataFrame(self.executor.get_best_selling_items(limit=limit))
    
    def extract_monthly_revenue(self) -> pd.DataFrame:
        """Extract monthly revenue trend."""
        return pd.DataFrame(self.executor.get_monthly_revenue())
    
    def extract_active_deliveries(self) -> pd.DataFrame:
        """Extract active deliveries."""
        return pd.DataFrame(self.executor.get_active_deliveries())
    
    def extract_menu_with_prices(self) -> pd.DataFrame:
        """Extract menu with all prices."""
        return pd.DataFrame(self.executor.get_menu_with_prices())
    
    def extract_all_tables(self) -> Dict[str, pd.DataFrame]:
        """Extract all key tables at once."""
        return {
            'customers': self.extract_customers(),
            'orders_summary': self.extract_orders_summary(),
            'revenue_by_category': self.extract_revenue_by_category(),
            'revenue_by_channel': self.extract_revenue_by_channel(),
            'top_customers': self.extract_top_customers(),
            'best_selling_items': self.extract_best_selling_items(),
            'monthly_revenue': self.extract_monthly_revenue(),
            'active_deliveries': self.extract_active_deliveries(),
            'menu_with_prices': self.extract_menu_with_prices(),
        }
    
    # ===== TRANSFORM PHASE =====
    
    def transform_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert date strings to datetime objects."""
        date_columns = df.select_dtypes(include=['object']).columns
        for col in date_columns:
            if 'DATE' in col.upper() or 'TIMESTAMP' in col.upper():
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    
    def transform_currency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure currency columns are numeric."""
        currency_keywords = ['AMOUNT', 'PRICE', 'REVENUE', 'COST', 'RATE', 'VALUE']
        for col in df.columns:
            if any(keyword in col.upper() for keyword in currency_keywords):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    def transform_remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows."""
        initial_count = len(df)
        df = df.drop_duplicates()
        removed = initial_count - len(df)
        if removed > 0:
            print(f"  ⚠️  Removed {removed} duplicate rows")
        return df
    
    def transform_fill_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle null values intelligently."""
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('N/A')
            elif df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(0)
        return df
    
    def transform_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run full transformation pipeline on a dataframe."""
        print(f"  📊 Transforming {len(df)} rows...")
        df = self.transform_dates(df)
        df = self.transform_currency(df)
        df = self.transform_remove_duplicates(df)
        df = self.transform_fill_nulls(df)
        print(f"  ✓ Transformation complete: {len(df)} rows")
        return df
    
    # ===== LOAD PHASE =====
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """Export dataframe to CSV."""
        filepath = os.path.join(self.export_dir, f"{filename}.csv")
        df.to_csv(filepath, index=False)
        print(f"    ✓ CSV: {os.path.basename(filepath)}")
        return filepath
    
    def export_to_json(self, df: pd.DataFrame, filename: str) -> str:
        """Export dataframe to JSON."""
        filepath = os.path.join(self.export_dir, f"{filename}.json")
        df.to_json(filepath, orient='records', indent=2, date_format='iso')
        print(f"    ✓ JSON: {os.path.basename(filepath)}")
        return filepath
    
    def export_to_parquet(self, df: pd.DataFrame, filename: str) -> str:
        """Export dataframe to Parquet (optimized for BI tools)."""
        try:
            filepath = os.path.join(self.export_dir, f"{filename}.parquet")
            df.to_parquet(filepath, index=False)
            print(f"    ✓ Parquet: {os.path.basename(filepath)}")
            return filepath
        except ImportError:
            print("    ⚠️  Parquet export skipped (install pyarrow: pip install pyarrow)")
            return None
    
    def export_all_formats(self, df: pd.DataFrame, filename: str):
        """Export to all formats."""
        self.export_to_csv(df, filename)
        self.export_to_json(df, filename)
        self.export_to_parquet(df, filename)
    
    # ===== FULL ETL RUN =====
    
    def run_full_etl(self, export_formats: List[str] = ['csv', 'json', 'parquet']) -> Dict:
        """Run complete ETL pipeline."""
        print("\n" + "="*70)
        print("🚀 STARTING FULL ETL PIPELINE")
        print("="*70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {}
        
        # Extract all tables
        print("\n📥 EXTRACT PHASE")
        print("-" * 70)
        all_data = self.extract_all_tables()
        print(f"✓ Extracted {len(all_data)} tables")
        
        # Transform and export each table
        print("\n🔄 TRANSFORM & LOAD PHASE")
        print("-" * 70)
        for table_name, df in all_data.items():
            print(f"\n📋 {table_name.upper()}")
            df_transformed = self.transform_pipeline(df)
            results[table_name] = df_transformed
            
            # Load/Export
            print(f"  💾 Exporting to formats:")
            for fmt in export_formats:
                if fmt == 'csv':
                    self.export_to_csv(df_transformed, f"{table_name}_{timestamp}")
                elif fmt == 'json':
                    self.export_to_json(df_transformed, f"{table_name}_{timestamp}")
                elif fmt == 'parquet':
                    self.export_to_parquet(df_transformed, f"{table_name}_{timestamp}")
        
        print("\n" + "="*70)
        print("✅ ETL PIPELINE COMPLETE")
        print("="*70)
        print(f"📁 Exported to: {os.path.abspath(self.export_dir)}/")
        
        return results
    
    # ===== QUALITY CHECKS =====
    
    def data_quality_report(self, df: pd.DataFrame, table_name: str = "Table") -> Dict:
        """Generate data quality report."""
        report = {
            'table_name': table_name,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': len(df[df.duplicated()]),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
        return report
    
    def generate_quality_report(self, data_dict: Dict[str, pd.DataFrame]) -> str:
        """Generate quality report for all tables."""
        reports = {}
        for table_name, df in data_dict.items():
            reports[table_name] = self.data_quality_report(df, table_name)
        
        # Save report
        report_path = os.path.join(self.export_dir, f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w') as f:
            json.dump(reports, f, indent=2)
        
        print(f"\n📋 Quality report: {os.path.basename(report_path)}")
        return report_path
