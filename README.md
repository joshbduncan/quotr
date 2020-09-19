## To-do's

### DATABASE

- [ ] sorting options
- [ ] quote updated date
- [ ] profile updates date
- [x] implement username urls instead of user id's
- [x] implement author name urls instead of author id's

### FUNCTIONS

- [x] animated gif processor
- [x] csv importer for initial base quotes
- [x] random date generator for sample quotes

### FRONTEND

- [ ] continuious scrolling, lazy loading
- [ ] better buttons# setup database on heroku

    from quotrapp import create_app, db
    from quotrapp.models import User, Author, Quote, Category
    import setup

    app = create_app()
    with app.app_context():
        setup.start()

# flask shell commands

    flask shell

## database

### setup new database from models
    db.create_all()

### drop all tables and start over
    db.drop_all()

### make a new author
    author = Author(name='Author Name')
    db.session.add(author)
    db.session.commit()

### make a new quote using author object
    quote = Quote(text='Quote Text', author_id=author.id, loves=1)
    db.session.add(quote)
    db.session.commit()

### grab all users by username
    user = User.query.filter_by(username='Josh').all()

### grab all quotes form an author
    author = Author.query.get(1)
    a.quotes.all()

### grab all quotes from the database
    quotes = Quote.query.all()

### get all authors in alphabetical order
    Author.query.order_by(Author.name.asc()).all()

### get paginated quotes from db
standard paginate returns 20 results
    
    quotes = Quote.query.paginate()

add per_page option to change

    Quote.query.paginate(per_page=10)

go to next certain page

    Quote.query.paginate(page=2)

limit records and go to next certain page

    Quote.query.paginate(per_page=10, page=2)

get total records

    quotes.total

### get quotes in order
Ascending Order

    from sqlalchemy import desc

    quotes = Quote.query.order_by(Quote.loves).paginate(page=1, per_page=10)

Descending Order

    quotes = Quote.query.order_by(desc(Quote.loves)).paginate(page=1, per_page=10)

### get random quote
    random_quote = Quote.query.order_by(func.random()).first()
