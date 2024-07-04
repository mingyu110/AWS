"""
-*- coding: utf-8 -*-
@File  : Add_Lambda_Function.py
@author: mingyu110
@Description : 
@Time  : 2024/06/29
"""
import pymysql
import json
import os
import requests


def lambda_handler(event, context):
    # Database connection details
    rds_host = os.environ['RDS_HOST']
    rds_username = os.environ['RDS_USERNAME']
    rds_password = os.environ['RDS_PASSWORD']
    rds_db_name = os.environ['RDS_DB_NAME']

    # Telegram Bot API details
    chat_token = os.environ['TELEGRAM_TOKEN']

    # Log the incoming event for debugging purposes
    event_log = json.dumps(event, indent=4)
    print(f"Event Log: {event_log}")

    try:
        # Parse the incoming message from Telegram
        if 'body' in event:
            body = json.loads(event['body'])
            if 'message' not in body:
                raise KeyError("The 'message' key is missing in the event body")
            message = body['message']
        else:
            raise KeyError("The 'body' key is missing in the event")

        chat_id = message['chat']['id']
        message_body = message['text']

        # Check if the message format is correct
        if ',' not in message_body:
            raise ValueError("Invalid message format. Expected 'task_name, time'.")

        # Assuming the format is "medication_name, time"
        task_name, time = map(str.strip, message_body.split(','))

        # Connect to the database
        connection = pymysql.connect(
            host=rds_host,
            user=rds_username,
            password=rds_password,
            db=rds_db_name
        )

        try:
            with connection.cursor() as cursor:
                # Insert data into MySQL
                sql = "INSERT INTO taskreminder (chatid, task_name, time) VALUES (%s, %s, %s)"
                cursor.execute(sql, (chat_id, task_name, time))
                connection.commit()
            print(f"Inserted task: {task_name} at {time} for chat ID: {chat_id}")

            # Send confirmation message back to the user
            send_chat_message(chat_token, chat_id, f"Task '{task_name}' has been saved for {time}.")

        except pymysql.MySQLError as e:
            print(f"Error occurred while saving task: {str(e)}")
            return {
                "statusCode": 500,
                'body': json.dumps(f"MySQL Error: {str(e)}")
            }
        finally:
            connection.close()

        return {
            "statusCode": 200,
            'body': json.dumps("Task saved successfully.")
        }
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return {
            "statusCode": 400,
            'body': json.dumps(f"Invalid message format: {str(e)}")
        }
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }


def send_chat_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print(f"Sent message: {message}")
