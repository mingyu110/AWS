output "compliance_lambda_arn" {
  description = "资源合规 Lambda 函数 ARN"
  value       = module.lambda.compliance_function_arn
}

output "cost_anomaly_lambda_arn" {
  description = "成本异常检测 Lambda 函数 ARN"
  value       = module.lambda.cost_anomaly_function_arn
}

output "config_rules" {
  description = "已创建的 AWS Config 规则"
  value       = module.config.config_rules
}

output "eventbridge_rules" {
  description = "已创建的 EventBridge 规则"
  value       = module.eventbridge.event_rules
} 