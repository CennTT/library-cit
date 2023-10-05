import base64
from sqlalchemy import func
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db, User, Book, RatingReview, PrinterBalance, Goods, BorrowingGoods, Rooms, BorrowingRooms


user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
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
        return redirect(url_for('user.homepage'))


@user_bp.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('name', None)
    return redirect(url_for('user.login'))


@user_bp.route("/")
@user_bp.route("/book")
def homepage():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    books = Book.query.all()

    return render_template('nonadmin/index.html', books=books)

@user_bp.route("/book/<path:title>/<int:id>")
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

@user_bp.route("/edit-review/<path:title>/<int:book_id>", methods=["GET", "POST"])
def edit_review(title, book_id):
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')

    user_review = RatingReview.query.filter_by(
        user_id=session.get('nim'),
        book_id=book_id
    ).first()

    if request.method == "POST":
        new_rating = request.form.get("rating")
        new_review = request.form.get("review")

        if user_review:
            user_review.rating = new_rating
            user_review.review = new_review
            db.session.commit()

    return redirect(url_for('user.book_details', title=title, id=book_id))

@user_bp.route("/deposit")
def printer_balance():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    id = session.get('nim')
    
    # printer_balance = PrinterBalance.query.get(id)
    # return render_template('nonadmin/deposit.html', printer_balance=printer_balance)
    return render_template('nonadmin/deposit.html')

@user_bp.route("/goods")
def goods_details():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    goods = Goods.query.all()

    return render_template('nonadmin/goods.html', goods=goods)

@user_bp.route("/rooms")
def rooms_details():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    rooms = Rooms.query.all()
    for room in rooms:
        if room.image:
            room.image = base64.b64encode(room.image).decode('utf-8')

    return render_template('nonadmin/rooms.html', rooms=rooms)

@user_bp.route("/procedures")
def procedures():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')

    return render_template('nonadmin/procedures.html')