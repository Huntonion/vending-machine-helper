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

# Prerequisites

* Docker
* AWS CLI
* boto3

## Setting up Node-RED and MosquittoMQTT

First start the docker containers:
```
docker run -itd -p 1880:1880 -v node_red_data:/data --network VMH --name nodered_VMH nodered/node-red

docker run -itd --network VMH --name mybroker eclipse-mosquitto mosquitto -c /mosquitto-no-auth.conf

docker run --rm --network VMH --name awslocal -it -p 4566:4566 -p 4571:4571 localstack/localstack
 ```






