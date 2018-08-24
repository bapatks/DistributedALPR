#!/usr/bin/env python
import os
import sys
import zmq
from PIL import Image
import sys, numpy, cv2, time, os, settings

class Transmit():
	def __init__(self, cntrl_address, control_port):
		self.sender = context.socket(zmq.PUSH)
		self.request = context.socket(zmq.REQ)
		#self.command = context.socket(zmq.REP)

		#IP address of server, as received from controller
		self.serv_ip = None

		#Send frames to server on this port
		self.data_port = None

		#Send requests to server(if any)
		self.command_port = None

		#Send control requests to controller
		self.control_port = control_port
		self.cntrl_ip = cntrl_address
		self.identity = 0
		
	
	#Send requests to controller - Ping the controller
	def ping(self, msg_req):
		self.request.connect("tcp://"+self.cntrl_ip+":"+self.control_port)
		
		if msg_req=="CONNECT":
			self.request.send_multipart([msg_req+"!", str(self.identity)])
			print("CONNECT request sent to tcp://"+self.cntrl_ip+":"+self.control_port)
			status, clientID, server_ip, serv_data_port = self.request.recv_multipart()

			#reply of the form <status><!><6-digit-unique_ID><server_IP:data_port>
			#					200!100000127.0.0.1:5556		(if success)
			#					400!							(if failed)
			if status== "200!":
				self.identity = clientID
				self.serv_ip = server_ip
	   			self.data_port = serv_data_port
	   	 	
	   	 		print("Server accepted the connection")
	   	 		print("Client: ID "+self.identity)
	   	 		return 1
	   		else:
	   			print("ERROR "+status)
	   			return 0

	   	elif msg_req=="DISCONNECT":
	   		self.request.send_multipart([msg_req+"!", str(self.identity)])
	   		print("DISCONNECT request sent to tcp://"+self.cntrl_ip+":"+self.control_port)
			status = self.request.recv_multipart()
			if status=="200!":
				self.identity = 0
				self.serv_ip = None
	   			self.data_port = None
	   			print("Disconnected gracefully")
	   			return 1
	   		else:
	   			print("ERROR")
	   			return 0


	def connection(self):
		#self.sender.setsockopt(zmq.SNDHWM, 100)
		self.sender.connect("tcp://"+self.serv_ip+":"+self.data_port)
		print("Connected to tcp://"+self.serv_ip+":"+self.data_port+" for data transfer")

	def send(self, video_file):
		capture = cv2.VideoCapture(os.getcwd() + "/" + video_file)            #capturing the video
		count=0
		while 1:
			#breaking into frames
			return_val, frame = capture.read()
			if return_val:
				#numpy func converting into bytes(not string)(name tostring is misleading)
				data = cv2.imencode('.jpg', frame)[1].tostring()
				self.sender.send(data+'END!')
				sys.stdout.write(".")
				sys.stdout.flush()
				count=count+1
				time.sleep(0.01)

			else:
				self.sender.send('STOP!')
				print("STOP sent")
				print("number of frames sent = "+str(count))
				break
		
		time.sleep(1)
		capture.release()
		print("--------------End of frame parsing--------------")

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage : python <script_name> <video-file>")
		sys.exit()

	do_exit = False
	context = zmq.Context()
	#print("Current libzmq version is %s" % zmq.zmq_version())
	#print("Current  pyzmq version is %s" % zmq.__version__)
	node = Transmit(settings.client['controller_ip'], settings.client['rrport'])
	
	status = node.ping("CONNECT")
	time.sleep(1)
	if status:
		node.connection()
		node.send(sys.argv[1])
		while do_exit==False:
			try:
				time.sleep(0.1)
			except KeyboardInterrupt:
				status = node.ping("DISCONNECT")
				if status==1:
					do_exit=True
				else:
					continue
		node.sender.close()
		node.request.close()
		context.term()
