import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import secrets
from models import db, User, Book, RatingReview, PrinterBalance

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

db.init_app(app)

@app.errorhandler(404)
def page_not_found(error):
    return "404 Page Not Found", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('nonadmin/login.html')
    elif request.method == 'POST':
        nim = request.form['nim']
        password = request.form['password']
        
        user = User.query.filter_by(nomor_induk=nim).first()
        print(user)

        if user is None:
            return render_template('nonadmin/login.html', error='Invalid username or password.')

        if user.password != password:
            return render_template('nonadmin/login.html', error='Invalid username or password.')

        session['logged_in'] = True
        session['name'] = user.name
        session['nim'] = nim
        return redirect(url_for('homepage'))


@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('name', None)
    return redirect(url_for('login'))


@app.route("/")
@app.route("/book")
def homepage():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    books = Book.query.all()

    return render_template('nonadmin/index.html', books=books)

@app.route("/book/<path:title>/<int:id>")
def book_details(title, id):
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    book = Book.query.get(id)

    if not book:
        return "Book not found", 404

    average_rate, num_reviews = (
        db.session.query(func.avg(RatingReview.rating), func.count(RatingReview.id))
        .filter_by(book_id=id)
        .first()
    )

    if num_reviews is None:
        num_reviews = 0

    average_rate = float(average_rate) if average_rate is not None else 0.0

    # Retrieve the user_id from the session
    user_id = session.get('nim')

    # Query the specific user's review for the book
    user_review = RatingReview.query.filter_by(book_id=id, user_id=user_id).first()

    ratings_reviews = (
    db.session.query(RatingReview, User) 
    .filter_by(book_id=id)
    .join(User)
    .all()
    )
    print(ratings_reviews[1])
    return render_template('nonadmin/book_details.html', book=book, ratings_reviews=ratings_reviews, average_rate=average_rate, num_reviews=num_reviews, user_review=user_review)


@app.route("/edit-review/<path:title>/<int:book_id>", methods=["GET", "POST"])
def edit_review(title, book_id):
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')

    # Get the user's review for the specified book
    user_review = RatingReview.query.filter_by(
        user_id=session.get('nim'),
        book_id=book_id
    ).first()

    if request.method == "POST":
        # Update the review based on the form data
        new_rating = request.form.get("rating")
        new_review = request.form.get("review")

        # Update the review in the database
        if user_review:
            user_review.rating = new_rating
            user_review.review = new_review
            db.session.commit()

    # Redirect back to the book details page
    return redirect(url_for('book_details', title=title, id=book_id))



@app.route("/deposit")
def printer_balance():
    if 'logged_in' not in session:
        return render_template('nonadmin/login_nonadmin.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login_nonadmin.html')
    
    id = session.get('nim')
    
    # printer_balance = PrinterBalance.query.get(id)
    # return render_template('nonadmin/deposit.html', printer_balance=printer_balance)
    return render_template('nonadmin/deposit.html')