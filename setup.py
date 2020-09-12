import csv
import datetime
import getpass
from quotrapp import db, bcrypt
from quotrapp.models import User, Author, Quote, Category, loves


def start():
    # cleanup old db
    db.drop_all()
    print(f'Database tables dropped...')

    # create new db tables
    db.create_all()
    print(f'Database tables created...')
    print('')

    # setup base user
    print('Setup base user for quotes import.')
    username = input('Enter base user username: ')
    email = input('Enter base user email: ')
    password = getpass.getpass('Enter base user password: ')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email,
                password=hashed_password)
    db.session.add(user)
    db.session.commit()
    print('')
    print('Base user added...')
    print('')

    quotes_added = 0

    with open('sample_quotes.csv', newline='') as csvfile:
        quotes = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(quotes):

            # csv format = datetime,category, content,author,loves

            # setup date in correct datetime format
            date = datetime.datetime.strptime(
                row['datetime'], '%Y-%m-%d %H:%M:%S.%f')

            # check to see if category already in db, if not create
            category_check = Category.query.filter_by(
                name=row['category']).first()
            if not category_check:
                category = Category(name=row['category'])
                db.session.add(category)
                db.session.commit()
            else:
                category = category_check

            # check to see if author already in db, if not create
            author_check = Author.query.filter_by(name=row['author']).first()
            if not author_check:
                author = Author(name=row['author'])
                db.session.add(author)
                db.session.commit()
            else:
                author = author_check

            # setup quote for db
            quote = Quote(content=row['content'], date=date, author_id=author.id,
                          user_id=user.id, category_id=category.id)

            # try adding the quote to the db
            try:
                db.session.add(quote)
                db.session.commit()
                quotes_added += 1
            except:
                print(f'Error adding record {i}...')

    print(f'{quotes_added} quotes added to the database.')
