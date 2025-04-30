variable "aws_region" {
  description = "AWS 区域"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "环境名称（如 dev, test, prod）"
  type        = string
  default     = "dev"
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

variable "resources_to_monitor" {
  description = "需要监控的资源类型列表"
  type        = list(string)
  default     = ["AWS::EC2::Instance", "AWS::S3::Bucket", "AWS::RDS::DBInstance"]
} 