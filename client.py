import Pyro4

frontEndURI = "pyro:FrontEnd@localhost:50001"


def printResponse(response): 
    for x in response:
        print("----------------")
        print("\n".join("{}\t{}".format(k, v) for k, v in x.items()))
    print("----------------")
    
def main():
    while True:
        option = input("""What would you like to do?
1) See all movies (If the list is very big, IDLE wont like it)
2) Check if a movie exists
3) Get all a movies reviews
4) Get average rating of a movie
5) Check your review on a rating
6) Update or add a new rating for a movie
7) See all of your reviews
8) Quit
Enter 1-7: """)
        
        if option == "1":
            frontEnd = Pyro4.Proxy(frontEndURI)
            response = frontEnd.getMovies()
            print(response)

        if option == "2":
            movie = input("Enter Movie: ")
            frontEnd = Pyro4.Proxy(frontEndURI)
            response = frontEnd.checkMovie(movie)
            if response:
                print(movie, "exists!")
            else:
                print(movie, "does not exist")

        if option == "3":
            movie = input("Enter Movie: ")
            frontEnd = Pyro4.Proxy(frontEndURI)
            response = frontEnd.viewMovieReviews(movie)
            if response == "Movie does not exist":
                print("Movie does not exist")
            else:
                printResponse(response)

        if option == "4":
            movie = input("Enter Movie: ")
            frontEnd = Pyro4.Proxy(frontEndURI)
            response = frontEnd.getAverageRating(movie)
            print("Average rating of movie:", response)

        if option == "5":
            user = input("Enter Unique Username: ")
            movie = input("Enter Movie: ")
            frontEnd = Pyro4.Proxy(frontEndURI)
            response = frontEnd.viewSingleReview(user, movie)
            print("\n".join("{}\t{}".format(k, v) for k, v in response.items()))
                
        if option == "6":
            movie = input("Enter Movie: ")
            rating = input("Enter Rating (0-5): ")
            user = input("Enter Unique Username: ")
            comment = input("Enter Comment: ")
            frontEnd = Pyro4.Proxy(frontEndURI)
            response = frontEnd.recieveUpdate(user, movie, int(rating), comment)
            print(response)

        if option == "7":
            user = input("Enter Unique ID: ")
            frontEnd = Pyro4.Proxy(frontEndURI)
            response = frontEnd.viewUserReviews(user)
            print(response)

        if option == "8":
            break
    

main()
