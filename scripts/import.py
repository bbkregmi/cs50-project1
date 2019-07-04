''' 
Imports files in project1/books.csv into the database. This is a separate script
that should be run during setup before doing a flask run
'''
import os
import requests
import sys
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def importBooks():
    # Check to make sure books table is empty
    books = db.execute("SELECT * from \"books\"").fetchall()
    if len(books) != 0:
        raise RuntimeError("Books database already populated")
    
    queryParams = []
    with open('../books.csv', 'r') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        first = True
        for row in readCSV:
            if first == True:
                first = False
            else:
                isbn = row[0]
                title = row[1]
                author = row[2]
                year = int(row[3])
                queryParam = {'isbn': isbn, 'title': title, 'author': author, 'year': year}
                queryParams.append(queryParam) 
    query = "INSERT into \"books\"(isbn, title, author, year) VALUES(:isbn, :title, :author, :year)"
    for queryParam in queryParams:
        db.execute(query, queryParam)
    db.commit()
            

importBooks()