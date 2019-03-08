Some definitions for when reading comments in the code:
    RM : Remote Machine (non-specific reference to any RM)
    FE : Front End (specific as there is only one FE)

To use code:
To run using local hosts, as in each server runs in a seperate process but on the same machine
1) Open all 5 seperate server.py files (0-4) and wait until they have started (may take up to 10 seconds to read data)
2) Once all are ready, it will say the server is online and they should be attempting to gossip with each other, which will be printed on screen.
3) Open the front end, followed by as many clients as you wish
4) You can now test the system using the client interface (it uses the movielens data set but I have also added a movie "Test_Movie_Name" to make testing easier)

Features of the system:
1) From the client interface, users can use the interface to find information that is stored in the database (note that the movie list is constant and not changeable)
2) The system uses a gossip architecture to ensure causal ordering in the system. Gossiping takes place every 5 seconds and each RM sends it's information to two other RMs)
3) The system uses timestamping to monitor non-stable and stable updates made to each RM
4) The front end stores it's own timestamp to make sure it is seeing the correct information when querying the system
5) Sending an update or query request from the client will always result in a response, the FE will keep trying until I goes through
6) For the purpose of this coursework, I have implemented a server "status" value which can either be "online", "overloaded" or "offline". 
These pretend the server is down/unavaible, and prevent the FE from accessing them (the FE will never get information from them), but the server is technically 
still active in Pyro. Each gossip cycle, a server has a 10% chance of going offline and a 20% chance of being overloaded, otherwise it will come back online or remain online.