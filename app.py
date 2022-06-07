import os, time, calendar
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session


from models import *

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
url = "postgresql://wyzhnlvbmulfqe:b8ce73f99585a033bfa39e08231c1cde226d40982302d5240f065064912a15b2@ec2-18-233-83-165.compute-1.amazonaws.com:5432/de3ele9n8tv96h"
app.config["SQLALCHEMY_DATABASE_URI"] = url

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def main():
	db.create_all()

with app.app_context():
	main()


def getDetailsFromDatabase():
	data = Users.query.order_by(Users.timestamp).all()
	details = []
	for user in data:
		det = []
		n = user.name
		p = user.password
		t = user.timestamp
		det.append(n)
		det.append(p)
		det.append(t)
		details.append(det)
	return details

def getAllMatches(key, value):
	books = []
	if key == "isbn":
		books = Book.query.filter(Book.isbn.ilike("%" + value + "%")).all()
	elif key == "title":
		books = Book.query.filter(Book.title.ilike("%" + value + "%")).all()
	elif key == "author":
		books = Book.query.filter(Book.author.ilike("%" + value + "%")).all()
	return books

def getMyBooks(name):
	books = []
	bookids = shelf.query.filter(shelf.name == name).all()
	for b in bookids:
		book = Book.query.filter(Book.isbn == b.isbn).first()
		books.append(book)
	return books

x = []

@app.route("/admin")
def admin():
	details = getDetailsFromDatabase()
	return render_template("admin.html", details=details)

@app.route("/")
def index():
	# return render_template("login.html")
	details = getDetailsFromDatabase()
	# print(details)
	return redirect(url_for('hello'))

@app.route("/logout")
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route("/home", methods=["POST", "GET"])
def auth():
	if 'username' in session:
		name = session['username']
		# print("home")
		books=[]
		x.clear()
		if 'keybutton' in request.form:
			key = request.form.get("selector")
			value = request.form.get("searchkey")
			# print(key + " " + value)
			books = getAllMatches(key, value)
			for b in books:
				# print(b.title)
				# print(b.author)
				x.append(b)
			# print("hello")
		# print(books)
		return redirect(url_for('authentication', name=name))
	return redirect(url_for('index'))

@app.route("/shelf/<name>", methods=["POST", "GET"])
def myshelf(name):
	books = getMyBooks(name)
	return render_template("shelf.html", name=name, books=books)

@app.route("/home/<name>", methods=["POST", "GET"])
def authentication(name):
	# print(x)
	if 'add' in request.form:
		item = shelf(isbn=name, name=session['username'])
		print(item)
		db.session.add(item)
		db.session.commit()
	elif 'remove' in request.form:
		shelf.query.filter(shelf.isbn == name, shelf.name == session['username']).delete()
		print("deleted")
		db.session.commit()


	if 'submit-review' in request.form:
		rev = request.form.get("review")
		rat = request.form.get("star")
		print(rev)
		print(rat)
		review = Review(isbn=name, name=session['username'], rating=int(rat), review=rev)
		db.session.add(review)
		db.session.commit()
	details = getDetailsFromDatabase()
	book = Book.query.filter(Book.isbn == name).all()
	# print(book)
	if len(book) != 0:
		b = book[0]
		# print(b.title)
		idNumber = b.isbn
		reviews = Review.query.filter(Review.isbn == idNumber).all()
		booksInShelf = getMyBooks(session['username'])
		params = [False, False]
		if b in booksInShelf:
			params[1] = True
		if session['username'] in (r.name for r in reviews):
			params[0] = True
			return render_template("book.html", book=b, reviews=reviews, name=session['username'], params=params)
		else:
			return render_template("book.html", book=b, reviews=reviews, name=session['username'], params=params)
	elif name not in (item[0] for item in details):
		session.pop('username', None)
		return render_template("register.html", message="User doesn't exist!")
	return render_template("index.html", name=name, books=x)


@app.route("/register", methods=["POST", "GET"])
def hello():
	d = []
	details = getDetailsFromDatabase()
	if 'login' in request.form:
		# print("Login button pressed")
		name = request.form.get("email")
		password = request.form.get("password")
		if (name, password) in ((item[0],item[1]) for item in details):
			# return render_template("index.html", name=name)
			x.clear()
			session['username'] = name
			return redirect(url_for('authentication', name=name))
		elif name in (item[0] for item in details):
			msg = "Wrong password!!"
			return render_template("register.html", message=msg)
		else:
			msg = "User doesn't exist. Please register first."
			return render_template("register.html", message=msg)
	elif 'register' in request.form:
		# print("Register button pressed")
		name = request.form.get("email")
		password = request.form.get("password")
		timestamp = calendar.timegm(time.gmtime())
		if name in (item[0] for item in details):
			msg = "User already registered!!"
			return render_template("register.html", message=msg)
		d.append(name)
		d.append(password)
		d.append(timestamp)
		# print(timestamp)
		user = Users(name=name, password=password, timestamp=timestamp)
		db.session.add(user)
		db.session.commit()

		details.append(d)
		message = name + " is successfully registered!!"
		return render_template("register.html", message=message)
	else:
		msg = "Welcome to Book-Reviews!"
		return render_template("register.html", message=msg)
