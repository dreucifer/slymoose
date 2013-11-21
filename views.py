from flask import render_template, redirect, url_for, flash, request
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import login_user, logout_user, current_user
from slymoose import app, db
from slymoose.models import Page, Category, User, Article
from slymoose.forms import RegistrationForm, LoginForm


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()

class CategoryModelView(AdminModelView):
    form_create_rules = ('slug', 'endpoint', 'description')
    form_edit_rules = ('slug', 'endpoint', 'description')

class PageModelView(AdminModelView):
    form_create_rules = ('slug', 'category', 'content')
    form_edit_rules = ('slug', 'category', 'content')


class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()


admin = Admin(app, index_view=AdminView())
admin.add_view(PageModelView(Page, db.session))
admin.add_view(CategoryModelView(Category, db.session))
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Article, db.session))

def goodrule(rule):
    response = True
    if not (len((rule.defaults or [])) >= len(rule.arguments)):
        response = False
    if 'admin' in str(rule) or rule.endpoint == 'static':
        response = False
    if rule.redirect_to is not None:
        response = False
    if is_logged_in():
        if rule.endpoint == 'login' or rule.endpoint == 'register':
            response = False
    else:
        if rule.endpoint == 'logout':
            response = False
    return response


@app.template_global()
def get_links():
    rules = app.url_map.iter_rules()
    return sorted([rule for rule in rules if goodrule(rule)])


@app.template_global()
def get_categories(endpoint):
    if endpoint != 'index':
        return sorted(
            (Category.query.filter(Category.endpoint == endpoint).all()
                or []), key=lambda x: x.slug)
    else:
        return sorted(
                (Category.query.filter(Category.endpoint != 'index').all() or []), key=lambda x: x.slug)


@app.template_global()
def is_logged_in():
    return current_user.is_authenticated()


@app.template_global()
def get_page_article(endpoint):
    page = Page.query.filter(Page.slug == endpoint).first()
    if page is None:
        return None, None
    article = page.article
    return page, article


@app.route('/')
def index():
    login_form = LoginForm()
    featured = Page.query.filter(Page.category_id != None).limit(4).all()
    page, article = get_page_article(request.endpoint)
    return render_template('index.html', **locals())


@app.route('/games/')
@app.route('/games/play/<string:game_name>', endpoint='games.play')
@app.route('/games/<category_name>')
def games(**kwargs):
    login_form = LoginForm()
    page, article = get_page_article(request.endpoint)
    game = None
    pages = None
    if kwargs:
        category_name = kwargs.get('category_name', None)
        game_id = kwargs.get('game_id', None)
        game_name = kwargs.get('game_name', None)
        if category_name is not None:
            if category_name == 'play':
                return redirect(url_for('games'))
            category = Category.query.filter(Category.slug == category_name).first()
            pages = category.pages.all()
            try:
                return render_template('game_category.html', **locals())
            except AttributeError:
                pass
        if game_name:
            game = Page.query.filter(Page.slug == game_name).first()
            article = game.article
            return render_template('play_game.html', **locals())
    return render_template('page.html', **locals())


@app.route('/images/', defaults={'category_name': 'index'})
@app.route('/images/view/<string:image_name>', endpoint='images.view')
@app.route('/images/<category_name>')
def images(**kwargs):
    login_form = LoginForm()
    page, article = get_page_article(request.endpoint)
    return render_template('page.html', **locals())


@app.route('/videos/', defaults={'category_name': 'index'})
@app.route('/videos/watch/<string:video_name>', endpoint='videos.watch')
@app.route('/videos/<category_name>')
def videos(**kwargs):
    login_form = LoginForm()
    page, article = get_page_article(request.endpoint)
    return render_template('page.html', **locals())


@app.route('/privacy-policy', endpoint='privacy-policy')
def privacy():
    login_form = LoginForm()
    page, article = get_page_article(request.endpoint)
    return render_template('page.html', **locals())


@app.route('/logout')
def logout():
    if not is_logged_in():
        flash('Not logged in')
    else:
        flash('Logged out successfully')
        logout_user()
    return redirect(url_for('login'))


@app.route('/login', methods=('GET', 'POST'))
def login():
    if is_logged_in():
        flash('Already logged in')
        return redirect(url_for('index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_user(login_form.user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', **locals())


@app.route('/register', methods=('GET', 'POST'))
def register():
    if is_logged_in():
        flash("Can't register twice!")
        return redirect(url_for('index'))
    login_form = LoginForm()
    registration = RegistrationForm()
    if registration.validate_on_submit():
        return redirect(url_for('login'))
    else:
        return render_template('register.html', **locals())
    return render_template('register.html', **locals())
