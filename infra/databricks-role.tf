

resource "aws_iam_role" "databricks_kinesis_dlt" {
  name = "DatabricksKinesisDLTRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = [
            "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL",
            "arn:aws:iam::211125482456:role/DatabricksKinesisDLTRole"
          ]
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.databricks_external_id
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "databricks_kinesis_policy" {
  name = "DatabricksKinesisAccess"
  role = aws_iam_role.databricks_kinesis_dlt.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:DescribeStreamSummary",
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:ListShards",
          "kinesis:ListStreams",
          "kinesis:SubscribeToShard"
        ]
        Resource = aws_kinesis_stream.iot_sensor_data.arn
      },
      {
        Effect = "Allow"
        Action = ["kinesis:ListStreams"]
        Resource = "*"
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

output "databricks_role_arn" {
  value       = aws_iam_role.databricks_kinesis_dlt.arn
  description = "ARN da role para configurar no Databricks Unity Catalog"
}

output "next_steps" {
  value = <<-EOT
  
  1. Copie o ARN: ${aws_iam_role.databricks_kinesis_dlt.arn}
  2. Crie Service Credential no Databricks com este ARN
  3. Copie o External ID gerado
  4. Execute: terraform apply -var="databricks_external_id=SEU_ID"
  
  EOT
}
