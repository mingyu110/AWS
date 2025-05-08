/*
 * Author: 刘晋勋
 * Description: EventBridge 规则配置，用于定时触发 Lambda 函数
 */

# 定时缩容规则
resource "aws_cloudwatch_event_rule" "scale_down" {
  name                = "eks-scale-down-${var.cluster_name}"
  description         = "定时触发 EKS 集群缩容"
  schedule_expression = var.scale_down_time
}

# 定时扩容规则
resource "aws_cloudwatch_event_rule" "scale_up" {
  name                = "eks-scale-up-${var.cluster_name}"
  description         = "定时触发 EKS 集群扩容"
  schedule_expression = var.scale_up_time
}

# EventBridge 目标配置（Lambda ARN 需在 Lambda 部署后补充）
resource "aws_cloudwatch_event_target" "scale_down_target" {
  rule      = aws_cloudwatch_event_rule.scale_down.name
  target_id = "ScaleDownLambda"
  arn       = "LAMBDA_ARN_PLACEHOLDER" # 部署 Lambda 后补充
}

resource "aws_cloudwatch_event_target" "scale_up_target" {
  rule      = aws_cloudwatch_event_rule.scale_up.name
  target_id = "ScaleUpLambda"
  arn       = "LAMBDA_ARN_PLACEHOLDER" # 部署 Lambda 后补充
}
