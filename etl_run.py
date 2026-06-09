#!/usr/bin/env python3
"""
ETL Pipeline Runner - Execute full extraction, transformation, and loading.
Run this script to update Power BI data exports.

Usage:
    python etl_run.py                    # Run full ETL with all formats
    python etl_run.py --format csv       # Only export CSV
    python etl_run.py --format parquet   # Only export Parquet
"""

import sys
import argparse
from python.db_connection import OracleConnection
from python.etl_pipeline import ETLPipeline


def main():
    """Main ETL execution."""
    parser = argparse.ArgumentParser(description='Run TwitsTreatsDB ETL Pipeline')
    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'parquet', 'all'],
        default='all',
        help='Export format (default: all)'
    )
    
    args = parser.parse_args()
    
    # Map format to list
    formats_map = {
        'csv': ['csv'],
        'json': ['json'],
        'parquet': ['parquet'],
        'all': ['csv', 'json', 'parquet']
    }
    export_formats = formats_map[args.format]
    
    try:
        # Connect to database
        print("\n🔗 Connecting to Oracle database...")
        db = OracleConnection()
        
        # Verify connection
        if not db.test_connection():
            print("❌ Failed to connect to database")
            print("   ℹ️  Check your .env file and Oracle connection settings")
            return 1
        
        print("✓ Database connection successful")
        
        # Initialize ETL pipeline
        pipeline = ETLPipeline(db)
        
        # Run full ETL
        data = pipeline.run_full_etl(export_formats=export_formats)
        
        # Generate quality report
        pipeline.generate_quality_report(data)
        
        print("\n✅ ETL completed successfully!")
        print("📊 Data ready for Power BI import")
        print("📁 Check 'data_exports/' folder for exported files\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ETL failed with error:")
        print(f"   {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
