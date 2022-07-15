# Vending Machine Helper
A project for the Serverless Computing for IoT class.

## Introduction

This application is used to process information regarding Vending Machines
each time an Item is sold, by sending an MQTT message to a gateway which 
will then put the message into an AWS SQS FIFO queue. The FIFO structure 
was adopted as it will guarantee that the sales will be processed exactly 
once and in the correct order. Eventually, if a Vending Machine's items 
quantity is getting under a certain value, The application will notify the 
user through IFTTT sending him an email. The Amazon Web Services were 
emulated using LocalStack. The core of this operations are the serverless 
functions (two in this case):
*One to update information about a certain vending machine in DynamoDB (or 
create a new item if the Vending Machine didn't have any entry yet)
*One to notify the user when there's a problem. 

Both the devices(vending machines) and the gateway were simulated on 
Node-RED running in a docker container. Also, the MQTT broker 
(MoquitoMQTT) and LocalStack are running in docker containers, and in 
order to let them communicate with each other a Docker network was 
utilized.


