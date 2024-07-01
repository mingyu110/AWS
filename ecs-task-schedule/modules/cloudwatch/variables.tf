variable "lambda_function_arn" {
  description = "The ARN of the Lambda function to trigger"
  type        = string
}

variable "schedule_expression_start" {
  description = "The schedule expression for the CloudWatch Event Rule"
  type        = string
}

variable "schedule_expression_stop" {
  description = "The schedule expression for the CloudWatch Event Rule"
  type        = string
}