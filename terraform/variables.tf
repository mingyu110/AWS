/*
 * Author: 刘晋勋
 * Description: Terraform 变量定义
 */

variable "aws_region" {
  description = "AWS 区域"
  type        = string
  default     = "ap-northeast-1"
}

variable "cluster_name" {
  description = "EKS 集群名称"
  type        = string
  default     = "eks-cost-optimization"
}

variable "vpc_cidr" {
  description = "VPC CIDR 块"
  type        = string
  default     = "10.0.0.0/16"
}

variable "node_groups" {
  description = "EKS 节点组配置"
  type        = map(any)
  default     = {
    default = {
      desired_capacity = 2
      max_capacity     = 5
      min_capacity     = 1
      instance_types   = ["t3.medium"]
    }
  }
}

variable "enable_karpenter" {
  description = "是否启用 Karpenter"
  type        = bool
  default     = true
}

variable "scale_down_time" {
  description = "定时缩容时间 (cron 表达式)"
  type        = string
  default     = "cron(0 20 ? * MON-FRI *)"  # 工作日晚上 8 点
}

variable "scale_up_time" {
  description = "定时扩容时间 (cron 表达式)"
  type        = string
  default     = "cron(30 7 ? * MON-FRI *)"  # 工作日早上 7:30
}
