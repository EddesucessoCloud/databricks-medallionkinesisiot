resource "aws_kinesis_stream" "iot_sensor_data" {
  name             = "iot-sensor-data"
  shard_count      = 1
  retention_period = 24

  shard_level_metrics = [
    "IncomingBytes",
    "IncomingRecords",
    "OutgoingBytes",
    "OutgoingRecords",
  ]

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  tags = {
    Name        = "IoT Sensor Data Stream"
    Environment = "production"
  }
}

resource "aws_kinesis_firehose_delivery_stream" "iot_to_s3" {
  name        = "iot-sensor-data-to-s3"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.iot_data.arn
    prefix     = "iot-data/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    error_output_prefix = "errors/"

    compression_format = "GZIP"
  }

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.iot_sensor_data.arn
    role_arn           = aws_iam_role.firehose_role.arn
  }
}

resource "aws_s3_bucket" "iot_data" {
  bucket = "iot-sensor-data-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_lifecycle_configuration" "iot_data_lifecycle" {
  bucket = aws_s3_bucket.iot_data.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 90
    }
  }
}

resource "aws_iam_role" "firehose_role" {
  name = "KinesisFirehoseIoTRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "firehose.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "firehose_policy" {
  name = "FirehoseS3Policy"
  role = aws_iam_role.firehose_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.iot_data.arn,
          "${aws_s3_bucket.iot_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListShards"
        ]
        Resource = aws_kinesis_stream.iot_sensor_data.arn
      }
    ]
  })
}


output "kinesis_stream_name" {
  value       = aws_kinesis_stream.iot_sensor_data.name
  description = "Nome do Kinesis Stream"
}

output "kinesis_stream_arn" {
  value       = aws_kinesis_stream.iot_sensor_data.arn
  description = "ARN do Kinesis Stream"
}

output "firehose_name" {
  value       = aws_kinesis_firehose_delivery_stream.iot_to_s3.name
  description = "Nome do Firehose Delivery Stream"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.iot_data.id
  description = "Nome do bucket S3 para dados IoT"
}
