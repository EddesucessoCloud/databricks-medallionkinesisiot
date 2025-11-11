# Databricks notebook source
import dlt
from pyspark.sql.types import *
from pyspark.sql.functions import col, when, current_timestamp

# Reference Table: Device Metadata (Static)
@dlt.table(
    comment="Device master data",
    table_properties={"quality": "silver", "type": "static"}
)
def silver_device_metadata():
    return spark.createDataFrame([
        ("SENSOR-001", "Bridge-North-Tower", "40.7128,-74.0060", "Critical Infrastructure"),
        ("SENSOR-002", "Bridge-South-Tower", "40.7124,-74.0065", "Critical Infrastructure"),
        ("SENSOR-003", "Building-MainOffice", "40.7150,-74.0050", "Monitoring"),
    ], ["device_id", "device_name", "location", "category"])

# Silver: Cleaned Sensor Data with Quality Checks
@dlt.table(
    comment="Cleaned and validated sensor data",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_temperature", (col("temperature_celsius") >= -50) & (col("temperature_celsius") <= 70))
@dlt.expect_or_drop("valid_humidity", (col("humidity_percent") >= 0) & (col("humidity_percent") <= 100))
@dlt.expect_or_drop("not_null_device_id", col("device_id").isNotNull())
@dlt.expect_or_drop("positive_battery", col("battery_level") > 0)
def silver_sensor_cleaned():
    return (
        dlt.read_stream("bronze_sensor_parsed")
        .filter(col("status") == "normal")  # Remove error states
        .withColumn("temperature_celsius", col("temperature"))
        .withColumn("humidity_percent", col("humidity"))
        .withColumn("vibration_category", 
                    when(col("vibration_intensity") > 1.0, "High")
                    .when(col("vibration_intensity") > 0.5, "Medium")
                    .otherwise("Low"))
        .select(
            "device_id", "device_name", "sensor_type",
            "temperature_celsius", "humidity_percent",
            "vibration_intensity", "vibration_category",
            "tilt_angle", "battery_level", "signal_strength",
            "timestamp"
        )
    )

# Silver: Enriched with Device Metadata (Stream-Static Join)
@dlt.table(
    comment="Sensor data enriched with device metadata",
    table_properties={"quality": "silver"}
)
def silver_sensor_enriched():
    return (
        dlt.read_stream("silver_sensor_cleaned")
        .join(
            dlt.read("silver_device_metadata"),
            on="device_id",
            how="left"
        )
        .select(
            col("device_id"), col("silver_device_metadata.device_name"),
            col("category"), col("sensor_type"),
            col("temperature_celsius"), col("humidity_percent"),
            col("vibration_intensity"), col("vibration_category"),
            col("tilt_angle"), col("battery_level"),
            col("timestamp"),
            current_timestamp().alias("enrichment_timestamp")
        )
    )

