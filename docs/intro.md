# Abercardsea Solution Documentation
Date: 12-09-2023

Author: Abercardsea

Hello,
Welcome to the Abercardsea Solution Documentation.

the code is structured as follows:
- bidder: the bidder module code that interacts with apis and submittes bids.
- database: all data from the bidder is saved to the database.
- server: This is a front-end 'Flask' server that displays contents of the database. (this only reads form the database and does not interact with the bidder.)

## General Warning and top tips.

This solution is written in python (:<) and uses the requests library to interact with the api. The main bidder is just a python module that can be run from the command line. The server is a flask server that can be run from the command line.
To make changes to the flask server it would be useful for you to first do a flask tutorial or equivalent.

SQL and the database. the sql knowledge you need is quite minimal most are for getting and writing data to the database. Use a database viewer to see the data in the database to test your queries.

## bidder

The main.py file contains the main bidding loop where the process of getting api data and determining bids is done.
this also submits the bids.

the src folder contains the code for the bidder. These are seperted by functionality and api interaction.

## database
The start construction code for the database is in the .sql file. This does not contain all the tables needed, the others are generated when the data is first called from the API.


## server

Some of this is in html, CSS, JS. Some familiarity would be useful.


## How to run the code

### bidder
To run the bidder you need to run the bidder as a module. It will excute the code in the main.py file. this can be done from the root dir as python -m bidder

### Server

This can be rin by stating the flask server from the root dir. I have written a python script to do this for you. This can be run as python start_server.py

### Database

The database is a sqlite database. This is a file that can be opened with a database viewer. I use DB Browser for SQLite. This can be downloaded from https://sqlitebrowser.org/

To create it there is a scrip in the database folder. in this folder the databse will live. The script is called create_db.py. Running this normally should initalise the database. If you want to start again you can delete the database file and run the script again.

## How to test the code

We have used pytest to test part of the code, although not holistic testing it does test some of the code. To run the tests you need to run pytest from the root dir. This will run all the tests in the tests folder.

## Docker

There is a docker file in the root dir. This can be used to build a docker image. This will build the image and run the server. This should be altered to expose a port to allow the webserver to be accessed. Especially when deploying to the web.

### Finally Good Luck!