import Pyro4
import uuid
import json
import random

@Pyro4.expose
class FrontEnd(object):
    knownURIs = ["PYRO:Server1@localhost:50002"]
    with open("frontend.json", "r") as f:
        vectors = json.load(f)
    frontEndTS = [0,0,0,0,0]

    def __mergeTS(a, b):
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out
    

    def sendUpdate(self, user, movie, rating):
        ID = = uuid.uuid4()
        server = Pyro4.proxy(knownURIs[0])
        response = server.recieveUpdate(frontEndTS, ID, (name, movie, rating))
        if response == "Invalid Update Request":
            print("Invalid Request")
            return "Invalid Request"
        frontEndTS = self.__mergeTS(frontEndTS, response)
        return "Valid Request"


daemon = Pyro4.Daemon(port=50001)
uri = daemon.register(FrontEnd, "FrontEnd")


print("Front End URI: ", uri)
daemon.requestLoop()
