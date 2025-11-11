# DLT-KinesisIOT: Real-Time IoT Sensor Data Pipeline

A production-ready **Delta Live Tables (DLT)** pipeline that ingests, processes, and analyzes real-time IoT sensor data from Amazon Kinesis using the Medallion architecture on Databricks.

## 📋 Project Overview

This pipeline demonstrates a complete end-to-end streaming data architecture using:
- **Data Source**: Amazon Kinesis (real-time sensor streams)
- **Processing**: Databricks Delta Live Tables (DLT)
- **Architecture**: Medallion (Bronze → Silver → Gold layers)
- **Authentication**: AWS Service Credentials for secure Kinesis access
- **Storage**: Delta Lake format for ACID compliance and time travel

### Key Features
✅ Real-time streaming ingestion from AWS Kinesis  
✅ Automated data quality checks and validation  
✅ Multi-layer medallion architecture for data governance  
✅ Windowed aggregations for time-series analytics  
✅ Real-time alerting for anomaly detection  
✅ Data lineage and versioning with Delta Lake  
✅ Production-ready error handling  

---

## 🏗️ Architecture

### Data Flow

```
Kinesis Stream (IoT Sensors)
         ↓
┌─────────────────────────────────┐
│     🟤 BRONZE LAYER             │
│  (Raw Ingestion)                │
│  - Raw JSON payload             │
│  - Kinesis metadata             │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│     ⚪ SILVER LAYER             │
│  (Cleansing & Validation)       │
│  - Data quality checks          │
│  - Schema validation            │
│  - Business enrichment          │
│  - Anomaly categorization       │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│     🟡 GOLD LAYER               │
│  (Analytics Ready)              │
│  - 10-min aggregations          │
│  - Real-time alerts             │
│  - Daily summaries              │
│  - KPI dashboards               │
└─────────────────────────────────┘
```

### Layer Responsibilities

#### 🟤 **BRONZE Layer** (Raw Ingestion)
- Reads streaming data from Amazon Kinesis
- Minimal transformation - preserves raw data
- Automatic data type casting
- Stores metadata (partition key, shard ID, sequence number)

**Tables:**
- `bronze_sensor_raw`: Raw Kinesis payload as strings
- `bronze_sensor_parsed`: JSON parsed with schema validation

#### ⚪ **SILVER Layer** (Data Quality & Enrichment)
- Validates data against business rules
- Cleans and standardizes values
- Categorizes vibration intensity (Low/Medium/High)
- Filters invalid status records
- Applies expectations (DLT data quality framework)

**Tables:**
- `silver_sensor_cleaned`: Production-ready sensor data with quality checks

#### 🟡 **GOLD Layer** (Analytics & Aggregation)
- Time-windowed aggregations (10-minute windows)
- Real-time anomaly alerts (threshold-based)
- Daily summaries for reporting
- Business-ready KPIs

**Tables:**
- `gold_sensor_aggregates_10min`: 10-minute windowed metrics
- `gold_sensor_alerts`: Real-time threshold violations
- `gold_daily_summary`: Daily aggregated KPIs

---

## 🗂️ Project Structure

```
DLT-KinesisIOT/
│
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
│
├── transformations/
│   ├── bronze_layer.py                # Bronze table definitions
│   ├── silver_layer.py                # Silver layer transformations
│   ├── gold_layer.py                  # Gold layer aggregations
│   └── dlt_pipeline.py                # Main DLT pipeline (all-in-one)
│
├── explorations/
│   ├── kinesis_data_exploration.py    # Exploratory analysis
│   ├── data_quality_analysis.py       # Quality metrics inspection
│   └── debugging_notes.py             # Troubleshooting reference
│
├── utilities/
│   ├── schemas.py                     # Reusable schema definitions
│   ├── config.py                      # Configuration constants
│   └── helpers.py                     # Helper functions
│
└── docs/
    ├── SETUP_GUIDE.md                 # AWS & Databricks setup
    ├── TROUBLESHOOTING.md             # Common issues & solutions
    └── ARCHITECTURE_DETAILS.md        # Deep dive on design
```

---

## 🚀 Getting Started

### Prerequisites

1. **AWS Account**
   - AWS IAM role with Kinesis permissions
   - Kinesis stream created (`iot-sensor-data`)
   - Service credentials configured

2. **Databricks Workspace**
   - Databricks on AWS enabled for Unity Catalog
   - Cluster with DBR 14.0+ (Spark 3.5+)
   - Service credential configured

3. **Tools**
   - Python 3.8+
   - Databricks CLI (optional)
   - AWS CLI (for Kinesis management)

### Step 1: Setup AWS Kinesis

```bash
# Create Kinesis stream
aws kinesis create-stream \
  --stream-name iot-sensor-data \
  --shard-count 1 \
  --region us-east-1

# Verify stream
aws kinesis describe-stream --stream-name iot-sensor-data --region us-east-1
```

### Step 2: Configure Databricks Service Credential

1. In Databricks workspace, go to **Admin Settings > Service Credentials**
2. Click **Create Credential**
3. Name: `kinesis-credential`
4. Role ARN: `arn:aws:iam::YOUR_ACCOUNT_ID:role/DatabricksKinesisDLTRole`
5. Copy the **External ID** generated
6. Update AWS IAM role trust policy with the External ID

### Step 3: Upload Pipeline Code

1. Clone/download this repository
2. Create a folder in your Databricks workspace: `/Workspace/DLT-KinesisIOT`
3. Upload files from `transformations/` folder

### Step 4: Create DLT Pipeline

1. In Databricks, go to **Workflows > Delta Live Tables > Create Pipeline**
2. **Pipeline name**: `dlt-kinesis-iot-pipeline`
3. **Notebook path**: `/DLT-KinesisIOT/transformations/dlt_pipeline.py`
4. **Storage location**: `s3://your-bucket/medallion-warehouse`
5. **Cluster mode**: Triggered (or Continuous for real-time)
6. Click **Create**

### Step 5: Start Sending Data

Use the Kinesis Data Generator to send test data:
[https://awslabs.github.io/amazon-kinesis-data-generator/web/producer.html](https://awslabs.github.io/amazon-kinesis-data-generator/web/producer.html)

**Template for KDG:**
```json
{
  "device_id": "SENSOR-{{random(1, 3)}}",
  "device_name": "Bridge-{{random(1, 3)}}",
  "location": "latitude:40.{{random(7100, 7200)}},longitude:-74.{{random(5, 100)}}",
  "sensor_type": "temperature",
  "temperature": {{random(15, 35)}},
  "humidity": {{random(50, 80)}},
  "vibration_intensity": {{random(0, 3)}},
  "tilt_angle": {{random(0, 5)}},
  "battery_level": {{random(20, 100)}},
  "signal_strength": {{random(-80, -40)}},
  "timestamp": "{{timestamp}}",
  "status": "normal"
}
```

### Step 6: Run the Pipeline

```sql
-- In Databricks SQL
-- View Bronze data
SELECT * FROM bronze_sensor_parsed LIMIT 10;

-- View Silver cleaned data
SELECT device_id, temperature, vibration_category FROM silver_sensor_cleaned LIMIT 10;

-- View Gold aggregations
SELECT * FROM gold_sensor_aggregates_10min LIMIT 5;

-- Check alerts
SELECT * FROM gold_sensor_alerts ORDER BY alert_timestamp DESC LIMIT 10;
```

---

## 📊 Data Schema

### Input Schema (IoT Sensors)

| Field | Type | Description |
|-------|------|-------------|
| device_id | String | Unique sensor identifier |
| device_name | String | Friendly sensor name |
| location | String | Lat/long coordinates |
| sensor_type | String | Type of sensor (temperature, etc) |
| temperature | Double | Temperature in Celsius |
| humidity | Double | Humidity percentage (0-100) |
| vibration_intensity | Double | Vibration magnitude |
| tilt_angle | Double | Tilt angle in degrees |
| battery_level | Integer | Battery percentage (0-100) |
| signal_strength | Integer | Signal strength in dBm |
| timestamp | Timestamp | Event timestamp (ISO 8601) |
| status | String | Sensor status (normal/error) |

### Gold Layer Aggregations (10-min window)

| Field | Type | Description |
|-------|------|-------------|
| window_start | Timestamp | Window start time |
| window_end | Timestamp | Window end time |
| device_id | String | Sensor ID |
| device_name | String | Sensor name |
| avg_temperature | Double | Average temperature in window |
| max_temperature | Double | Maximum temperature in window |
| min_temperature | Double | Minimum temperature in window |
| avg_humidity | Double | Average humidity |
| max_vibration | Double | Peak vibration intensity |
| avg_vibration | Double | Average vibration |
| min_battery | Integer | Lowest battery level in window |
| record_count | Long | Number of records in window |

---

## 🔧 Configuration

### Edit Pipeline Parameters

File: `utilities/config.py`

```python
# Kinesis Configuration
STREAM_NAME = "iot-sensor-data"
SERVICE_CREDENTIAL = "kinesis-credential"
INITIAL_POSITION = "TRIM_HORIZON"  # or "LATEST"
MAX_RECORDS_PER_FETCH = 10000
MAX_FETCH_RATE = 2.0
REGION = "us-east-1"

# Alert Thresholds
TEMP_HIGH_THRESHOLD = 50  # Celsius
TEMP_LOW_THRESHOLD = 5    # Celsius
HUMIDITY_HIGH_THRESHOLD = 85  # %
VIBRATION_HIGH_THRESHOLD = 2.0  # intensity units
BATTERY_LOW_THRESHOLD = 20  # %

# Aggregation Windows
WINDOW_DURATION = "10 minutes"
```

---

## 📈 Monitoring & Observability

### View Pipeline Progress

```sql
-- Check table lineage
SELECT * FROM dlt.event_log WHERE table IN (
  'bronze_sensor_raw', 
  'silver_sensor_cleaned', 
  'gold_sensor_alerts'
);

-- Monitor data quality expectations
SELECT 
  table_name,
  expectation_name,
  passed_records,
  failed_records
FROM dlt.event_log 
WHERE event_type = 'flow_definition'
ORDER BY timestamp DESC;
```

### Create Dashboards

Example queries for dashboarding:

```sql
-- Temperature trends (10-min)
SELECT 
  window_start,
  device_name,
  avg_temperature,
  max_temperature
FROM gold_sensor_aggregates_10min
ORDER BY window_start DESC;

-- Alert frequency by device
SELECT 
  device_name,
  alert_type,
  COUNT(*) as alert_count
FROM gold_sensor_alerts
GROUP BY device_name, alert_type
ORDER BY alert_count DESC;

-- Daily sensor performance
SELECT 
  date,
  device_name,
  daily_avg_temp,
  high_vibration_count,
  daily_min_battery
FROM gold_daily_summary
WHERE date >= CURRENT_DATE - INTERVAL 7 DAY
ORDER BY date DESC;
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Kinesis credentials invalid
```
Solution: Verify service credential External ID matches AWS IAM trust policy
```

**Issue**: JSON parsing errors (all NULL values)
```
Solution: Ensure raw_payload is String type, not struct. Use from_json(col("raw_payload"), schema) without .cast()
```

**Issue**: Data quality expectations failing
```
Solution: Check alert thresholds in utilities/config.py match your data ranges
```

See `docs/TROUBLESHOOTING.md` for more detailed solutions.

---

## 🔐 Security Best Practices

✅ **Use Service Credentials** - Never hardcode AWS access keys  
✅ **Enable Audit Logging** - Track all data access via Unity Catalog  
✅ **Encrypt Storage** - Use S3 encryption for medallion warehouse  
✅ **Scope IAM Permissions** - Use least privilege for Kinesis role  
✅ **Rotate Credentials** - Regularly update service credentials  
✅ **Mask Sensitive Data** - Use column-level security for PII (if applicable)  

---

## 📝 Usage Examples

### Query Real-Time Aggregations

```python
# PySpark
df_agg = spark.table("gold_sensor_aggregates_10min") \
  .filter("window_start >= current_timestamp() - INTERVAL 1 HOUR") \
  .filter("device_name = 'Bridge-North-Tower'")

display(df_agg)
```

### Export to External Systems

```python
# Export alerts to S3
spark.table("gold_sensor_alerts") \
  .write \
  .mode("append") \
  .parquet("s3://my-bucket/alerts/")

# Export to Redshift
df = spark.table("gold_daily_summary")
df.write \
  .format("redshift") \
  .option("url", "jdbc:redshift://...") \
  .mode("overwrite") \
  .save()
```

### Schedule Pipeline

```bash
# Using Databricks CLI
databricks jobs create --json '{
  "name": "DLT-KinesisIOT-Nightly",
  "schedule": {"quartz_cron_expression": "0 0 * * * ?"},
  "pipeline_task": {
    "pipeline_id": "<pipeline-id>"
  }
}'
```

---

## 📚 Resources

- **Databricks DLT Documentation**: [https://docs.databricks.com/dlt](https://docs.databricks.com/dlt)
- **AWS Kinesis Documentation**: [https://docs.aws.amazon.com/kinesis/](https://docs.aws.amazon.com/kinesis/)
- **Delta Lake Format**: [https://delta.io/](https://delta.io/)
- **Medallion Architecture**: [https://www.databricks.com/blog/2022/06/24/simplify-data-pipelines-with-delta-live-tables.html](https://www.databricks.com/blog/2022/06/24/simplify-data-pipelines-with-delta-live-tables.html)

---

## 🤝 Contributing

To contribute improvements:
1. Create a feature branch
2. Test changes locally in Databricks workspace
3. Submit pull request with detailed description
4. Update documentation

---

## 📄 License

This project is provided as-is for educational and production use.

---

## 👤 Author

**Your Name** | Cloud Data Engineer  
📧 Email: your-email@example.com  
💼 LinkedIn: [your-profile](https://linkedin.com/in/your-profile)  
🔗 GitHub: [your-repo](https://github.com/your-repo)

---

## 🗓️ Changelog

### v1.0.0 (Nov 11, 2025)
- ✅ Initial release with Bronze, Silver, Gold layers
- ✅ Real-time alerting with threshold detection
- ✅ 10-minute aggregations for time-series analytics
- ✅ Data quality checks with DLT expectations
- ✅ Production-ready Kinesis integration

---

## 📞 Support

For issues or questions:
1. Check `docs/TROUBLESHOOTING.md`
2. Review `explorations/debugging_notes.py`
3. Open an issue in the repository
4. Contact the development team

---

**Last Updated**: November 11, 2025  
**Status**: Production Ready ✅
