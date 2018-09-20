import zmq, time, json, os, numpy, cv2, pickle, settings

#binding the aggregator with an address
context = zmq.Context()
pull_port = context.socket(zmq.PULL)
pull_port.bind("tcp://127.0.0.2:9999")
req_port = context.socket(zmq.REQ)
req_port.connect("tcp://127.0.0.1:7777")



class Frame_Data():
    def __init__(self):
        self.frame = None
        self.server_identity = ""
        self.time = ""
        self.matched_plates = None

def deserialize(raw_data, counter):
    f = Frame_Data()
    f.frame = cv2.imdecode( numpy.fromstring(raw_data.byte_frame, numpy.uint8), cv2.IMREAD_COLOR)
    f.server_identity = str(raw_data.server_identity)
    f.time = raw_data.time
    f.matched_plates = raw_data.matched_plates
    cv2.imwrite(os.getcwd() + "/frames/" + f.server_identity + "_f" + str(counter) + "frame.jpg", f.frame)
    return f



def Write_to_file(frame_data_object, filename, counter):
	file.write(frame_data_object.server_identity)
	file.write("_f" + str(counter) + "\t\t")
	for x in frame_data_object.matched_plates:
		file.write(str(x))
	file.write("\t\t" + frame_data_object.time + "\t" + time.asctime(time.localtime(time.time())) + "\n\n")
	



def Receive_Data():
	counter = 1
	while True:
		raw_data = pickle.loads(pull_port.recv())
		frame_data_object = deserialize(raw_data, counter)
		print("Received a matched frame!")
		Write_to_file(frame_data_object, filename, counter)
		counter += 1



if __name__ == '__main__':
	
	#File_Operations
	filename = "LogFile.txt"
	file = open(filename, 'a')

	req_port.send("JOIN!127.0.0.2:9999")
	reply = req_port.recv()
	if(reply == "200!"):
		print("OK")
		Receive_Data()
	else:
		print("exiting")


