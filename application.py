import os
import requests
import sys
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from scripts.password_hash import encrypt, decrypt
from scripts.encodekey import getencodekey 

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
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/register_user", methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    confirmpassword = request.form['confirm-password']

    if password != confirmpassword:
        return render_template("register.html", unmatchedPassword="true")

    userExists = None
    registerSuccess = None

    preexisting_user = db.execute("SELECT * FROM \"user\" WHERE username=:val", {'val': username}).fetchall()
    if len(preexisting_user) != 0:
        userExists = True
    else:
        key = getencodekey()
        password_hash = encrypt(key, password)
        query = "INSERT into \"user\"(username, password) VALUES (:username, :password)"
        queryParams = {'username': username, 'password': password_hash}
        db.execute(query, queryParams)
        registerSuccess = True;

    db.commit()
    return render_template("register.html", userExists=userExists, registerSuccess=registerSuccess)

