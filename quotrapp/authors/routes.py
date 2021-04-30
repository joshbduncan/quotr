from flask import render_template, abort, Blueprint, current_app
from sqlalchemy import asc, desc
from quotrapp import db
from quotrapp.models import Quote, Author


authors_bp = Blueprint('authors_bp', __name__)


@authors_bp.route('/authors/<author>')
def quotes_by_author(author):
    if '-' in author:
        author = author.replace('-', ' ')
    if '+' in author:
        author = author.replace('+', ' ')

    author = Author.query.filter_by(name=author).first_or_404()

    quotes = Quote.query.filter_by(
        author_id=author.id).order_by(
        desc(Quote.loves_count)).paginate(per_page=current_app.config['POSTS_PER_PAGE'])

    title = f'quotes from {author.name}'

    if quotes.total > 0:
        return render_template('quotes_by_author.html', title=title, quotes=quotes, author=author.name)
    else:
        abort(404)


@authors_bp.route('/authors')
def authors():

    authors = Author.query.order_by(asc(Author.name)).all()

    title = f'all authors'
    return render_template('authors.html', title=title, authors=authors)


@authors_bp.route('/authors/most-loved')
def author_love():
    authors = Author.query.all()

    loves_count = {}

    for author in authors:
        # skip over author "Unknown" since it skews the results
        if author.name == 'Unknown':
            continue
        for quote in author.quotes:
            if quote.author.name not in loves_count:
                loves_count[quote.author.name] = 0
            loves_count[quote.author.name] += quote.loves_count

    sorted_authors = sorted(loves_count.items(),
                            key=lambda item: item[1], reverse=True)

    title = f'most loved authors'
    return render_template('loved_authors.html', title=title, authors=sorted_authors[:10])


# @authors_bp.route('/quotes/popular-authors')
# def popular_authors():
#     pass
#     quotes = Quote.query.order_by(desc(Quote.loves_count)).paginate(
#         per_page=current_app.config['POSTS_PER_PAGE'])

#     title = f'most loved quotes'
#     return render_template('loved_quotes.html', title=title, quotes=quotes)
