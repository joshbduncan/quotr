from quotrapp import db
from quotrapp.models import User, Author, Quote, Category, loves


def get_all_users():
    users = User.query.all()
    for user in users:
        print(user)


def get_all_quotes():
    quotes = Quote.query.all()
    for quote in quotes:
        print(quote)
