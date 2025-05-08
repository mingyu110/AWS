# -*- coding: utf-8 -*-
"""
Author: 刘晋勋
Description: 自动缩容 EKS 集群的 Lambda 函数
"""

import boto3
import os
import logging

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 环境变量
EKS_CLUSTER_NAME = os.environ.get("EKS_CLUSTER_NAME")
NODEGROUP_NAME = os.environ.get("NODEGROUP_NAME")
MIN_SIZE = int(os.environ.get("MIN_SIZE", 1))

def lambda_handler(event, context):
    """
    定时触发，自动将指定 EKS 节点组缩容到最小值
    
    Args:
        event: EventBridge 事件数据
        context: Lambda 上下文
        
    Returns:
        dict: 操作结果
    """
    logger.info(f"开始缩容 EKS 集群 {EKS_CLUSTER_NAME} 的节点组 {NODEGROUP_NAME}")
    
    try:
        eks = boto3.client('eks')
        asg = boto3.client('autoscaling')
        
        # 获取节点组信息
        nodegroup = eks.describe_nodegroup(
            clusterName=EKS_CLUSTER_NAME,
            nodegroupName=NODEGROUP_NAME
        )['nodegroup']
        
        # 获取 ASG 名称
        asg_name = nodegroup['resources']['autoScalingGroups'][0]['name']
        
        # 缩容 ASG
        asg.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MinSize=MIN_SIZE,
            DesiredCapacity=MIN_SIZE
        )
        
        logger.info(f"成功将 {asg_name} 缩容到 {MIN_SIZE} 台节点")
        return {
            "statusCode": 200,
            "body": f"成功将 {asg_name} 缩容到 {MIN_SIZE} 台节点"
        }
    except Exception as e:
        logger.error(f"缩容失败: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"缩容失败: {str(e)}"
        }
