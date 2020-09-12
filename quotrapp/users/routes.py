from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from quotrapp import db, bcrypt
from quotrapp.models import User, Quote
from quotrapp.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm
from quotrapp.users.utils import save_profile_picture, resize_gif, thumbnails, delete_old_profile_picture, send_reset_email


users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # disable new user registration
        # flash('Sorry, registration is currently unavailable!', 'warning')

        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)

        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!', 'success')

        return redirect(url_for('users_bp.login'))

    return render_template('register.html', title='Register', form=form)


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users_bp.profile'))
        # return redirect(url_for('main_bp.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('users_bp.profile'))
        else:
            flash('Login Unsuccessful! Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_bp.index'))


@users_bp.route('/profile')
@login_required
def profile():
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)

    # check to see if user has any posts to determine button display on profile page
    if Quote.query.filter_by(user_id=current_user.id).count() > 0:
        quotes = True
    else:
        quotes = False

    return render_template('profile.html', title='Profile', image_file=image_file, quotes=quotes, user_id=current_user.id)


@users_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()

    if form.validate_on_submit():
        # if a new picture is uploaded save and update db
        if form.picture.data:
            old_picture_file = current_user.image_file
            picture_file = save_profile_picture(
                form.picture.data, current_app.root_path)
            current_user.image_file = picture_file

            # delete old profile if it's not the default
            if old_picture_file != 'default.jpg':
                delete_old_profile_picture(
                    old_picture_file, current_app.root_path)

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users_bp.profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)

    return render_template('update_profile.html', title='Profile', image_file=image_file, form=form)


# @users_bp.route('/quotes/user/<username>')


@users_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():

    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to help reset your password.', 'warning')
        return redirect(url_for('users_bp.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@users_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    user = User.verify_reset_token(token)

    if not user:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('users_bp.reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        flash(f'Your password has been updated!', 'success')
        return redirect(url_for('users_bp.login'))

    return render_template('reset_password.html', title='Reset Password', form=form)
