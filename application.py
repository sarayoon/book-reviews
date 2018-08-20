import os
import psycopg2
import requests

from flask import Flask, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# this means you're creating an app with this file
app = Flask(__name__)

try:
    conn = psycopg2.connect(os.environ['DATABASE_CREDENTIALS'])
except:
    print("I am unable to connect to the database")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("layout.html")


@app.route("/login", methods=["GET", "POST"])
def login():
	cur = conn.cursor()
	# log user in
	if request.method == "GET":
			return render_template("login.html")

		# ensure username was submitted
	username = request.form['username']
	password = request.form['password']
	if not username:
			return ("must provide username")
	elif not password:
			return ("must provide password")
	# query database for username
	cur.execute("SELECT * FROM users WHERE username = %s",
	            (request.form['username'],))
	result = cur.fetchall()
	print(result)
	if len(result) != 1 or not check_password_hash(result[0][2], password):
		return ("invalid username or password")

	# remember user session id
	session["user_id"] = result[0][0]

	return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
	cur = conn.cursor()
	# user registers a username
	if request.method == "GET":
		return render_template("register.html")

	cur.execute("SELECT * FROM users where username = %s",
	            (request.form['username'],))
	result = cur.fetchall()
	# make sure user typed in a username

	if not request.form['username']:
		return("please enter a username")
	# make sure user typed in a password
	elif not request.form['password']:
		return("please enter a password")
	# make sure password matches confirm password
	elif not request.form['password'] == request.form['confirmation']:
		return("password and confirmation do not match")
	# ensure username does not exist
	elif len(result) > 0:
		return("username already exists")
	# store it into users table
	hash = generate_password_hash(request.form['password'])
	update = cur.execute(
	    "INSERT INTO users (username, hash) VALUES (%s, %s)", (request.form['username'], hash))
	result = cur.execute(
	    "SELECT * FROM users WHERE username = %s", (request.form['username'],))
	newResult = cur.fetchall()
	print(newResult)
	session["user_id"] = newResult[0][0]
	print(session["user_id"])
	# redirect to /
	return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("logout.html")


@app.route("/search", methods=["GET", "POST"])
def search():
	if request.method == "GET":
		return render_template("search.html")
	cur = conn.cursor()
	var = request.form['bookinfo']
	cur.execute("SELECT * FROM books WHERE (title LIKE %s) OR (author LIKE %s) OR (isbn LIKE %s) OR (year LIKE %s);",
						 ('%' + var + '%', '%' + var + '%', var + '%', var + '%'))
	result = cur.fetchall()
	length = int(len(result))
	print(length)
	print(result)
	return render_template("searchresult.html", result=result, len=length)


@app.route('/book/<int:bookid>', methods=["GET", "POST"])
def book(bookid):
	if request.method == "GET":
		cur = conn.cursor()
		cur.execute("SELECT * FROM books WHERE id = %s", (bookid,))
		result = cur.fetchall()
		isbn = result[0][1]
		apiRating = requests.get("https://www.goodreads.com/book/review_counts.json",
		                         params={"key": "OWAVdV7YOyJ08Kc2G3nuw", "isbns": isbn}).json()
		update = cur.execute("INSERT INTO reviews (books_id, user_id, rating, review) VALUES (%s, %s, %s, %s)", (bookid, session["user_id"], request.form['rating'], request.form['review'])
		cur.execute("SELECT * FROM reviews WHERE books_id = %s", (bookid,))
		reviewResult=cur.fetchall()
		return render_template("bookpage.html", result=result, apiRating=apiRating, reviewResult=reviewResult)

@app.route('/api/<isbn>', methods=["GET"])
def isbnGet(isbn):
		if request.method == "GET":
			cur=conn.cursor()
			cur.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
			result=cur.fetchall()
			isbnInput=isbn
			apiRating=requests.get("https://www.goodreads.com/book/review_counts.json",
			                       params={"key": "OWAVdV7YOyJ08Kc2G3nuw", "isbns": isbnInput}).json()
			return render_template("ispn.html", result=result, apiRating=apiRating)