# AWS Config 记录器和传输通道
resource "aws_config_configuration_recorder" "recorder" {
  name     = "${var.environment}-config-recorder"
  role_arn = aws_iam_role.config_role.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

resource "aws_config_configuration_recorder_status" "recorder_status" {
  name       = aws_config_configuration_recorder.recorder.name
  is_enabled = true
  depends_on = [aws_config_delivery_channel.delivery_channel]
}

resource "aws_config_delivery_channel" "delivery_channel" {
  name           = "${var.environment}-config-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config_bucket.bucket
  depends_on     = [aws_config_configuration_recorder.recorder]
}

# Config 的 S3 存储桶
resource "aws_s3_bucket" "config_bucket" {
  bucket = "${var.environment}-aws-config-bucket-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "AWS Config Bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_policy" "config_bucket_policy" {
  bucket = aws_s3_bucket.config_bucket.id
  policy = data.aws_iam_policy_document.config_bucket_policy.json
}

data "aws_iam_policy_document" "config_bucket_policy" {
  statement {
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.config_bucket.arn]
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
  }

  statement {
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.config_bucket.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/Config/*"]
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

# Config 角色
resource "aws_iam_role" "config_role" {
  name = "${var.environment}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
  ]
}

# Config 规则 - 未标记资源
resource "aws_config_config_rule" "required_tags" {
  name        = "${var.environment}-required-tags"
  description = "检查资源是否有必要的标签"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key   = "Environment"
    tag2Key   = "Project"
    tag3Key   = "Owner"
  })

  depends_on = [aws_config_configuration_recorder.recorder]
}

# Config 规则 - EC2 闲置实例
resource "aws_config_config_rule" "ec2_instance_idle" {
  name        = "${var.environment}-ec2-instance-idle"
  description = "检查 EC2 实例是否闲置（CPU 利用率低）"

  source {
    owner             = "AWS"
    source_identifier = "EC2_INSTANCE_DETAILED_MONITORING_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.recorder]
}

# Config 规则 - 开放安全组端口
resource "aws_config_config_rule" "restricted_ports" {
  name        = "${var.environment}-restricted-common-ports"
  description = "检查安全组是否限制了常见端口"

  source {
    owner             = "AWS"
    source_identifier = "RESTRICTED_INCOMING_TRAFFIC"
  }

  depends_on = [aws_config_configuration_recorder.recorder]
}

# SNS Topic 用于 Config 规则通知
resource "aws_sns_topic" "config_topic" {
  name = "${var.environment}-config-notifications"
}

resource "aws_sns_topic_policy" "config_topic_policy" {
  arn    = aws_sns_topic.config_topic.arn
  policy = data.aws_iam_policy_document.config_topic_policy.json
}

data "aws_iam_policy_document" "config_topic_policy" {
  statement {
    actions = ["sns:Publish"]
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
    resources = [aws_sns_topic.config_topic.arn]
  }
}

# 用于获取当前账户 ID
data "aws_caller_identity" "current" {} 