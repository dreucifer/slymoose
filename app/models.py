from . import db


class UserMixin(object):
    '''
    This provides default implementations for the methods that Flask-Login
    expects user objects to have.
    '''

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id_)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __eq__(self, other):
        '''
        Checks the equality of two `UserMixin` objects using `get_id`.
        '''
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        '''
        Checks the inequality of two `UserMixin` objects using `get_id`.
        '''
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


class AnonymousUserMixin(object):
    '''
    This is the default object for representing an anonymous user.
    '''
    def is_authenticated(self):
        return False

    def is_active(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return


class Category(db.Model):
    __tablename__ = 'categories'
    id_ = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True)
    endpoint = db.Column(db.String(25))
    description = db.Column(db.Text)
    pages = db.relationship('Page', backref='category', lazy='dynamic')

    def __unicode__(self):
        return self.slug.title()


class Page(db.Model):
    __tablename__ = 'pages'
    id_ = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(25), unique=True)
    thumbnail = db.Column(db.String(75))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id_'))
    content = db.Column(db.Text)

    def __unicode__(self):
        return self.slug.title()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id_ = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(25), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.Text, unique=True)
    active = db.Column(db.Boolean)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.slug = username.lower().replace(' ', '-').rstrip('_')
        self.active = False

    def __repr__(self):
        return "<Users(%s, %s)>" % (self.username, self.email)

    def __unicode__(self):
        return self.username

    def check_password(self, password):
        if self.password == password:
            return True
        return False


class Article(db.Model):
    __tablename__ = 'articles'
    id_ = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id_'))
    page = db.relationship('Page', backref=db.backref('article'), uselist=False)

    seo_title = db.Column(db.String(67))
    seo_description = db.Column(db.String(150))
    seo_keywords = db.Column(db.String(150))

    title = db.Column(db.String(70))
    fold = db.Column(db.Text)
    cut = db.Column(db.Text)

    post_date = db.Column(db.DateTime)

    def __unicode__(self):
        return self.seo_title

    def get_title(self):
        return self.title
