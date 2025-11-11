# Databricks notebook source
import dlt
from pyspark.sql.types import *
from pyspark.sql.functions import col, from_json, current_timestamp, unbase64, window, avg, max, min, count, when, lit, to_timestamp, to_date

# ===== 🟤 BRONZE LAYER =====

# Bronze: Raw Kinesis Stream

@dlt.table(
    comment="Raw IoT sensor data from Kinesis",
    table_properties={"quality": "bronze", "source": "kinesis"}
)
def bronze_sensor_raw():
    return (
        spark.readStream
        .format("kinesis")
        .option("streamName", "iot-sensor-data")
        .option("initialPosition", "TRIM_HORIZON")
        .option("maxRecordsPerFetch", 10000)
        .option("maxFetchRate", 2.0)
        .option("serviceCredential", "databricskinesis")
        .option("region", "us-east-1")
        .load()
        .select(col("data").cast(StringType()).alias("raw_payload"))
    )


# COMMAND ----------

# Parse JSON from Kinesis
@dlt.table(
    comment="Parsed sensor data with schema validation",
    table_properties={"quality": "bronze"}
)
@dlt.expect_or_drop("valid_id", col("device_id").isNotNull())
def bronze_sensor_parsed():
    schema = StructType([
        StructField("device_id", StringType()),
        StructField("device_name", StringType()),
        StructField("location", StringType()),
        StructField("sensor_type", StringType()),
        StructField("temperature", DoubleType()),
        StructField("humidity", DoubleType()),
        StructField("vibration_intensity", DoubleType()),
        StructField("tilt_angle", DoubleType()),
        StructField("battery_level", IntegerType()),
        StructField("signal_strength", IntegerType()),
        StructField("timestamp", TimestampType()),
        StructField("status", StringType())
    ])
    
    return (
        dlt.read_stream("bronze_sensor_raw")
        .select(
            from_json(col("raw_payload"), schema).alias("parsed_data")
        )
        .select("parsed_data.*")  # ✅ Expand columns
        .withColumn("ingestion_timestamp", current_timestamp())
    )

