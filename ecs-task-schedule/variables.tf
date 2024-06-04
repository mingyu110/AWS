# variables.tf
variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-west-2" # Replace with your desired region
}

variable "function_name" {
  description = "The name of the AWS Lambda function"
  type        = string
}

variable "s3_bucket_lambda_functions_storage_bucket" {
  description = "The name of the S3 bucket where the Lambda function code is stored"
  type        = string
}

variable "iam_role_ecs_task_scheduler_lambda_exec_role_arn" {
  description = "The ARN of the IAM role that Lambda will assume to execute the function"
  type        = string
}

variable "ecs_weekday_start_tasks_schedule_arn" {
  description = "The ARN of the CloudWatch Event Rule for starting ECS tasks"
  type        = string
}

variable "ecs_weekday_stop_tasks_schedule_arn" {
  description = "The ARN of the CloudWatch Event Rule for stopping ECS tasks"
  type        = string
}

variable "iam_role_name" {
  description = "The name of the IAM role to attach the policy to"
  type        = string
}

variable "policy_name" {
  description = "The name of the IAM policy"
  type        = string
  default     = "ecs-task-scheduler-policy"
}

variable "policy_description" {
  description = "The description of the IAM policy"
  type        = string
  default     = "Policy for ECS task scheduler Lambda function"
}



