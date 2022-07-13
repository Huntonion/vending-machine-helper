from cgitb import handler
import boto3

def lambda_handler(event,context):

    return{
        event['saluto']
    }