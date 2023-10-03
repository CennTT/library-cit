import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
import secrets
from models import db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

db.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('nonadmin/login_nonadmin.html')
    elif request.method == 'POST':
        nim = request.form['nim']
        password = request.form['password']
        
        user = User.query.filter_by(nomor_induk=nim).first()
        print(user)

        if user is None:
            return render_template('nonadmin/login_nonadmin.html', error='Invalid username or password.')

        if user.password != password:
            return render_template('nonadmin/login_nonadmin.html', error='Invalid username or password.')

        session['logged_in'] = True
        session['name'] = user.name
        return redirect(url_for('homepage'))


@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('name', None)
    return redirect(url_for('login'))


@app.route("/")
def homepage():
    if 'logged_in' not in session:
        return render_template('nonadmin/login_nonadmin.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login_nonadmin.html')

    return render_template('nonadmin/index.html')


@app.route("/login-page")
def login_page():
    pass
    