#cloudwatch.tf
resource "aws_cloudwatch_event_target" "ecs_weekday_stop_tasks_target" {
  rule      = aws_cloudwatch_event_rule.ecs_weekday_stop_tasks_schedule.name
  target_id = "ecsTaskSchedulerWeekdayStop"
  arn       = var.lambda_function_arn

  input = jsonencode({
    action      = "stop"
    environment = "scheduled"
  })
}

resource "aws_cloudwatch_event_rule" "ecs_weekday_start_tasks_schedule" {
  name                = "ECSWeekdayStartTasksSchedule"
  description         = "Schedule to start ECS tasks on weekdays at 5:00 BST"
  schedule_expression = var.schedule_expression_start  # Weekdays at 5:00 BST
  is_enabled          = true
}

resource "aws_cloudwatch_event_rule" "ecs_weekday_stop_tasks_schedule" {
  name                = "ECSWeekdayStopTasksSchedule"
  description         = "Schedule to stop ECS tasks on weekdays at 22:00 BST"
  schedule_expression = var.schedule_expression_stop # Weekdays at 22:00 BST
  is_enabled          = true
}
resource "aws_cloudwatch_event_target" "ecs_weekday_start_tasks_target" {
  rule      = aws_cloudwatch_event_rule.ecs_weekday_start_tasks_schedule.name
  target_id = "ecsTaskSchedulerWeekdayStart"
  arn       = var.lambda_function_arn

  input = jsonencode({
    action      = "start"
    environment = "scheduled"
  })
}