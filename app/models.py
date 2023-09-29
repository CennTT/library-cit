from flask_sqlalchemy import SQLAlchemy
from app import app

# Initialize the SQLAlchemy extension
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def check_password(self, password):
        return password == self.password