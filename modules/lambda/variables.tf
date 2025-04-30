variable "aws_region" {
  description = "AWS 区域"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}

variable "dingtalk_webhook" {
  description = "钉钉机器人 Webhook URL"
  type        = string
}

variable "dingtalk_secret" {
  description = "钉钉机器人安全设置的密钥"
  type        = string
  sensitive   = true
}

variable "threshold_percentage" {
  description = "成本异常阈值百分比"
  type        = number
  default     = 10
} 