from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80),nullable=False) #make all these fields required in html
    email = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(150),nullable=False)
    phone=db.Column(db.Integer)
    gender=db.Column(db.String(1))
    favourites = db.relationship('Favourite',backref='author',lazy=True)

class Favourite(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    recipe_id=db.Column(db.Integer,nullable=False)
