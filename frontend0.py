import Pyro4
import uuid
import json
import random

@Pyro4.expose
class FrontEnd(object):
    def __init__(self):
        self.knownURIs = ["PYRO:Server1@localhost:50003"]
        self.frontEndTS = [1,0,0,0,0]

    def mergeTS(self, a, b):
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out      
    

    def recieveUpdate(self, user, movie, rating, comment):
        print("Update Request Recieved")
        ID = uuid.uuid4()
        server = Pyro4.Proxy(self.knownURIs[0])
        response = server.recieveUpdate(self.frontEndTS, ID, (user, movie, rating, comment))
        if response == "Invalid Update Request":
            print("Invalid Request")
            return "Invalid Request"
        self.frontEndTS = self.mergeTS(self.frontEndTS, response)
        print("Valid Request")
        print("New TS:", response)
        return "Valid Request"


daemon = Pyro4.Daemon(port=50001)
uri = daemon.register(FrontEnd, "FrontEnd")


print("Front End URI: ", uri)
daemon.requestLoop()
