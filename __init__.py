from flask import Flask, render_template, url_for

app = Flask(__name__)
app.debug = True

def goodrule(rule):
    return (len((rule.defaults or [])) >= len(rule.arguments))

@app.route("/games")
def games():
    return "games!"

@app.route("/images")
def images():
    return "images!"

@app.route("/videos")
def videos():
    return "videos!"

@app.route("/")
def index():
    rules = app.url_map.iter_rules()
    links = [rule.endpoint for rule in rules if goodrule(rule)]
    return render_template('index.html', links=links)
