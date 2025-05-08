/*
 * Author: 刘晋勋
 * Description: Karpenter 控制器和相关资源配置
 */

resource "aws_iam_instance_profile" "karpenter" {
  count = var.enable_karpenter ? 1 : 0
  name  = "KarpenterNodeInstanceProfile-${var.cluster_name}"
  role  = module.eks.eks_managed_node_groups["default"].iam_role_name
}

# Karpenter 控制器 IAM 角色
resource "aws_iam_role" "karpenter_controller" {
  count = var.enable_karpenter ? 1 : 0
  name  = "karpenter-controller-${var.cluster_name}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = module.eks.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${module.eks.oidc_provider}:sub": "system:serviceaccount:karpenter:karpenter"
          }
        }
      }
    ]
  })
}

# Karpenter 控制器策略
resource "aws_iam_policy" "karpenter_controller" {
  count = var.enable_karpenter ? 1 : 0
  name  = "KarpenterController-${var.cluster_name}"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateLaunchTemplate",
          "ec2:DeleteLaunchTemplate",
          "ec2:CreateFleet",
          "ec2:RunInstances",
          "ec2:TerminateInstances",
          "ec2:DescribeLaunchTemplates",
          "ec2:DescribeInstances",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:DescribeInstanceTypes",
          "ec2:DescribeInstanceTypeOfferings",
          "ec2:DescribeAvailabilityZones",
          "ec2:DescribeSpotPriceHistory",
          "pricing:GetProducts",
          "ssm:GetParameter"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = module.eks.eks_managed_node_groups["default"].iam_role_arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "karpenter_controller" {
  count      = var.enable_karpenter ? 1 : 0
  role       = aws_iam_role.karpenter_controller[0].name
  policy_arn = aws_iam_policy.karpenter_controller[0].arn
}

# Karpenter Provisioner 资源
resource "kubernetes_manifest" "karpenter_provisioner" {
  count = var.enable_karpenter ? 1 : 0
  manifest = {
    apiVersion = "karpenter.sh/v1alpha5"
    kind       = "Provisioner"
    metadata = {
      name = "default"
    }
    spec = {
      requirements = [
        {
          key      = "karpenter.sh/capacity-type"
          operator = "In"
          values   = ["spot", "on-demand"]
        },
        {
          key      = "kubernetes.io/arch"
          operator = "In"
          values   = ["amd64"]
        },
        {
          key      = "node.kubernetes.io/instance-type"
          operator = "In"
          values   = ["t3.medium", "t3.large", "m5.large", "m5.xlarge"]
        }
      ]
      limits = {
        resources = {
          cpu    = "100"
          memory = "100Gi"
        }
      }
      provider = {
        instanceProfile = aws_iam_instance_profile.karpenter[0].name
        subnetSelector = {
          "karpenter.sh/discovery" = var.cluster_name
        }
        securityGroupSelector = {
          "kubernetes.io/cluster/${var.cluster_name}" = "owned"
        }
      }
      ttlSecondsAfterEmpty = 30
    }
  }

  depends_on = [
    module.eks
  ]
}

# Karpenter Spot Provisioner 资源
resource "kubernetes_manifest" "karpenter_spot_provisioner" {
  count = var.enable_karpenter ? 1 : 0
  manifest = {
    apiVersion = "karpenter.sh/v1alpha5"
    kind       = "Provisioner"
    metadata = {
      name = "spot"
    }
    spec = {
      requirements = [
        {
          key      = "karpenter.sh/capacity-type"
          operator = "In"
          values   = ["spot"]
        },
        {
          key      = "kubernetes.io/arch"
          operator = "In"
          values   = ["amd64"]
        }
      ]
      provider = {
        instanceProfile = aws_iam_instance_profile.karpenter[0].name
        subnetSelector = {
          "karpenter.sh/discovery" = var.cluster_name
        }
        securityGroupSelector = {
          "kubernetes.io/cluster/${var.cluster_name}" = "owned"
        }
      }
      ttlSecondsAfterEmpty = 30
    }
  }

  depends_on = [
    module.eks
  ]
}
