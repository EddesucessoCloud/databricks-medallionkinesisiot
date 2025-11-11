# Databricks notebook source
import dlt
from pyspark.sql.functions import col, when, current_timestamp, window, to_date, avg, count, max, min, expr

# Gold: 10-Minute Windowed Aggregations
@dlt.table(
    comment="10-minute aggregated metrics by device",
    table_properties={"quality": "gold", "refresh": "triggered"}
)
def gold_sensor_aggregates_10min():
    return (
        dlt.read_stream("silver_sensor_enriched")
        .groupby(
            window(col("timestamp"), "10 minutes"),
            col("device_id"),
            col("device_name"),
            col("category")
        )
        .agg(
            avg(col("temperature_celsius")).alias("avg_temperature"),
            max(col("temperature_celsius")).alias("max_temperature"),
            min(col("temperature_celsius")).alias("min_temperature"),
            avg(col("humidity_percent")).alias("avg_humidity"),
            max(col("vibration_intensity")).alias("max_vibration"),
            avg(col("vibration_intensity")).alias("avg_vibration"),
            max(col("tilt_angle")).alias("max_tilt"),
            min(col("battery_level")).alias("min_battery"),
            count("*").alias("record_count")
        )
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("device_id"),
            col("device_name"),
            col("category"),
            col("avg_temperature"),
            col("max_temperature"),
            col("min_temperature"),
            col("avg_humidity"),
            col("max_vibration"),
            col("avg_vibration"),
            col("max_tilt"),
            col("min_battery"),
            col("record_count")
        )
    )

# Gold: Alerts - Anomaly Detection
@dlt.table(
    comment="Real-time alerts for anomalies",
    table_properties={"quality": "gold"}
)
def gold_sensor_alerts():
    return (
        dlt.read_stream("silver_sensor_enriched")
        .filter(
            (col("temperature_celsius") > 50) |  # Too hot
            (col("temperature_celsius") < 5) |   # Too cold
            (col("humidity_percent") > 85) |     # Too humid
            (col("vibration_intensity") > 2.0) | # High vibration
            (col("battery_level") < 20)          # Low battery
        )
        .select(
            col("device_id"),
            col("device_name"),
            col("category"),
            col("timestamp"),
            col("temperature_celsius"),
            col("vibration_intensity"),
            col("battery_level"),
            when(col("temperature_celsius") > 50, "High Temperature")
            .when(col("temperature_celsius") < 5, "Low Temperature")
            .when(col("humidity_percent") > 85, "High Humidity")
            .when(col("vibration_intensity") > 2.0, "High Vibration")
            .when(col("battery_level") < 20, "Low Battery")
            .otherwise("Unknown").alias("alert_type"),
            current_timestamp().alias("alert_timestamp")
        )
    )

# Gold: Daily Summary Dashboard Table
@dlt.table(
    comment="Daily summary for dashboards and reports",
    table_properties={"quality": "gold", "refresh": "triggered"}
)
def gold_daily_summary():
    return (
        dlt.read_stream("silver_sensor_enriched")
        .groupBy(
            to_date(col("timestamp")).alias("date"),
            col("device_id"),
            col("category")
        )
        .agg(
            avg(col("temperature_celsius")).alias("daily_avg_temp"),
            max(col("vibration_intensity")).alias("daily_max_vibration"),
            min(col("battery_level")).alias("daily_min_battery"),
            count("*").alias("total_records"),
            expr("count_if(vibration_category = 'High')").alias("high_vibration_count")
        )
        .select(
            col("date"),
            col("device_id"),
            col("category"),
            col("daily_avg_temp"),
            col("daily_max_vibration"),
            col("daily_min_battery"),
            col("total_records"),
            col("high_vibration_count")
        )
    )

