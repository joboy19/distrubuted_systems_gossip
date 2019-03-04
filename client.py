import Pyro4

knownFrontEnds = ["localhost:50001"]
option = input("Would you like to update a movie's review (1) or view a rating (2) ")

if option == "1":
    movie = input("What movie? ")
    rating = input("Give a rating 0-10: ")
    frontEnd = Pyro4.Proxy("pyro:FrontEnd@" + knownFrontEnds[0])
    response = frontEnd.recieveUpdate(movie, int(rating))
    print(response)
    
