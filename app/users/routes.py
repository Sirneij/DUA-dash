from flask       import url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from app         import db, bcrypt, login_manager
from app.models    import User
from app.users.forms     import LoginForm, RegisterForm, UpdateAccountForm
import os, shutil, re, cgi, json, random, time


users = Blueprint('users', __name__)
# provide login manager with load_user callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# logout route user
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        current_user.about = form.about.data
        user = User(username=current_user.username, firstName=current_user.firstName, email=current_user.email, lastName=current_user.lastName, about=current_user.about, image_file=image_file)
        db.session.commit()

        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
    image_file = url_for('static', filename='profile/' + current_user.image_file)
    return render_template( 'account.html', title='Account details', description='ipNX Dashboard', image_file=image_file, form=form)

# register user
@users.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegisterForm()
    msg = None
    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password, firstName=form.firstName.data, email=form.email.data, lastName=form.lastName.data, about=form.about.data, image_file=form.picture.data)
        user.save()
        msg = 'User created, please <a class="custom-button" href="' + url_for('users.login') + '">login</a>'
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profiles/' + current_user.image_file)
        return render_template( 'register.html', title='Register',form=form, msg=msg, image_file=image_file)
    else:
        return render_template( 'register.html', title='Register',form=form, msg=msg)

#Customer data detailed analysis page.
@users.route('/detailed')
@login_required
def detailed():

    if current_user.is_authenticated:
        image_file = url_for('static', filename='profiles/' + current_user.image_file)
        return render_template( 'detailed.html', title='Data Breakdown', image_file=image_file)
    else:
        return render_template( 'detailed.html', title='Data Breakdown')


# authenticate user
@users.route('/', methods=['GET', 'POST'])
@users.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
