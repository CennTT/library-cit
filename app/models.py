from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import LargeBinary
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    nomor_induk = db.Column(db.String(9), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f'<User nomor_induk={self.nomor_induk}>'
    
    
class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    nomor_induk = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<AdminUser nomor_induk={self.nomor_induk}>'
    
    
class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    writer = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(255), nullable=False)
    book_cover = db.Column(db.String(255), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'), nullable=True)

    genre = db.relationship('Genre', backref='books')

    def __repr__(self):
        return f'<Book book_id={self.book_id}>'
    
    
class Genre(db.Model):
    __tablename__ = 'genres'

    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f'<Genre genre_id={self.genre_id} name={self.name}>'
    


class BookBorrowing(db.Model):
    __tablename__ = 'book_borrowings'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    borrowing_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    fine = db.Column(db.Float, nullable=True)
    nomor_induk = db.Column(db.String(9), db.ForeignKey('users.nomor_induk'), nullable=False)

    book = db.relationship('Book', backref='book_borrowings')
    user = db.relationship('User', backref='book_borrowings')
    
    def __repr__(self):
        return f'<BookBorrowing id={self.id}>'
    

class PrinterBalance(db.Model):
    __tablename__ = 'printer_balances'

    nomor_induk = db.Column(db.String(64), db.ForeignKey('users.nomor_induk'), primary_key=True)
    balance = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship('User', backref='printer_balance')

    def __repr__(self):
        return f'<PrinterBalance nomor_induk={self.nomor_induk}>'
    


class PrinterBalanceDeposit(db.Model):
    __tablename__ = 'printer_balance_deposits'

    deposit_id = db.Column(db.Integer, primary_key=True)
    nomor_induk = db.Column(db.String(64), db.ForeignKey('users.nomor_induk'), nullable=False)
    deposited_balance = db.Column(db.Integer, nullable=False)
    proof = db.Column(LargeBinary, nullable=True) 
    status = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='printer_balance_deposits')

    def __repr__(self):
        return f'<PrinterBalanceDeposit deposit_id={self.deposit_id}>'


class RatingReview(db.Model):
    __tablename__ = 'rating_reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(9), db.ForeignKey('users.nomor_induk'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    review = db.Column(db.Text, nullable=True)

    # Define relationships
    user = db.relationship('User', backref='ratings_reviews')
    book = db.relationship('Book', backref='ratings_reviews')

    def __repr__(self):
        return f'<RatingReview id={self.id}>'