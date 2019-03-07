import Pyro4

knownFrontEnds = ["pyro:FrontEnd@localhost:50001"]

### TODO ###
# ask user if they want to use 

def printResponse(response):
    try:
        if isinstance(response, list):
            for x in response:
                print("----------------")
                print("\n".join("{}\t{}".format(k, v) for k, v in x.items()))
            return
        print(response)
        return
    except:
        print(reponse)
        return

def main():
    while True:
        option = input("""
        What would you like to do?
        1) See all movies
        2) Check if a movie exists
        3) See a movies ratings
        4) Check your review on a rating
        5) Add a rating/Update your rating for a movie
        6) Quit
        """)
        
        if option == "1":
            frontEnd = Pyro4.Proxy(knownFrontEnds[0])
            response = frontEnd
                
        if option == "4":
            movie = input("Enter Movie: ")
            rating = input("Enter Rating (0-10): ")
            user = input("Enter Unique ID: ")
            comment = input("Enter Comment: ")
            frontEnd = Pyro4.Proxy(knownFrontEnds[0])
            response = frontEnd.recieveUpdate(user, movie, int(rating), comment)
            printResponse(response)

        if option == "6":
            break
    

#frontEnd = Pyro4.Proxy(knownFrontEnds[0])
#response = frontEnd.recieveUpdate("joe", "spiderman", 10, "was good")
#print(response)
