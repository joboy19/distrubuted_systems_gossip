import Pyro4
import json
import queue
import threading
import time
import random
import csv
serverNum = 4

#["PYRO:Server0@localhost:50002", "PYRO:Server1@localhost:50003", "PYRO:Server2@localhost:50004", "PYRO:Server3@localhost:50005", "PYRO:Server4@localhost:50006"]

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")                             #only create a single instance of the server
class Server(object):
    def __init__(self):                                             #initialize RM variables, including starting the threadsafe variables
        print("Starting Server")
        self.serverNumber = 4
        self.serverInfo = queue.Queue()                             #threadsafe values which allow for blocking of other processes whilst processing
        values = self.createReviews()
        self.serverInfo.put({"replicaTS":[0,0,0,0,0], "updateLog":[], "valueTS":[0,0,0,0,0], "value":values, "exOps":[]})
        self.movies = self.createMovies() + ["Test_Movie_Title"]
        self.knownRMs = ["PYRO:Server1@localhost:50003", "PYRO:Server2@localhost:50004", "PYRO:Server3@localhost:50005", "PYRO:Server0@localhost:50002"]
                                                                    #hardcoded list of other known RMs
        self.status = "online"
        threading.Thread(target=self.mainLoop).start()              #start the gossip loop for this server

    def createMovies(self):                                         #gathers movie data from movielens and reads into RMs memory
        out = []
        with open("data/movies.csv", "r", encoding="utf8") as fn:
            reader = csv.reader(fn, delimiter=",")
            next(reader)
            for row in reader:
                out.append( row[1] )
        return out

    def createReviews(self):                                        #gathers reviews data from movielens and reads into RMs memory 
        movies = []                                                 #NOTE: This takes around 10 seconds with the provided dataset
        with open("data/movies.csv", "r", encoding="utf8") as fn:
            reader = csv.reader(fn, delimiter=",")
            next(reader)
            for row in reader:
                movies.append( {"id":row[0], "movie":row[1]} )
        out = []
        with open("data/ratings.csv", "r", encoding="utf8") as fn:
            reader = csv.reader(fn, delimiter=",")
            next(reader)
            for row in reader:
                for x in movies:
                    if row[1] == x["id"]:
                        movieTitle = x["movie"]
                        break
                out.append( {"user":row[0], "movie":movieTitle, "rating":row[2], "comment":"no comment added"} )
        return out

        
##    def searchMoviesID(self, ID):
##        for x in self.movies:
##            if x["id"] == ID:
##                return x["movie"]
##
##    def searchMovieMovie(self, movie):
##        for x in self.movies:
##            if x["movie"] == movie:
##                return x["id"]

    def mergeTS(self, a, b):    #merge two timestamps, returning the must up-to-date combination of the two
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out

    def lessThanTS(self, a, b):    #returns true if timestamp a is less than or equal to timestamp b
        for x in range(len(a)):
            if not (a[x] <= b[x]):
                return False
        return True

    def sortLog(self, log):    #use bubble sort to sort the update log
        n = len(log)
        out = list(log)
        print(log)

        for x in range(n):
            for y in range(0, n - x - 1):
                if self.lessThanTS(out[y+1][1], out[y][1]):
                    out[y+1], out[y] = out[y], out[y+1]
        return out
        

    def recieveUpdate(self, uPREV, uID, uOP):                                   #function called when a new update is recieved from a FE
                                                                                #uPREV = Current time stamp of the FE, uID = Unique ID of this update, uOP = the information in this update
        data = self.serverInfo.get(block = True, timeout = None)                #get the thread safe information
        print("Incoming message: ", uPREV, uID, uOP)
        
        if not (uOP[1] in self.movies):                                         #check if the movie exists (movie list cannot be changed)
            self.serverInfo.put(data)                                           #unblock the threadsafe data store and send back to the FE that the update is invalid
            return "Invalid Update Request"
        
        if uID in data["exOps"]:                                                #if the new update's ID is in the executed table (already taken place)
            self.serverInfo.put(data)                                           #unblock the threadsafe data store
            return data["valueTS"]                                              #return the new timestamp to the FE
        
                                                                                #otherwise the update is valid
        data["replicaTS"][self.serverNumber] += 1                               #increment this RMs timestamp in the element corresponding to this RM
        TS = list(uPREV)                                                        #hard copy uPREV 
        TS[self.serverNumber] = data["replicaTS"][self.serverNumber]            #generate a new time stamp, TS, which is equal to uPREV but with the entry corresponding to this
                                                                                #RM replaced with the same entry in this RMs Time Stamp
        
        data["updateLog"].append( [self.serverNumber, TS, uOP, uPREV, uID] )    #add this update to the update log for this RM
        data = self.checkForStable(data)                                        #check if any updates have now become stable, ready for application (the new update may be immediately applied)
        self.serverInfo.put(data)                                               #unblock the threadsafe data store
        return TS                                                               #return TS to FE
    
    @Pyro4.oneway #ensures that a request for this function doesn't wait for a response
    def recieveGossip(self, inLog, inTS, RMNo):                                 #function called whenever gossip is sent to this RM
                                                                                #inLog = Update log of another RM, inTS = Time stamp of the same RM, RMNo = The number of this RM
        
        data = self.serverInfo.get(block = True, timeout = None)                #get the thread safe information

        
        for x in inLog:                                                         #loop through each update in this new log
            if not self.lessThanTS(x[1], data["replicaTS"]):                    #check if the update's TS is greater than the RMs time stamp
                add = True
                for y in data["updateLog"]:                                     #if its a valid update, check if the update is already in this RMs update log, by comparing update IDs
                    if y[4] == x[4]:
                        add = False
                if add:                                                         #if it's acceptable, add it to this RMs update log
                    data["updateLog"].append(x)

        data = self.checkForStable(data)                                        #check for stable updates, as more might have been recieved
        self.serverInfo.put(data)                                               #unblock the threadsafe data store

    def checkForStable(self, data):                                             #function which runs through all updates in the update log, applies any stable ones
        data["updateLog"] = self.sortLog(data["updateLog"])                     #sort the log
        x = 0
        while x < len(data["updateLog"]):
                                                                                #apply the update, merge the time stamp for stable updates in this RM and add to the executed log
            if (not data["updateLog"][x][4] in data["exOps"]) and self.lessThanTS(data["updateLog"][x][3], data["valueTS"]):
                data["value"] = self.updateValue(data["updateLog"][x][2], data["value"])
                data["valueTS"] = self.mergeTS(data["valueTS"], data["updateLog"][x][1])
                data["exOps"].append(data["updateLog"][x][4])
                x = 0                                                           #if an update becomes stable, the whole log must be checked again incase previous updates are now stable
            x += 1
        return data                                                             #return all data to be put back into the queue
                
            
    def updateValue(self, newUpdate, data):                                     #function called to actually apply the information in an update to be stored in memory
        outData = data      
        for x in outData:                                                       #check if the review already exists, if it does update it, if not append it
            if x["user"] == newUpdate[0]:
                if x["movie"] == newUpdate[1]:
                    x["rating"] = newUpdate[2]
                    return outData
        outData.append( {"user":newUpdate[0], "movie":newUpdate[1], "rating":newUpdate[2], "comment":newUpdate[3]} )
        return outData

    def getMovies(self):    #returns full list of movies
        return self.movies

    def checkMovie(self, movie):    #returns true if a movie exists in the data set
        return (movie in self.movies)

    def viewMovieReviews(self, qOP, qPREV):                                     #function to handle a query request for viewing all reviews on a single movie
                                                                                #(all three of these query request functions operate in identical ways, differing slightly in what data is looked up)
                                                                                #qOP = Data for the query request, qPREV = FEs current timestamp
        data = self.serverInfo.get(block = True, timeout = None)
        if not self.lessThanTS(qPREV, data["valueTS"]):                         #check to make sure if this RMs data is at least as up-to-date as the FE accessing it, by comparing timestamps
            self.serverInfo.put(data)                                           #if it's not, inform the FE that it is and unblock the data
            return "Timestamp too new"
        self.serverInfo.put(data)
        reviews = []                                    
        for x in data["value"]:                                                 #loop through data to find all the reviews
            if x["movie"] == qOP:
                reviews.append(x)
        return reviews, data["valueTS"]                                         #return the reviews and the time stamp of the data that the FE just saw

    def viewUserReviews(self, qOP, qPREV):
        data = self.serverInfo.get(block = True, timeout = None)
        if not self.lessThanTS(qPREV, data["valueTS"]):
            self.serverInfo.put(data)
            return "Timestamp too new"
        self.serverInfo.put(data)
        reviews = []
        for x in data["value"]:
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
        return "Review Was Not Found", data["valueTS"]

    def getAverageRating(self, qOP, qPREV):                                     #only difference here is that it calculates a value rather than sending stored data
        data = self.serverInfo.get(block = True, timeout = None)
        if not self.lessThanTS(qPREV, data["valueTS"]):
            self.serverInfo.put(data)
            return "Timestamp too new"
        self.serverInfo.put(data)
        total = 0
        count = 0
        for x in data["value"]:
            if x["movie"] == qOP:
                total += float(x["rating"])
                count += 1
        
        return (total/count) if count else "No Reviews For This Movie" , data["valueTS"]
        
    
    def getStatus(self): #returns status of RM
        return self.status

    def mainLoop(self):                                                         #main loop which handles the gossiping every iteration (set to 5 seconds)
        while True:
            print("Gossip Time: ", time.time(), "Status: ", self.status)
            time.sleep(5)
            self.status = "online"                                              #randomly change the RMs status to simmulate going offline/being busy
            statusChange = random.random()
            if statusChange < 0.1:
                self.status = "offline"
            elif statusChange < 0.3:
                self.status = "overloaded"
            else:                                                               #if its online, then begin this iteration of gossip
                
                data = self.serverInfo.get(block = True, timeout = False)       #get data from threadsafe variable and put it back
                gossipInfo = ( data["replicaTS"], data["updateLog"] )
                self.serverInfo.put(data)
                
                random1, random2 = random.randint(0, 3), random.randint(0, 3)   #pick two random URIs from the list of known URIs for RMs
                URI1 = self.knownRMs[random1]
                URI2 = self.knownRMs[random2]
                
                try:                                                            #try send gossip information to them, but only if they're online too, otherwise catch errors
                    gossipPart = Pyro4.Proxy(self.knownRMs[random1])
                    if gossipPart.getStatus() == "online":
                        gossipPart.recieveGossip(gossipInfo[1], gossipInfo[0], random1)
                    else:
                        print("RM: ", URI1, "is not ready for Gossiping")
                except:
                    print("Error connecting to: ", URI1)
                try:
                    gossipPart = Pyro4.Proxy(self.knownRMs[random2])
                    if gossipPart.getStatus() == "online":
                        gossipPart.recieveGossip(gossipInfo[1], gossipInfo[0], random2)
                    else:
                        print("RM: ", URI1, "is not ready for Gossiping")
                except:
                    print("Error connecting to: ", URI2)
 
            

#set up information for this RM
#calculate portnumber and server name from servernumber and register the server object into the pyro daemon
portNum = 50002 + serverNum
daemon = Pyro4.Daemon(port=portNum)
uri = daemon.register(Server, "Server" + str(serverNum))

print("Server{0}".format(serverNum))
print("URI:", uri)

#put the requestloop into a thread and start it
threading.Thread(target=daemon.requestLoop).start()
#poke the server to wake it
with Pyro4.Proxy(uri) as rm:
    print("Status: {0}".format(rm.getStatus()))

