from cgitb import handler
from http import client
import json
from urllib import response
import boto3

#expected event message
# {
#     "Records": [
#         {
#             "messageId": "11d6ee51-4cc7-4302-9e22-7cd8afdaadf5",
#             "receiptHandle": "AQEBBX8nesZEXmkhsmZeyIE8iQAMig7qw...",
#             "body": {"serial":"VM0",
#                      "price":"1.00",
#                       "name":"cola",
#                       "left":50,
#                       "percentage":98},
#             "attributes": {
#                 "ApproximateReceiveCount": "1",
#                 "SentTimestamp": "1573251510774",
#                 "SequenceNumber": "18849496460467696128",
#                 "MessageGroupId": "1",
#                 "SenderId": "AIDAIO23YVJENQZJOL4VO",
#                 "MessageDeduplicationId": "1",
#                 "ApproximateFirstReceiveTimestamp": "1573251510774"
#             },
#             "messageAttributes": {},
#             "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
#             "eventSource": "aws:sqs",
#             "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:fifo.fifo",
#             "awsRegion": "us-east-2"
#         }
#     ]
# }

def lambda_handler(event,context):
    dynamodb = boto3.client('dynamodb',endpoint_url='http://localhost:4566')
    for record in event['Records']:
        msgBody = json.loads(record['body'])
        serial = msgBody['serial']
        price = msgBody['price']
        itemLeft = str(msgBody['left'])
        dynamodb.update_item(TableName = 'vending-machine-helper',Key = {'serial':{'S':serial}}
        ,AttributeUpdates= {'total':{'Value':{'N':price},'Action':'ADD'},'earnings':{'Value':{'N':price},'Action':'ADD'},'itemsLeft':{'Value':{'N':itemLeft},'Action':'PUT'}})
