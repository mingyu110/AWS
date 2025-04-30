import json
import os
import boto3
import sys
import logging
from datetime import datetime

# 添加 Lambda 层路径
# /opt - AWS Lambda 层的标准路径，层中的库会被解压到此目录，便于共享依赖并减小部署包大小
sys.path.append('/opt')
# 添加项目根目录到路径，确保能够导入同级目录中的模块（如utils），支持本地开发和生产环境的代码结构兼容
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dingtalk import DingTalkClient

# 设置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 环境变量
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
DINGTALK_WEBHOOK = os.environ.get('DINGTALK_WEBHOOK')
DINGTALK_SECRET = os.environ.get('DINGTALK_SECRET')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

# AWS 客户端
config_client = boto3.client('config')
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')
sns_client = boto3.client('sns')

# 钉钉客户端
dingtalk = DingTalkClient(DINGTALK_WEBHOOK, DINGTALK_SECRET)

def get_resource_details(resource_type, resource_id):
    """获取资源详细信息"""
    if resource_type == 'AWS::EC2::Instance':
        response = ec2_client.describe_instances(InstanceIds=[resource_id])
        instance = response['Reservations'][0]['Instances'][0] if response['Reservations'] else None
        return instance
    elif resource_type == 'AWS::S3::Bucket':
        try:
            tags = s3_client.get_bucket_tagging(Bucket=resource_id)
            return {'BucketName': resource_id, 'Tags': tags.get('TagSet', [])}
        except s3_client.exceptions.NoSuchTagSet:
            return {'BucketName': resource_id, 'Tags': []}
        except Exception as e:
            logger.error(f"获取存储桶标签时出错: {str(e)}")
            return {'BucketName': resource_id, 'Tags': []}
    elif resource_type == 'AWS::RDS::DBInstance':
        response = rds_client.describe_db_instances(DBInstanceIdentifier=resource_id)
        return response['DBInstances'][0] if response['DBInstances'] else None
    return None

def tag_resource(resource_type, resource_id):
    """为资源添加标签"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if resource_type == 'AWS::EC2::Instance':
        try:
            ec2_client.create_tags(
                Resources=[resource_id],
                Tags=[
                    {'Key': 'AutoTagged', 'Value': 'True'},
                    {'Key': 'TaggedOn', 'Value': current_time},
                    {'Key': 'RequiresReview', 'Value': 'True'}
                ]
            )
            logger.info(f"已为 EC2 实例 {resource_id} 添加标签")
            return True
        except Exception as e:
            logger.error(f"为 EC2 实例添加标签时出错: {str(e)}")
            return False
    
    elif resource_type == 'AWS::S3::Bucket':
        try:
            # 获取现有标签
            try:
                existing_tags = s3_client.get_bucket_tagging(Bucket=resource_id).get('TagSet', [])
            except s3_client.exceptions.NoSuchTagSet:
                existing_tags = []
            
            # 添加新标签
            new_tags = existing_tags + [
                {'Key': 'AutoTagged', 'Value': 'True'},
                {'Key': 'TaggedOn', 'Value': current_time},
                {'Key': 'RequiresReview', 'Value': 'True'}
            ]
            
            # 删除重复标签
            unique_tags = []
            keys_seen = set()
            for tag in new_tags:
                if tag['Key'] not in keys_seen:
                    unique_tags.append(tag)
                    keys_seen.add(tag['Key'])
            
            s3_client.put_bucket_tagging(
                Bucket=resource_id,
                Tagging={'TagSet': unique_tags}
            )
            logger.info(f"已为 S3 存储桶 {resource_id} 添加标签")
            return True
        except Exception as e:
            logger.error(f"为 S3 存储桶添加标签时出错: {str(e)}")
            return False
    
    elif resource_type == 'AWS::RDS::DBInstance':
        try:
            rds_client.add_tags_to_resource(
                ResourceName=resource_id,
                Tags=[
                    {'Key': 'AutoTagged', 'Value': 'True'},
                    {'Key': 'TaggedOn', 'Value': current_time},
                    {'Key': 'RequiresReview', 'Value': 'True'}
                ]
            )
            logger.info(f"已为 RDS 实例 {resource_id} 添加标签")
            return True
        except Exception as e:
            logger.error(f"为 RDS 实例添加标签时出错: {str(e)}")
            return False
    
    return False

def stop_idle_instance(instance_id):
    """停止闲置的 EC2 实例"""
    try:
        ec2_client.stop_instances(InstanceIds=[instance_id])
        logger.info(f"已停止闲置的 EC2 实例 {instance_id}")
        return True
    except Exception as e:
        logger.error(f"停止 EC2 实例时出错: {str(e)}")
        return False

def handle_compliance_change(event):
    """处理合规性变更事件"""
    
    # 获取规则和资源信息
    rule_name = event['detail']['configRuleName']
    resource_id = event['detail']['resourceId']
    resource_type = event['detail']['resourceType']
    compliance_type = event['detail']['newEvaluationResult']['complianceType']
    
    logger.info(f"处理合规性变更: 规则={rule_name}, 资源={resource_id}, 类型={resource_type}, 状态={compliance_type}")
    
    # 如果资源不合规
    if compliance_type == 'NON_COMPLIANT':
        resource_details = get_resource_details(resource_type, resource_id)
        
        # 根据规则类型执行不同操作
        if 'required-tags' in rule_name.lower():
            # 为资源添加标签
            tagged = tag_resource(resource_type, resource_id)
            
            # 发送通知
            title = f"【{ENVIRONMENT}】资源缺少必要标签"
            markdown_content = f"""
## AWS 成本优化 - 资源缺少必要标签

- **环境**: {ENVIRONMENT}
- **资源 ID**: {resource_id}
- **资源类型**: {resource_type}
- **规则**: {rule_name}
- **状态**: 不合规 (缺少必要标签)
- **自动操作**: {'已自动添加标签' if tagged else '自动添加标签失败'}

请登录 AWS Console 查看并确认标签是否符合要求。
            """
            
            dingtalk.send_markdown(title, markdown_content)
            
        elif 'ec2-instance-idle' in rule_name.lower() and resource_type == 'AWS::EC2::Instance':
            # 自动停止闲置实例
            stopped = stop_idle_instance(resource_id)
            
            # 发送通知
            title = f"【{ENVIRONMENT}】检测到闲置 EC2 实例"
            markdown_content = f"""
## AWS 成本优化 - 检测到闲置 EC2 实例

- **环境**: {ENVIRONMENT}
- **实例 ID**: {resource_id}
- **规则**: {rule_name}
- **状态**: 不合规 (实例闲置)
- **自动操作**: {'已自动停止实例' if stopped else '自动停止实例失败'}

实例已被自动停止以节约成本。如需恢复使用，请登录 AWS Console 启动该实例。
            """
            
            dingtalk.send_markdown(title, markdown_content)
            
        elif 'restricted-common-ports' in rule_name.lower():
            # 安全组开放端口问题
            title = f"【{ENVIRONMENT}】检测到安全组不合规"
            markdown_content = f"""
## AWS 成本优化 - 安全组配置不合规

- **环境**: {ENVIRONMENT}
- **资源 ID**: {resource_id}
- **资源类型**: {resource_type}
- **规则**: {rule_name}
- **状态**: 不合规 (安全组开放敏感端口)

请登录 AWS Console 检查并修复安全组配置，限制不必要的端口访问。
            """
            
            dingtalk.send_markdown(title, markdown_content)
    
    return {
        'statusCode': 200,
        'body': json.dumps('已成功处理合规性变更事件')
    }

def handle_ec2_state_change(event):
    """处理 EC2 状态变更事件"""
    instance_id = event['detail']['instance-id']
    state = event['detail']['state']
    
    logger.info(f"处理 EC2 状态变更: 实例={instance_id}, 状态={state}")
    
    # 只处理启动的实例
    if state == 'running':
        # 检查实例是否有必要的标签
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0] if response['Reservations'] else None
        
        if instance:
            tags = instance.get('Tags', [])
            tag_keys = [tag['Key'] for tag in tags]
            
            # 检查是否缺少必要的标签
            required_tags = ['Environment', 'Project', 'Owner']
            missing_tags = [tag for tag in required_tags if tag not in tag_keys]
            
            if missing_tags:
                # 为实例添加标签
                tagged = tag_resource('AWS::EC2::Instance', instance_id)
                
                # 发送通知
                title = f"【{ENVIRONMENT}】新启动的 EC2 实例缺少标签"
                markdown_content = f"""
## AWS 成本优化 - 新启动的 EC2 实例缺少标签

- **环境**: {ENVIRONMENT}
- **实例 ID**: {instance_id}
- **缺少的标签**: {', '.join(missing_tags)}
- **自动操作**: {'已自动添加标签' if tagged else '自动添加标签失败'}

请登录 AWS Console 检查并完善实例标签。
                """
                
                dingtalk.send_markdown(title, markdown_content)
    
    return {
        'statusCode': 200,
        'body': json.dumps('已成功处理 EC2 状态变更事件')
    }

def handler(event, context):
    """Lambda 处理函数"""
    logger.info(f"收到事件: {json.dumps(event)}")
    
    try:
        # 根据事件类型处理
        if 'detail-type' in event:
            if event['detail-type'] == 'Config Rules Compliance Change':
                return handle_compliance_change(event)
            elif event['detail-type'] == 'EC2 Instance State-change Notification':
                return handle_ec2_state_change(event)
        
        return {
            'statusCode': 200,
            'body': json.dumps('事件处理完成')
        }
        
    except Exception as e:
        logger.error(f"处理事件时出错: {str(e)}")
        # 发送错误通知
        error_message = f"AWS 成本优化 Lambda 函数出错: {str(e)}"
        dingtalk.send_text(error_message)
        
        return {
            'statusCode': 500,
            'body': json.dumps(f'处理事件时出错: {str(e)}')
        } 