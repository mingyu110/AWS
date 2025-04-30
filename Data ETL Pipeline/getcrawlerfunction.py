import json
import boto3

def lambda_handler(event, context):
    target = event["crawlername"]
    glueclient = boto3.client('glue')
    response = glueclient.get_crawler(Name=target)
    return {
        'state': response['Crawler']['State']
    }