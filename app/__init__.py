import base64
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import secrets
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import Book, db
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/images/book_cover'

db.init_app(app)
migrate = Migrate(app, db)

@app.template_filter('limit_text')
def limit_text(text, max_length):
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length] + '...'

@app.errorhandler(404)
def page_not_found(error):
    return "404 Page Not Found", 404

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route("/add-book", methods=["GET", "POST"])
def add_book():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    if request.method == "POST":
        new_title = request.form["title"]
        uploaded_file = request.files['cover']
        new_writer = request.form.get("author")
        new_description = request.form.get("description")
        new_genre_id = request.form["genre"]


        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(filename))
        uploaded_file.save(file_path)
        new_book_cover = 'images/book_cover/' + filename

        new_book = Book(title=new_title, book_cover=new_book_cover, writer=new_writer, 
                        description=new_description, status="Available", genre_id=new_genre_id)

        db.session.add(new_book)
        db.session.commit()

    return redirect(url_for('admin.admin_book'))


@app.route("/edit-book/<path:title>/<int:book_id>", methods=["GET", "POST"])
def edit_book(title, book_id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if request.method == "POST":
        new_title = request.form.get("title")
        uploaded_file = request.files['cover']
        new_writer = request.form["author"]
        new_description = request.form.get("description")
        if new_description == None:
            new_description = request.form.get("before_description")
        new_genre_id = request.form["genre"]

        if book:
            if uploaded_file:
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(filename))
                uploaded_file.save(file_path)
                new_book_cover = 'images/book_cover/' + filename
                book.book_cover = new_book_cover
            book.title = new_title
            book.book_cover = book.book_cover
            book.writer = new_writer
            book.description = new_description
            book.genre_id = new_genre_id
            db.session.commit()

    return redirect(url_for('admin.admin_book', title=title, id=book_id))