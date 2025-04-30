# Config 规则状态变更事件规则
resource "aws_cloudwatch_event_rule" "config_rule_compliance" {
  name        = "${var.environment}-config-rule-compliance"
  description = "捕获 AWS Config 规则合规性状态变更"

  event_pattern = jsonencode({
    source      = ["aws.config"]
    detail-type = ["Config Rules Compliance Change"]
  })
}

resource "aws_cloudwatch_event_target" "config_compliance_target" {
  rule      = aws_cloudwatch_event_rule.config_rule_compliance.name
  target_id = "lambda"
  arn       = var.lambda_compliance_arn
}

resource "aws_lambda_permission" "allow_eventbridge_compliance" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = element(split(":", var.lambda_compliance_arn), 6)
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.config_rule_compliance.arn
}

# EC2 状态变更事件规则
resource "aws_cloudwatch_event_rule" "ec2_state_change" {
  name        = "${var.environment}-ec2-state-change"
  description = "捕获 EC2 实例状态变更"

  event_pattern = jsonencode({
    source      = ["aws.ec2"]
    detail-type = ["EC2 Instance State-change Notification"]
    detail = {
      state = ["running", "stopped", "terminated"]
    }
  })
}

resource "aws_cloudwatch_event_target" "ec2_state_change_target" {
  rule      = aws_cloudwatch_event_rule.ec2_state_change.name
  target_id = "lambda"
  arn       = var.lambda_compliance_arn
}

resource "aws_lambda_permission" "allow_eventbridge_ec2" {
  statement_id  = "AllowExecutionFromEventBridgeEC2"
  action        = "lambda:InvokeFunction"
  function_name = element(split(":", var.lambda_compliance_arn), 6)
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_state_change.arn
}

# 创建 EventBridge 和 SNS 之间的连接
resource "aws_cloudwatch_event_target" "sns_target" {
  rule      = aws_cloudwatch_event_rule.config_rule_compliance.name
  target_id = "SendToSNS"
  arn       = var.config_topic_arn
} 