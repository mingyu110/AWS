# 创建 Lambda 函数执行角色
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.environment}-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

# 附加自定义策略允许 Lambda 访问所需资源
resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.environment}-lambda-policy"
  description = "允许 Lambda 函数访问 AWS 资源以进行成本优化"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "config:GetComplianceDetailsByConfigRule",
          "config:GetComplianceDetailsByResource",
          "ec2:DescribeInstances",
          "ec2:CreateTags",
          "ec2:StopInstances",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "rds:DescribeDBInstances",
          "rds:AddTagsToResource"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.lambda_topic.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# SNS 主题用于 Lambda 通知
resource "aws_sns_topic" "lambda_topic" {
  name = "${var.environment}-lambda-notifications"
}

# 资源合规 Lambda 函数
data "archive_file" "resource_compliance_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/resource_compliance"
  output_path = "${path.module}/../../lambda/dist/resource_compliance.zip"
}

resource "aws_lambda_function" "resource_compliance" {
  function_name    = "${var.environment}-resource-compliance"
  filename         = data.archive_file.resource_compliance_zip.output_path
  source_code_hash = data.archive_file.resource_compliance_zip.output_base64sha256
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "index.handler"
  runtime          = "python3.9"
  timeout          = 60
  memory_size      = 128

  environment {
    variables = {
      SNS_TOPIC_ARN     = aws_sns_topic.lambda_topic.arn
      ENVIRONMENT       = var.environment
      DINGTALK_WEBHOOK  = var.dingtalk_webhook
      DINGTALK_SECRET   = var.dingtalk_secret
    }
  }
}

# 成本异常检测 Lambda 函数
data "archive_file" "cost_anomaly_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/cost_anomaly"
  output_path = "${path.module}/../../lambda/dist/cost_anomaly.zip"
}

resource "aws_lambda_function" "cost_anomaly" {
  function_name    = "${var.environment}-cost-anomaly"
  filename         = data.archive_file.cost_anomaly_zip.output_path
  source_code_hash = data.archive_file.cost_anomaly_zip.output_base64sha256
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "index.handler"
  runtime          = "python3.9"
  timeout          = 120
  memory_size      = 256

  environment {
    variables = {
      SNS_TOPIC_ARN       = aws_sns_topic.lambda_topic.arn
      ENVIRONMENT         = var.environment
      DINGTALK_WEBHOOK    = var.dingtalk_webhook
      DINGTALK_SECRET     = var.dingtalk_secret
      THRESHOLD_PERCENTAGE = tostring(var.threshold_percentage)
    }
  }
}

# EventBridge 规则 - 每日成本分析
resource "aws_cloudwatch_event_rule" "daily_cost_check" {
  name                = "${var.environment}-daily-cost-check"
  description         = "每晚运行成本异常检测"
  schedule_expression = "cron(0 1 * * ? *)"  # 每天 UTC 1:00 AM (根据需要调整)
}

resource "aws_cloudwatch_event_target" "cost_anomaly_target" {
  rule      = aws_cloudwatch_event_rule.daily_cost_check.name
  target_id = "cost_anomaly_lambda"
  arn       = aws_lambda_function.cost_anomaly.arn
}

resource "aws_lambda_permission" "allow_eventbridge_cost_anomaly" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_anomaly.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_cost_check.arn
}

# 创建 Lambda 函数目录 (不会在远程状态中创建)
resource "null_resource" "create_lambda_dist_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/../../lambda/dist"
  }
} 