# 🔄 Power BI Integration & ETL Workflow Guide

This guide shows how to create an end-to-end ETL pipeline from your Oracle database to Power BI dashboards.

---

## 📊 Architecture Overview

```
Oracle Database
    ↓
Python ETL Pipeline
    ├─ Extract (SQL queries)
    ├─ Transform (data cleaning/aggregation)
    └─ Load (CSV/JSON/Direct)
    ↓
Data Export (CSV/JSON/Parquet)
    ↓
Power BI Desktop
    ├─ Data Modeling
    ├─ DAX Calculations
    └─ Dashboard Visualization
    ↓
Power BI Service (Cloud)
    ├─ Publishing
    ├─ Sharing
    └─ Real-time Refresh
```

---

## 🚀 Step 1: Install Required Python Packages

Add to your `requirements.txt`:

```bash
pandas>=1.3.0
pyarrow>=6.0.0        # For Parquet support
```

Then install:
```bash
pip install -r requirements.txt
```

---

## 🚀 Step 2: Run the ETL Pipeline

### **Quick Start**

```bash
# Run full ETL with all export formats (CSV, JSON, Parquet)
python etl_run.py

# Export only CSV
python etl_run.py --format csv

# Export only Parquet
python etl_run.py --format parquet
```

### **What Happens**

```
📥 EXTRACT → Queries all tables from Oracle
🔄 TRANSFORM → Cleans data, handles nulls, validates types
💾 LOAD → Exports to CSV/JSON/Parquet files
📊 REPORT → Generates data quality report
```

### **Output Location**

All exports go to: `data_exports/`

```
data_exports/
├── customers_20260609_153000.csv
├── customers_20260609_153000.parquet
├── orders_summary_20260609_153000.csv
├── revenue_by_category_20260609_153000.parquet
├── monthly_revenue_20260609_153000.json
└── quality_report_20260609_153000.json
```

---

## 📊 Step 3: Connect Power BI to Your Data

### **Option A: Import CSV Files (Easiest for Testing)**

1. **Open Power BI Desktop**
2. **Click "Get Data" → "Text/CSV"**
3. **Navigate to `data_exports/` folder**
4. **Select `orders_summary_*.csv`** and click Open
5. **Click "Load"**
6. **Repeat for other CSVs** you want to analyze

### **Option B: Import Parquet Files (Better Performance)**

1. **Open Power BI Desktop**
2. **Click "Get Data" → "More..."**
3. **Search for "Parquet"** and select
4. **Navigate to `data_exports/`**
5. **Select `.parquet` files**
6. **Click "Load"**

### **Option C: Direct Oracle Connection (Production)**

1. **Open Power BI Desktop**
2. **Click "Get Data" → "Database" → "Oracle Database"**
3. **Enter:**
   - Server: `localhost:1521/ORCL`
   - Database: *(leave blank)*
4. **Click OK**
5. **Enter credentials:**
   - Username: `system`
   - Password: `your_password`
6. **Select Tables:**
   - ✓ VW_ORDER_SUMMARY
   - ✓ VW_MENU_WITH_PRICES
   - ✓ VW_ACTIVE_DELIVERIES
   - ✓ VW_REVENUE_BY_CATEGORY
7. **Click Load**

---

## 🎨 Step 4: Create Power BI Data Model

### **Set Up Relationships**

Once data is loaded:

1. **Click "Model" tab** on the left
2. **Drag and drop to create relationships:**
   - `CUSTOMERS.CUSTOMER_ID` → `VW_ORDER_SUMMARY.CUSTOMER_ID`
   - `MENU_ITEMS.CATEGORY` → `VW_REVENUE_BY_CATEGORY.CATEGORY`

---

## 📈 Step 5: Create Key Measures (DAX)

In Power BI, create these calculated measures:

```dax
-- Total Revenue
Total Revenue = SUM('revenue_by_channel'[total_revenue])

-- Average Order Value
Avg Order Value = AVERAGE('orders_summary'[order_amount])

-- Total Orders
Total Orders = COUNTA('orders_summary'[order_id])

-- Customer Count
Total Customers = DISTINCTCOUNT('customers'[customer_id])

-- Month-over-Month Growth
Revenue Growth % = 
    DIVIDE(
        [Total Revenue] - CALCULATE([Total Revenue], DATEADD('monthly_revenue'[order_month], -1, MONTH)),
        CALCULATE([Total Revenue], DATEADD('monthly_revenue'[order_month], -1, MONTH))
    ) * 100
```

---

## 🎯 Step 6: Build Dashboard Pages

### **Page 1: Executive Summary**

**Visualizations:**
- 📊 **KPI Card 1:** Total Revenue (use [Total Revenue])
- 📊 **KPI Card 2:** Average Order (use [Avg Order Value])
- 📊 **KPI Card 3:** Total Orders (use [Total Orders])
- 📊 **KPI Card 4:** Customer Count (use [Total Customers])
- 📈 **Line Chart:** Monthly Revenue Trend (X: order_month, Y: monthly_revenue)
- 🥧 **Pie Chart:** Revenue by Channel (Legend: ORDER_CHANNEL, Values: total_revenue)
- 📊 **Column Chart:** Revenue by Category (X: CATEGORY, Y: category_revenue)

### **Page 2: Customer Analytics**

**Visualizations:**
- 📊 **Table:** Top 10 Customers (Columns: full_name, total_orders, lifetime_value)
- 📊 **Slicer:** Filter by Customer (Drag CUSTOMER_ID)
- 📈 **Scatter Plot:** Lifetime Value vs Order Count (X: total_orders, Y: lifetime_value)
- 📊 **Card:** Average Customer Value (use [Avg Order Value])

### **Page 3: Product Performance**

**Visualizations:**
- 📊 **Bar Chart:** Top 10 Items (Y: ITEM_NAME, X: times_ordered)
- 📈 **Area Chart:** Sales by Category (X: CATEGORY, Y: category_revenue)
- 📊 **Table:** Menu Pricing (Columns: ITEM_NAME, min_price, max_price, avg_price)
- 🥧 **Pie Chart:** Available vs Unavailable Items (IS_AVAILABLE)

### **Page 4: Delivery & Operations**

**Visualizations:**
- 📊 **Card:** Active Deliveries (Count of DELIVERY_ID where DELIVERY_STATUS = 'ON-GOING')
- 🥧 **Pie Chart:** Delivery Status (DELIVERY_STATUS, Count)
- 📊 **Bar Chart:** Deliveries by Type (X: DELIVERY_TYPE, Y: Count)
- 📊 **Table:** Staff Workload (Columns: staff_name, deliveries_assigned, total_delivery_value_handled)

---

## 🔄 Step 7: Automate Refresh Schedule

### **Local Automation (Windows Task Scheduler)**

1. **Press Win+R**, type `taskschd.msc`, press Enter
2. **Right-click "Task Scheduler" → "Create Basic Task"**
3. **Name:** "TwitsTreatsDB ETL"
4. **Trigger:** 
   - Frequency: Daily
   - Time: 6:00 AM
5. **Action:**
   - Program: `python.exe`
   - Arguments: `C:\path\to\etl_run.py`
   - Start in: `C:\path\to\TwitsTreatsDB`
6. **Finish**

### **Linux/Mac Automation (Crontab)**

```bash
# Open crontab
crontab -e

# Add this line (runs daily at 6 AM)
0 6 * * * cd /path/to/TwitsTreatsDB && python etl_run.py

# Or run every 6 hours
0 */6 * * * cd /path/to/TwitsTreatsDB && python etl_run.py
```

### **Cloud Automation (Power BI Service)**

1. **Publish Dashboard to Power BI Service:**
   - File → Publish → Select Workspace
2. **Set Refresh Schedule:**
   - Power BI Service → Settings ⚙️
   - Datasets → Select your dataset
   - Refresh schedules → Set Daily/Hourly
3. **For On-Premises Database:**
   - Install "On-Premises Data Gateway"
   - Configure connection
   - Power BI will use gateway for refresh

---

## 📋 Data Quality Checks

After running ETL, check the quality report:

```bash
cat data_exports/quality_report_*.json
```

You'll see:
```json
{
  "orders_summary": {
    "row_count": 12,
    "column_count": 14,
    "null_counts": {"SPECIAL_INSTRUCTIONS": 5},
    "duplicate_rows": 0,
    "memory_usage_mb": 0.02
  }
}
```

**✅ Good sign:** null_counts low, duplicate_rows = 0

---

## 🚀 Publish to Power BI Service (Cloud)

### **Step 1: Save Your Report**
```
File → Save As → "TwitsTreatsDB_Dashboard"
```

### **Step 2: Publish**
```
File → Publish → Select Workspace → Publish
```

### **Step 3: Share**
- Power BI Service (web) → Click report
- Share button (top right)
- Enter colleague emails
- Click Share

### **Step 4: Set Up Refresh**
- Power BI Service → Settings ⚙️
- Datasets → Select dataset
- Refresh schedules → 
  - Toggle ON
  - Frequency: Daily
  - Time: 7:00 AM
  - Timezone: Your timezone
  - Send refresh failure notification: ON

---

## 🔍 Troubleshooting

| Issue | Solution |
|---|---|
| **Connection timeout** | Check .env, verify Oracle is running: `lsnrctl status` |
| **CSV too large** | Use Parquet format instead: `python etl_run.py --format parquet` |
| **Power BI can't find CSV** | Check file path, ensure `data_exports/` folder exists |
| **Refresh fails in cloud** | Install On-Premises Data Gateway if using local Oracle |
| **Slow refresh** | Use DirectQuery mode or filter data before import |
| **Memory issues** | Split large tables by date range, use Parquet |

---

## 📊 Power BI Best Practices

✅ **Do:**
- Use Parquet format for large datasets (faster, compressed)
- Create slicers for date ranges, channels, categories
- Use DirectQuery for real-time data (slower but current)
- Set up row-level security (RLS) for multi-user
- Add drill-through pages for detailed analysis
- Test performance on large datasets

❌ **Don't:**
- Import millions of rows (use DirectQuery instead)
- Create circular relationships
- Use very large image files on dashboards
- Forget to set up refresh schedule
- Share sensitive data without RLS

---

## 📚 Next Steps Checklist

- [ ] Run `python etl_run.py` to export data
- [ ] Open Power BI Desktop
- [ ] Import CSV/Parquet files
- [ ] Create relationships between tables
- [ ] Build 4-page dashboard
- [ ] Test all visualizations
- [ ] Save report locally
- [ ] Publish to Power BI Service
- [ ] Set up refresh schedule
- [ ] Share with team

---

## 🎉 Congratulations!

You now have a **complete end-to-end ETL pipeline** feeding Power BI dashboards with real business data!

**Next time you need fresh data:**
```bash
python etl_run.py
# Files auto-refresh in Power BI via schedule
```

For questions, see `docs/SCHEMA_OVERVIEW.md` for database details.
