from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    # id (int), name (string), description (string), dateandtime (string)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='user')
    diets = db.relationship('Diet', backref='owner', lazy=True)

class Diet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    # Unique because if you already have, you can edit. '-'
    description = db.Column(db.String(80), nullable=True)
    date = db.Column(db.String(80), nullable=False)
    ondiet = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('diets1', lazy=True))