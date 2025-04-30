import json
import os
import boto3
import sys
import logging
from datetime import datetime, timedelta

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
THRESHOLD_PERCENTAGE = float(os.environ.get('THRESHOLD_PERCENTAGE', 10))

# AWS 客户端
ce_client = boto3.client('ce')  # Cost Explorer
sns_client = boto3.client('sns')

# 钉钉客户端
dingtalk = DingTalkClient(DINGTALK_WEBHOOK, DINGTALK_SECRET)

def get_date_range():
    """获取日期范围：今天、昨天和过去 7 天"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # 格式化日期为 AWS Cost Explorer 需要的格式
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    week_ago_str = week_ago.strftime('%Y-%m-%d')
    
    return yesterday_str, today_str, week_ago_str

def get_daily_costs(start_date, end_date):
    """获取每日成本数据"""
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        return response
    except Exception as e:
        logger.error(f"获取成本数据时出错: {str(e)}")
        return None

def get_weekly_average_by_service():
    """计算每个服务过去 7 天的平均每日成本"""
    yesterday, today, week_ago = get_date_range()
    
    # 获取过去 7 天的成本数据
    cost_data = get_daily_costs(week_ago, today)
    if not cost_data:
        return {}
    
    # 计算每个服务的总成本
    service_total_costs = {}
    service_days = {}
    
    for result_by_time in cost_data['ResultsByTime']:
        for group in result_by_time['Groups']:
            service = group['Keys'][0]
            cost_str = group['Metrics']['UnblendedCost']['Amount']
            cost = float(cost_str)
            
            if service not in service_total_costs:
                service_total_costs[service] = 0
                service_days[service] = 0
            
            service_total_costs[service] += cost
            service_days[service] += 1
    
    # 计算每个服务的平均每日成本
    service_averages = {}
    for service, total in service_total_costs.items():
        days = service_days[service]
        if days > 0:
            service_averages[service] = total / days
        else:
            service_averages[service] = 0
    
    return service_averages

def get_yesterday_costs():
    """获取昨天的成本数据按服务划分"""
    yesterday, today, _ = get_date_range()
    
    # 获取昨天的成本数据
    cost_data = get_daily_costs(yesterday, today)
    if not cost_data:
        return {}
    
    # 提取每个服务的成本
    service_costs = {}
    
    for result_by_time in cost_data['ResultsByTime']:
        for group in result_by_time['Groups']:
            service = group['Keys'][0]
            cost_str = group['Metrics']['UnblendedCost']['Amount']
            cost = float(cost_str)
            service_costs[service] = cost
    
    return service_costs

def detect_cost_anomalies():
    """检测成本异常"""
    # 获取过去 7 天各服务的平均成本
    weekly_averages = get_weekly_average_by_service()
    
    # 获取昨天各服务的成本
    yesterday_costs = get_yesterday_costs()
    
    # 检测异常
    anomalies = []
    
    for service, yesterday_cost in yesterday_costs.items():
        # 如果服务在过去 7 天内有数据
        if service in weekly_averages:
            weekly_avg = weekly_averages[service]
            
            # 如果成本为 0，跳过
            if weekly_avg == 0:
                continue
            
            # 计算增长百分比
            percentage_increase = ((yesterday_cost - weekly_avg) / weekly_avg) * 100
            
            # 如果增长超过阈值，记录异常
            if percentage_increase > THRESHOLD_PERCENTAGE:
                anomalies.append({
                    'service': service,
                    'yesterday_cost': yesterday_cost,
                    'weekly_average': weekly_avg,
                    'percentage_increase': percentage_increase
                })
    
    return anomalies

def format_cost(cost):
    """格式化成本为美元显示"""
    return f"${cost:.2f}"

def handler(event, context):
    """Lambda 处理函数"""
    logger.info(f"开始运行成本异常检测")
    
    try:
        # 检测成本异常
        anomalies = detect_cost_anomalies()
        
        if anomalies:
            # 构建通知内容
            yesterday, _, _ = get_date_range()
            
            title = f"【{ENVIRONMENT}】检测到 AWS 成本异常"
            markdown_content = f"""
## AWS 成本优化 - 检测到成本异常

检测到以下服务的成本异常（超过过去 7 天平均值 {THRESHOLD_PERCENTAGE}%）：

| 服务 | 昨日成本 | 周平均成本 | 增长率 |
| ---- | ------- | --------- | ----- |
"""
            
            # 添加异常详情
            for anomaly in anomalies:
                service = anomaly['service']
                yesterday_cost = format_cost(anomaly['yesterday_cost'])
                weekly_average = format_cost(anomaly['weekly_average'])
                percentage = f"{anomaly['percentage_increase']:.2f}%"
                
                markdown_content += f"| {service} | {yesterday_cost} | {weekly_average} | {percentage} |\n"
            
            markdown_content += f"""
### 建议操作

1. 检查是否有未终止的资源或新创建的资源
2. 查看成本探索器了解详细消费情况
3. 评估资源是否符合业务需求，考虑调整资源规模

请登录 AWS Cost Explorer 查看详细信息。
"""
            
            # 发送钉钉通知
            dingtalk.send_markdown(title, markdown_content)
            
            # 返回结果
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': '成本异常检测完成，已发送通知',
                    'anomalies': len(anomalies)
                })
            }
        else:
            logger.info("未检测到成本异常")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': '成本异常检测完成，未发现异常',
                    'anomalies': 0
                })
            }
    
    except Exception as e:
        logger.error(f"处理成本异常检测时出错: {str(e)}")
        # 发送错误通知
        error_message = f"AWS 成本优化 Lambda 函数出错: {str(e)}"
        dingtalk.send_text(error_message)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'处理成本异常检测时出错: {str(e)}',
                'error': str(e)
            })
        } 