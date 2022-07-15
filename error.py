import requests
import boto3
import datetime
import json

def lambda_handler(event, context):
	key = "<key>"
	url = "https://maker.ifttt.com/trigger/vmh_error/with/key/"+key
	for record in event['Records']:
		msgBody = json.loads(record['body'])
		error = msgBody['error']
		requests.post(url, json={"value1": error})
