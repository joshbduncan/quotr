from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from quotrapp import db, login_manager
from flask_login import UserMixin


loves = db.Table('loves',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('quote_id', db.Integer, db.ForeignKey('quote.id'))
                 )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    quotes = db.relationship('Quote', backref='user', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'User: {self.username} ({self.id}), {self.email}, {self.image_file}'


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    quotes = db.relationship('Quote', backref='author', lazy=True)

    def __repr__(self):
        return f'Author: {self.name} ({self.id})'


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), unique=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # loves = db.Column(db.Integer, nullable=False, default=1)
    loves = db.relationship('User', secondary=loves,
                            backref=db.backref('user_loves'), lazy='dynamic')
    loves_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'), nullable=False)
    author_id = db.Column(db.Integer,
                          db.ForeignKey('author.id'), nullable=False)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'ID: {self.id}, Date: {self.date}, Quote: {self.content[:25].strip()}..., Author: {self.author.name}, Loves: {self.loves.count()}'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    quotes = db.relationship('Quote', backref='category', lazy=True)

    def __repr__(self):
        return f'Category: {self.name} (ID: {self.id})'


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Token: {self.token} (ID: {self.id})'
