/*
 * Author: 刘晋勋
 * Description: Terraform 输出值
 */

output "cluster_name" {
  description = "EKS 集群名称"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS 集群 API 服务器端点"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "EKS 集群安全组 ID"
  value       = module.eks.cluster_security_group_id
}

output "lambda_role_arn" {
  description = "Lambda 执行角色 ARN"
  value       = aws_iam_role.lambda_exec.arn
}

output "karpenter_instance_profile_name" {
  description = "Karpenter 节点实例配置文件名称"
  value       = var.enable_karpenter ? aws_iam_instance_profile.karpenter[0].name : null
}

output "karpenter_controller_role_arn" {
  description = "Karpenter 控制器角色 ARN"
  value       = var.enable_karpenter ? aws_iam_role.karpenter_controller[0].arn : null
}
