# outputs.tf
output "ecs_weekday_stop_tasks_schedule_arn" {
  description = "The ARN of the CloudWatch event rule for stopping ECS tasks on weekdays"
  value       = module.cloudwatch.ecs_weekday_stop_tasks_schedule_arn
}

output "ecs_weekday_start_tasks_schedule_arn" {
  description = "The ARN of the CloudWatch event rule for starting ECS tasks on weekdays"
  value       = module.cloudwatch.ecs_weekday_start_tasks_schedule_arn
}

output "ecs_task_scheduler_policy_arn" {
  description = "The ARN of the IAM policy for the ECS task scheduler"
  value       = module.iam.ecs_task_scheduler_policy_arn
}

output "iam_role_name" {
  description = "The name of the IAM role"
  value       = var.iam_role_name
}