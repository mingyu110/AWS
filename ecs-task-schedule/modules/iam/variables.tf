variable "iam_role_name" {
  description = "The name of the IAM role to attach the policy to"
  type        = string
}

variable "policy_name" {
  description = "The name of the IAM policy"
  type        = string
}

variable "policy_description" {
  description = "The description of the IAM policy"
  type        = string
}

variable "policy_statements" {
  description = "The policy statements for the IAM policy"
  type = list(object({
    effect   = string
    actions  = list(string)
    resource = string
  }))
  default = [
    {
      effect   = "Allow"
      actions  = ["ecs:UpdateService", "ecs:ListTasks", "ecs:DescribeTasks", "ecs:DescribeServices"]
      resource = "*"
    },
    {
      effect   = "Allow"
      actions  = ["application-autoscaling:RegisterScalableTarget", "application-autoscaling:DeregisterScalableTarget", "application-autoscaling:DescribeScalableTargets"]
      resource = "*"
    },
    {
      effect   = "Allow",
      actions  = ["elasticloadbalancing:RegisterTargets", "elasticloadbalancing:DeregisterTargets", "elasticloadbalancing:DescribeTargetGroups", "elasticloadbalancing:DescribeListeners", "elasticloadbalancing:DescribeRules"],
      resource = "*"
    },
    {
      effect   = "Allow",
      actions  = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      resource = "arn:aws:logs:*:*:*"
    }
  ]
}