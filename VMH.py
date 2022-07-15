from urllib import response
from urllib.request import Request
from aiohttp import ClientError
import boto3
import botocore
from prettytable import PrettyTable
from boto3.dynamodb.conditions import Key, Attr
import requests


dynamodb = boto3.client('dynamodb',endpoint_url='http://localhost:4566')
t = PrettyTable(['Serial', '# Left','Total Earnings','Local Earnings'])


print('Welcome to Vending Machine Helper!')
print('Accepted Commands:')
print('INFO *serial* in order to show informations regarding a specific machine')
print('CLEAR *serial* in order to set the local total of a machine to 0')
print('REFILL to restore all the machine to the initial configuration of the json file')
print('QUIT to exit.')
while True:
    user_input = input("Command:")
    vmlist = user_input.split()
    del(vmlist[0])
    if(user_input.startswith('INFO ')):
        try:
            batch_keys = {
                'vending-machine-helper':{
                    'Keys':[{'serial':{'S':serial}} for serial in vmlist]
                }
            }
            response = dynamodb.batch_get_item(RequestItems=batch_keys)
            for element in response['Responses']['vending-machine-helper']:
                serial=element['serial'] 
                itemsLeft=element['itemsLeft']
                total=element['total']
                earnings=element['earnings']
                t.add_row([serial['S'],itemsLeft['N'],total['N']+'€',earnings['N']+'€'])
            print(t)
            t.clear_rows()
        except botocore.exceptions.ClientError as e:
            print("The inserted values contain duplicates.")
    elif(user_input.startswith('CLEAR ')):
        try:
            for element in vmlist:
                dynamodb.update_item(
                    TableName='vending-machine-helper',
                    Key={
                        'serial':{
                            'S':element
                        }
                    },
                UpdateExpression ='SET earnings= :val',
                ExpressionAttributeValues={
                    ':val':{
                        'N':'0'
                    }
                },
                ConditionExpression='attribute_exists(serial)'
                )
            print('Cleared!')
        except botocore.exceptions.ClientError as e:
            print("One or more of the inserted values are not correct.")

    elif user_input == 'REFILL':
        URL = "http://localhost:1880/refill"
        r = requests.get(url = URL)
        if r.status_code == 200:
            print('Refilled!!')
        else:
            print('There was an error with your request.')
    elif user_input == 'QUIT':
    
        break
    else:
        print('Please insert a valid command.')
