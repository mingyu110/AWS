import json
import boto3

def lambda_handler(event, context):
    target = event["crawlername"]
    glueclient = boto3.client('glue')
    glueclient.start_crawler(Name=target)

