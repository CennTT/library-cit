import base64
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import secrets
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

db.init_app(app)

@app.errorhandler(404)
def page_not_found(error):
    return "404 Page Not Found", 404

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)