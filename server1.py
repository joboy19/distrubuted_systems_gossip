import Pyro4
import json
import queue
import threading
import time
import random
serverNum = 1


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server():
    def __init__(self):                                 #initialize some variables, including starting the threadsafe variables
        print("Starting Server")
        self.serverNumber = 1
        with open("server{0}ratings.json".format(self.serverNumber), "r") as f:
            inValue = json.load(f)
        self.serverInfo = queue.Queue()
        self.serverInfo.put({"replicaTS":[0,0,0,0,0], "updateLog":[], "valueTS":[0,0,0,0,0], "value":[], "exOps":[]})
        self.movies = ["spiderman", "bee movie"]
        self.knownRMs = ["PYRO:Server0@localhost:50002"]
        self.status = "online"
        threading.Thread(target=self.mainLoop).start()

    def mergeTS(self, a, b):
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out

    def lessThanTS(self, a, b):
        for x in range(len(a)):
            if not (a[x] <= b[x]):
                return False
        return True

    def sortLog(self, log):
        n = len(log)
        out = list(log)

        for x in range(n):
            for y in range(0, n - x - 1):
                if self.lessThanTS(out[y+1][1], out[y][0]):
                    out[y+1], out[y] = out[y], out[y+1]
        return out
        

    def recieveUpdate(self, uPREV, uID, uOP):
        data = self.serverInfo.get(block = True, timeout = None)
        print("Incoming message: ", uPREV, uID, uOP)
        if not (uOP[1] in self.movies):
            self.serverInfo.put(data)
            return "Invalid Update Request"
        if uID in data["exOps"]:
            self.serverInfo.put(data)
            return data["valueTS"]
        data["replicaTS"][self.serverNumber] += 1
        TS = list(uPREV)
        TS[self.serverNumber] = data["replicaTS"][self.serverNumber]
        data["updateLog"].append( [self.serverNumber, TS, uOP, uPREV, uID] )
        data = self.checkForStable(data)
        self.serverInfo.put(data)
        return TS
    
    @Pyro4.oneway
    def recieveGossip(self, inLog, inTS, RMNo):
        data = self.serverInfo.get(block = True, timeout = None)
        print("recieved update log:", inLog)
        for x in inLog:
            if not self.lessThanTS(x[1], data["replicaTS"]):
                add = True
                for y in data["updateLog"]:
                    if y[4] == x[4]:
                        add = False
                if add:
                    data["updateLog"].append(x)
        data = self.checkForStable(data)
        self.serverInfo.put(data)

    def checkForStable(self, data):
        data["updateLog"] = self.sortLog(data["updateLog"])
        x = 0
        while x < len(data["updateLog"]):
            if (not data["updateLog"][x][4] in data["exOps"]) and self.lessThanTS(data["updateLog"][x][3], data["valueTS"]):
                data["value"] = self.updateValue(data["updateLog"][x][2], data["value"])
                data["valueTS"] = self.mergeTS(data["valueTS"], data["updateLog"][x][1])
                data["exOps"].append(data["updateLog"][x][4])
                x = 0
            x += 1
        return data
        
    
                
            
    def updateValue(self, newUpdate, data):
        outData = data
        for x in outData:
            if x["user"] == newUpdate[0]:
                if x["movie"] == newUpdate[1]:
                    x["rating"] = newUpdate[2]
                    return outData
        outData.append( {"user":newUpdate[0], "movie":newUpdate[1], "rating":newUpdate[2], "comment":newUpdate[3]} )
        return outData

    def getMovies(self):
        return self.movies

    def checkMovie(self, movie):
        return (movie in self.movies)

    def viewMovieReviews(self, qOP, qPREV):
        data = self.serverInfo.get(block = True, timeout = None)
        if not self.lessThanTS(qPREV, data["valueTS"]):
            self.serverInfo.put(data)
            return "Timestamp too new"
        self.serverInfo.put(data)
        reviews = []
        for x in data["value"]:
            if x["movie"] == qOP:
                reviews.append(x)
        return reviews, data["valueTS"]

    def viewUserReviews(self, qOP, qPREV):
        data = self.serverInfo.get(block = True, timeout = None)
        if not self.lessThanTS(qPREV, data["valueTS"]):
            self.serverInfo.put(data)
            return "Timestamp too new"
        self.serverInfo.put(data)
        reviews = []
        for x in data["value"]:
            print("sikljdufhasioeufhaei", x)
            if x["user"] == qOP:
                reviews.append(x)
        return reviews, data["valueTS"]

    def viewSingleReview(self, qOP, qPREV):
        data = self.serverInfo.get(block = True, timeout = None)
        if not self.lessThanTS(qPREV, data["valueTS"]):
            self.serverInfo.put(data)
            return "Timestamp too new"
        self.serverInfo.put(data)
        for x in data["value"]:
            if x["user"] == qOP[0]:
                if x["movie"] == qOP[1]:
                    return x, data["valueTS"]
        return "Review Was No Found", data["valueTS"]
        
    def getStatus(self):
        return self.status

    def mainLoop(self):
        while True:
            time.sleep(5)
            print("Gossip time", time.time())
            data = self.serverInfo.get(block = True, timeout = False)
            print("updatelog:", data["updateLog"])
            print("value table:", data["value"])
            print("valueTS: ", data["valueTS"])
            gossipInfo = ( data["replicaTS"], data["updateLog"] )
            random1, random2 = 0, 0#random.randint(0, 4), random.randint(0, 4)
            self.serverInfo.put(data)
            gossipPart = Pyro4.Proxy(self.knownRMs[random1])
            gossipPart.recieveGossip(gossipInfo[1], gossipInfo[0], random1)
 
            

    
portNum = 50002 + serverNum
daemon = Pyro4.Daemon(port=portNum)
uri = daemon.register(Server, "Server" + str(serverNum))

print("Server{0}".format(serverNum))
print("URI:", uri)

threading.Thread(target=daemon.requestLoop).start()

with Pyro4.Proxy(uri) as rm:
    print("Status: {0}".format(rm.getStatus()))

