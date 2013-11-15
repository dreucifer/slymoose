from flask import render_template, redirect, url_for, flash, request
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from slymoose import app, db
from slymoose.models import Pages, Category, User
from slymoose.forms import RegistrationForm, LoginForm


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()


class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()


admin = Admin(app, index_view=AdminView())
admin.add_view(AdminModelView(Pages, db.session))
admin.add_view(AdminModelView(Category, db.session))
admin.add_view(AdminModelView(User, db.session))

def goodrule(rule):
    return (
        len((rule.defaults or [])) >= len(rule.arguments)) and 'admin' not in str(rule) and rule.redirect_to is None


@app.template_global()
def get_links():
    rules = app.url_map.iter_rules()
    return sorted([rule for rule in rules if goodrule(rule)])


@app.template_global()
def get_categories(endpoint):
    return sorted(
        (Category.query.filter(Category.endpoint == endpoint).all()
            or []), key=lambda x: x.slug)


@app.route('/')
def index():
    login = LoginForm()
    return render_template(
        'index.html', title='SlyMoose', login=login)


@app.route('/games/', defaults={'category_name': 'index'})
@app.route('/games/play/<string:game_name>')
@app.route('/games/play/<int:game_id>')
@app.route('/games/<category_name>')
def games(**kwargs):
    login = LoginForm()
    if kwargs:
        category_name = kwargs.get('category_name', None)
        game_id = kwargs.get('game_id', None)
        game_name = kwargs.get('game_name', None)
        if category_name:
            if category_name == 'play':
                return redirect(url_for('games'))
    return render_template('games.html', login=login)


@app.route('/images/')
def images():
    login = LoginForm()
    return render_template('page.html', login=login)


@app.route('/videos/')
def videos():
    login = LoginForm()
    return render_template('page.html', login=login)


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))


@app.route('/login', methods=('GET', 'POST'))
def login():
    login = LoginForm()
    if login.validate_on_submit():
        login_user(login.user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', login=login)


@app.route('/register', methods=('GET', 'POST'))
def register():
    login = LoginForm()
    registration = RegistrationForm()
    if registration.validate_on_submit():
        user = User(
            registration.username.data,
            registration.email.data,
            registration.password.data)
        db.session.add(user)
        flash('Thanks for registering')
        try:
            db.session.commit()
        except IntegrityError:
            registration.email.errors.append('Email Already in Use')
            return render_template('register.html', registration=registration, login=login)
        return redirect(url_for('login'))
    return render_template('register.html', registration=registration, login=login)
