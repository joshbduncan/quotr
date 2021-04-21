from quotrapp import db
from quotrapp.models import User, Author, Quote, Category, loves


def get_users():
    users = User.query.all()
    for user in users:
        print(user)


def get_quotes():
    quotes = Quote.query.all()
    for quote in quotes:
        print(quote)


def get_authors():
    authors = Author.query.all()
    for author in authors:
        print(author)


def get_categories():
    categories = Category.query.all()
    for category in categories:
        print(category)
