# -*- coding: utf-8 -*-
"""
Author: 刘晋勋
Description: 监控 Spot 实例中断通知的 Lambda 函数
"""

import boto3
import json
import logging
import os

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 环境变量
EKS_CLUSTER_NAME = os.environ.get("EKS_CLUSTER_NAME")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

def lambda_handler(event, context):
    """
    处理 EC2 Spot 实例中断通知
    
    Args:
        event: EventBridge 事件数据
        context: Lambda 上下文
        
    Returns:
        dict: 操作结果
    """
    logger.info(f"收到事件: {json.dumps(event)}")
    
    # 检查是否为 Spot 中断通知
    if event.get("source") == "aws.ec2" and event.get("detail-type") == "EC2 Spot Instance Interruption Warning":
        instance_id = event["detail"]["instance-id"]
        logger.info(f"Spot 实例 {instance_id} 将在 2 分钟内被中断")
        
        try:
            ec2 = boto3.client('ec2')
            
            # 获取实例详情
            instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
            
            # 获取实例标签
            tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
            
            # 检查是否为 EKS 节点
            if tags.get("kubernetes.io/cluster/" + EKS_CLUSTER_NAME) == "owned":
                logger.info(f"实例 {instance_id} 是 EKS 集群 {EKS_CLUSTER_NAME} 的节点")
                
                # 发送通知
                if SNS_TOPIC_ARN:
                    sns = boto3.client('sns')
                    sns.publish(
                        TopicArn=SNS_TOPIC_ARN,
                        Subject=f"Spot 实例中断警告: {instance_id}",
                        Message=f"EKS 集群 {EKS_CLUSTER_NAME} 的 Spot 实例 {instance_id} 将在 2 分钟内被中断。\n\n"
                                f"实例详情: {json.dumps(instance, default=str)}"
                    )
                    logger.info(f"已发送中断通知到 SNS 主题 {SNS_TOPIC_ARN}")
                
                return {
                    "statusCode": 200,
                    "body": f"已处理 Spot 实例 {instance_id} 的中断通知"
                }
            else:
                logger.info(f"实例 {instance_id} 不是 EKS 集群 {EKS_CLUSTER_NAME} 的节点")
                
        except Exception as e:
            logger.error(f"处理 Spot 中断通知失败: {str(e)}")
            return {
                "statusCode": 500,
                "body": f"处理失败: {str(e)}"
            }
    
    return {
        "statusCode": 200,
        "body": "事件不是 Spot 中断通知或不需要处理"
    }
