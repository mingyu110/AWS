variable "aws_region" {
  description = "AWS 区域"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}

variable "lambda_compliance_arn" {
  description = "资源合规 Lambda 函数 ARN"
  type        = string
}

variable "lambda_cost_anomaly_arn" {
  description = "成本异常检测 Lambda 函数 ARN"
  type        = string
}

variable "config_topic_arn" {
  description = "AWS Config 通知 SNS Topic ARN"
  type        = string
} 