variable "aws_region" {
  description = "AWS 区域"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}

variable "sns_topic_arn" {
  description = "通知使用的 SNS Topic ARN"
  type        = string
} 