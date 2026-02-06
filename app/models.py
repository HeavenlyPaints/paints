from . import db
from flask_login import UserMixin
from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)  # smallest unit (kobo/cents)
    image = db.Column(db.String(300))
    sold = db.Column(db.Integer, default=0)
    delivered = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(200))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(60))
    items = db.Column(db.Text)  # JSON stringified list
    amount = db.Column(db.Integer)
    paid = db.Column(db.Boolean, default=False)
    delivered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered = db.Column(db.Boolean, default=False)
    terminated = db.Column(db.Boolean, default=False)

class Referer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    whatsapp = db.Column(db.String(50))
    approved = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(64), unique=True, default=lambda: uuid.uuid4().hex[:12])
    earnings = db.Column(db.Integer, default=0)
    referrals_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=True)
    bank = db.relationship('Bank', backref='referers')


class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referer_id = db.Column(db.Integer, db.ForeignKey('referer.id'))
    amount = db.Column(db.Integer)
    account_details = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending/paid/rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    referer = db.relationship('Referer', backref=db.backref('withdrawals', lazy=True))

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    stars = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('ratings', lazy=True))

#class Referer(db.Model):
 #   __tablename__ = 'referer'
  #  __table_args__ = {'extend_existing': True}

#    id = db.Column(db.Integer, primary_key=True)
 #   name = db.Column(db.String(120))
  #  phone = db.Column(db.String(20))
#    whatsapp = db.Column(db.String(20))
 #   email = db.Column(db.String(120))
  #  earnings = db.Column(db.Integer, default=0)
#    referrals_count = db.Column(db.Integer, default=0)
 #   token = db.Column(db.String(100), unique=True)
  #  status = db.Column(db.String(20), default="pending")  # pending, approved, rejected



class Staff(db.Model, UserMixin):
    __tablename__ = 'staffs'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    nationality = db.Column(db.String(50))
    state = db.Column(db.String(50))
    lga = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    nin = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))
    bank_name = db.Column(db.String(50))
    bank_code = db.Column(db.String(10))
    account_number = db.Column(db.String(20))
    account_name = db.Column(db.String(100))
    profile_image = db.Column(db.String(200))
    documents = db.Column(db.String(500))
    documents = db.Column(db.Text)

    verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(50), default="pending")  # pending, approved, rejected
    rejection_reason = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Staff {self.name} ({self.staff_id}) - Verified: {self.verified}>"


class Bank(db.Model):
    __tablename__ = "bank"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=True)
