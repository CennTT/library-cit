import base64
import datetime
from sqlalchemy import func
from flask import Flask, flash, request, render_template, redirect, url_for, session, Blueprint
from models import PrinterBalanceDeposit, db, User, Book, RatingReview, PrinterBalance, Goods, BorrowingGoods, Rooms, BorrowingRooms, Genre


user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('nonadmin/login.html')
    elif request.method == 'POST':
        nim = request.form['nim']
        password = request.form['password']
        
        user = User.query.filter_by(nomor_induk=nim).first()

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
    
    account_name = session.get('name')
    
    average_ratings = {}
    
    for book in books:
        average_rating = db.session.query(db.func.avg(RatingReview.rating)).filter_by(book_id=book.book_id).scalar()

        average_rating = float(average_rating) if average_rating is not None else 0.0

        average_ratings[book.book_id] = average_rating
        
        genre = Genre.query.get(book.genre_id)  
        genre_name = genre.name if genre else None
        book.genre_name = genre_name 

    return render_template('nonadmin/index.html', books=books, average_ratings=average_ratings, account_name=account_name)

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

    account_name = session.get('name')
    # Query the specific user's review for the book
    user_review = RatingReview.query.filter_by(book_id=id, user_id=user_id).first()
    ratings_reviews = (
    db.session.query(RatingReview, User) 
    .filter_by(book_id=id)
    .join(User)
    .all()
    )
    return render_template('nonadmin/book_details.html', book=book, ratings_reviews=ratings_reviews, average_rate=average_rate, num_reviews=num_reviews, user_review=user_review, account_name=account_name)

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
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    if request.method == 'GET':
        return redirect(url_for('user.book_details', title=title, id=book_id))
    if request.method == 'POST':
        print("sini")
        rating = request.form["rating"]
        review = request.form["review"]
        nim = session.get('nim')
        review = RatingReview(
            id = book_id,
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
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    id = session.get('nim')
    account_name = session.get('name')
    
    user_balance = PrinterBalance.query.filter_by(nomor_induk=id).first()

    deposit_history = PrinterBalanceDeposit.query.filter_by(nomor_induk=id).all()

    return render_template('nonadmin/deposit.html', account_name=account_name, user_balance=user_balance, deposit_history=deposit_history)

@user_bp.route("/top-up", methods=["GET", "POST"])
def top_up():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')

    if not session['logged_in']:
        return render_template('nonadmin/login.html')

    id = session.get('nim')
    print("post")

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

        user_balance = PrinterBalance.query.filter_by(nomor_induk=id).first()
        if user_balance:
            user_balance.balance += int(amount)
            db.session.commit()

        flash('Top-up submitted successfully', 'success')
        return render_template('nonadmin/deposit.html')
    
    else:
        return render_template('nonadmin/deposit.html')
    

@user_bp.route("/goods")
def goods_details():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    goods = Goods.query.all()
    for item in goods:
        if item.image:
            item.image = base64.b64encode(item.image).decode('utf-8')
    account_name = session.get('name')
    return render_template('nonadmin/goods.html', goods=goods, account_name=account_name)

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

    account_name = session.get('name')
    return render_template('nonadmin/rooms.html', rooms=rooms, account_name=account_name)


@user_bp.route("/reserve_room/<int:room_id>", methods=["POST"])
def reserve_room(room_id):
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')

    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    
    user_id = session.get('nim')
    today = datetime.date.today()
    reservation = BorrowingRooms(
        room_id=room_id,
        borrowing_date=today,  
        time_started=start_time,
        time_ended=end_time,
        nomor_induk=user_id,
        status="Reserved", 
    )

    db.session.add(reservation)
    db.session.commit()

    return redirect(url_for('user.rooms_details')) 



@user_bp.route("/procedures")
def procedures():
    if 'logged_in' not in session:
        return render_template('nonadmin/login.html')
    
    if not session['logged_in']:
        return render_template('nonadmin/login.html')
    
    account_name = session.get('name')

    return render_template('nonadmin/procedures.html', account_name=account_name)