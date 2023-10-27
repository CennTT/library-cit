import base64
import datetime
from sqlalchemy import and_, func
from flask import Flask, flash, request, render_template, redirect, url_for, session, Blueprint
from models import BookBorrowing, PrinterBalanceDeposit, db, User, Book, RatingReview, PrinterBalance, Genre

from app import admin_bp


user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('nonadmin/login.html')
    elif request.method == 'POST':
        session.clear()
        nim = request.form['nim']
        password = request.form['password']
        
        user = User.query.filter_by(nomor_induk=nim).first()

        if user is None:
            return render_template('nonadmin/login.html', error='Invalid username or password.')

        if user.password != password:
            return render_template('nonadmin/login.html', error='Invalid username or password.')

        session['user_logged_in'] = True
        session['name'] = user.name
        session['nim'] = nim
        return redirect(url_for('user.homepage'))


@user_bp.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('name', None)
    return redirect(url_for('user.login'))


@user_bp.route("/")
def homepage():
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    books = Book.query.all() 
    genres = Genre.query.all()
    nim = session.get('nim')
    
    account_name = session.get('name')
    
    average_ratings = {}
    
    for book in books:
        average_rating = db.session.query(db.func.avg(RatingReview.rating)).filter_by(book_id=book.book_id).scalar()

        average_rating = float(average_rating) if average_rating is not None else 0.0

        average_ratings[book.book_id] = average_rating
        genre = Genre.query.get(book.genre_id)  
        genre_name = genre.name if genre else None
        book.genre_name = genre_name 
        
    borrowed_books = db.session.query(BookBorrowing, Book.title).join(Book, and_(
                        BookBorrowing.book_id == Book.book_id,
                        BookBorrowing.nomor_induk == nim,
                        BookBorrowing.return_date == None
                        )).all()
    print(borrowed_books)

    return render_template('nonadmin/index.html', books=books, average_ratings=average_ratings, account_name=account_name, genre=genres, borrowed_books=borrowed_books)


@user_bp.route("/search-book", methods=["POST"])
def search_book():
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    book_name = request.form["book_name"]

    if book_name:
        books = Book.query.filter(Book.title.like(f"%{book_name}%")).all()
    else:
        books = []
    genres = Genre.query.all()
    
    account_name = session.get('name')
    
    average_ratings = {}
    
    for book in books:
        average_rating = db.session.query(db.func.avg(RatingReview.rating)).filter_by(book_id=book.book_id).scalar()

        average_rating = float(average_rating) if average_rating is not None else 0.0

        average_ratings[book.book_id] = average_rating
        
        genre = Genre.query.get(book.genre_id)  
        genre_name = genre.name if genre else None
        book.genre_name = genre_name 
        
    return render_template('nonadmin/index.html', books=books, average_ratings=average_ratings, account_name=account_name, genre=genres)


@user_bp.route("/book/<int:genre_id>")
def genre_page(genre_id):
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    books = Book.query.filter_by(genre_id=genre_id) 
    genres = Genre.query.all()
    
    account_name = session.get('name')
    
    average_ratings = {}
    
    for book in books:
        average_rating = db.session.query(db.func.avg(RatingReview.rating)).filter_by(book_id=book.book_id).scalar()

        average_rating = float(average_rating) if average_rating is not None else 0.0

        average_ratings[book.book_id] = average_rating
        
        genre = Genre.query.get(book.genre_id)  
        genre_name = genre.name if genre else None
        book.genre_name = genre_name 
        
        
    return render_template('nonadmin/index.html', books=books, average_ratings=average_ratings, account_name=account_name, genre=genres)


@user_bp.route("/book/<path:title>/<int:id>")
def book_details(title, id):
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
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

    user_id = session.get('nim')
    
    today = datetime.datetime.today()

    two_weeks_later = today + datetime.timedelta(days=14)

    today_str = today.strftime('%Y-%m-%d')
    two_weeks_later_str = two_weeks_later.strftime('%d-%m-%Y')
    
    book_borrowed = (
    BookBorrowing.query
    .filter(
        (BookBorrowing.nomor_induk == user_id) &
        (BookBorrowing.book_id == id)
    )
    .all()
    )

    account_name = session.get('name')
    user_review = RatingReview.query.filter_by(book_id=id, user_id=user_id).first()
    ratings_reviews = (
    db.session.query(RatingReview, User) 
    .filter_by(book_id=id)
    .join(User)
    .all()
    )
    return render_template('nonadmin/book_details.html', book=book, ratings_reviews=ratings_reviews, average_rate=average_rate, num_reviews=num_reviews, user_review=user_review, account_name=account_name, due_date=two_weeks_later_str, book_borrowed=book_borrowed)


@user_bp.route("/borrow/<path:title>/<int:book_id>")
def borrow(title, book_id):
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    user_id = session.get('nim')
    
    borrowing_date = datetime.datetime.today().date()
    due_date = borrowing_date + datetime.timedelta(days=14)

    # Create a new book borrowing record
    new_borrowing = BookBorrowing(
        book_id=book_id,
        borrowing_date=borrowing_date,
        due_date=due_date,
        nomor_induk=user_id
    )
    
    book = Book.query.get(book_id)
    if book:
        book.status = "Borrowed"  

    db.session.add(new_borrowing)
    db.session.commit()
    
    return redirect(url_for("user.book_details", title=title, id=book_id))


@user_bp.route("/edit-review/<path:title>/<int:book_id>", methods=["GET", "POST"])
def edit_review(title, book_id):
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')

    user_review = RatingReview.query.filter_by(
        user_id=session.get('nim'),
        book_id=book_id
    ).first()
    if request.method == 'GET':
        return redirect(url_for('user.book_details', title=title, id=book_id))
    if request.method == "POST":
        new_rating = request.form["rating"]
        new_review = request.form["review"]

        if user_review:
            user_review.rating = new_rating
            user_review.review = new_review
            db.session.commit()

    return redirect(url_for('user.book_details', title=title, id=book_id))

@user_bp.route("/add-review/<path:title>/<int:book_id>", methods=["GET", "POST"])
def add_review(title, book_id):
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    if request.method == 'GET':
        return redirect(url_for('user.book_details', title=title, id=book_id))
    if request.method == 'POST':
        rating = request.form["rating"]
        review = request.form["review"]
        nim = session.get('nim')
        review = RatingReview(
            user_id = nim,
            book_id = book_id,
            rating = rating,
            review = review,
        )
        
        db.session.add(review)
        db.session.commit()

    return redirect(url_for('user.book_details', title=title, id=book_id))

@user_bp.route("/deposit")
def printer_balance():
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    id = session.get('nim')
    account_name = session.get('name')
    
    user_balance = PrinterBalance.query.filter_by(nomor_induk=id).first()
    if user_balance is None:
        user_balance = PrinterBalance
        user_balance.balance = 0 

    deposit_history = PrinterBalanceDeposit.query.filter_by(nomor_induk=id).all()
    if deposit_history:
        for history in deposit_history:
            history.proof = base64.b64encode(history.proof).decode('utf-8')

    return render_template('nonadmin/deposit.html', account_name=account_name, user_balance=user_balance, deposit_history=deposit_history)

@user_bp.route("/top-up", methods=["GET", "POST"])
def top_up():
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')

    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')

    id = session.get('nim')

    if request.method == 'POST':
        amount = request.form.get('amount')
        
        uploaded_file = request.files['input-file']
        file_data = uploaded_file.read() 

        new_deposit = PrinterBalanceDeposit(
            nomor_induk=id,
            deposited_balance=amount,
            proof=file_data,
            status='Pending'
        )

        db.session.add(new_deposit)
        db.session.commit()

        return redirect(url_for("user.printer_balance"))
    
    else:
        return redirect(url_for("user.printer_balance"))
    

@user_bp.route("/procedures")
def procedures():
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    account_name = session.get('name')

    return render_template('nonadmin/procedures.html', account_name=account_name)


@user_bp.route("/show-image/<int:image_id>")
def show_image(image_id):
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')

    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')

    deposit = PrinterBalanceDeposit.query.get(image_id)

    if deposit:
        image_data = base64.b64encode(deposit.proof).decode('utf-8')
    else:
        image_data = None

    return render_template('show_image.html', image_data=image_data)


@user_bp.route("/borrow-book")
def borrow_book():
    if 'user_logged_in' not in session:
        return render_template('nonadmin/login.html')

    if not session['user_logged_in']:
        return render_template('nonadmin/login.html')
    
    nomor_induk = session.get("nim")
    
    account_name = session.get('name')
    
    borrowed_books = (
        db.session.query(Book, BookBorrowing)
        .join(BookBorrowing, Book.book_id == BookBorrowing.book_id)
        .filter(BookBorrowing.nomor_induk == nomor_induk)
        .all()
    )
    
    return render_template('nonadmin/borrowing_book.html', borrowed_books=borrowed_books, account_name=account_name)
