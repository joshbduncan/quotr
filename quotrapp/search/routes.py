from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from sqlalchemy import desc
from string import punctuation
from re import escape, sub
from quotrapp import db
from quotrapp.models import Quote, Token
from quotrapp.search.forms import SearchForm
from quotrapp.search.utils import Search, analyze


search_bp = Blueprint('search_bp', __name__)
search_idx = Search()


@search_bp.before_app_first_request
def before_app_first_request():
    quotes = Quote.query.all()
    search_idx.index_tokens(quotes)


@search_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()

    if form.validate_on_submit():
        q = form.q.data.lower()
        return redirect(url_for('search_bp.search_results', q=' '.join(analyze(q))))

    return render_template('search.html', title='Search', form=form)


@search_bp.route('/quotes/search', methods=['GET', 'POST'])
def search_results():

    if request.args:
        q = request.args.get('q')
        # print(f'**** SEARCH QUERY = {q} ****')
        quote_ids = search_idx.search(q)
        # print(f'**** SEARCH QUERY = {quote_ids} ****')

        if quote_ids:
            # add search tokens to db
            tokens = q.split()
            token_objects = []
            for token in tokens:
                if search_idx.search(token):
                    check = Token.query.filter_by(token=token).first()
                    if not check:
                        t = Token(token=token, count=1)
                        token_objects.append(t)
                    else:
                        check.count += 1

            # add all tokens to db at once
            if token_objects:
                db.session.add_all(token_objects)

            db.session.commit()

        # potential future solution to lots of returned results
        # https://stackoverflow.com/questions/444475/sqlalchemy-turning-a-list-of-ids-to-a-list-of-objects/28370511#28370511
        quotes = Quote.query.filter(Quote.id.in_(quote_ids)).paginate(
            per_page=current_app.config['POSTS_PER_PAGE'])

        if quotes.total > 0:
            title = f'search results for "{q}"'
            return render_template('quotes_by_search.html', title=title, tokens=q, quotes=quotes)
        else:
            flash(
                f'sorry, there were no matches for your search', 'warning')
        return redirect(url_for('search_bp.search'))

    form = SearchForm()

    return render_template('search.html', title='Search', form=form)


@search_bp.route('/quotes/search/most-searched', methods=['GET', 'POST'])
def most_searched():

    tokens = Token.query.order_by(desc(Token.count)).limit(100).all()

    title = f'most searched terms'
    return render_template('searched_tokens.html', title=title, tokens=tokens)
