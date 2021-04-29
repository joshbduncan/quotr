from quotrapp import create_app, db
from quotrapp.models import User, Author, Quote, Category, Token


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db, 'User': User, 'Author': Author, 'Quote': Quote, 'Category': Category, 'Token': Token}
