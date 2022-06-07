from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
	__tablename__ = "users"
	name = db.Column(db.String, primary_key=True)
	password = db.Column(db.String, nullable=False)
	timestamp = db.Column(db.Integer, nullable=False)

class Book(db.Model):
	__tablename__ = "books"
	isbn = db.Column(db.String, primary_key=True)
	title = db.Column(db.String, nullable=False)
	author = db.Column(db.String, nullable=False)
	year = db.Column(db.Integer, nullable=False)

class Review(db.Model):
	__tablename__ = "reviews"
	isbn = db.Column(db.String, primary_key=True)
	name = db.Column(db.String, primary_key=True)
	rating = db.Column(db.Integer, nullable=False)
	review = db.Column(db.String, nullable=False)

class shelf(db.Model):
	__tablename__ = "shelf"
	isbn = db.Column(db.String, primary_key=True)
	name = db.Column(db.String, primary_key=True)