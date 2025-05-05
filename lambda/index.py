import json
import os
import boto3
import re
import urllib.request

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("Processing message:", message)

        messages = conversation_history.copy()
        messages.append({
            "role": "user",
            "content": message
        })

        request_payload = {
            "prompt": str(message),  
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        req = urllib.request.Request(
            url='https://529a-34-16-172-54.ngrok-free.app/generate',
            data=json.dumps(request_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method='POST'
        )

        with urllib.request.urlopen(req) as res:
            response_body = json.loads(res.read().decode('utf-8'))
            theHttpsStatus = res.getcode()
        


        # 応答の検証
        if 'generated_text' not in response_body:
            raise Exception("No 'generated_text' in response")

        assistant_response = response_body['generated_text']

        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "generated_text": str(assistant_response),
                "response_time": 0
            })

        }
        
    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
