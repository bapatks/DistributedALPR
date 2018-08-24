# DistributedALPR
The project is based on designing virtual network for dynamically aggregating smart community devices - IoT sensors/actuators, edge and cloud computing resources through overlay virtual private networks(VPNs).\
This repo provides scripts to create the network, manage image data transfer and frame-by-frame analytics of stored and live video feeds.

## What's new?
A new controller module is introduced. The controller authenticates the clients & servers and is supposed to manage the overall client/server network.\
The code uses zmq PUSH-PULL communication pattern for data transfer and zmq ROUTER-REP and REQ-REP patterns for control and command.\
Designed to be scalable and introduces commands and error codes.\
A *ClientConnectionRule* module is introduced that can be used to dynamically control which clients are connected to which servers. The module can be easily expanded to add new rules.\
Testing is done to a good extent.

## Terminology
A server JOINS a network, effectively after being authenticated by the controller, and it DISJOINS to leave the network.\
A client CONNECTS to the server(after authentication by controller) and DISCONNECTS from the server.

## Known Issues
Some frames that are sent to the server may sometimes give a corrupt jpg error when parsed using OpenALPR. 

## Controller
To be updated

## Server
To be updates

## Client
To be updated
