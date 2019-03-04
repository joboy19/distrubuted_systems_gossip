import Pyro4
import json
import queue
import threading
import time
import random

"""
To do:
Add querying -> Dont know about how holding the request works, could just point the FE in the right way

"""

@Pyro4.expose
class Server(object):

    def __init__(self):
        with open("server1ratings.json", "r") as f:
            inValue = json.load(f)
        self.serverInfo = queue.Queue()
        self.serverInfo.put({"replicaTS":[0,0,0,0,0], "updateLog":[], "valueTS":[0,0,0,0,0], "value":inValue, "exOps":[]})
        self.serverNumber = 0
        self.movies = ["spiderman", "bee movie"]
        self.knownRMs = ["PYRO:Server2@localhost:50003"]

    def __mergeTS(self, a, b):
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out

    def __lessThanTS(self, a, b):
        for x in range(len(a)):
            if not (a[x] <= b[x]):
                return False
        return True

    def recieveUpdate(self, uPREV, uID, uOP):
        data = self.serverInfo.get(block = True, timeout = None)
        if not (uOP[1] in self.movies):
            return "Invalid Update Request"
        if uID in data["exOps"]:
            Server.serverInfo.put(data)
            return data["valueTS"]
        data["replicaTS"][self.serverNumber] += 1
        TS = uPREV
        TS[self.serverNumber] = data["replicaTS"][self.serverNumber]
        data["updateLog"].append( [self.serverNumber, TS, uOP, uPREV, uID] )
        self.serverInfo.put(data)
        return TS

    def recieveGossip(inLog, inTS, RMNo):
        data = self.serverInfo.get(block = True, timeout = None)
        for x in inLog:
            if self.__lessThanTS(x[1], data["replicaTS"]):
                data["updateLog"].append(x)
        x = 0
        while x < range(len(data["updateLog"])):
            if self.__lessThanTS(data["updateLog"][x][3], data["valueTS"]):
                data["value"] = update(newUpdate, data["value"])
                data["valueTS"] = self.__merge(data["valueTS"], data["updateLog"][x][1])
                data["exOps"].append(data["updateLog"][x][1])
                x = 0
            x += 1
        newLog = []
            
        self.data.put(data)
                
            
    def update(self, update, data):
        outData = data
        for x in outData:
            if x["name"] == newUpdate[0]:
                if x["movie"] == newUpdate[1]:
                    x["rating"] = newUpdate[2]
                    return outData
        outData.append( {"name":newUpdate[0], "movie":newUpdate[1], "rating":newUpdate[0]} )
        return outData
        

    def test(self):
        return "you can do it"


    def mainLoop(self):
        print("We online")
        while True:
            time.sleep(1)
            print("server online!", time.time())
            data = self.serverInfo.get(block = True, timeout = False)
            gossipInfo = ( data["replicaTS"], data["updateLog"] )
            random1, random2 = random.randint(0, 4), random.randint(0, 4)
            self.serverInfo.put(data)
            gossipPart = Pyro4.Proxy(self.knownRMs[random1])
            gossipPart.recieveGossip(gossipInfo[1], gossipInfo[0], random1)
            
            

    

daemon = Pyro4.Daemon(port=50002)
uri = daemon.register(Server, "Server1")

print("Server1 URI: ", uri)
threading.Thread(target=daemon.requestLoop).start()

Server().mainLoop()
