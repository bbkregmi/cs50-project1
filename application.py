import os
import requests
import sys
from flask import \
    Flask, session, render_template, request, \
    escape, redirect, url_for
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
    sessionUser = session['username']
    if sessionUser is None:
        return render_template('login.html')
    else:
        return redirect(url_for('home'))


@app.route("/login", methods=['POST'])
def login():
    username = escape(request.form['username'])
    password = escape(request.form['password'])
    if len(username) == 0 or len(password) == 0:
        return render_template("login.html", loginFailed=True)

    userQuery = "SELECT * FROM \"user\" WHERE username=:username"
    queryParams = {'username': username}
    userList = db.execute(userQuery, queryParams).fetchall()

    # Query was by username, so we should only have 1 user
    if len(userList) == 0:
        db.commit()
        return render_template("/", loginFailed=True)
    if len(userList) > 1:
        return "Internal Server Error"
    
    user = userList[0]
    print(" %s " % (user.password))
    passwordKey = getencodekey()
    decodedPassword = decrypt(passwordKey, user.password).decode("utf-8")
    print("decoded password: %s" % (decodedPassword))
    if password == decodedPassword:
        db.commit()
        session["username"] = username
        return redirect(url_for('home'))
    else:
        db.commit()
        return render_template("login.html", loginFailed=True)

    
@app.route('/home')
def home():
    username = session["username"]
    if username is None:
        return redirect(url_for('index'))

    return render_template('home.html', username=username)

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/register_user", methods=['POST'])
def register_user():
    username = escape(request.form['username'])
    password = escape(request.form['password'])
    confirmpassword = escape(request.form['confirm-password'])

    if len(username) == 0 or len(password) == 0:
        return render_template("register.html", invalidForm=True)

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
        registerSuccess = True

    db.commit()
    return render_template("register.html", userExists=userExists, registerSuccess=registerSuccess)

@app.route("/search", methods=['GET', 'POST'])
def search():
    query = None
    if request.method == 'POST':
        query = escape(request.form['searchinput'])
    else:
        query = escape(request.args.get('searchinput'))
    if query is None or len(query) == 0:
        redirect(url_for('home'))
    query_string = "SELECT from \"books\" where {} LIKE '{}'"
    isbnQuery = query_string.format("isbn", query)
    titleQuery = query_string.format("title", query)
    authorQuery = query_string.format("author", query)
    print("\nisbn: %s\ntitle: %s\nauthor: %s\n" % (isbnQuery, titleQuery, authorQuery))
    return render_template("results.html", searchVal=query)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('index'))
