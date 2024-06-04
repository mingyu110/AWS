resource "aws_iam_policy" "ecs_task_scheduler_policy" {
  name        = var.policy_name
  description = var.policy_description

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
    for statement in var.policy_statements : {
      Effect   = statement.effect
      Action   = statement.actions
      Resource = statement.resource
    }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_scheduler_policy_attach" {
  role       = var.iam_role_name
  policy_arn = aws_iam_policy.ecs_task_scheduler_policy.arn
}

