# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "cloudwatch" {
  source = "./modules/cloudwatch"
  lambda_function_arn = module.lambda.lambda_function_arn
  schedule_expression_start = "cron(0 5 ? * MON-FRI *)"
  schedule_expression_stop = "cron(0 22 ? * MON-FRI *)"
}

module "lambda" {
  source = "./modules/lambda"
  function_name                            = var.function_name
  s3_bucket_lambda_functions_storage_bucket = var.s3_bucket_lambda_functions_storage_bucket
  iam_role_ecs_task_scheduler_lambda_exec_role_arn = var.iam_role_ecs_task_scheduler_lambda_exec_role_arn
  ecs_weekday_start_tasks_schedule_arn      = var.ecs_weekday_start_tasks_schedule_arn
  ecs_weekday_stop_tasks_schedule_arn       = var.ecs_weekday_stop_tasks_schedule_arn
}

module "iam" {
  source             = "./modules/iam"
  iam_role_name      = var.iam_role_name
  policy_name        = var.policy_name
  policy_description = var.policy_description
}

resource "aws_iam_role_policy_attachment" "ecs_task_scheduler_policy_attach" {
  role       = var.iam_role_name
  policy_arn = module.iam.ecs_task_scheduler_policy_arn
}