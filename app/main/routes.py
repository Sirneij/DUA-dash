from flask import url_for, render_template, request, Blueprint
from flask_login import current_user, login_required
from app.models import User

main = Blueprint('main', __name__)
@main.route('/home')
@login_required
def home():
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profiles/' + current_user.image_file)
        return render_template( 'home.html', title='Home page', image_file=image_file)
    else:
        return render_template( 'home.html', title='Home page')
