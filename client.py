import Pyro4

knownFrontEnds = ["pyro:FrontEnd@localhost:50001"]


def main():
    option = input("""
    What would you like to do?
    1) See all movies
    2) Check if a movie exists
    3) See a movies ratings
    4) Add a rating/Update your rating for a movie

    """)
            

    if option == "4":
        movie = input("Enter Movie: ")
        rating = input("Enter Rating (0-10): ")
        user = input("Enter Unique ID: ")
        comment = input("Enter Comment: ")
        frontEnd = Pyro4.Proxy(knownFrontEnds[0])
        response = frontEnd.recieveUpdate(user, movie, int(rating), comment)
        print(response)
    

frontEnd = Pyro4.Proxy(knownFrontEnds[0])
response = frontEnd.recieveUpdate("joe", "spiderman", 10, "was good")
print(response)
