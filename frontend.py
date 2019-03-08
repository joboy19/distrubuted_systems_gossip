import Pyro4
import uuid
import json
import random

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")                             #only create a single instance of the FE
class FrontEnd(object):
    def __init__(self): 
        self.knownURIs = ["PYRO:Server0@localhost:50002", "PYRO:Server1@localhost:50003", "PYRO:Server2@localhost:50004", "PYRO:Server3@localhost:50005", "PYRO:Server4@localhost:50006"]#hardcode RM URIs
        self.frontEndTS = [0,0,0,0,0]

    def mergeTS(self, a, b):  #merge two timestamps, returning the must up-to-date combination of the two
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out

    def getURI(self):  #select random URI from list
        return random.choice(self.knownURIs)   

    def recieveUpdate(self, user, movie, rating, comment):          #function called when a client wants to send an update
        print("Update Request Recieved", self.frontEndTS)
        ID = uuid.uuid4()                                           #generate a new, unique ID
        offlineURIs = []
        
        while True:                                                 #randomly try send update request to RMs
                                                                    #if they're offline then try another one, avoiding known-to-be offline RMs
            if len(offlineURIs) == 5:                               #if all offline, then try them all again
                offlineURIs = []                                    #if theyre busy, dont send the update but don't consider it offline
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            try:
                server = Pyro4.Proxy(URI)
                status = server.getStatus()
                if status == "offline":
                    print("offline:", URI)
                    offlineURIs.append(URI)
                elif status == "online":
                    print(self.frontEndTS)                          #once successful, send the update request to the RM and recieve it's response
                    response = server.recieveUpdate(self.frontEndTS, ID, (user, movie, rating, comment))
                    break
            except:
                print("Error connecting to RM with URI:", URI)
        
        if response == "Invalid Update Request":                    #if update was invalid, notify client
            print("Invalid Request")
            return "Invalid Request"
        self.frontEndTS = self.mergeTS(self.frontEndTS, response)   #else, merge the responses time stamp with the FEs time stamp and notify the client it was a success
        print("Valid Request")
        print("New TS:", response, self.frontEndTS)
        return "Valid Request"

    def getMovies(self):            #simple query request for a constant piece of data (movie list), returning to the client
        print("Get All Movies")
        while True:
            URI = self.getURI()
            try:
                server = Pyro4.Proxy(URI)
                response = server.getMovies()
                break
            except:
                print("Error connecting to RM with URI:", URI)
        return response
    
    def checkMovie(self, movie):   #simple query request for a constant piece of data (movie in the movie list), returning to the client
        print("Check For Movies")
        while True:
            URI = self.getURI()
            try:
                server = Pyro4.Proxy(URI)
                response = server.checkMovie(movie)
                break
            except:
                print("Error connecting to RM with URI:", URI)
        return response

    def viewMovieReviews(self, movie):                          #main query request, asking for all reviews for a single movie
        print("View Movies Reviews Request Recieved")
        
        offlineURIs = []
        while True:                                             #randomly try send query request to RMs
                                                                #if they're offline then try another one, avoiding known-to-be offline RMs
            if len(offlineURIs) == 5:                           #if all offline, then try them all again
                offlineURIs = []                                #if theyre busy, dont send the update but don't consider it offline
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            try:
                server = Pyro4.Proxy(URI)
                status = server.getStatus()
                if status == "offline":
                    print("offline:", URI)
                    offlineURIs.append(URI) 
                elif status == "online":
                    if not server.checkMovie(movie):    #check if the movie exists, if it does not, tell the client
                        return "Movie does not exist"
                    response = server.viewMovieReviews(movie, self.frontEndTS)
                    if response != "Timestamp too new": #if the server accepts the time stamp then update FE timestamp and send response to client, otherwise repeat the loop
                        print("Response:", response)
                        self.frontEndTS = self.mergeTS(self.frontEndTS, response[1])
                        return response[0]
            except:
                print("Error connecting to RM with URI:", URI)
        

    def viewUserReviews(self, user):                    #as in the RM, all query function are very simliar, differing only on what data is being sent or being requested
        print("View Users Reviews Request Recieved")

        offlineURIs = []
        while True:
            if len(offlineURIs) == 5:
                offlineURIs = []
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            try:
                server = Pyro4.Proxy(URI)
                status = server.getStatus()
                if status == "offline":
                    print("offline:", URI)
                    offlineURIs.append(URI) 
                elif status == "online":
                    response = server.viewUserReviews(user, self.frontEndTS)
                    if response != "Timestamp too new":
                        print("Response:", response)
                        self.frontEndTS = self.mergeTS(self.frontEndTS, response[1])
                        return response[0]
            except:
                print("Error connecting to RM with URI:", URI)

    def viewSingleReview(self, user, movie):
        print("View Users Reviews Request Recieved")

        offlineURIs = []
        while True:
            if len(offlineURIs) == 5:
                offlineURIs = []
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            try:
                server = Pyro4.Proxy(URI)
                status = server.getStatus()
                if status == "offline":
                    print("offline:", URI)
                    offlineURIs.append(URI) 
                elif status == "online":
                    response = server.viewSingleReview((user, movie), self.frontEndTS)
                    if response != "Timestamp too new":
                        print("Response:", response)
                        self.frontEndTS = self.mergeTS(self.frontEndTS, response[1])
                        return response[0]
            except:
                print("Error connecting to RM with URI:", URI)

    def getAverageRating(self, movie):
        offlineURIs = []
        while True:
            if len(offlineURIs) == 5:
                offlineURIs = []
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            try:
                server = Pyro4.Proxy(URI)
                status = server.getStatus()
                if status == "offline":
                    print("offline:", URI)
                    offlineURIs.append(URI) 
                elif status == "online":
                    response = server.getAverageRating(movie, self.frontEndTS)
                    if response != "Timestamp too new":
                        print("Response:", response)
                        self.frontEndTS = self.mergeTS(self.frontEndTS, response[1])
                        return response[0]
            except:
                print("Error connecting to RM with URI:", URI)
        
        

#initialize the FE object ready for communication and begin loop
daemon = Pyro4.Daemon(port=50001)
uri = daemon.register(FrontEnd, "FrontEnd")


print("Front End URI: ", uri)
daemon.requestLoop()
