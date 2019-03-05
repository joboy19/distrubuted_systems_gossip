import Pyro4
import uuid

knownURIs = ["PYRO:Server0@localhost:50002", "PYRO:Server1@localhost:50003"]

frontEndTS = [0,0,0,0,0]

def mergeTS(a, b):
        out = []
        for x in range(len(a)):
            out.append(max(a[x], b[x]))
        return out      
  
server = Pyro4.Proxy(knownURIs[0])
response = server.recieveUpdate(frontEndTS, uuid.uuid4(), ("joe", "spiderman", 5, "was good"))
frontEndTS = mergeTS(response, frontEndTS)

server = Pyro4.Proxy(knownURIs[1])
response = server.recieveUpdate(frontEndTS, uuid.uuid4(), ("joe", "spiderman", 4, "was good"))
frontEndTS = mergeTS(response, frontEndTS)

server = Pyro4.Proxy(knownURIs[0])
response = server.recieveUpdate(frontEndTS, uuid.uuid4(), ("joe2", "spiderman", 1, "was good"))
frontEndTS = mergeTS(response, frontEndTS)

server = Pyro4.Proxy(knownURIs[1])
response = server.recieveUpdate(frontEndTS, uuid.uuid4(), ("joe", "bee movie", 6, "was good"))
frontEndTS = mergeTS(response, frontEndTS)

server = Pyro4.Proxy(knownURIs[0])
response = server.recieveUpdate(frontEndTS, uuid.uuid4(), ("joe", "bee movie", 1, "was good"))
frontEndTS = mergeTS(response, frontEndTS)

print(response)



