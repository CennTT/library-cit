import base64
from datetime import datetime, timedelta
import os
from sqlalchemy import func
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db, User, AdminUser, Book, BookBorrowing, PrinterBalanceDeposit, RatingReview, PrinterBalance
import app


admin_bp = Blueprint('admin', __name__)

# Login and Logout

@admin_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/admin_login.html')
    elif request.method == 'POST':
        session.clear()
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


# Books

@admin_bp.route('/admin-book')
def admin_book():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')
    
    books = Book.query.all()
        
    return render_template('admin/book_handler.html', books=books)

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
        db.session.delete(book)
        db.session.commit()

    return redirect(url_for('admin.admin_book', title=title, id=book_id))


# Books Borrowing Handler

@admin_bp.route('/admin-borrowing-handler')
def admin_borrow():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')
    
    books_borrowing = BookBorrowing.query.filter(
                        BookBorrowing.return_date.is_(None)
                        ).all()
    users = User.query.all()
    books = Book.query.all()
    available_books = Book.query.filter_by(
                        status="Available"
                        ).all()

    # Calculate and update fines for overdue records
    today = datetime.utcnow().date()
    for borrowing in books_borrowing:
        if borrowing.due_date < today:
            days_overdue = (today - borrowing.due_date).days
            # Calculate fine (2000 per day)
            fine = days_overdue * 2000
            borrowing.fine = fine
            db.session.commit()

    return render_template('admin/borrowing_handler.html', books_borrowing=books_borrowing, users=users, books=books, available_books=available_books)

@admin_bp.route("/add-borrowing-handler", methods=["GET", "POST"])
def add_borrow():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    if request.method == "POST":
        new_nomor_induk = request.form["nim"]
        new_book_id = request.form["book"]
        new_borrowing_date = request.form["borrowing-date"]
        
        # Calculate due date as 2 weeks (14 days) after borrowing date
        borrowing_date = datetime.strptime(new_borrowing_date, '%Y-%m-%d')  # Convert to a datetime object
        new_due_date = borrowing_date + timedelta(days=14)  # Add 14 days to the borrowing date


        new_book_borrowing = BookBorrowing(book_id=new_book_id, borrowing_date=new_borrowing_date, 
                                            due_date=new_due_date, nomor_induk=new_nomor_induk)

        book = Book.query.filter_by(
            book_id=new_book_id
        ).first()

        book.status = "Borrowed"

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
        new_nomor_induk = book_borrowing.nomor_induk
        new_book_id = request.form["book"]
        new_borrowing_date = request.form["borrowing-date"]
        new_due_date = request.form["due-date"]
        new_return_date = request.form["returning-date"]
        new_fine = request.form.get("fine")

        if book_borrowing:

            if new_book_id != book_borrowing.book_id:
                book_borrowing.book.status = "Available"
                book = Book.query.filter_by(
                                    book_id=new_book_id
                                    ).first()
                book.status = "Borrowed"

            book_borrowing.book_id = new_book_id
            book_borrowing.borrowing_date = new_borrowing_date
            book_borrowing.due_date = new_due_date
            book_borrowing.fine = new_fine
            book_borrowing.nomor_induk =new_nomor_induk

            if new_return_date != '':
                book_borrowing.return_date = new_return_date
                book_borrowing.book.status = "Available"

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
        book_borrowing.book.status = "Available"
        db.session.delete(book_borrowing)
        db.session.commit()

    return redirect(url_for('admin.admin_borrow', id=id))


# Deposit

@admin_bp.route('/admin-deposit')
def admin_deposit():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    deposits = PrinterBalanceDeposit.query.filter_by(
        status="Pending"
        ).all()

    return render_template('admin/deposit_handler.html', deposits=deposits) 


# Acc Deposit
@admin_bp.route('/accept-deposit/<int:id>/<path:nomor_induk>')
def accept_deposit(id, nomor_induk):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')
    
    deposit = PrinterBalanceDeposit.query.filter_by(deposit_id=id).first()
    user_balance = PrinterBalance.query.filter_by(nomor_induk=nomor_induk).first()
    
    if not user_balance:
        new_user_balance = PrinterBalance(
            nomor_induk=nomor_induk,
            balance=deposit.deposited_balance
        )
        db.session.add(new_user_balance)
    else:
        user_balance.balance += deposit.deposited_balance
        
    deposit.status = 'Accepted'
    db.session.commit()
    
    return redirect(url_for('admin.admin_deposit'))


# Users

@admin_bp.route('/admin-users')
def admin_users():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    users = User.query.all()

    return render_template('admin/user_handler.html', users=users)

@admin_bp.route("/add-user", methods=["GET", "POST"])
def add_user():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    if request.method == "POST":
        new_nomor_induk = request.form["nim"]
        new_name = request.form["name"]
        new_password = request.form["password"]
        new_email = request.form["email"]

        new_user = User(nomor_induk=new_nomor_induk, name=new_name, password=new_password, 
                        email=new_email)

        db.session.add(new_user)
        db.session.commit()

    return redirect(url_for('admin.admin_users'))

@admin_bp.route("/edit-user/<int:nomor_induk>", methods=["GET", "POST"])
def edit_user(nomor_induk):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    user = User.query.filter_by(
        nomor_induk=nomor_induk
    ).first()

    if request.method == "POST":
        new_nomor_induk = user.nomor_induk
        new_name = request.form["name"]
        new_password = request.form["password"]
        new_email = request.form["email"]

        if user:
            user.nomor_induk = new_nomor_induk
            user.name = new_name
            user.password = new_password
            user.email = new_email
            db.session.commit()

    return redirect(url_for('admin.admin_users', nomor_induk=nomor_induk))

@admin_bp.route("/delete-user/<int:nomor_induk>")
def delete_user(nomor_induk):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    user = User.query.filter_by(
        nomor_induk=nomor_induk
    ).first()

    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('admin.admin_users', nomor_induk=nomor_induk))
