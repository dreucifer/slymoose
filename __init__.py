"""Slymoose website"""
from flask import Flask, render_template, url_for

app = Flask(__name__)

def goodrule(rule):
    return (len((rule.defaults or [])) >= len(rule.arguments))

def getlinks():
    rules = app.url_map.iter_rules()
    return sorted([rule for rule in rules if goodrule(rule)])

@app.route("/")
def index():
    return render_template(
        'index.html', links=getlinks(), title="SlyMoose")

@app.route("/games/")
def games():
    return render_template('page.html', links=getlinks())

@app.route("/images/")
def images():
    return render_template('page.html', links=getlinks())

@app.route("/videos/")
def videos():
    return render_template('page.html', links=getlinks())
