from . import db

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80),nullable=False) #make all these fields required in html
    email = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(50),nullable=False)
