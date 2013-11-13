from slymoose import db

class Categories(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True)
    endpoint = db.Column(db.String(25))
    description = db.Column(db.Text)
    pages = db.relationship('Pages', backref='category', lazy='dynamic')

    def __unicode__(self):
        return self.slug.title()


class Pages(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(25), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id_'))
    content = db.Column(db.Text)

    def __unicode__(self):
        return self.slug.title()


if __name__ == '__main__':
    db.create_all()
