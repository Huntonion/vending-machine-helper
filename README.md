# Vending Machine Helper
A project for the Serverless Computing for IoT class.

## Introduction

This application is used to process information regarding Vending Machines
each time an Item is sold, by sending an MQTT message to a gateway which 
will then put the message into an AWS SQS FIFO queue. The FIFO structure 
was adopted as it will guarantee that the sales will be processed exactly 
once and in the correct order. Eventually, if a Vending Machine's items 
quantity is getting under a certain value, The application will notify the 
user through IFTTT sending him an email. The core of this operations are the serverless 
functions (two in this case):

* One to update information about a certain vending machine in DynamoDB 
(or 
create a new item if the Vending Machine didn't have any entry yet)
* One to notify the user when there's a problem. 

Which are both message triggered.


## Architecture

![Architecture](https://github.com/Huntonion/vending-machine-helper/blob/main/pictures/VMH.jpeg?raw=true)

The Amazon Web Services were emulated using LocalStack. Both the 
devices(vending machines) and the gateway were simulated on 
Node-RED running in a docker container. Also, the MQTT broker 
(MoquittoMQTT) and LocalStack are running in docker containers, and in 
order to let them communicate with each other a Docker network was 
utilized. The interactive application consists in a python script which 
used the functionalities offered by the boto3 library.


## Installation

## Prerequisites

* Docker
* AWS CLI


## Setting up Node-RED and MosquittoMQTT

First of all run

```
git clone https://github.com/Huntonion/vending-machine-helper
```

Then start the docker containers
```
docker run -itd -p 1880:1880 -v node_red_data:/data --network VMH --name nodered_VMH nodered/node-red

docker run -itd --network VMH --name mybroker eclipse-mosquitto mosquitto -c /mosquitto-no-auth.conf

 ```
In order to simulate the devices, the application uses a Json file (devices.json), which at the moment includes 8 devices, however, as long as the document is correctly formatted, you can add as many devices as you want up to potentially an infinite number. Therefore, the next step is to copy the devices.json file into the volume, to do so:
*Note:this project was developed on MAC OS , and accessing the volume directly is not possible, therefore the most suitable solution was to copy and paste the files out and back in the volume*

```
docker cp devices.json nodered_VMH:/data/devices.json
```
Then, since some of the nodes in the project use the aws-sdk, first it has to be installed on the container:
```
docker exec nodered_VMH npm install aws-sdk
```
Copy the settings.js out of the volume:
```
Docker cp nodered_VMH:/data/settings.js settings.js
```
And add a line in the file
```
FunctionGlobalContext:{
   os:require('os'),
   awsModule:require('aws-sdk') //add this line
},
```
And copy back the file into the volume.
```
Docker cp settings.js nodered_VMH:/data/settings.js
```
Now open node red by accessing `localhost:1880` and on the menu choose `import flow` and select the `flow.json` file.
Restart Node-RED.

Before starting the simulation, it is necessary to set up the cloud environment first.

## Setting up LocalStack
```
docker run --rm --network VMH --name awslocal -it -p 4566:4566 -p 4571:4571  localstack/localstack
```
Once the container is running, run `aws config` to configurate it.

Create a role for our lambda function:
```
aws iam create-role --role-name lambdaVMHRole \
--assume-role-policy-document \
file://role.json --endpoint-url=http://localhost:4566
```

And assign a policy to it:
```
aws iam put-role-policy --role-name lambdaVMHRole --policy-name \
lambdaPolicy --policy-document file://policy.json \
--endpoint-url=http://localhost:4566
```
### Note:
Before zipping the error function, setting up IFTTT is necessary since the file `error.py` requires a key. Informations on how to setup IFTTT are reported in the next section.

zip both functions:
```
zip function.zip error.py
zip function.zip sale.py
```

And create the functions:
```
aws lambda create-function --function-name sale --zip-file \
fileb://function.zip --handler sale.lambda_handler --runtime python3.6 \
--role arn:aws:iam::000000000000:role/lambdaVMHRole \
--endpoint-url=http://localhost:4566
```
```
aws lambda create-function --function-name error --zip-file \
fileb://function.zip --handler error.lambda_handler --runtime python3.6 \
--role arn:aws:iam::000000000000:role/lambdaVMHRole \
--endpoint-url=http://localhost:4566 
```
Make sure that the arn is correct, otherwise it won't work.
Create the dynamoDB table:
```
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
--table-name vending-machine-helper \
--attribute-definitions AttributeName=serial,AttributeType=S \
--key-schema AttributeName=serial,KeyType=HASH \
--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```
For the purpose of this project ReadCapacityUnits and WriteCapacityUnits were set to 5 as most likely it will never reach that capacity.
Create the Queues:
```
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name \
sale.fifo --attributes FifoQueue=true
```
```
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name \
error.fifo --attributes FifoQueue=true
```
Create the event source mappings in order to call the functions whenever an item is sent to that queue.
```
aws lambda create-event-source-mapping --function-name sale --batch-size 3 \
--event-source-arn arn:aws:sqs:us-east-2:000000000000:sale.fifo \
--endpoint-url=http://localhost:4566
```
```
aws lambda create-event-source-mapping --function-name error --batch-size 3 \
--event-source-arn arn:aws:sqs:us-east-2:000000000000:error.fifo \
--endpoint-url=http://localhost:4566
```
The cloud environment should now be functioning.


## Setting up IFTTT 

go on https://ifttt.com/, and create a new applet:
* Select in 'If This' add a webhook, and select receive a web request. Choose the parameters to set up
* In "Then that" choose 'email' and complete the configuration. 
* Retrive the key from the webhook and copy it into the error.py function.

## Running the simulation

The node Configuration on Node red is composed of two sections: The one above labeled "Start" and the one below named "Actual business logic". First inject the `START` node which will read the devices.json to allow the simulation of the devices. 
Then the flows can be operated either by injecting the `run simulation` node which will trigger every node it's connected to continuosly, or you can add an inject node and connect it to the specific machine you want to operate. 

![Architecture](https://github.com/Huntonion/vending-machine-helper/blob/main/pictures/nodered.png?raw=true)

## Interacting with the application

First it is necessary to install the dependencies:
```
pip install -r requirements.txt
```
Then simply run:
```
python3 VMH.py
```
The python application will look like this: 

![Architecture](https://github.com/Huntonion/vending-machine-helper/blob/main/pictures/VMHapp.png?raw=true)

The available commands are: 
* INFO *serials*, to retrive information about the products relative to the serials inserted. For instance `INFO VM1 VM2`
* CLEAR *serials*, to set the local earnings to zero. Example: `CLEAR VM1 VM2`
* REFILL, to refill all the machines. Unfortunately Vending Machine Helper does not support single machine refill yet.
* QUIT, to quit.
