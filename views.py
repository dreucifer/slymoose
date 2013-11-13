from flask import render_template, redirect, url_for
from flask.ext.admin.contrib.sqla import ModelView
from slymoose import app, admin, db
from slymoose.models import Pages, Categories

admin.add_view(ModelView(Pages, db.session))
admin.add_view(ModelView(Categories, db.session))

def goodrule(rule):
    return (len((rule.defaults or [])) >= len(rule.arguments)) and 'admin' not in str(rule)

@app.template_global()
def get_links():
    rules = app.url_map.iter_rules()
    return sorted([rule for rule in rules if goodrule(rule)])

@app.template_global()
def get_categories(endpoint):
    return sorted((Categories.query.filter(Categories.endpoint == endpoint).all() or []), key=lambda x: x.slug)


@app.route('/')
def index():
    return render_template(
        'index.html', title='SlyMoose')

@app.route('/games/', defaults={'category_name': 'index'})
@app.route('/games/play/<string:game_name>')
@app.route('/games/play/<int:game_id>')
@app.route('/games/<category_name>')
def games(**kwargs):
    if kwargs:
        category_name = kwargs.get('category_name', None)
        game_id = kwargs.get('game_id', None)
        game_name = kwargs.get('game_name', None)
        if category_name:
            if category_name == 'play':
                return redirect(url_for('games'))
    return render_template('games.html')

@app.route('/images/')
def images():
    return render_template('page.html')

@app.route('/videos/')
def videos():
    return render_template('page.html')
