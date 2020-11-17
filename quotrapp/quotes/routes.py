from flask import render_template, url_for, flash, redirect, request, abort, Response, Blueprint, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func, asc, desc
from quotrapp import db
from quotrapp.models import Quote, Author, User, Category
from quotrapp.quotes.forms import PostForm, UpdatePostForm


quotes_bp = Blueprint('quotes_bp', __name__)


@quotes_bp.route('/quote/new', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()

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
                      author_id=author.id, user_id=current_user.id, category_id=form.category.data.id)

        db.session.add(quote)
        db.session.commit()
        flash('Your quote has been posted!', 'success')
        return redirect(url_for('quotes_bp.quote', quote_id=quote.id))

    return render_template('post.html', title='New Quote', form=form, js_extras=True, legend='Post Quote', autocomplete_js=True)


@quotes_bp.route('/author/_autocomplete', methods=['GET'])
def author_autocomplete():
    authors = [author.name for author in Author.query.all()]
    return jsonify(authors)


@quotes_bp.route('/quote/<int:quote_id>')
def quote(quote_id):
    # permalink for invidual quotes for sharing
    quote = Quote.query.get_or_404(quote_id)

    return render_template('quote.html', title=f'quote by {quote.author.name}', quote=quote)


def get_categories():
    categories = []
    for category in Category.query.order_by('name'):
        categories.append((str(category.id), category.name))
    return categories


@quotes_bp.route('/quote/<int:quote_id>/update', methods=['GET', 'POST'])
@login_required
def update_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)

    # check to see if post was created by current user before editing
    if quote.user != current_user:
        abort(403)

    form = UpdatePostForm()

    if form.validate_on_submit():
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

        db.session.commit()

        flash('Your quote has been updated!', 'success')
        return redirect(url_for('quotes_bp.quote', quote_id=quote.id))

    elif request.method == 'GET':
        form.quote.data = quote.content
        form.author.data = quote.author.name
        form.category.choices = get_categories()
        form.category.data = str(quote.category.id)

    # test_field = SelectField("Test: ", choices=[(1, "Abc"), (2, "Def")], default=2)

    return render_template('post.html', title='Update Quote', form=form, legend='Update Quote', quote_id=quote_id, autocomplete_js=True)


@quotes_bp.route('/quote/<int:quote_id>/delete', methods=['POST'])
@login_required
def delete_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)

    # check to see if post was created by current user before deleting
    if quote.user != current_user:
        abort(403)

    db.session.delete(quote)
    db.session.commit()

    flash('Your quote has been deleted!', 'success')
    return redirect(url_for('quotes_bp.quotes', username=current_user.username))


@quotes_bp.route('/quotes')
@quotes_bp.route('/quotes/')
def quotes():

    # page = request.args.get('page', 1, type=int)
    # quantity = request.args.get('quantity', 5, type=int)
    # sort = desc if request.args.get('sort', 'asc', type=str) == 'desc' else asc
    # order_by = request.args.get('order_by', 'date', type=str)

    # kwargs = {}
    # title = f'all quotes sorted by {order_by}'

    # if username:
    #     user = User.query.filter_by(username=username).first_or_404()
    #     if user.quotes != []:
    #         kwargs = {'user_id': user.id}
    #         title = f'quotes posted by {user.username}'
    # elif author:
    #     author = Author.query.filter_by(name=author).first_or_404()
    #     if author.quotes != []:
    #         kwargs = {'author_id': author.id}
    #         title = f'quotes from {author.name}'
    # elif category:
    #     category = Category.query.filter_by(name=category).first_or_404()
    #     if category.quotes != []:
    #         kwargs = {'category_id': category.id}
    #         title = f'{category.name} quotes'

    # quotes = Quote.query.filter_by(**kwargs).order_by(sort(getattr(Quote, order_by))).paginate(
    #     page=page, per_page=quantity)

    quantity = 5
    kwargs = {}
    quotes = Quote.query.filter_by().paginate(per_page=quantity)

    title = f'all quotes'

    if quotes.total > 0:
        return render_template('quotes.html', title=title, quotes=quotes)
    else:
        abort(404)


@quotes_bp.route('/quotes/user/<username>')
def quotes_by_user(username):
    quantity = 5
    user = User.query.filter_by(username=username).first_or_404()
    quotes = Quote.query.filter_by(user_id=user.id).paginate(per_page=quantity)

    title = f'quotes posted by {user.username}'

    if quotes.total > 0:
        return render_template('quotes_by_user.html', title=title, quotes=quotes, username=username)
    else:
        abort(404)


@quotes_bp.route('/quotes/author/<author>')
def quotes_by_author(author):
    if '-' in author:
        author = author.replace('-', ' ')

    quantity = 5
    author = Author.query.filter_by(name=author).first_or_404()
    quotes = Quote.query.filter_by(
        author_id=author.id).paginate(per_page=quantity)

    title = f'quotes from {author.name}'

    if quotes.total > 0:
        return render_template('quotes_by_author.html', title=title, quotes=quotes, author=author.name)
    else:
        abort(404)


@quotes_bp.route('/quotes/category/<category>')
def quotes_by_category(category):
    quantity = 5
    category = Category.query.filter_by(name=category).first_or_404()
    quotes = Quote.query.filter_by(
        category_id=category.id).paginate(per_page=quantity)

    title = f'{category.name} quotes'

    if quotes.total > 0:
        return render_template('quotes_by_category.html', title=title, quotes=quotes, category=category.name)
    else:
        abort(404)


@quotes_bp.route('/quote/_loved', methods=['POST'])
@login_required
def loved():
    quote_id = request.form['id']
    action = request.form['action']

    quote = Quote.query.filter_by(id=quote_id).first()
    user = current_user

    if action == 'increase':
        quote.loves.append(user)
        db.session.commit()
    else:
        quote.loves.remove(user)
        db.session.commit()

    return jsonify({'id': quote.id, 'loves': quote.loves.count()})
