import os
import requests, json
import datetime

from flask import Flask, render_template, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return(render_template("index.html", homepage=True))

@app.route("/login", methods=['GET', 'POST'])
def login():
  username = request.form.get("username")
  password = request.form.get("password")
  newusername = request.form.get("newusername")
  newpassword = request.form.get("newpassword")
  if newusername != '' and newpassword != '':
    message="Wecome to the site, glad you were able to create an account!"
    session['logged_in'] = True
    session['username'] = newusername
    db.execute("INSERT INTO login (username, password) VALUES (:username, :password)",
      {"username": newusername, "password": newpassword})
  elif username != '' and password != '':
    # See if user exists.
    rowcount = db.execute("SELECT * FROM login WHERE username = :username and password = :password", {"username": username, "password": password}).rowcount
    if rowcount == 1:
      message="Welcome Back!"
      session['username'] = username
      session['logged_in'] = True
    elif rowcount == 0:
      message="No user found, please try logging in again or create an account"
      session['logged_in'] = False

  #message=""

  # All done commit to database!
  db.commit()
  return(render_template("login.html", message=message))

@app.route("/location")
def location():
    zipcode = request.args.get('zipcode')
    returned_zip_info = db.execute("SELECT * from locations WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()
    lat = returned_zip_info[4]
    long = returned_zip_info[5]
    query = requests.get("https://api.darksky.net/forecast/34b6298c5f0fe67d3cc741bb29bb0e22/42.37,-71.11").json()
    #query = requests.get("https://api.darksky.net/forecast/34b6298c5f0fe67d3cc741bb29bb0e22/{lat},{long}").json()
    temp = query["currently"]["temperature"]
    location_comments = db.execute("SELECT * FROM checkin where zipcode = :zipcode", {"zipcode": zipcode}).fetchall()
    print(f"temp is {temp}")
    return(render_template("location.html", zipcode=zipcode, returned_zip_info=returned_zip_info, lat=lat, long=long, temp=temp, location_comments=location_comments ))

@app.route("/checkin", methods=['POST'])
def checkin():
     print('got in here')
     yourusername = request.form.get("yourusername")
     comment = request.form.get("comment")
     zipcode = request.form.get("zipcode")
     print(comment)
     db.execute("INSERT INTO checkin (zipcode, username, comment) VALUES (:zipcode, :username, :comment)", {"zipcode": zipcode, "username": yourusername, "comment": comment})
     db.commit()
     return(render_template("location.html"))

@app.route("/currenttemp")
def currenttemp():
    # 34b6298c5f0fe67d3cc741bb29bb0e22
    # return "Project 1: TODO"
    query = requests.get("https://api.darksky.net/forecast/34b6298c5f0fe67d3cc741bb29bb0e22/{{lat}},{{long}}").json()
    temp = query["currently"]["temperature"]
    # print(json.dumps(query["currently"], indent = 2))
    # print(f"the temperature is {temp}")
    return(render_template("currenttemp.html", temp=temp))

@app.route("/searchresults", methods=['GET', 'POST'])
def searchresults():
    zipcode = request.form.get("zipcode")
    returned_zip_info = db.execute("SELECT * from locations WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()
    print(returned_zip_info)
    lat = returned_zip_info[4]
    long = returned_zip_info[5]
    query = requests.get("https://api.darksky.net/forecast/34b6298c5f0fe67d3cc741bb29bb0e22/{{lat}},{{long}}").json()
    print(query)
    #print(json.dumps(query["currently"], indent = 2))
    #temp = query["currently"]["temperature"]
    temp = "84";
    print(f"returned zipcode information is {returned_zip_info}")
    return(render_template("searchresults.html", returned_zip_info=returned_zip_info, zipcode=zipcode, temp=temp))

