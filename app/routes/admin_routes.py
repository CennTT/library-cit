import base64
from sqlalchemy import func
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db, User, Book, RatingReview, PrinterBalance, Goods, BorrowingGoods, Rooms, BorrowingRooms


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    # ...
    pass

