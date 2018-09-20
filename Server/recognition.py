from openalpr import Alpr
import cv2, sys, time, numpy, zmq, time, json, os, pickle


class Frame_Data():
    def __init__(self, path_to_frame, server_identity, time, matched_plates):
        self.byte_frame = cv2.imencode('.jpg', cv2.imread(path_to_frame, cv2.IMREAD_COLOR) )[1].tostring()
        self.server_identity = server_identity
        self.time = time
        self.matched_plates = matched_plates



class Recognize():
    def __init__(self, no_of_speculations, country_region, confidence):
        print("OpenAlpr is loading.....")
        try:
            self.ALPR = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
        except:
            print("Error loading OpenAlpr")
            sys.exit(1)
        self.NO_OF_SPECULATIONS = no_of_speculations
        self.COUNTRY_REGION =country_region
        self.CONFIDENCE = confidence
        self.PLATES_REPOSITORY = ["WKX212", "7UFX735"]
        self.MATCHING_LENGTH = 3
        self.ALPR.set_top_n(self.NO_OF_SPECULATIONS)
        self.ALPR.set_default_region(self.COUNTRY_REGION)


    def Identify_Frame(self, path_to_frame, server_identity, aggr_sender):
        results = self.ALPR.recognize_file(path_to_frame)
        matched_plates = []
    
        for plate in results['results']:
            for candidate in plate['candidates']:
                # print(server_identity + " " +candidate['plate'])

                if self.CONFIDENCE <= candidate['confidence']:
                    for x in self.PLATES_REPOSITORY:
                        length = self.LongestCommonString(x, candidate['plate'], len(x), len(candidate['plate']))
                        
                        if length >= self.MATCHING_LENGTH:
                            matched_plates.append([x, str(candidate['plate']), candidate['confidence']])

        data = None
        if len(matched_plates) > 0:
            data = Frame_Data(path_to_frame, server_identity, "", matched_plates)

        if data:
            aggr_sender.send(pickle.dumps(data))



    #returns the length of longest common substring matched
    def LongestCommonString(self, X, Y, m, n):  
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