import Pyro4
import uuid
import json
import random

@Pyro4.expose
class FrontEnd(object):
    def __init__(self):
        self.knownURIs = ["PYRO:Server0@localhost:50002", "PYRO:Server1@localhost:50003"]
        self.frontEndTS = [0,0,0,0,0]

    def mergeTS(self, a, b):
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out

    def getURI(self):
        return random.choice(self.knownURIs)   

    def recieveUpdate(self, user, movie, rating, comment):
        print("Update Request Recieved")
        ID = uuid.uuid4()
        offlineURIs = []
        
        while True:
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            server = Pyro4.Proxy(URI)
            status = server.getStatus()
            if status == "offline":
                print("offline:", URI)
                offlineURIs.append(URI)
            elif status == "online":   
                response = server.recieveUpdate(self.frontEndTS, ID, (user, movie, rating, comment))
                break
        
        if response == "Invalid Update Request":
            print("Invalid Request")
            return "Invalid Request"
        self.frontEndTS = self.mergeTS(self.frontEndTS, response)
        print("Valid Request")
        print("New TS:", response)
        return "Valid Request"

    def getMovies(self):
        print("Check For Movies")
        server = Pyro4.Proxy(self.getURI())
        response = server.getMovies()
        return response
    
    def checkMovie(self, movie):
        print("Check For Movies")
        server = Pyro4.Proxy(self.getURI())
        response = server.checkMovie(movie)
        return response

    def viewMovieReviews(self, movie):
        print("View Movies Reviews Request Recieved")
        
        offlineURIs = []
        while True:
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            server = Pyro4.Proxy(URI)
            status = server.getStatus()
            if status == "offline":
                print("offline:", URI)
                offlineURIs.append(URI) 
            elif status == "online":
                if not server.checkMovie(movie):
                    return "Movie does not exist"
                response = server.viewMovieReviews(movie, self.frontEndTS)
                if response != "Timestamp too new":
                    print("Response:", response)
                    self.frontEndTS = self.mergeTS(self.frontEndTS, response[1])
                    return response[0]
        

    def viewUserReviews(self, user):
        print("View Users Reviews Request Recieved")

        offlineURIs = []
        while True:
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
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

    def viewSingleReview(self, user, movie):
        print("View Users Reviews Request Recieved")

        offlineURIs = []
        while True:
            URI = self.getURI()
            while (URI in offlineURIs): 
                URI = self.getURI()
            server = Pyro4.Proxy(URI)
            status = server.getStatus()
            if status == "offline":
                print("offline:", URI)
                offlineURIs.append(URI) 
            elif status == "online":
                response = server.viewMovieReviews((user, movie), self.frontEndTS)
                if response != "Timestamp too new":
                    print("Response:", response)
                    self.frontEndTS = self.mergeTS(self.frontEndTS, response[1])
                    return response[0]
        
        
        


daemon = Pyro4.Daemon(port=50001)
uri = daemon.register(FrontEnd, "FrontEnd")


print("Front End URI: ", uri)
daemon.requestLoop()
