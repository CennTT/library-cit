import base64
from sqlalchemy import func
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db, User, Book, RatingReview, PrinterBalance, Goods, BorrowingGoods, Rooms, BorrowingRooms


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin-login')
def admin_login():
    return render_template('admin/admin_login.html', error='Invalid username or password.')

@admin_bp.route('/admin-book')
def admin_book():
    return render_template('admin/book_handler.html')


@admin_bp.route('/admin-deposit')
def admin_deposit():
    return render_template('admin/deposit_handler.html')


@admin_bp.route('/admin-goods')
def admin_goods():
    return render_template('admin/goods_rooms_handler.html')

