import base64
from sqlalchemy import func
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db, AdminUser, Book, RatingReview, PrinterBalance, Goods, BorrowingGoods, Rooms, BorrowingRooms


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
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin-book')
def admin_book():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    return render_template('admin/book_handler.html')

@admin_bp.route('/admin-deposit')
def admin_deposit():
    return render_template('admin/deposit_handler.html')


@admin_bp.route('/admin-goods')
def admin_goods():
    return render_template('admin/goods_rooms_handler.html')

@admin_bp.route('/admin-users')
def admin_users():
    return render_template('admin/user_handler.html')