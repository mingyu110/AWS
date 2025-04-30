output "compliance_function_arn" {
  description = "资源合规 Lambda 函数 ARN"
  value       = aws_lambda_function.resource_compliance.arn
}

output "cost_anomaly_function_arn" {
  description = "成本异常检测 Lambda 函数 ARN"
  value       = aws_lambda_function.cost_anomaly.arn
}

output "lambda_execution_role_arn" {
  description = "Lambda 执行角色 ARN"
  value       = aws_iam_role.lambda_execution_role.arn
}

output "sns_topic_arn" {
  description = "Lambda 通知 SNS Topic ARN"
  value       = aws_sns_topic.lambda_topic.arn
} 