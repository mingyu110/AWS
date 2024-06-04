resource "aws_lambda_function" "ecs_task_scheduler" {
  function_name    = var.function_name
  s3_bucket        = var.s3_bucket_lambda_functions_storage_bucket
  s3_key           = "ecs-task-scheduler.zip"
  handler          = "app.lambda_handler"
  runtime          = "python3.12"
  role             = var.iam_role_ecs_task_scheduler_lambda_exec_role_arn
  timeout          = 300 # 5 minutes
}

resource "aws_lambda_permission" "ecs_weekday_start_tasks_allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvokeLambdaWeekdayStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ecs_task_scheduler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = var.ecs_weekday_start_tasks_schedule_arn
}

resource "aws_lambda_permission" "ecs_weekday_stop_tasks_allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvokeLambdaWeekdayStop"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ecs_task_scheduler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = var.ecs_weekday_stop_tasks_schedule_arn
}