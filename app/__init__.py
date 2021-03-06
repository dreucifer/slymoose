"""Slymoose website"""
from flask import Flask, render_template, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.markdown import Markdown

app = Flask('slymoose')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slymoose.db'
app.secret_key = 'super_secret'
markdown_manager = Markdown(app)
login_manager = LoginManager(app)
db = SQLAlchemy(app)

import views

@login_manager.user_loader
def load_user(userid):
    from slymoose.models import User
    return User.query.get(userid)
