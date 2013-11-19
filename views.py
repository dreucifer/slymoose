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


class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()


admin = Admin(app, index_view=AdminView())
admin.add_view(AdminModelView(Page, db.session))
admin.add_view(AdminModelView(Category, db.session))
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


@app.route('/')
def index():
    login_form = LoginForm()
    page = Page.query.filter(Page.slug == request.endpoint).first()
    article = page.article[0]
    return render_template('index.html', **locals())


@app.route('/games/')
@app.route('/games/play/<string:game_name>', endpoint='games.play')
@app.route('/games/<category_name>')
def games(**kwargs):
    login_form = LoginForm()
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
            try:
                return render_template('game_category.html', **locals())
            except AttributeError:
                pass
        if game_name:
            game = Page.query.filter(Page.slug == game_name).first()
            article = game.article[0]
            return render_template('play_game.html', **locals())
    return render_template('games.html', **locals())


@app.route('/images/', defaults={'category_name': 'index'})
@app.route('/images/view/<string:image_name>', endpoint='images.view')
@app.route('/images/<category_name>')
def images(**kwargs):
    login_form = LoginForm()
    contents = ''
    return render_template('page.html', **locals())


@app.route('/videos/', defaults={'category_name': 'index'})
@app.route('/videos/watch/<string:video_name>', endpoint='videos.watch')
@app.route('/videos/<category_name>')
def videos(**kwargs):
    login_form = LoginForm()
    contents = ''
    return render_template('page.html', **locals())


@app.route('/privacy-policy', endpoint='privacy-policy')
def privacy():
    contents = """
If you require any more information or have any questions about our privacy policy, please feel free to contact us by email at info@slymoose.com.

At SlyMoose.com, the privacy of our visitors is of extreme importance to us. This privacy policy document outlines the types of personal information is received and collected by SlyMoose.com and how it is used.

### Log Files
Like many other Web sites, SlyMoose.com makes use of log files. The information inside the log files includes internet protocol ( IP ) addresses, type of browser, Internet Service Provider ( ISP ), date/time stamp, referring/exit pages, and number of clicks to analyze trends, administer the site, track user's movement around the site, and gather demographic information. IP addresses, and other such information are not linked to any information that is personally identifiable.

### Cookies and Web Beacons
SlyMoose.com does use cookies to store information about visitors preferences, record user-specific information on which pages the user access or visit, customize Web page content based on visitors browser type or other information that the visitor sends via their browser.
DoubleClick DART Cookie

* Google, as a third party vendor, uses cookies to serve ads on SlyMoose.com.
* Google's use of the DART cookie enables it to serve ads to your users based on their visit to SlyMoose.com and other sites on the Internet.
* Users may opt out of the use of the DART cookie by visiting the Google ad and content network privacy policy at the following URL - http://www.google.com/privacy_ads.html

Some of our advertising partners may use cookies and web beacons on our site. Our advertising partners include .......
Google Adsense

These third-party ad servers or ad networks use technology to the advertisements and links that appear on SlyMoose.com send directly to your browsers. They automatically receive your IP address when this occurs. Other technologies ( such as cookies, JavaScript, or Web Beacons ) may also be used by the third-party ad networks to measure the effectiveness of their advertisements and / or to personalize the advertising content that you see.

SlyMoose.com has no access to or control over these cookies that are used by third-party advertisers.

You should consult the respective privacy policies of these third-party ad servers for more detailed information on their practices as well as for instructions about how to opt-out of certain practices. SlyMoose.com's privacy policy does not apply to, and we cannot control the activities of, such other advertisers or web sites.

If you wish to disable cookies, you may do so through your individual browser options. More detailed information about cookie management with specific web browsers can be found at the browsers' respective websites.
    """
    login_form = LoginForm()
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
