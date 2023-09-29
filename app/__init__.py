from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a Flask application instance
app = Flask(__name__)

# Initialize the SQLAlchemy extension
db = SQLAlchemy(app)