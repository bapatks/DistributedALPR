from openalpr import Alpr
import cv2, sys, time, numpy
import zmq, time, json, os

class Recognize():
    global alpr, path
    alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
    path = ''

    def __init__(self, no_of_speculations, country_region):
        global alpr, path
        if not alpr.is_loaded():
            print("Error loading OpenALPR")
            sys.exit(1)
        alpr.set_top_n(no_of_speculations)
        alpr.set_default_region(country_region)
        print("OpenAlpr is loaded")
        time.sleep(2)

    def utility(self, image_name):
        global alpr, path
        results, i = alpr.recognize_file(image_name), 0

        plate_no = "710CAS"
        ans = []

        for plate in results['results']:
            i += 1
            flag = 0
            #print("Plate #%d" % i)
            #print("   %12s %12s" % ("Plate", "Confidence"))
            for candidate in plate['candidates']:
                prefix = "-"
                
                if candidate['matches_template']:
                    prefix = "*"
                
                #print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))

                #print(candidate['plate'])
                length = self.LCS(plate_no, candidate['plate'], len(plate_no), len(candidate['plate']))
                conf_level = candidate['confidence']

                if length >= 4 and conf_level > 70: 
                    flag = True
                    ans.append( [candidate['plate'], candidate['confidence']] )
        if flag:
            frame = cv2.imread(image_name, cv2.IMREAD_COLOR)
            return cv2.imencode('.jpg', frame)[1].tostring()


    def LCS(self, X, Y, m, n):  
        LCSuff = [[0 for k in range(n+1)] for l in range(m+1)] 
        result = 0 
      
        for i in range(m + 1): 
            for j in range(n + 1): 
                if (i == 0 or j == 0): 
                    LCSuff[i][j] = 0
                elif (X[i-1] == Y[j-1]): 
                    LCSuff[i][j] = LCSuff[i-1][j-1] + 1
                    result = max(result, LCSuff[i][j]) 
                else: 
                    LCSuff[i][j] = 0
        return result



context = zmq.Context()
aggre_socket = context.socket(zmq.PUSH)


path = os.getcwd() + "/frame.jpeg"
my_object = Recognize(4, "ca")
data = my_object.utility(path)
print("done")

aggre_socket.connect("tcp://127.0.0.1:9999")
aggre_socket.send(data)
