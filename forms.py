from flask import flash
from sqlalchemy.exc import IntegrityError
from flask_wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators
from slymoose import db
from slymoose.models import User

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service', [validators.Required()])

    def validate(self):
        from slymoose.views import is_logged_in
        if not Form.validate(self):
            return False
        if is_logged_in():
            return False
        user = User(
            self.username.data,
            self.email.data,
            self.password.data)
        db.session.add(user)
        flash('Thanks for registering')
        try:
            db.session.commit()
        except IntegrityError:
            self.email.errors.append('Email Already in Use')
            flash('Registration failed')
            return False
        return True


class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        user = self.get_user()

        if user is None:
            self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        if not user.active:
            self.username.errors.append('User is not active')
            return False

        self.user = user
        return True

    def get_user(self):
        return User.query.filter(
            User.username == self.username.data).first()
