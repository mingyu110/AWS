/*
 * Author: 刘晋勋
 * Description: EKS 集群配置
 */

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 18.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.24"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # 集群访问配置
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = true

  # 节点组配置
  eks_managed_node_groups = var.node_groups

  # 集群附加组件
  cluster_addons = {
    coredns = {
      resolve_conflicts = "OVERWRITE"
    }
    kube-proxy = {
      resolve_conflicts = "OVERWRITE"
    }
    vpc-cni = {
      resolve_conflicts = "OVERWRITE"
    }
  }

  # 集群安全组配置
  cluster_security_group_additional_rules = {
    egress_all = {
      description      = "允许所有出站流量"
      protocol         = "-1"
      from_port        = 0
      to_port          = 0
      type             = "egress"
      cidr_blocks      = ["0.0.0.0/0"]
    }
  }

  tags = local.tags
}
