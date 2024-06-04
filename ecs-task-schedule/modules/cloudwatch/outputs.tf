#outputs.tf
output "ecs_weekday_start_tasks_schedule_arn" {
  value = aws_cloudwatch_event_rule.ecs_weekday_start_tasks_schedule.arn
}

output "ecs_weekday_stop_tasks_schedule_arn" {
  value = aws_cloudwatch_event_rule.ecs_weekday_stop_tasks_schedule.arn
}