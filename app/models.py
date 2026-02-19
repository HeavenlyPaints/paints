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
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(300))
    sold = db.Column(db.Integer, default=0)
    delivered = db.Column(db.Integer, default=0)
    product_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)

    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    terminated = db.Column(db.Boolean, default=False)
    amount = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)

    pickup_code = db.Column(db.String(10), unique=True)
    pickup_generated_at = db.Column(db.DateTime)
    delivered = db.Column(db.Boolean, default=False)

    pickup_expired = db.Column(db.Boolean, default=False)
    shifted = db.Column(db.Boolean, default=False)

    ref_token = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    @property
    def is_fully_collected(self):
        return all(
            item.collected_quantity >= item.quantity
            for item in self.order_items
        )



class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    collected_quantity = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship(
        'Order',
         backref=db.backref('order_items', lazy=True, cascade="all, delete-orphan")
     )

    product = db.relationship('Product')

    @property
    def remaining_quantity(self):
        return max(self.quantity - self.collected_quantity, 0)



class Referer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    whatsapp = db.Column(db.String(50))
    token = db.Column(db.String(64), unique=True, default=lambda: uuid.uuid4().hex[:12])
    earnings = db.Column(db.Integer, default=0)
    referrals_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=True)
    bank = db.relationship('Bank', backref='referers')
    bank_name = db.Column(db.String(120))
    account_number = db.Column(db.String(20))
    account_name = db.Column(db.String(120))



class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referer_id = db.Column(db.Integer, db.ForeignKey('referer.id'))
    amount = db.Column(db.Integer)
    account_details = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
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
    documents = db.Column(db.Text)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(50), default="pending")
    rejection_reason = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Staff {self.name} ({self.staff_id}) - Verified: {self.verified}>"


class Bank(db.Model):
    __tablename__ = "bank"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=True)


class ReferralEarning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referer_id = db.Column(db.Integer, db.ForeignKey('referer.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
