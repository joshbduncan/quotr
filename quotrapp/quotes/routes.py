from flask import render_template, url_for, flash, redirect, request, abort, Response, Blueprint, jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy import func, asc, desc
from quotrapp import db
from quotrapp.models import Quote, Author, User, Category, Token
from quotrapp.quotes.forms import PostForm, SearchForm
from quotrapp.search import Search


quotes_bp = Blueprint('quotes_bp', __name__)
search_idx = Search()


def get_categories():
    categories = []
    for category in Category.query.order_by('name'):
        categories.append(category)
    return categories


def get_category_choices(categories):
    tup_categories = []
    for category in categories:
        tup_categories.append((category.id, category.name))
    return tup_categories


@quotes_bp.before_app_first_request
def before_app_first_request():
    quotes = Quote.query.all()
    search_idx.index_tokens(quotes)
    # print(search_idx.index)


@quotes_bp.route('/quote/new', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    categories = get_categories()
    form.category.choices = get_category_choices(categories)

    # pre-select the uncategorized category as a default
    uncategorized_category_id = Category.query.filter_by(
        name='uncategorized').first().id
    form.category.data = uncategorized_category_id

    # grab authors for autocomplete javascript
    authors = sorted([author.name for author in Author.query.all()])

    if form.validate_on_submit():
        # check to see if author already exists, if not, add them to db
        check = Author.query.filter_by(name=form.author.data).first()
        if not check:
            author = Author(name=form.author.data)
            db.session.add(author)
            db.session.commit()
        else:
            author = check

        quote = Quote(content=form.quote.data,
                      author_id=author.id, user_id=current_user.id, category_id=form.category.data)

        db.session.add(quote)
        db.session.commit()

        # add new quote tokens to search
        search_idx.index_tokens([quote])

        flash('Your quote has been posted!', 'success')
        return redirect(url_for('quotes_bp.quote', quote_id=quote.id))

    return render_template('post.html', title='New Quote', form=form, js_extras=True, legend='Post Quote', authors=authors, autocomplete_js=True)


# @quotes_bp.route('/author/_autocomplete', methods=['GET'])
# def author_autocomplete():
#     authors = sorted([author.name for author in Author.query.all()])
#     return jsonify(authors)


# @quotes_bp.route('/category/_autocomplete', methods=['GET'])
# def category_autocomplete():
#     categories = [category.name for category in Category.query.all()]
#     return jsonify(categories)


@quotes_bp.route('/quote/<int:quote_id>')
def quote(quote_id):
    # permalink for invidual quotes for sharing
    quote = Quote.query.get_or_404(quote_id)

    return render_template('quote.html', title=f'quote by {quote.author.name}', quote=quote)


@quotes_bp.route('/quote/<int:quote_id>/update', methods=['GET', 'POST'])
@login_required
def update_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)

    # check to see if post was created by current user before editing
    if quote.user != current_user:
        abort(403)

    form = PostForm()
    # must stay here so choices validate
    categories = get_categories()
    form.category.choices = get_category_choices(categories)

    if form.validate_on_submit():
        # set previous author for later check of deletion
        prev_author = Author.query.get(quote.author_id)

        # remove all search tokens for this quote
        search_idx.remove_deleted_quote_tokens(quote)

        # check to see if author already exists, if not, add them to db
        check = Author.query.filter_by(name=form.author.data).first()
        if not check:
            author = Author(name=form.author.data)
            db.session.add(author)
            db.session.commit()
        else:
            author = check

        quote.content = form.quote.data
        quote.author_id = author.id
        quote.category_id = form.category.data

        '''
        check to see if authors match after update
        if not check to see if the previous author
        no longer had any quoted stored
        if not, then delete the author from the db
        '''
        if prev_author.id != author.id:
            if len(prev_author.quotes) == 1:
                db.session.delete(prev_author)

        db.session.commit()

        # add updated quote tokens to search
        search_idx.index_tokens([quote])

        # add new quote tokens to search
        search_idx.index_tokens([quote])

        flash('Your quote has been updated!', 'success')
        return redirect(url_for('quotes_bp.quote', quote_id=quote.id))

    elif request.method == 'GET':
        form.quote.data = quote.content
        form.author.data = quote.author.name

        categories = get_categories()
        form.category.choices = get_category_choices(categories)
        form.category.data = quote.category.id

        # grab authors for autocomplete javascript
        authors = sorted([author.name for author in Author.query.all()])

    return render_template('post.html', title='Update Quote', form=form, legend='Update Quote', authors=authors, quote_id=quote_id, autocomplete_js=True)


@quotes_bp.route('/quote/<int:quote_id>/delete', methods=['POST'])
@login_required
def delete_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)

    # check to see if post was created by current user before deleting
    if quote.user != current_user:
        abort(403)

    db.session.delete(quote)

    # check to see if this was the authors only quote
    author = Author.query.get(quote.author_id)
    if len(author.quotes) == 0:
        db.session.delete(author)

    # remove all search tokens for this quote
    search_idx.remove_deleted_quote_tokens(quote)

    db.session.commit()

    flash('Your quote has been deleted!', 'success')
    return redirect(url_for('quotes_bp.quotes', username=current_user.username))


@quotes_bp.route('/quotes')
def quotes():
    quotes = Quote.query.filter_by().paginate(
        per_page=current_app.config['POSTS_PER_PAGE'])

    title = f'all quotes'

    if quotes.total > 0:
        return render_template('quotes.html', title=title, quotes=quotes)
    else:
        abort(404)


@quotes_bp.route('/quotes/user/<username>')
def quotes_by_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    quotes = Quote.query.filter_by(user_id=user.id).paginate(
        per_page=current_app.config['POSTS_PER_PAGE'])

    title = f'quotes posted by {user.username}'

    if quotes.total > 0:
        return render_template('quotes_by_user.html', title=title, quotes=quotes, username=username)
    else:
        abort(404)


@quotes_bp.route('/quotes/author/<author>')
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


@quotes_bp.route('/quotes/categories')
def categories():
    categories = get_categories()
    # TODO add category count

    title = 'Quote Categories'

    return render_template('categories.html', title=title, categories=categories)


@quotes_bp.route('/quotes/category/<category>')
def quotes_by_category(category):
    category = Category.query.filter_by(name=category).first_or_404()
    quotes = Quote.query.filter_by(
        category_id=category.id).paginate(per_page=current_app.config['POSTS_PER_PAGE'])

    title = f'{category.name} quotes'

    if quotes.total > 0:
        return render_template('quotes_by_category.html', title=title, quotes=quotes, category=category.name)
    else:
        abort(404)


@quotes_bp.route('/quotes/most-loved')
def quotes_love():
    quotes = Quote.query.order_by(desc(Quote.loves_count)).paginate(
        per_page=10)

    title = f'most loved quotes'
    return render_template('loved_quotes.html', title=title, quotes=quotes)


@quotes_bp.route('/quote/_loved', methods=['POST'])
@login_required
def loved():
    quote_id = request.form['id']
    action = request.form['action']

    quote = Quote.query.filter_by(id=quote_id).first()
    user = current_user

    if action == 'increase':
        quote.loves.append(user)
        quote.loves_count += 1
        db.session.commit()
    else:
        quote.loves.remove(user)
        quote.loves_count -= 1
        db.session.commit()

    return jsonify({'id': quote.id, 'loves': quote.loves.count()})


@quotes_bp.route('/quotes/most-loved-authors')
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


@quotes_bp.route('/quotes/popular-authors')
def popular_authors():
    quotes = Quote.query.order_by(desc(Quote.loves_count)).paginate(
        per_page=current_app.config['POSTS_PER_PAGE'])

    title = f'most loved quotes'
    return render_template('loved_quotes.html', title=title, quotes=quotes)


@quotes_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()

    # grab the 5 most loved quotes
    quotes = Quote.query.order_by(desc(Quote.loves_count)).paginate(
        per_page=current_app.config['POSTS_PER_PAGE'])

    if form.validate_on_submit():
        q = form.q.data.lower()
        # print(f'**** SEARCH QUERY = {q} ****')

        if quotes.total > 0:
            return redirect(url_for('quotes_bp.search_results', q=q))
        else:
            flash(
                f'sorry, there were no matches for "{q}"', 'warning')
        return redirect(url_for('quotes_bp.search'))

    return render_template('search.html', title='Search', form=form, quotes=quotes)


@quotes_bp.route('/quotes/search', methods=['GET', 'POST'])
def search_results():

    if request.args:
        q = request.args.get('q')
        # print(f'**** SEARCH QUERY = {q} ****')
        quote_ids = search_idx.search(q)
        # print(f'**** SEARCH QUERY = {quote_ids} ****')

        # potential future solution to lots of returned results
        # https://stackoverflow.com/questions/444475/sqlalchemy-turning-a-list-of-ids-to-a-list-of-objects/28370511#28370511
        quotes = Quote.query.filter(Quote.id.in_(quote_ids)).paginate(
            per_page=current_app.config['POSTS_PER_PAGE'])

        if quotes.total > 0:
            # add search tokens to db
            tokens = q.split()
            token_objects = []
            for token in tokens:
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

            title = f'search results for "{q}"'
            return render_template('quotes_by_search.html', title=title, tokens=q, quotes=quotes)
        else:
            flash(
                f'sorry, there were no matches for "{q}"', 'warning')
        return redirect(url_for('quotes_bp.search'))

    form = SearchForm()

    return render_template('search.html', title='Search', form=form)


@quotes_bp.route('/quotes/search/most-searched', methods=['GET', 'POST'])
def most_searched():
    # tokens = db.session.query(Token, func.count(
    #     'token')).group_by('token').all()

    tokens = Token.query.order_by(desc(Token.count)).limit(100).all()

    # TODO make sure the tokens are in desc
    for t in tokens:
        print(t)

    title = f'most searched terms'
    return render_template('searched_tokens.html', title=title, tokens=tokens)
