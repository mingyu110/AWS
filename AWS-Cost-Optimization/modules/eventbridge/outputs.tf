output "event_rules" {
  description = "创建的 EventBridge 规则列表"
  value = [
    aws_cloudwatch_event_rule.config_rule_compliance.name,
    aws_cloudwatch_event_rule.ec2_state_change.name
  ]
} 