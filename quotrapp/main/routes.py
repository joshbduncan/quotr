from flask import render_template, request, Blueprint, current_app
from sqlalchemy import func
from quotrapp.models import Quote, Author


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
@main_bp.route('/index')
def index():
    quote = Quote.query.order_by(func.random()).first()
    return render_template('index.html', quote=quote)


@main_bp.route('/about')
def about():
    return render_template('about.html', title='About')
