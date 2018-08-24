#!/usr/bin/env python
import zmq, threading, thread, time
from controller_utils import StoppableThread

class ManageServers(StoppableThread):
	def __init__(self, config):
		StoppableThread.__init__(self)
		self.thread = threading.Thread(name="Listen_server_requests", target=self.run, args=(config,))
		self.thread.start()

	def run(self, config):
		while self.stop_event.is_set()==False:
			self._join(config)

	def _join(self, config):
		server, empty, msg, ID, serv_ip, serv_cmd_port = config.serv_control.recv_multipart()
		#["JOIN!", config.servID, config.host_ip, config.command_port]
		print("Server: "+msg+ID+serv_ip+serv_cmd_port)

		if msg == "JOIN!" and ID=="0":
			try:
				config.command.connect("tcp://"+serv_ip+":"+serv_cmd_port)
				req = "CHECK!"+serv_ip+":"+serv_cmd_port
				config.command.send(req)
				#print("Sent CHECK! to server on tcp://"+receive[6:])
				reply = config.command.recv()
				print("Server: "+reply)

				while reply == "400!":
					#retry nudging the server
					config.command.connect("tcp://"+serv_ip+":"+serv_cmd_port)
					req = "CHECK!"+serv_ip+":"+serv_cmd_port
					config.command.send(req)
					print("Resent CHECK! to server on tcp://"+serv_ip+":"+serv_cmd_port)
					reply = config.command.recv()
					print("Server: "+reply)

				
				if reply == "200!":
					if not config.serv_meta:
						#serv_meta is empty, assign servID to first server
						servID = "s100"
						print(servID)
					else:
						serv_list = sorted(config.serv_meta)
						servID = "s"+str(int(serv_list[-1][1:])+1)

					config.serv_meta[servID] = [serv_ip]
					config.serv_meta[servID].append(serv_cmd_port)
					print(config.serv_meta)
					config.serv_load[servID] = 0
					print(config.serv_load)
					reply_msg = "200!"+servID
					config.serv_control.send_multipart([server, "", reply_msg])

			except:
				#400 - Bad request
				config.serv_control.send_multipart([server, "", "400!"])

			#for reliable working of REQ-REP
			config.command.disconnect("tcp://"+serv_ip+":"+serv_cmd_port)
			

		elif msg == "DISJOIN!" and ID!="0":
			print("feature coming soon")