from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80),nullable=False) #make all these fields required in html
    email = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(50),nullable=False)
