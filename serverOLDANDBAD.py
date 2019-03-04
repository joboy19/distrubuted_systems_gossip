import Pyro4
import json
import queue
import threading
import time

@Pyro4.expose
class Server(object):
    ratings = queue.Queue()
    with open("server1ratings.json", "r") as f:                                     #load all ratings from JSON
        ratings.put(json.load(f))                                     #hard-code movies
    knownRMs = ["PYRO:Server2@localhost:50003"]                                 #hard-code other RMs
    doneOps = queue.Queue()
    doneOps.put([])

    def __init__(self):
        self.serverNumber = 0
        self.movies = ["spiderman", "bee movie"]
    
    def updateMovie(self, movie, newRating, user, knownVector):
        print("got movie {0} with rating {1} from user {2} with vector {3}".format(movie, newRating, user, knownVector))
        ratingID = user + movie                                                 #make ID and check movies
        if not movie in self.movies:
            return False
        
        
        ratings = Server.ratings.get(block=True, timeout=None)
        succ = False
        for x in ratings:
            if x["ratingID"] == ratingID:
                succ = True
                vector = x["vector"]
                #print("vector: ", vector)
                if knownVector[self.serverNumber] <= vector[self.serverNumber]:           #stability check
                    x["rating"] = newRating
                    vector[self.serverNumber] = vector[self.serverNumber] + 1             #update vector
                    for y in range(len(vector)):
                        if y != self.serverNumber:
                            vector[y] = max(vector[y], knownVector[y])
                    x["vector"] = vector                                        #***maybe add to known updates
                    x["rating"] = newRating #do the update
                    Server.ratings.put(ratings)
                    return vector
                Server.ratings.put(ratings)
                return False
        
        if not succ:
            ratings.append( { "ratingID":ratingID, "user":user, "rating":newRating, "vector":[1,0,0,0,0] } )
                                                                                #if rating doesnt exist, add it
            Server.ratings.put(ratings)
            return [1,0,0,0,0]


    def requestGossip(self):
        out = (Server.movies.get(block=True, timeout=None), Server.RMtimeStamps.get(block=True, timeout=None))
        Server.movies.put(out[0])
        Server.RMtimeStamps.put(out[1])
        return out

    def gossip(self):
        for x in self.knownRMS:
            currentCon = Pyro4.proxy(x)
            recievedGoss = currentCon.requestGossip()
            

    def test(self):
        return "you can do it"


    def mainLoop(self):
        print("We online")
        while True:
            time.sleep(5)
            print("server online!", time.time())

    

daemon = Pyro4.Daemon(port=50002)
uri = daemon.register(Server, "Server1")

print("Server1 URI: ", uri)
threading.Thread(target=daemon.requestLoop).start()

Server().mainLoop()
