import secure

from quotrapp import create_app, db
from quotrapp.models import User, Author, Quote, Category, Token


app = create_app()

secure_headers = secure.Secure()


@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db, 'User': User, 'Author': Author, 'Quote': Quote, 'Category': Category, 'Token': Token}

@app.after_request
def set_secure_headers(response):
    secure_headers.framework.flask(response)
    return response