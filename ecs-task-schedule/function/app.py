"""
-*- coding: utf-8 -*-
@File  : app.py
@author: mingyu110
@Description :
@Time  : 2024/06/04 06:37
"""
import boto3
from botocore.exceptions import ClientError

def update_service(cluster_name, service_name, desired_count):
    client = boto3.client('ecs')
    application_autoscaling_client = boto3.client('application-autoscaling')

    # Control the minimum number of tasks in the AutoScaling policy
    scalable_targets = application_autoscaling_client.describe_scalable_targets(
        ServiceNamespace='ecs',
        ResourceIds=[f'service/{cluster_name}/{service_name}'],
        ScalableDimension='ecs:service:DesiredCount'
    )['ScalableTargets']

    for scalable_target in scalable_targets:
        application_autoscaling_client.register_scalable_target(
            ServiceNamespace='ecs',
            ResourceId=f'service/{cluster_name}/{service_name}',
            ScalableDimension='ecs:service:DesiredCount',
            MinCapacity=0 if desired_count == 0 else 1,
            MaxCapacity=scalable_target['MaxCapacity']
        )

    # Update the service
    service_update_result = client.update_service(
        cluster=cluster_name,
        service=service_name,
        desiredCount=desired_count
    )
    print(service_update_result)

# Handler function for Lambda
def lambda_handler(event, context):
    try:
        client = boto3.client('ecs')
        elbv2_client = boto3.client('elbv2')

        action = event.get('action')  # 'stop' or 'start'
        environment = event.get('environment')  # 'scheduled' or 'manual'

        clusters_services_scheduled = [
            ('example-cluster', 'example-service-stg')
        ]

        clusters_services_manual = [
            ('example-cluster', 'example-service-dev')
        ]

        if environment == 'scheduled':
            clusters_services = clusters_services_scheduled
        elif environment == 'manual':
            clusters_services = clusters_services_manual
        else:
            raise ValueError("Invalid environment specified")

        desired_count = 0 if action == 'stop' else 1

        for cluster_name, service_name in clusters_services:
            update_service(cluster_name, service_name, desired_count)

        if action == 'start':
            for cluster_name, service_name in clusters_services:
                # Retrieve new task IDs and register them with the target group
                tasks = client.list_tasks(
                    cluster=cluster_name,
                    serviceName=service_name
                )['taskArns']

                task_descriptions = client.describe_tasks(
                    cluster=cluster_name,
                    tasks=tasks
                )['tasks']

                # Retrieve target group information associated with the service
                load_balancers = client.describe_services(
                    cluster=cluster_name,
                    services=[service_name]
                )['services'][0]['loadBalancers']

                for load_balancer in load_balancers:
                    target_group_arn = load_balancer['targetGroupArn']

                    for task in task_descriptions:
                        task_id = task['taskArn'].split('/')[-1]
                        elbv2_client.register_targets(
                            TargetGroupArn=target_group_arn,
                            Targets=[{'Id': task_id}]
                        )

    except ClientError as e:
        print(f"Exception: {e}")
    except ValueError as e:
        print(f"Exception: {e}")
