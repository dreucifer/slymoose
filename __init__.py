"""Slymoose website"""
from flask import Flask, render_template, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin

app = Flask('slymoose')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slymoose.db'
app.secret_key = 'super_secret'
db = SQLAlchemy(app)
admin = Admin(app)

import slymoose.views
