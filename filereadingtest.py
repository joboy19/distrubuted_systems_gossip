import csv

def idToMovie(inID):
    with open("data/movies.csv", "r", encoding="utf8") as fn:
        reader = csv.reader(fn, delimiter=",")
        for row in reader:
            if row[0] == inID:
                return row[1]
    return False

def movieToID(inID):
    with open("data/movies.csv", "r", encoding="utf8") as fn:
        reader = csv.reader(fn, delimiter=",")
        for row in reader:
            if row[1] == inID:
                return row[0]
    return False

