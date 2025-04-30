output "config_topic_arn" {
  description = "AWS Config 通知 SNS Topic ARN"
  value       = aws_sns_topic.config_topic.arn
}

output "config_rules" {
  description = "创建的 AWS Config 规则列表"
  value = [
    aws_config_config_rule.required_tags.name,
    aws_config_config_rule.ec2_instance_idle.name,
    aws_config_config_rule.restricted_ports.name
  ]
}

output "config_role_arn" {
  description = "AWS Config IAM 角色 ARN"
  value       = aws_iam_role.config_role.arn
} 