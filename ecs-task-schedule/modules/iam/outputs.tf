output "ecs_task_scheduler_policy_arn" {
  description = "The ARN of the IAM policy for the ECS task scheduler"
  value       = aws_iam_policy.ecs_task_scheduler_policy.arn
}