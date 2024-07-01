"""
-*- coding: utf-8 -*-
@File  : OpenAI_Lambda_Function.py
@author: mingyu110
@Description : 
@Time  : 2024/06/29
"""
import os
import json
import requests
import pymysql


def lambda_handler(event, context):
    # Database connection details
    rds_host = os.environ['RDS_HOST']
    rds_username = os.environ['RDS_USERNAME']
    rds_password = os.environ['RDS_PASSWORD']
    rds_db_name = os.environ['RDS_DB_NAME']

    # API key of Telegram and OpenAI
    telegram_token = os.environ['TELEGRAM_TOKEN']
    openai_api_key = os.environ['OPENAI_API_KEY']

    # Parse messages from Telegram
    message = get_message(event)
    chat_id = message['chat']['id']
    text = message['text'].strip()

    # Connect database
    connection = pymysql.connect(
        host=rds_host,
        user=rds_username,
        password=rds_password,
        db=rds_db_name
    )

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT task_name, time 
            FROM taskreminder 
            WHERE chat_id = %s
            """
        cursor.execute(query, (chat_id,))
        tasks = cursor.fetchall()

        task_info = '\n'.join([f"{task[0]} at {task[1]}" for task in tasks])
        prompt = f"Sam's work tasks:\n{task_info}\n\nSam's question: {text}"

        # Invoke ChatGPT API
        response_text = call_chatgpt_api(openai_api_key, prompt)

        # Return response to the inquirer
        send_telegram_message(telegram_token, chat_id, response_text)

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': json.dumps('Response sent successfully!')
    }


def get_message(event):
    """ Extract the message from the incoming event """
    if 'message' in event:
        return event['message']
    elif 'body' in event:
        body = json.loads(event['body'])
        if 'message' in body:
            return body['message']
    raise KeyError("The 'message' key is missing in the event")


def call_chatgpt_api(api_key, prompt):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'prompt': prompt,
        'max_tokens': 150,
    }
    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['text'].strip()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "I'm sorry, I couldn't process your request right now."


def send_telegram_message(token, chat_id, message):
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
