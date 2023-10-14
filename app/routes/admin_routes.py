import base64
from sqlalchemy import func
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db, User, AdminUser, Book, BookBorrowing, PrinterBalanceDeposit, RatingReview, PrinterBalance, Goods, BorrowingGoods, Rooms, BorrowingRooms


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/admin_login.html')
    elif request.method == 'POST':
        nim = request.form['nim']
        password = request.form['password']
    
    admin = AdminUser.query.filter_by(nomor_induk=nim).first()
    print(admin)

    if admin is None:
        return render_template('admin/admin_login.html', error='Invalid username or password.')

    if admin.password != password:
        return render_template('admin/admin_login.html', error='Invalid username or password.')

    session['logged_in'] = True
    session['nim'] = nim
    return redirect(url_for('admin.admin_book'))

@admin_bp.route("/admin-logout")
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin-book')
def admin_book():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')
    
    books = Book.query.all()

    return render_template('admin/book_handler.html', books=books)

@admin_bp.route("/add-book", methods=["GET", "POST"])
def add_book():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    if request.method == "POST":
        new_title = request.form.get("title")
        new_book_cover = request.form.get("cover")
        new_writer = request.form.get("author")
        new_description = request.form.get("description")

        new_book = Book(title=new_title, book_cover=new_book_cover, writer=new_writer, 
                        description=new_description, status="Available")

        db.session.add(new_book)
        db.session.commit()

    return redirect(url_for('admin.admin_book'))

@admin_bp.route("/edit-book/<path:title>/<int:book_id>", methods=["GET", "POST"])
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
        new_book_cover = request.form.get("cover")
        new_writer = request.form.get("author")
        new_description = request.form.get("description")


        if book:
            book.title = new_title
            book.book_cover = new_book_cover
            book.writer = new_writer
            book.description = new_description
            db.session.commit()

    return redirect(url_for('admin.admin_book', title=title, id=book_id))

@admin_bp.route("/delete-book/<path:title>/<int:book_id>")
def delete_book(title, book_id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if book:
        book.delete()
        db.session.commit()

    return redirect(url_for('admin.admin_book', title=title, id=book_id))

@admin_bp.route('/admin-borrowing-handler')
def admin_borrow():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')
    
    books_borrowing = BookBorrowing.query.all()
    # Kalau mau ambil book title, coba {{ books_borrowing.book.title }}

    return render_template('admin/borrowing_handler.html', books_borrowing=books_borrowing)

@admin_bp.route("/add-borrowing-handler", methods=["GET", "POST"])
def add_borrow():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    if request.method == "POST":
        new_nomor_induk = request.form.get("nim")
        new_book_title = request.form.get("book")
        new_borrowing_date = request.form.get("borrowing-date")
        new_due_date = request.form.get("due-date")
        new_return_date = request.form.get("returning-date")
        new_fine = request.form.get("fine")

        book = Book.query.filter(
            Book.title == new_book_title
        ).first()

        if book:
            new_book_id = book.book_id

        new_book_borrowing = BookBorrowing(book_id=new_book_id, borrowing_date=new_borrowing_date, 
                                            due_date=new_due_date, return_date=new_return_date, 
                                            fine=new_fine, nomor_induk=new_nomor_induk)

        db.session.add(new_book_borrowing)
        db.session.commit()

    return redirect(url_for('admin.admin_borrow', id=id))

@admin_bp.route("/edit-borrowing-handler/<int:id>", methods=["GET", "POST"])
def edit_borrow(id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book_borrowing = BookBorrowing.query.filter_by(
        id=id
    ).first()

    if request.method == "POST":
        new_nomor_induk = request.form.get("nim")
        new_book_title = request.form.get("book")
        new_borrowing_date = request.form.get("borrowing-date")
        new_due_date = request.form.get("due-date")
        new_return_date = request.form.get("returning-date")
        new_fine = request.form.get("fine")

        book = Book.query.filter(
            Book.title == new_book_title
        ).first()

        if book:
            new_book_id = book.book_id

        if book_borrowing:
            book_borrowing.book_id = new_book_id
            book_borrowing.borrowing_date = new_borrowing_date
            book_borrowing.due_date = new_due_date
            book_borrowing.return_date = new_return_date
            book_borrowing.fine = new_fine
            book_borrowing.nomor_induk =new_nomor_induk
            db.session.commit()

    return redirect(url_for('admin.admin_borrow', id=id))

@admin_bp.route("/delete-borrowing-handler/<int:id>")
def delete_borrow(id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book_borrowing = BookBorrowing.query.filter_by(
        id=id
    ).first()

    if book_borrowing:
        book_borrowing.delete()
        db.session.commit()

    return redirect(url_for('admin.admin_borrow', id=id))

@admin_bp.route('/admin-deposit')
def admin_deposit():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    deposits = PrinterBalanceDeposit.query.all()

    return render_template('admin/deposit_handler.html', deposits=deposits)

@admin_bp.route('/admin-goods')
def admin_goods():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    goods = Goods.query.all()

    return render_template('admin/goods_rooms_handler.html', goods=goods)

@admin_bp.route('/admin-users')
def admin_users():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    users = User.query.all()

    return render_template('admin/user_handler.html', users=users)