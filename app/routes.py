import uuid
from functools import wraps
import random
import string
import requests
from .utils import generate_pickup_code
import secrets
from .models import Staff, Task
from jinja2 import TemplateNotFound
from flask import render_template, session, abort
from flask_login import logout_user, login_required
from sqlalchemy.exc import IntegrityError
from flask import send_file, abort, current_app
import io
from twilio.rest import Client
from threading import Thread
import os
from PIL import Image
from .models import OrderItem
from .models import BiometricCredential
from .models import SiteFeedback
from app.models import Bank
import zipfile
from io import BytesIO
import csv
from flask import Response
from app import db
import os
from flask import current_app
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
from . import db, login_manager
from .models import Coupon
from .models import Subscriber
from .models import Admin, Product, Order, Referer, Withdrawal, Rating
from .forms import AdminLoginForm, ProductForm, RefererApplyForm, CheckoutForm, WithdrawalForm, ChangeAdminForm
from .utils import initialize_paystack, verify_paystack_transaction, validate_paystack_webhook, send_email
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from cloudinary.uploader import upload
from flask import session,  abort
from app.models import Staff
import time
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from .utils import save_base64_image
from webauthn import (
    generate_registration_options, 
    verify_registration_response,
    generate_authentication_options, 
    verify_authentication_response,
    options_to_json
)
from webauthn.helpers.structs import PublicKeyCredentialDescriptor
import base64

RP_ID = os.environ.get("RP_ID", "localhost") 
RP_NAME = "Heavenly Paint Limited"
EXPECTED_ORIGIN = f"https://{RP_ID}" if RP_ID != "localhost" else "http://localhost:5000"
from .utils import (
    initialize_paystack,
    verify_paystack_transaction,
    validate_paystack_webhook,
    send_email,
    save_base64_image,
    save_multiple_files
)
from flask import Blueprint

bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@bp.context_processor
def inject_site_settings():
    from app.models import SiteSettings
    return dict(SiteSettings=SiteSettings)

from threading import Thread
from flask_mailman import EmailMessage

def send_async_email(app, msg):
    with app.app_context():
        msg.send()

from flask import render_template

def send_welcome_email(user_email, user_name, user_role):

    html_content = render_template('emails/welcome_staff.html',
                                   name=user_name,
                                   role=user_role)
    subject = "Application Received - Heavenly Paint Limited"
    msg = EmailMessage(
        subject,
        html_content,
        to=[user_email]
    )
    msg.content_subtype = "html"
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
def send_status_email(user_email, user_name, status, reason=None):
    html_content = render_template('emails/staff_status.html',
                                   name=user_name,
                                   status=status,
                                   reason=reason)
    subject = f"Heavenly Paint Limited - Account {status.title()}"
    msg = EmailMessage(subject, html_content, to=[user_email])
    msg.content_subtype = "html"
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
def send_task_email(user_email, user_name, task_title, task_desc, task_link):
    html_content = render_template('emails/new_task.html',
                                   name=user_name,
                                   task_title=task_title,
                                   task_desc=task_desc,
                                   task_link=task_link)
    subject = f"New Task Assigned: {task_title}"
    msg = EmailMessage(subject, html_content, to=[user_email])
    msg.content_subtype = "html"
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_async_twilio(client, from_number, to_number, body):
    try:
        client.messages.create(
            from_=f"whatsapp:{from_number}",
            body=body,
            to=f"whatsapp:{to_number}"
        )
    except Exception as e:
        print(f"Twilio WhatsApp Error: {e}")

def send_async_twilio(client, from_number, to_number, body):
    try:
        client.messages.create(
            from_=f"whatsapp:{from_number}",
            body=body,
            to=f"whatsapp:{to_number}"
        )
    except Exception as e:
        print(f"Twilio WhatsApp Error: {e}")

def send_whatsapp_welcome(phone_number, name):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')
    
    if not all([account_sid, auth_token, from_number]):
        print("Credentials retrieval error!")
        return

    client = Client(account_sid, auth_token)

    clean_phone = phone_number.replace(" ", "")
    if clean_phone.startswith("0"):
        clean_phone = "+234" + clean_phone[1:]
    elif not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    body = f"Hello {name}! 🎉\n\nWelcome to the Heavenly Paint Limited Referral Program. We are thrilled to have you.\n\nColor your world with Shree."
    Thread(target=send_async_twilio, args=(client, from_number, clean_phone, body)).start()

def send_whatsapp_admin_alert(referer_name, referer_phone):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')
    admin_number = os.environ.get('ADMIN_WHATSAPP_NUMBER') 

    if not all([account_sid, auth_token, from_number, admin_number]):
        print("Missing Twilio credentials or Admin Number.")
        return

    client = Client(account_sid, auth_token)
    body = f"🚨 *New Referrer Application*\n\nName: {referer_name}\nPhone: {referer_phone}\n\nLog in to the Heavenly Paint dashboard to approve them."
    Thread(target=send_async_twilio, args=(client, from_number, admin_number, body)).start()

def notify_referer(referer, action, reason=None, amount=None):
    """
    Centralized helper to send branded emails to referrers based on their actions.
    """
    from flask import render_template, url_for, current_app
    
    if not hasattr(referer, 'email') or not referer.email:
        print(f"Skipping email: No email address for referer {referer.name}")
        return 

    if action == "pending":
        subject = "Application Received - Heavenly Paint Limited"
        template = 'emails/referer_pending.html'
        
    elif action == "approved":
        subject = "Your Account is Approved! 🎉"
        template = 'emails/referer_approved.html'
        
    elif action == "rejected":
        subject = "Update on your Application"
        template = 'emails/referer_rejected.html'
        
    elif action == "withdrawal_request":
        subject = "Withdrawal Request Received"
        html_body = f"<h2>Withdrawal Initiated</h2><p>Hello {referer.name}, we have received your request to withdraw ₦{amount:,.2f}. It is currently being processed.</p>"
        send_email(subject, [referer.email], html_body)
        return

    login_link = url_for('main.referer_login', _external=True)
    html_body = render_template(template, name=referer.name, login_link=login_link, reason=reason)
    send_email(subject, [referer.email], html_body)

def create_paystack_recipient(name, account_number, bank_code):
    """Generates a recipient code for the referrer's bank account."""
    url = "https://api.paystack.co/transferrecipient"
    headers = {
        "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "nuban", "name": name,
        "account_number": account_number, "bank_code": bank_code, "currency": "NGN"
    }
    try:
        res = requests.post(url, headers=headers, json=payload).json()
        if res.get("status"): return res["data"]["recipient_code"]
    except Exception as e: print(f"Paystack Recipient Error: {e}")
    return None

def initiate_paystack_transfer(amount_naira, recipient_code, reason="Referral Payout"):
    """Deducts from your Paystack balance and sends to the recipient."""
    url = "https://api.paystack.co/transfer"
    headers = {
        "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "source": "balance", 
        "amount": int(float(amount_naira) * 100),
        "recipient": recipient_code,
        "reason": reason
    }
    try:
        return requests.post(url, headers=headers, json=payload).json()
    except Exception as e:
        return {"status": False, "message": "API Connection Error"}
def fetch_paystack_bank_code(bank_name):
    """Fetches the official bank code from Paystack based on a text name."""
    url = "https://api.paystack.co/bank"
    headers = {"Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None

        banks = resp.json().get('data', [])
        search_term = bank_name.lower().strip()

        if search_term == "opay": search_term = "paycom"
        if "gtb" in search_term: search_term = "guaranty"
        if "first bank" in search_term: search_term = "first bank of nigeria"

        for b in banks:
            if search_term in b['name'].lower():
                return b['code']
    except Exception:
        return None

    return None
@bp.route("/")
def index():
    from app.models import Product, Catalog
    try:
        products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
    except Exception:
        db.session.rollback()
        products = Product.query.order_by(Product.created_at.desc()).all()

    total_ordered = db.session.query(func.sum(Product.sold)).scalar() or 0
    total_delivered = db.session.query(func.sum(Product.delivered)).scalar() or 0
    featured_projects = Catalog.query.filter_by(show_on_home=True).order_by(Catalog.created_at.desc()).all()

    return render_template(
        "index.html",
        products=products,
        featured_projects=featured_projects,
        total_ordered=total_ordered,
        total_delivered=total_delivered,
        paystack_public=current_app.config.get("PAYSTACK_PUBLIC"),
        current_year=datetime.now().year
    )
@bp.route('/force-upgrade-db')
def force_upgrade_db():
    from flask_migrate import upgrade
    try:
        upgrade()
        return "Database upgraded successfully! You can now log in."
    except Exception as e:
        return f"Error upgrading database: {str(e)}"

def staff_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            staff_id = session.get('staff_id')
            if not staff_id:
                flash("Please log in first.", "warning")
                return redirect(url_for('main.staff_way'))
            staff = Staff.query.get(staff_id)
            if not staff:
                flash("Staff not found.", "danger")
                return redirect(url_for('main.staff_way'))
            if role and staff.role.lower() != role.lower():
                flash("Access denied.", "danger")
                return redirect(url_for('main.staff_hood'))
            return f(*args, staff=staff, **kwargs)
        return wrapper
    return decorator

@bp.route("/product/<int:pid>")
def product(pid):
    p = Product.query.get_or_404(pid)
    return render_template("product.html", product=p)

@bp.route("/rate", methods=["POST"])
def rate_product():
    data = request.get_json(force=True)
    product_id = data.get("product_id")
    stars = data.get("stars")
    comment = data.get("comment")
    order_ref = data.get("order_ref")
    if not product_id or not stars:
        return jsonify({"status": False, "message": "product_id and stars required"}), 400
    try:
        product_id = int(product_id); stars = int(stars)
    except:
        return jsonify({"status": False, "message": "invalid types"}), 400
    if stars < 1 or stars > 5:
        return jsonify({"status": False, "message": "stars must be 1-5"}), 400
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"status": False, "message": "product not found"}), 404
    order_id = None
    if order_ref:
        o = Order.query.filter_by(reference=order_ref).first()
        if o and o.delivered:
            order_id = o.id
        else:
            return jsonify({"status": False, "message": "Order not delivered or invalid"}), 400
    rating = Rating(product_id=product_id, stars=stars, comment=comment, order_id=order_id)
    db.session.add(rating)
    db.session.commit()
    summary = compute_ratings_summary(product_id)
    return jsonify({"status": True, "message": "saved", "summary": summary}), 201

@bp.route("/ratings-summary")
def ratings_summary():
    pid = request.args.get("product_id", type=int)
    if not pid:
        return jsonify({"status": False, "message": "product_id required"}), 400
    product = Product.query.get(pid)
    if not product:
        return jsonify({"status": False, "message": "product not found"}), 404
    summary = compute_ratings_summary(pid)
    return jsonify({"status": True, "summary": summary})

def compute_ratings_summary(product_id):
    counts = db.session.query(Rating.stars, func.count(Rating.id)).filter(Rating.product_id == product_id).group_by(Rating.stars).all()
    counts_map = {s: c for s, c in counts}
    values = [int(counts_map.get(i, 0)) for i in range(1,6)]
    total = sum(values)
    average = round(sum((i * values[i-1]) for i in range(1,6)) / total, 2) if total else 0.0
    labels = [f"{i}★" for i in range(1,6)]
    return {"product_id": product_id, "total": total, "average": average, "labels": labels, "values": values}

def _get_cart():
    return session.get('cart', [])

def _save_cart(cart):
    session['cart'] = cart


@bp.route("/cart/add", methods=["POST"])
def cart_add():
    payload = request.get_json(force=True)
    pid = int(payload.get("product_id"))
    
    try:
        qty = float(payload.get("qty", 1.0))
    except ValueError:
        qty = 1.0

    color_name = payload.get("color_name")
    color_hex = payload.get("color_hex")
    unit = payload.get("unit", "buckets").lower()
    p = Product.query.get_or_404(pid)
    cart = _get_cart()

    if unit == "liters":

        calculated_price = float(p.price) / 20.0
    else:

        calculated_price = float(p.price)

    cart.append({
        "product_id": pid,
        "name": p.name,
        "price": calculated_price,
        "qty": qty,
        "unit": unit,
        "color_name": color_name,
        "color_hex": color_hex
    })

    _save_cart(cart)
    return jsonify({"status": True, "cart": cart})


@bp.route('/cart/apply-coupon', methods=['POST'])
def apply_coupon():
    payload = request.get_json(force=True)
    code = payload.get('code', '').upper().strip()
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()

    if not coupon:
        session.pop('applied_coupon', None)
        return jsonify({
            "status": False, 
            "message": "Invalid or inactive coupon code."
        })

    from datetime import datetime, timedelta
    now_local = datetime.utcnow() + timedelta(hours=1)

    if coupon.expires_at and now_local > coupon.expires_at:
        coupon.is_active = False
        db.session.commit()
        session.pop('applied_coupon', None)
        return jsonify({
            "status": False,
            "message": "This coupon code has expired."
        })

    session['applied_coupon'] = {
        "code": coupon.code,
        "discount_pct": coupon.discount_pct
    }
    session.modified = True

    return jsonify({
        "status": True,
        "message": f"Success! {coupon.discount_pct}% discount applied.",
        "discount_pct": coupon.discount_pct
    })

@bp.route("/cart/remove", methods=["POST"])
def cart_remove():
    payload = request.get_json(force=True)
    pid = int(payload.get("product_id"))

    cart = _get_cart()
    for i, item in enumerate(cart):
        if item["product_id"] == pid:
            cart.pop(i)
            break

    _save_cart(cart)
    return jsonify({"status": True, "cart": cart})


@bp.route("/cart/clear", methods=["POST"])
def cart_clear():
    session['cart'] = []
    session.pop('applied_coupon', None) 
    return jsonify({"status": True, "cart": []})


@bp.route("/cart")
def cart_view():
    cart = _get_cart()
    applied_coupon = session.get('applied_coupon')
    discount_pct = applied_coupon.get('discount_pct', 0) if applied_coupon else 0
    return jsonify({
        "cart": cart,
        "discount_pct": discount_pct 
    })


@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    form = CheckoutForm()
    cart = _get_cart()

    if not cart:
        flash("Cart is empty", "warning")
        return redirect(url_for("main.index"))

    amount = sum(it["price"] * it["qty"] for it in cart)

    applied_coupon = session.get('applied_coupon')
    if applied_coupon:
        discount_pct = applied_coupon.get('discount_pct', 0)
        discount_amount = amount * (discount_pct / 100.0)
        amount = amount - discount_amount
    amount_kobo = int(amount * 100)

    if form.validate_on_submit():
        reference = uuid.uuid4().hex
        ref_token = session.get("ref_token")

        order = Order(
            reference=reference,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            amount=amount,
            ref_token=ref_token
        )
        db.session.add(order)
        wants_newsletter = request.form.get("subscribe") 

        if wants_newsletter == "yes":
            existing_sub = Subscriber.query.filter_by(email=form.email.data).first()
            if not existing_sub:
                new_sub = Subscriber(email=form.email.data, is_active=True)
                db.session.add(new_sub)
            elif not existing_sub.is_active:
                existing_sub.is_active = True
        db.session.commit() 

        callback = url_for("main.paystack_callback", _external=True)

        try:
            init = initialize_paystack(reference, order.email, amount_kobo, callback)
        except requests.exceptions.ReadTimeout:
            flash("Payment service is slow. Please try again.", "danger")
            return redirect(url_for("main.checkout"))
        except requests.exceptions.RequestException:
            flash("Unable to connect to payment service.", "danger")
            return redirect(url_for("main.checkout"))

        if not init or not init.get("status"):
            flash("Payment initialization failed.", "danger")
            return redirect(url_for("main.checkout"))

        return redirect(init["data"]["authorization_url"])

    return render_template("checkout.html", form=form, cart=cart, amount=amount)


@bp.route("/paystack/callback")
def paystack_callback():
    reference = request.args.get("reference")
    if not reference:
        flash("Invalid payment callback", "danger")
        return redirect(url_for("main.index"))

    try:
        res = verify_paystack_transaction(reference)
    except Exception:
        flash("Payment verification failed. Try again.", "danger")
        return redirect(url_for("main.index"))

    if not (res.get("status") and res["data"]["status"] == "success"):
        flash("Payment verification failed", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.filter_by(reference=reference).first()
    if not order:
        flash("Order not found", "danger")
        return redirect(url_for("main.index"))

    if order.paid:
        flash("Order already processed", "info")
        return redirect(url_for("main.index"))

    order.paid = True

    if not order.pickup_code:
        order.pickup_code = generate_pickup_code()
        order.pickup_generated_at = datetime.utcnow()

    cart = session.get("cart", [])

    for item in cart:
        product = Product.query.get(item["product_id"])

        if product:
            product.sold += item["qty"]

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
		unit=item.get("unit"),
                quantity=item["qty"],
                color_name=item.get("color_name"),
                color_hex=item.get("color_hex")
            )

            db.session.add(order_item)

    db.session.commit()


    session["cart"] = []
    session.pop("applied_coupon", None)

    referrer = None
    if order.ref_token:
        referrer = Referer.query.filter_by(
            token=order.ref_token,
            status="approved"
        ).first()

    if referrer:
        earn = int(order.amount * 0.07)
        referrer.earnings += earn
        db.session.commit()

    send_email(
        "Order successful",
        [order.email],
        f"""
        <p>Payment for order <b>{order.reference}</b> successful.</p>
        <p><b>Your pickup code:</b> {order.pickup_code}</p>
        <p>Please present this code when picking up your product.</p>
        """
    )

    items_html = ""
    for item in cart:
        items_html += f"""
        <p>
            {item.get('name')} - Qty: {item.get('qty')}<br>
            Color: {item.get('color_name')} ({item.get('color_hex')})
        </p>
        """

    send_email(
        "New order received",
        [current_app.config.get("MAIL_USERNAME")],
        f"""
        <p>Order {order.reference} placed.</p>
        {items_html}
        """
    )

    flash("Payment confirmed. Order placed.", "success")
    return render_template("payment_confirmation.html", order=order)


@bp.route("/webhook/paystack", methods=["POST"])
def paystack_webhook():
    if not validate_paystack_webhook(request):
        return jsonify({"status": False}), 400
    payload = request.get_json()
    event = payload.get("event")
    if event == "charge.success":
        ref = payload["data"]["reference"]
        order = Order.query.filter_by(reference=ref).first()
        if order and not order.paid:
            order.paid = True
            db.session.commit()
    return jsonify({"status": True}), 200


def generate_pickup_code(length=7):
    """Generate a unique alphanumeric pickup code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@bp.route("/admin/order/manual", methods=["GET", "POST"])
@login_required
def admin_manual_order():
    if current_user.username != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        customer_name = request.form.get("name", "Walk-in Customer")
        customer_phone = request.form.get("phone", "N/A")
        customer_email = request.form.get("email", "cash@heavenlypaint.com")
        product_id = request.form.get("product_id")
        unit = request.form.get("unit", "buckets").lower()
        color_name = request.form.get("color_name", "Standard")
        color_hex = request.form.get("color_hex", "")

        try:
            qty = float(request.form.get("qty", 1.0))
        except ValueError:
            qty = 1.0

        product = Product.query.get(product_id)
        if not product:
            flash("Invalid product selected.", "danger")
            return redirect(request.url)

        if unit == "liters":
            price_per_unit = float(product.price) / 20.0
        else:
            price_per_unit = float(product.price)

        total_amount = price_per_unit * qty
        reference = f"HP-{uuid.uuid4().hex[:7].upper()}"
        unique_pickup = f"WK-{uuid.uuid4().hex[:7].upper()}"

        order = Order(
            reference=reference,
            name=customer_name,
            email=customer_email,
            phone=customer_phone,
            amount=total_amount,
            paid=True,
            delivered=True,
            pickup_code=unique_pickup,
            pickup_expired=True
        )

        db.session.add(order)
        db.session.commit()
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            unit=unit,
            quantity=qty,
            color_name=color_name,
            color_hex=color_hex,
            collected_quantity=qty
        )

        product.sold += qty
        product.delivered += qty
        db.session.add(order_item)
        db.session.commit()

        flash(f"Manual cash sale recorded successfully! Reference: {reference}", "success")
        return redirect(url_for("main.admin_orders"))

    products = Product.query.order_by(Product.name).all()
    return render_template("admin/manual_order.html", products=products)



@bp.route('/apply-referer', methods=['GET', 'POST'])
def apply_referer():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        whatsapp = request.form.get("whatsapp_number")
        bank_name = request.form.get("bank")
        email = request.form.get("email")
        account_number = request.form.get("account_number")
        account_name = request.form.get("account_name")
        
        existing = Referer.query.filter_by(whatsapp=whatsapp).first()
        if existing:
            flash("You have already applied.", "warning")
            return redirect(url_for("main.referer_login"))

        bank = Bank.query.filter_by(name=bank_name).first()
        token = uuid.uuid4().hex

        r = Referer(
            name=full_name,
            whatsapp=whatsapp,
            bank_id=bank.id if bank else None,
            bank_name=bank_name,
            email=email,
            account_number=account_number,
            account_name=account_name,
            status="pending",
            earnings=0,
            referrals_count=0,
            token=token
        )
        db.session.add(r)
        db.session.commit()

        notify_referer(r, "pending")
        send_whatsapp_welcome(r.whatsapp, r.name)
        send_whatsapp_admin_alert(r.name, r.whatsapp)
        send_email(
            "New Referer Application",
            [current_app.config["MAIL_USERNAME"]],
            f"<h3>New Referer Application</h3>"
            f"<p>{r.name} ({r.whatsapp}) applied.</p>"
        )

        return redirect(url_for("main.referer_pending", token=r.token))

    return render_template("apply_referer.html")


@bp.route("/generate_link/<token>")
def generate_link(token):
    r = Referer.query.filter_by(token=token, status="approved").first_or_404()
    link = f"{url_for('main.index', _external=True)}?ref={r.token}"
    return jsonify({"status": True, "link": link})



#@bp.before_app_request
#def capture_ref():
#    ref = request.args.get("ref")
#    if ref:
#        session["ref_token"] = ref

db_fixed = False

@bp.before_app_request
def run_before_requests():
    ref = request.args.get("ref")
    if ref:
        session["ref_token"] = ref

    global db_fixed
    if not db_fixed:
        try:
            from sqlalchemy import text
            db.session.execute(text("ALTER TABLE coupon ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;"))
            db.session.commit()
        except Exception:
            db.session.rollback()
        db_fixed = True

@bp.route('/api/referer/fingerprint/setup/start', methods=['POST'])
def referer_fingerprint_start():
    data = request.get_json()
    r = Referer.query.filter_by(token=data.get("token")).first_or_404()
    options = generate_registration_options(
        rp_id=RP_ID, rp_name=RP_NAME,
        user_id=str(r.id).encode('utf-8'), user_name=r.name,
    )
    options_dict = json.loads(options_to_json(options))
    session[f'webauthn_reg_{r.id}'] = options_dict['challenge']

    return jsonify({"options": options_dict})


@bp.route('/api/referer/withdraw/start', methods=['POST'])
def referer_withdraw_start():
    """Validates balance and challenges the phone for a fingerprint."""
    data = request.get_json()
    r = Referer.query.filter_by(token=data.get("token")).first_or_404()
    amount = float(data.get("amount", 0))

    if amount < 2000: 
        return jsonify({"status": False, "message": "Minimum withdrawal is ₦2,000"}), 400
    if amount > r.earnings: 
        return jsonify({"status": False, "message": "Insufficient balance"}), 400

    user_creds = BiometricCredential.query.filter_by(referer_id=r.id).all()
    if not user_creds:
        return jsonify({"status": False, "message": "No fingerprint setup. Please secure your account first."}), 403

    allow_credentials = [PublicKeyCredentialDescriptor(id=c.credential_id) for c in user_creds]
    options = generate_authentication_options(rp_id=RP_ID, allow_credentials=allow_credentials)
    options_dict = json.loads(options_to_json(options))
    session[f'webauthn_auth_{r.id}'] = options_dict['challenge']
    session[f'pending_amount_{r.id}'] = amount

    return jsonify({"options": options_dict})

@bp.route('/api/referer/fingerprint/setup/finish', methods=['POST'])
def referer_fingerprint_finish():
    data = request.get_json()
    r = Referer.query.filter_by(token=data.get("token")).first_or_404()
    saved_challenge_str = session.get(f'webauthn_reg_{r.id}')
    if not saved_challenge_str:
        return jsonify({"status": False, "message": "Session expired. Try again."}), 400
    padding = '=' * (4 - (len(saved_challenge_str) % 4))
    expected_challenge_bytes = base64.urlsafe_b64decode(saved_challenge_str + padding)

    try:
        verification = verify_registration_response(
            credential=data.get("credential"),
            expected_challenge=expected_challenge_bytes,
            expected_rp_id=RP_ID,
            expected_origin=EXPECTED_ORIGIN
        )
        new_cred = BiometricCredential(
            referer_id=r.id,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count
        )
        db.session.add(new_cred)
        db.session.commit()
        return jsonify({"status": True, "message": "Fingerprint locked to your account!"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)}), 400
@bp.route('/api/referer/withdraw/finish', methods=['POST'])
def referer_withdraw_finish():
    data = request.get_json()
    r = Referer.query.filter_by(token=data.get("token")).first_or_404()
    amount = session.get(f'pending_amount_{r.id}')
    
    saved_challenge_str = session.get(f'webauthn_auth_{r.id}')
    
    if not amount or not saved_challenge_str: 
        return jsonify({"status": False, "message": "Session expired. Try again."}), 400

    padding = '=' * (4 - (len(saved_challenge_str) % 4))
    expected_challenge_bytes = base64.urlsafe_b64decode(saved_challenge_str + padding)

    try:
        raw_id = data.get('credential', {}).get('id', '') + '=='
        cred_id_bytes = base64.urlsafe_b64decode(raw_id)
        saved_cred = BiometricCredential.query.filter_by(credential_id=cred_id_bytes).first()
        verification = verify_authentication_response(
            credential=data.get("credential"),
            expected_challenge=expected_challenge_bytes,
            expected_rp_id=RP_ID, 
            expected_origin=EXPECTED_ORIGIN,
            credential_public_key=saved_cred.public_key,
            credential_current_sign_count=saved_cred.sign_count
        )
        saved_cred.sign_count = verification.new_sign_count
        bank = Bank.query.get(r.bank_id)
        if not bank:
            return jsonify({"status": False, "message": "Bank details missing from account."}), 400
        bank_code = bank.code
        if not bank_code:
            bank_code = fetch_paystack_bank_code(bank.name)
            if bank_code:
                bank.code = bank_code
                db.session.commit()
            else:
                return jsonify({"status": False, "message": f"Paystack does not recognize '{bank.name}'. Update your bank details."}), 400
        recipient_code = create_paystack_recipient(r.account_name, r.account_number, bank_code)
        if not recipient_code: 
            return jsonify({"status": False, "message": "Invalid bank details. Paystack rejected the account."}), 400
        transfer = initiate_paystack_transfer(amount, recipient_code)
        if not transfer.get("status"):
            return jsonify({"status": False, "message": transfer.get("message", "Paystack transfer failed (Check Heavenly Paint Limited balance).")}), 400

        r.earnings -= amount
        w = Withdrawal(referer_id=r.id, amount=amount, account_details=r.account_number, status="paid")
        db.session.add(w)
        db.session.commit()
        session.pop(f'pending_amount_{r.id}', None)
        return jsonify({"status": True, "message": f"Verified! ₦{amount} sent instantly to your account."})
    except Exception as e:
        return jsonify({"status": False, "message": f"Verification or Payout Failed: {str(e)}"}), 400

@bp.route("/referer/<token>/dashboard")
def referer_dashboard(token):
    referer = Referer.query.filter_by(token=token).first_or_404()

    if referer.status != "approved":
        return redirect(url_for("main.referer_pending", token=referer.token))

    badge = None
    pct = 0

    total_withdrawn = db.session.query(func.sum(Withdrawal.amount))\
        .filter_by(referer_id=referer.id, status="paid").scalar() or 0

    pending_withdraw = db.session.query(func.sum(Withdrawal.amount))\
        .filter_by(referer_id=referer.id, status="pending").scalar() or 0

    start_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_withdrawn = db.session.query(func.sum(Withdrawal.amount))\
        .filter(
            Withdrawal.referer_id == referer.id,
            Withdrawal.created_at >= start_month
        ).scalar() or 0
    has_biometric = BiometricCredential.query.filter_by(referer_id=referer.id).first() is not None

    return render_template(
        "referer/dashboard.html",
        referrer=referer,
        badge=badge,
        pct=pct,
        monthly_earnings=referer.earnings,
        total_withdrawn=total_withdrawn,
        pending_withdraw=pending_withdraw,
        monthly_withdrawn=monthly_withdrawn,
        has_biometric=has_biometric
    )


@bp.route("/referer-login", methods=["GET", "POST"])
def referer_login():
    if request.method == "POST":
        whatsapp = request.form.get("whatsapp_number", "")
        whatsapp = whatsapp.replace(" ", "").replace("+", "").strip()
        referer = Referer.query.filter_by(whatsapp=whatsapp).first()

        if not referer:
            flash("No account found with that WhatsApp number.", "danger")
            return redirect(url_for("main.referer_login"))

        if referer.status in ["pending", "rejected"]:
            return redirect(url_for("main.referer_pending", token=referer.token))
        return redirect(url_for("main.referer_dashboard", token=referer.token))
    return render_template("referer_login.html")

@bp.route('/referer/update-settings', methods=['POST'])
def referer_update_settings():
    token = request.form.get('token')
    referer = Referer.query.filter_by(token=token).first_or_404()

    new_email = request.form.get('email')
    new_whatsapp = request.form.get('whatsapp').replace(" ", "").replace("+", "").strip()
    new_account_number = request.form.get('account_number').strip()
    new_bank_name = request.form.get('bank_name').strip()

    if new_whatsapp != referer.whatsapp:
        existing_user = Referer.query.filter_by(whatsapp=new_whatsapp).first()
        if existing_user:
            flash("That WhatsApp number is already registered.", "danger")
            return redirect(url_for('main.referer_dashboard', token=referer.token))
        
        from app.models import BiometricCredential
        BiometricCredential.query.filter_by(referer_id=referer.id).delete()
        flash("WhatsApp updated. Please re-register your fingerprint.", "warning")

    referer.email = new_email
    referer.whatsapp = new_whatsapp
    
    if new_account_number != referer.account_number or new_bank_name != referer.bank_name:
        referer.account_number = new_account_number
        referer.bank_name = new_bank_name
        
        from app.models import Bank
        bank = Bank.query.filter_by(name=new_bank_name).first()
        if bank:
            referer.bank_id = bank.id
            
        referer.account_name = referer.name 
        
    db.session.commit()
    
    flash("Settings updated successfully!", "success")
    return redirect(url_for('main.referer_dashboard', token=referer.token))

@bp.route('/webauthn/login/options', methods=['POST'])
def webauthn_login_options():
    data = request.get_json()
    whatsapp = data.get('whatsapp_number', '').replace(" ", "").replace("+", "").strip()
    referer = Referer.query.filter_by(whatsapp=whatsapp).first()
    if not referer:
        return jsonify({"error": "No account", "fallback": True})

    if referer.status != "approved":
        return jsonify({"error": "Not approved", "fallback": True})

    user_creds = BiometricCredential.query.filter_by(referer_id=referer.id).all()
    if not user_creds:
        return jsonify({"fallback": True})

    allow_credentials = [PublicKeyCredentialDescriptor(id=c.credential_id) for c in user_creds]
    options = generate_authentication_options(
        rp_id=RP_ID, 
        allow_credentials=allow_credentials
    )
    options_dict = json.loads(options_to_json(options))
    session[f'login_challenge_{referer.id}'] = options_dict['challenge']

    return jsonify(options_dict)


@bp.route('/webauthn/login/verify', methods=['POST'])
def webauthn_login_verify():
    data = request.get_json()
    whatsapp = data.get('whatsapp_number', '').replace(" ", "").replace("+", "").strip()
    assertion = data.get('assertion')

    referer = Referer.query.filter_by(whatsapp=whatsapp).first()
    if not referer:
        return jsonify({"verified": False, "message": "Referrer not found"})

    saved_challenge_str = session.get(f'login_challenge_{referer.id}')
    if not saved_challenge_str:
        return jsonify({"verified": False, "message": "Session expired"})

    padding = '=' * (4 - (len(saved_challenge_str) % 4))
    expected_challenge_bytes = base64.urlsafe_b64decode(saved_challenge_str + padding)

    try:
        raw_id = assertion.get('id', '') + '=='
        cred_id_bytes = base64.urlsafe_b64decode(raw_id)
        saved_cred = BiometricCredential.query.filter_by(credential_id=cred_id_bytes).first()

        if not saved_cred:
            return jsonify({"verified": False, "message": "Credential not found in database"})

        verification = verify_authentication_response(
            credential=assertion,
            expected_challenge=expected_challenge_bytes,
            expected_rp_id=RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            credential_public_key=saved_cred.public_key,
            credential_current_sign_count=saved_cred.sign_count
        )

        saved_cred.sign_count = verification.new_sign_count
        db.session.commit()
        session.pop(f'login_challenge_{referer.id}', None)

        return jsonify({"verified": True, "token": referer.token})

    except Exception as e:
        return jsonify({"verified": False, "message": str(e)})

@bp.route('/referer/pending/<token>')
def referer_pending(token):
    referer = Referer.query.filter_by(token=token).first_or_404()
    if referer.status == 'approved':
        flash("Your account has been approved! Please log in.", "success")
        return redirect(url_for('main.referer_login'))
    return render_template("referer_pending.html", referer=referer)


@bp.route("/referer-logout")
def referer_logout():
    session.pop("referer_id", None)
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))



@bp.route("/admin/referer/<int:id>/approve", methods=["POST"])
@login_required
def admin_approve_referer(id):
    referer = Referer.query.get_or_404(id)
    referer.status = "approved"
    db.session.commit()
    notify_referer(referer, "approved")
    flash(f"{referer.name} approved.", "success")
    return redirect(url_for("main.referer_requests"))

@bp.route("/admin/referer/<int:id>/delete", methods=["POST"])
@login_required
def admin_delete_referer(id):
    if current_user.username != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.index'))

    referer = Referer.query.get_or_404(id)

    from app.models import Withdrawal, BiometricCredential

    BiometricCredential.query.filter_by(referer_id=referer.id).delete()
    Withdrawal.query.filter_by(referer_id=referer.id).delete()
    db.session.delete(referer)
    db.session.commit()

    flash(f"Referrer {referer.name} has been permanently deleted.", "success")
    return redirect(request.referrer or url_for('main.admin_doe'))

@bp.route("/admin/verify-pickup", methods=["POST"])
@login_required
def admin_verify_pickup():
    data = request.get_json()
    code = data.get("pickup_code")

    if not code:
        return jsonify(success=False, message="Pickup code required")

    order = Order.query.filter_by(pickup_code=code).first()

    if not order:
        return jsonify(success=False, message="Invalid pickup code")

    if not order.paid:
        return jsonify(success=False, message="Order not paid")

    if order.pickup_expired:
        return jsonify(success=False, message="Pickup code expired")

    items_data = []

    for item in order.order_items:
        items_data.append({
            "item_id": item.id,
            "product_name": item.product.name,
            "ordered_quantity": item.quantity,
            "collected_quantity": item.collected_quantity,
            "remaining_quantity": item.remaining_quantity
        })
    if order.is_fully_collected:
        order.delivered = True
        order.pickup_expired = True
        db.session.commit()

    return jsonify(
        success=True,
        order_id=order.id,
        customer=order.name,
        items=items_data,
        delivered=order.delivered
    )

@bp.route("/admin/collect-items", methods=["POST"])
@login_required
def collect_items():

    data = request.get_json()

    order_id = data.get("order_id")
    updates = data.get("updates")

    order = Order.query.get(order_id)

    if not order:
        return jsonify(success=False, message="Order not found")

    if order.pickup_expired or order.shifted:
        return jsonify(success=False, message="Pickup not allowed")

    for update in updates:

        item = OrderItem.query.get(update["item_id"])

        if not item:
            continue

        collect_qty = int(update["collect_qty"])

        if collect_qty <= 0:
            continue

        if collect_qty > item.remaining_quantity:
            return jsonify(
                success=False,
                message=f"Cannot collect more than remaining for {item.product.name}"
            )

        item.collected_quantity += collect_qty
        item.product.delivered += collect_qty


    if order.is_fully_collected:
        order.delivered = True
        order.pickup_expired = True

    db.session.commit()

    return jsonify(
        success=True,
        message="Items collected successfully",
        fully_collected=order.is_fully_collected
    )

@bp.route("/staff/verify-pickup")
@login_required
def verify_pickup_page():
    return render_template("staff/sales/verify_pickup.html")

@bp.route("/admin/referer/<int:id>/reject", methods=["POST"])
@login_required
def admin_reject_referer(id):
    referer = Referer.query.get_or_404(id)
    referer.status = "rejected"
    db.session.commit()
    flash(f"{referer.name} rejected.", "danger")
    return redirect(url_for("main.referer_requests"))

@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()

    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()

        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(url_for("main.admin_doe"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("main.admin_path"))

    return render_template("admin/login.html", form=form)

@bp.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.admin_path"))

@bp.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store,no-cache,must-revalidate,max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.username != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('main.index'))

    products = Product.query.all()

    pending_referers = Referer.query.filter_by(status="pending").all()
    approved_referers = Referer.query.filter_by(status="approved").all()
    rejected_referers = Referer.query.filter_by(status="rejected").all()

    orders = Order.query.order_by(Order.created_at.desc()).all()

    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    start_of_next_month = datetime(now.year + 1, 1, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)

    monthly_sum = db.session.query(func.sum(Order.amount)).filter(
        Order.paid == True,
        Order.created_at >= start_of_month,
        Order.created_at < start_of_next_month
    ).scalar() or 0

    monthly_earnings = int(monthly_sum)
    orders_count = Order.query.count()
    referrers_count = Referer.query.count()
    pending_staff_count = Staff.query.filter_by(verification_status="pending").count()
    pending_withdrawals_count = Withdrawal.query.filter_by(status="pending").count()
    pending_orders_count = Order.query.filter_by(paid=True, delivered=False).count()
    pending_referers_count = len(pending_referers)
    chart_labels = []
    chart_data = []
    today = datetime.utcnow().date()
    sales_dict = {(today - timedelta(days=i)): 0.0 for i in range(6, -1, -1)}
    seven_days_ago = today - timedelta(days=6)
    recent_orders = Order.query.filter(
        Order.paid == True, 
        Order.created_at >= seven_days_ago
    ).all()

    for order in recent_orders:
        order_date = order.created_at.date()
        if order_date in sales_dict:
            sales_dict[order_date] += float(order.amount)

    for date_obj, total in sales_dict.items():
        chart_labels.append(date_obj.strftime("%b %d"))
        chart_data.append(total)
        active_subscribers_count = Subscriber.query.filter_by(is_active=True).count()
    return render_template(
        "admin/dashboard.html",
        products=products,
        pending_referers=pending_referers,
        approved_referers=approved_referers,
        rejected_referers=rejected_referers,
        orders=orders,
        monthly_earnings=monthly_earnings,
        orders_count=orders_count,
        referrers_count=referrers_count,
        pending_staff_count=pending_staff_count,
        pending_withdrawals_count=pending_withdrawals_count,
        pending_orders_count=pending_orders_count,
        pending_referers_count=pending_referers_count,
        chart_labels=chart_labels,
        chart_data=chart_data,
        subscriber_count=active_subscribers_count
    )


def send_whatsapp_message(phone_number, message):
    api_key = current_app.config.get("CALLMEBOT_API_KEY")
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={message}&apikey={api_key}"
    try:
        requests.get(url)
    except Exception as e:
        print("WhatsApp message failed:", e)

from flask_login import login_required, current_user

@bp.route('/admin/tasks', methods=['GET', 'POST'])
@login_required
def admin_tasks():
    if current_user.username != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('main.index'))

    from app.models import Task, Staff

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        staff_id = request.form.get('staff_id')
        new_task = Task(title=title, description=description, staff_id=staff_id)
        db.session.add(new_task)
        db.session.commit()
        staff = Staff.query.get(staff_id)

        if staff:
            dashboard_link = url_for('main.staff_hood', _external=True) 
            send_task_email(staff.email, staff.name, new_task.title, new_task.description, dashboard_link)

        flash('Task assigned successfully!', 'success')
        return redirect(url_for('main.admin_tasks'))

    staff_members = Staff.query.filter_by(verification_status='approved').all()
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    
    return render_template('admin/tasks.html', staff_members=staff_members, tasks=tasks)

@bp.route('/admin/tasks/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_task(id):
    if current_user.username != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('main.index'))

    from app.models import Task
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully.', 'success')
    return redirect(url_for('main.admin_tasks'))
@bp.route('/staff/tasks', methods=['GET'])
def staff_tasks():
    if 'staff_id' not in session:
        flash("Your staff session expired. Please log in again.", "danger")
        return redirect(url_for('main.staff_way'))

    from app.models import Task, Staff
    staff = Staff.query.get(session['staff_id'])
    my_tasks = Task.query.filter_by(staff_id=staff.id).order_by(Task.created_at.desc()).all()

    return render_template('staff/work.html', staff=staff, tasks=my_tasks)

@bp.route('/staff/tasks/complete/<int:id>', methods=['POST'])
def staff_complete_task(id):
    if 'staff_id' not in session: 
        return redirect(url_for('main.staff_way'))

    from app.models import Task
    task = Task.query.get_or_404(id)
    if task.staff_id == session['staff_id']:
        task.status = 'Completed' if task.status == 'Pending' else 'Pending'
        db.session.commit()
        flash('Task status updated!', 'success')

    return redirect(url_for('main.staff_tasks'))

@bp.route('/admin/broadcast', methods=['GET', 'POST'])
@login_required
def admin_broadcast():
    if request.method == 'POST':
        subject = request.form.get('subject')
        raw_message = request.form.get('message')
        formatted_message = raw_message.replace('\n', '<br>')
        subscribers = Subscriber.query.filter_by(is_active=True).all()
        if not subscribers:
            flash("You don't have any active subscribers yet.", "warning")
            return redirect(url_for('main.admin_broadcast'))
        for sub in subscribers:
            html_body = render_template('emails/broadcast.html', 
                                        message=formatted_message, 
                                        email=sub.email)
            send_email(subject, [sub.email], html_body)
        flash(f"Broadcast successfully queued for {len(subscribers)} subscribers!", "success")
        return redirect(url_for('main.admin_broadcast'))
    return render_template('admin_broadcast.html')

@bp.route('/unsubscribe/<email>')
def unsubscribe(email):
    sub = Subscriber.query.filter_by(email=email).first()
    if sub and sub.is_active:
        sub.is_active = False
        db.session.commit()
        flash("You have been successfully unsubscribed from our mailing list.", "success")
    elif sub and not sub.is_active:
        flash("You are already unsubscribed.", "info")
    else:
        flash("We couldn't find your email in our subscriber list.", "warning")
    return redirect(url_for('main.index'))

@bp.route("/admin/profile")
@login_required
def admin_profile():
    if current_user.username != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.index'))
    return render_template("admin/admin_profile.html")


@bp.route("/admin/change-password", methods=["POST"])
@login_required
def admin_change_password():
    if current_user.username != 'admin':
        return redirect(url_for('main.index'))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not check_password_hash(current_user.password_hash, current_password):
        flash("Incorrect current password.", "danger")
        return redirect(url_for('main.admin_profile'))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('main.admin_profile'))

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    flash("Admin password updated successfully!", "success")
    return redirect(url_for('main.admin_profile'))

@bp.route("/admin/product/add", methods=["GET","POST"])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        image_url = None 
        f = form.image.data
        if f:
            upload_result = upload(f, width=1200, height=1200, crop="limit")
            image_url = upload_result['secure_url']
        p = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=image_url
        )
        db.session.add(p)
        db.session.commit()
        flash("Product added to cloud storage", "success")
        return redirect(url_for("main.admin_doe"))
    return render_template("admin/add_product.html", form=form)

@bp.route("/admin/product/delete/<int:pid>", methods=["POST"])
@login_required
def admin_delete_product(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p); db.session.commit()
    flash("Product deleted", "info")
    return redirect(url_for("main.admin_doe"))

@bp.route("/admin/referer-requests")
@login_required
def referer_requests():
    if current_user.username != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.index'))
    all_referrers = Referer.query.order_by(Referer.id.desc()).all()
    return render_template("admin/referer_requests.html", all_referrers=all_referrers)


def send_whatsapp_message(phone_number, message):
    """Send WhatsApp message using CallMeBot API (or your preferred provider)."""
    api_key = current_app.config.get("CALLMEBOT_API_KEY")
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={message}&apikey={api_key}"
    try:
        requests.get(url)
    except Exception as e:
        print("WhatsApp message failed:", e)

@bp.route('/api/referer/withdraw/password', methods=['POST'])
def referer_withdraw_password():
    data = request.get_json()
    r = Referer.query.filter_by(token=data.get("token")).first_or_404()
    amount = float(data.get("amount", 0))
    password_attempt = data.get("password", "").strip()

    if amount < 2000: 
        return jsonify({"status": False, "message": "Minimum withdrawal is ₦2,000"}), 400
    if amount > r.earnings: 
        return jsonify({"status": False, "message": "Insufficient balance"}), 400

    expected_number = r.whatsapp.replace(" ", "").replace("+", "").strip()
    provided_number = password_attempt.replace(" ", "").replace("+", "").strip()
    if provided_number != expected_number:
        return jsonify({"status": False, "message": "Verification failed. Incorrect account phone number."}), 403

    try:
        bank = Bank.query.get(r.bank_id)
        recipient_code = create_paystack_recipient(r.account_name, r.account_number, bank.code)
        if not recipient_code:
            raise ValueError("Invalid bank details. Paystack rejected the account.")
        transfer = initiate_paystack_transfer(amount, recipient_code)
        if not transfer.get("status"):
            raise ValueError(transfer.get("message", "Paystack transfer failed."))
        r.earnings -= amount
        w = Withdrawal(referer_id=r.id, amount=amount, account_details=r.account_number, status="paid")
        db.session.add(w)
        db.session.commit()
        session.pop(f'pending_amount_{r.id}', None)
        return jsonify({"status": True, "message": f"Verified via fallback! ₦{amount} sent instantly."})
    except Exception as e:
        return jsonify({"status": False, "message": f"Payout Failed: {str(e)}"}), 400

@bp.route("/admin/withdrawals", endpoint="admin_withdrawals_view")
@login_required
def admin_withdrawals():
    ws = Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()
    return render_template("admin/withdrawals.html", withdrawals=ws)


@bp.route("/admin/withdrawals/pay/<int:id>", methods=["GET", "POST"], endpoint="admin_pay_withdrawal")
@login_required
def admin_pay_withdrawal(id):
    w = Withdrawal.query.get_or_404(id)
    w.status = 'paid'
    db.session.commit()
    flash("Marked as paid", "success")
    return redirect(url_for("main.admin_withdrawals_view"))


@bp.route("/uploads/<filename>")
def uploaded_file(filename):
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])

    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(upload_folder, filename)

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/faqs")
def faqs():
    return render_template("faqs.html")

@bp.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if current_user.username != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                upload_result = upload(image_file, width=1200, height=1200, crop="limit")
                product.image = upload_result['secure_url']
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.admin_doe'))
    return render_template('admin/edit_product.html', product=product)


#@bp.route('/admin/delete_product/<int:id>', methods=['POST'])
#@login_required
#def delete_product(id):
#    if current_user.username != 'admin':
#        flash('Access denied.', 'danger')
#        return redirect(url_for('main.index'))

#    product = Product.query.get_or_404(id)
#    db.session.delete(product)
#    db.session.commit()
#    flash('Product deleted successfully!', 'success')
#    return redirect(url_for('main.admin_doe'))
@bp.route('/admin/product/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_product(id):
    if current_user.username != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    from app.models import Product
    product = Product.query.get_or_404(id)
    product.is_active = not product.is_active
    from app import db
    db.session.commit()
    status = "restored to the public store" if product.is_active else "archived (hidden from the public store)"
    flash(f'Product "{product.name}" has been {status}.', 'success')
    return redirect(url_for('main.admin_doe'))

@bp.route('/verify_account', methods=['POST'])
def verify_account():
    data = request.get_json()
    bank_code = data.get('bank_code')
    account_number = data.get('account_number')

    url = "https://api.flutterwave.com/v3/accounts/resolve"
    headers = {"Authorization": "Bearer YOUR_FLUTTERWAVE_SECRET_KEY"}
    params = {
        "account_number": account_number,
        "account_bank": bank_code
    }

    res = requests.get(url, headers=headers, params=params)
    response_data = res.json()

    if response_data.get("status") == "success":
        account_name = response_data["data"]["account_name"]
        return jsonify({"account_name": account_name})
    else:
        return jsonify({"error": "Account verification failed"}), 400

@bp.route("/admin/orders")
@login_required
def admin_orders():
    if current_user.username != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))

    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders)


@bp.route("/admin/order/<int:order_id>")
@login_required
def admin_order_view(order_id):
    if current_user.username != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.get_or_404(order_id)
    items = order.order_items
    return render_template("admin/order_view.html", order=order, items=items)


@bp.route("/admin/order/<int:order_id>/toggle_delivered", methods=["POST"])
@login_required
def admin_toggle_delivered(order_id):
    if current_user.username != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.get_or_404(order_id)

    if not order.paid:
        flash("Cannot mark an unpaid order as delivered.", "warning")
        return redirect(url_for("main.admin_order_view", order_id=order_id))

    order.delivered = not order.delivered
    if order.delivered:
        for item in order.order_items:
            item.collected_quantity = item.quantity
    db.session.commit()

    flash(f"Order marked as {'delivered' if order.delivered else 'not delivered'}.", "success")
    return redirect(url_for("main.admin_orders"))


@bp.route('/admin/toggle-hiring', methods=['POST'])
@login_required
def admin_toggle_hiring():
    from app.models import SiteSettings
    
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings(hiring_mode=False)
        db.session.add(settings)
    
    settings.hiring_mode = not settings.hiring_mode
    
    try:
        db.session.commit()
        status = "OPEN" if settings.hiring_mode else "CLOSED"
        flash(f"Hiring Mode is now {status}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Database error while toggling: {str(e)}", "error")

    return redirect(url_for('main.admin_doe'))


@bp.route("/admin/order/<int:order_id>/delete", methods=["POST"])
@login_required
def admin_delete_order(order_id):
    if current_user.username != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.get_or_404(order_id)


    for item in order.order_items:
        db.session.delete(item)

    db.session.delete(order)
    db.session.commit()

    flash("Order permanently deleted from the database.", "success")
    return redirect(url_for("main.admin_orders"))

@bp.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name', 'Anonymous').strip()
    message = request.form.get('message', '').strip()

    if not name:
        name = "Anonymous"

    if message:
        new_feedback = SiteFeedback(name=name, message=message)
        db.session.add(new_feedback)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
    else:
        flash("Feedback message cannot be empty.", "danger")

    return redirect(url_for('main.index'))

@bp.route("/admin/feedback")
@login_required
def admin_feedback():
    if current_user.username != 'admin':
        return redirect(url_for('main.index'))
    
    feedbacks = SiteFeedback.query.order_by(SiteFeedback.created_at.desc()).all()
    return render_template("admin/feedback.html", feedbacks=feedbacks)

@bp.route("/admin/feedback/delete/<int:id>", methods=["POST"])
@login_required
def admin_delete_feedback(id):
    if current_user.username != 'admin':
        return redirect(url_for('main.index'))
    
    fb = SiteFeedback.query.get_or_404(id)
    db.session.delete(fb)
    db.session.commit()
    flash("Feedback deleted successfully.", "success")
    return redirect(url_for('main.admin_feedback'))


@bp.route("/payment_confirmation/<reference>")
def payment_confirmation(reference):
    order = Order.query.filter_by(reference=reference).first_or_404()
    return render_template("payment_confirmation.html", order=order)

@bp.route("/resend-pickup-code", methods=["POST"])
def resend_pickup_code():
    data = request.get_json()
    reference = data.get("reference")
    email = data.get("email")

    if not reference or not email:
        return jsonify(success=False, message="Reference and email required")

    order = Order.query.filter_by(reference=reference, email=email).first()

    if not order:
        return jsonify(success=False, message="Order not found")

    if not order.paid:
        return jsonify(success=False, message="Order not paid")

    if order.delivered:
        return jsonify(success=False, message="Order already delivered")

    send_email(
        "Your Pickup Code",
        [order.email],
        f"""
        <p>Your order <b>{order.reference}</b></p>
        <p><b>Pickup Code:</b> {order.pickup_code}</p>
        <p>You can use this code any day to collect your product.</p>
        """
    )

    return jsonify(success=True, message="Pickup code sent to your email")


@bp.route("/retrieve-pickup")
def retrieve_pickup():
    return render_template("retrieve_pickup.html")



@bp.route('/staff/signup', methods=['GET','POST'])
def staff_signup():
    from app.models import SiteSettings, Staff
    settings = SiteSettings.query.first()
    if not settings or not settings.hiring_mode:
        flash("We are not currently accepting staff applications.", "error")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.form

        if Staff.query.filter_by(username=data['username']).first():
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for('main.staff_signup'))

        if Staff.query.filter_by(email=data['email']).first():
            flash("Email already exists. Please use a different email.", "error")
            return redirect(url_for('main.staff_signup'))

        if Staff.query.filter_by(nin=data['nin']).first():
            flash("NIN already exists. Please check your NIN.", "error")
            return redirect(url_for('main.staff_signup'))
        profile_image = None
        if 'image' in data and data['image']:
            upload_result = upload(data['image'], width=400, height=400, crop="fill", folder="staff_profiles")
            profile_image = upload_result['secure_url']
        documents = None
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            saved_docs = []

            for file in files:
                if file and file.filename:
                    doc_upload = upload(file, resource_type="auto", folder="staff_documents")
                    saved_docs.append(doc_upload['secure_url'])

            if saved_docs:
                documents = ",".join(saved_docs)

        staff = Staff(
            staff_id=f"HPL{int(time.time())}",
            name=data.get('name'),
            age=data.get('age'),
            nationality=data.get('nationality'),
            state=data.get('state'),
            lga=data.get('lga'),
            gender=data.get('gender'),
            nin=data.get('nin'),
            email=data.get('email'),
            role=data.get('role'),
            username=data.get('username'),
            password=generate_password_hash(data.get('password')),
            bank_name=data.get('bank_name'),
            bank_code=data.get('bank_code'),
            account_number=data.get('account_number'),
            account_name=data.get('account_name'),
            profile_image=profile_image,
            documents=documents,
            verified=False,
            verification_status="pending"
        )

        try:
            db.session.add(staff)
            db.session.commit()
            send_welcome_email(staff.email, staff.name, staff.role)
            flash("Registration successful. Please check your email for confirmation.", "success")
            return redirect(url_for('main.staff_way'))

        except Exception as e:
            db.session.rollback()
            flash(f"There was an error saving your data: {str(e)}", "error")
            return redirect(url_for('main.staff_signup'))

    return render_template('staff/signup.html')

@bp.route('/staff/login', methods=['GET','POST'])
def staff_login():
    if request.method == 'POST':
        staff = Staff.query.filter_by(username=request.form['username']).first()

        if staff and check_password_hash(staff.password, request.form['password']):
            session['staff_id'] = staff.id
            return redirect(url_for('main.staff_hood'))

        flash('Invalid credentials')

    return render_template('staff/login.html')


@bp.route('/staff/forgot-password', methods=['GET', 'POST'])
def staff_forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        staff = Staff.query.filter_by(email=email).first()

        if staff:
            staff.reset_token = secrets.token_urlsafe(32)
            staff.reset_token_expires = datetime.utcnow() + timedelta(minutes=30)
            db.session.commit()

            reset_link = url_for(
                'main.staff_reset_password',
                token=staff.reset_token,
                _external=True
            )

            flash("Reset link generated. Contact admin or check server log.", "info")
            print("RESET LINK:", reset_link)
            return redirect(reset_link)


        flash("If the email exists, a reset link has been sent.")
        return redirect(url_for('main.staf_way'))

    return render_template('staff/forgot_password.html')

@bp.route('/staff/reset-password/<token>', methods=['GET', 'POST'])
def staff_reset_password(token):
    staff = Staff.query.filter_by(reset_token=token).first()

    if not staff:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('main.staff_way'))

    if staff.reset_token_expires < datetime.utcnow():
        flash("Reset link has expired.", "danger")
        return redirect(url_for('main.staff_forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if not password or not confirm:
            flash("All fields are required.", "warning")
            return redirect(request.url)

        if password != confirm:
            flash("Passwords do not match.", "warning")
            return redirect(request.url)

        staff.password = generate_password_hash(password)
        staff.reset_token = None
        staff.reset_token_expires = None
        db.session.commit()

        flash("Password has been reset successfully.", "success")
        return redirect(url_for('main.staff_way'))

    return render_template('staff/reset_password.html', token=token)


@bp.route('/staff/dashboard')
def staff_dashboard():
    if 'staff_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('main.staff_way'))

    staff = Staff.query.get_or_404(session['staff_id'])
    pending_tasks_count = Task.query.filter_by(
        staff_id=staff.id,
        status='Pending'
    ).count()

    return render_template(
        'staff/dashboard.html',
        staff=staff, 
        pending_tasks_count=pending_tasks_count
    )


@bp.route('/admin/staff-verification')
def staff_verification():
    staffs = Staff.query.all()
    return render_template('admin/staff_verification.html', staffs=staffs)

@bp.route('/admin/verify/<int:id>', methods=['POST'])
def verify_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.verification_status = 'approved'
    staff.verified = True
    db.session.commit()
    send_status_email(staff.email, staff.name, "approved")
    flash(f"{staff.name} has been approved.", "success")
    return redirect(url_for('main.staff_verification'))


@bp.route('/admin/decline/<int:id>', methods=['POST'])
def decline_staff(id):
    staff = Staff.query.get_or_404(id)
    reason = request.form.get('reason')
    staff.verification_status = 'declined'
    staff.verified = False
    staff.rejection_reason = reason
    db.session.commit()
    send_status_email(staff.email, staff.name, "declined", reason=reason)
    flash(f"{staff.name} has been declined.", "warning")
    return redirect(url_for('main.staff_verification'))


@bp.route('/admin/delete/<int:id>', methods=['POST'])
def delete_staff(id):
    from app.models import Staff, Task
    staff = Staff.query.get_or_404(id)
    if staff.profile_image:
        path = os.path.join(current_app.static_folder, staff.profile_image)
        if os.path.exists(path):
            os.remove(path)

    if staff.documents:
        for doc in staff.documents.split(','):
            path = os.path.join(current_app.static_folder, doc)
            if os.path.exists(path):
                os.remove(path)

    Task.query.filter_by(staff_id=staff.id).delete()
    db.session.delete(staff)
    db.session.commit()

    flash("Staff and all associated tasks deleted successfully", "success")
    return redirect(url_for('main.staff_verification'))

@bp.route('/admin/export-staff-csv')
def export_staff_csv():
    staffs = Staff.query.filter_by(verified=True).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name','Bank','Account Number','Account Name'])

    for s in staffs:
        writer.writerow([s.name, s.bank_name, s.account_number, s.account_name])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition':'attachment; filename=staff_payments.csv'}
    )


@bp.route('/staff/work')
def staff_work():
    if 'staff_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('main.staff_way'))

    staff = Staff.query.get_or_404(session['staff_id'])

    if staff.verification_status != "approved":
        flash("Your account is not approved yet.")
        return redirect(url_for('main.staff_hood'))
    if staff.role.lower() == "sales":
        return redirect(url_for('main.sales_dashboard'))
    template_path = f"roles/{staff.role.lower()}.html"
    try:
        return render_template(template_path, staff=staff)
    except:
        abort(404, description="Dashboard not available for your role yet.")

@bp.route('/staff/profile')
def staff_profile():

    if 'staff_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('main.staff_way'))
        
    staff = Staff.query.get_or_404(session['staff_id'])
    return render_template('staff/staff_profile.html', staff=staff)

@bp.route('/staff/update-info', methods=['POST'])
def staff_update_info():
    if 'staff_id' not in session:
        return redirect(url_for('main.staff_way'))
    staff = Staff.query.get(session['staff_id'])
    if not staff:
        return redirect(url_for('main.staff_way'))
    new_name = request.form.get('name')
    new_username = request.form.get('username')
    if new_name:
        staff.name = new_name
    if new_username and new_username != staff.username:
        if Staff.query.filter_by(username=new_username).first():
            flash("That username is already taken.", "error")
            return redirect(url_for('main.staff_profile'))
        staff.username = new_username
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename != '':
            upload_result = upload(file, width=400, height=400, crop="fill", folder="staff_profiles")
            staff.profile_image = upload_result['secure_url']
    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'error')

    return redirect(url_for('main.staff_profile'))

@bp.route('/staff/change-password', methods=['POST'])
def staff_change_password():
    if 'staff_id' not in session:
        return redirect(url_for('main.staff_way'))
        
    staff = Staff.query.get(session['staff_id'])
    
    curr_pw = request.form.get("current_password")
    new_pw = request.form.get("new_password")
    conf_pw = request.form.get("confirm_password")

    if not check_password_hash(staff.password, curr_pw):
        flash("Current password incorrect.", "error")
    elif new_pw != conf_pw:
        flash("New passwords do not match.", "error")
    else:
        staff.password = generate_password_hash(new_pw)
        db.session.commit()
        flash("Password updated successfully!", "success")

    return redirect(url_for('main.staff_profile'))


@bp.route('/staff/logout', methods=['POST'])
def staff_logout():
    session.pop('staff_id', None)
    flash('You have been logged out successfully.')
    return redirect(url_for('main.staff_way'))



def pay_staffs(staffs):
    url = "https://api.paystack.co/transfer/bulk"
    headers = {"Authorization": "Bearer PAYSTACK_SECRET"}
    payload = {
        "currency": "NGN",
        "source": "balance",
        "transfers": [
            {
                "amount": 500000,
                "recipient": s.account_number,
                "reason": "Staff payment"
            } for s in staffs
        ]
    }
    return requests.post(url, headers=headers, json=payload).json()

def verify_nin_face(nin, image):
    url = "https://api.dojah.io/api/v1/kyc/nin/verify"
    headers = {
        "Authorization": "Bearer DOJAH_SECRET_KEY",
        "AppId": "DOJAH_APP_ID"
    }
    payload = {
        "nin": nin,
        "image": image
    }
    return requests.post(url, headers=headers, json=payload).json()


from flask_login import login_required, current_user
from flask import abort

@bp.route('/staff/sales/dashboard')
def sales_dashboard():
    staff = staff_required(role="sales")

    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template(
        'staff/sales/sales_dashboard.html',
        staff=staff,
        products=products,
        orders=orders
    )


@bp.route('/staff/product/add', methods=['GET','POST'])
def staff_add_product():
    staff = staff_required(role="sales")

    if staff.role != 'Sales':
        abort(403)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files.get('image')

        filename = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        product = Product(
            name=name,
            description=description,
            price=price,
            image=filename
        )

        db.session.add(product)
        db.session.commit()

        flash("Product published successfully", "success")
        return redirect(url_for('main.sales_dashboard'))

    return render_template('staff/sales/add_product.html')


@bp.route('/staff/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def staff_edit_product(id):
    staff = staff_required(role="sales")
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']

        image = request.files.get('image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            product.image = filename

        db.session.commit()
        flash("Product updated successfully", "success")
        return redirect(url_for('main.sales_dashboard'))

    return render_template('staff/sales/edit_product.html', product=product)


@bp.route('/staff/product/delete/<int:id>', methods=['POST'])
def staff_delete_product(id):
    staff = staff_required(role="sales")

    product = Product.query.get_or_404(id)

    if product.image:
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image)
        if os.path.exists(img_path):
            os.remove(img_path)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully", "success")
    return redirect(url_for('main.sales_dashboard'))


@bp.route('/staff/order/<int:order_id>/toggle_shipped', methods=['POST'])
def staff_toggle_shipped(order_id):
    staff = staff_required(role="sales")
    order = Order.query.get_or_404(order_id)

    if not order.paid:
        flash("Order not paid yet.", "warning")
        return redirect(url_for('main.sales_dashboard'))

    if order.delivered:
        flash("This order has already been shipped and cannot be undone.", "warning")
        return redirect(url_for('main.sales_dashboard'))

    order.delivered = True
    db.session.commit()

    flash("Order successfully marked as shipped.", "success")
    return redirect(url_for('main.sales_dashboard'))


def staff_required(role=None):
    if 'staff_id' not in session:
        abort(401)

    staff = Staff.query.get(session['staff_id'])
    if not staff:
        abort(401)

    if staff.verification_status != "approved":
        abort(403)

    if role and staff.role.lower() != role.lower():
        abort(403)

    return staff


@bp.route('/admin/download-documents/<int:staff_id>')
def download_documents(staff_id):
    staff = Staff.query.get_or_404(staff_id)

    if not staff.documents:
        abort(404, description="No documents found for this staff.")

    doc_list = staff.documents.split(',')
    memory_file = BytesIO()

    with zipfile.ZipFile(memory_file, 'w') as zf:
        for i, doc_path in enumerate(doc_list):
            doc_path = doc_path.strip()
            if doc_path.startswith('http'):
                try:
                    response = requests.get(doc_path)
                    if response.status_code == 200:
                        ext = doc_path.split('.')[-1] if '.' in doc_path[-5:] else 'pdf'
                        filename = f"document_{i+1}.{ext}"
                        zf.writestr(filename, response.content)
                except Exception as e:
                    print(f"Error downloading {doc_path}: {e}")
            else:
                abs_path = os.path.join(current_app.static_folder, doc_path)
                if os.path.exists(abs_path):
                    zf.write(abs_path, arcname=os.path.basename(abs_path))

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype='application/zip',
        download_name=f"{staff.staff_id}_documents.zip",
        as_attachment=True
    )


@bp.route('/signup')
def signup():
    banks = Bank.query.order_by(Bank.name).all()
    return render_template('signup.html', banks=banks)

@bp.route('/admin/coupons', methods=['GET', 'POST'])
@login_required
def admin_coupons():
    if current_user.username != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.index'))
        
    from datetime import datetime, timedelta
    
    now_local = datetime.utcnow() + timedelta(hours=1)
    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE coupon ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    expired_coupons = Coupon.query.filter(
        Coupon.expires_at != None,
        Coupon.expires_at <= now_local,
        Coupon.is_active == True
    ).all()
    
    if expired_coupons:
        for ec in expired_coupons:
            ec.is_active = False
        db.session.commit()

    if request.method == 'POST':
        code = request.form.get('code', '').upper().strip()
        expires_str = request.form.get('expires_at')
        
        try:
            discount = float(request.form.get('discount_pct', 0))
        except ValueError:
            discount = 0.0
            
        if not code or discount <= 0:
            flash("Please enter a valid code and a discount greater than 0.", "error")
            return redirect(url_for('main.admin_coupons'))

        expires_at = None
        if expires_str:
            try:
                if len(expires_str) > 16:
                    expires_at = datetime.strptime(expires_str, '%Y-%m-%dT%H:%M:%S')
                else:
                    expires_at = datetime.strptime(expires_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        if Coupon.query.filter_by(code=code).first():
            flash("That coupon code already exists!", "error")
        else:
            new_coupon = Coupon(code=code, discount_pct=discount, expires_at=expires_at)
            db.session.add(new_coupon)
            db.session.commit()
            flash(f"Coupon {code} created successfully!", "success")
            
        return redirect(url_for('main.admin_coupons'))
        
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()

    return render_template('admin/coupons.html', coupons=coupons, now=now_local)

@bp.route('/admin/coupons/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_coupon(id):
    if current_user.username != 'admin':
        return redirect(url_for('main.index'))
        
    coupon = Coupon.query.get_or_404(id)
    coupon.is_active = not coupon.is_active
    db.session.commit()
    status = "activated" if coupon.is_active else "deactivated"
    flash(f"Coupon {coupon.code} has been {status}.", "success")
    return redirect(url_for('main.admin_coupons'))


@bp.route('/admin/coupons/delete/<int:id>', methods=['POST'])
@login_required
def delete_coupon(id):
    if current_user.username != 'admin':
        return redirect(url_for('main.index'))
        
    coupon = Coupon.query.get_or_404(id)
    db.session.delete(coupon)
    db.session.commit()
    flash("Coupon permanently deleted.", "success")
    return redirect(url_for('main.admin_coupons'))

@bp.route("/admin/export/staffs")
@login_required
def export_staffs():
    if current_user.username != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('main.index'))

    staffs = Staff.query.all()
    si = io.StringIO()
    cw = csv.writer(si)

    column_names = [col.name for col in Staff.__table__.columns]
    
    clean_headers = [col.replace('_', ' ').title() for col in column_names]
    cw.writerow(clean_headers)

    for s in staffs:
        row_data = [getattr(s, col) for col in column_names]
        cw.writerow(row_data)

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=hpl_staff_complete_backup.csv"}
    )


@bp.route("/admin/export/referrers")
@login_required
def export_referrers():
    if current_user.username != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('main.index'))

    referrers = Referer.query.all()
    si = io.StringIO()
    cw = csv.writer(si)

    column_names = [col.name for col in Referer.__table__.columns]
    
    clean_headers = [col.replace('_', ' ').title() for col in column_names]
    cw.writerow(clean_headers)

    for r in referrers:
        row_data = [getattr(r, col) for col in column_names]
        cw.writerow(row_data)

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=hpl_referrers_complete_backup.csv"}
    )


@bp.route('/staff/reapply', methods=['GET', 'POST'])
def staff_reapply():
    if 'staff_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('main.staff_way'))

    staff = Staff.query.get_or_404(session['staff_id'])

    if staff.verification_status != 'declined':
        return redirect(url_for('main.staff_hood'))

    if request.method == 'POST':
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            saved_docs = []

            upload_dir = os.path.join(current_app.static_folder, "documents")
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    rel_path = f"documents/{filename}"
                    abs_path = os.path.join(current_app.static_folder, rel_path)
                    file.save(abs_path)
                    saved_docs.append(rel_path)

            if saved_docs:
                new_docs_str = ",".join(saved_docs)
                if staff.documents:
                    staff.documents += "," + new_docs_str
                else:
                    staff.documents = new_docs_str

        staff.verification_status = 'pending'
        db.session.commit()

        flash("Your application has been updated and re-submitted for review!", "success")
        return redirect(url_for('main.staff_hood'))

    return render_template('staff/reapply.html', staff=staff)


@bp.route("/receipt/<reference>")
def view_receipt(reference):

    order = Order.query.filter_by(reference=reference).first_or_404()

    return render_template("receipt.html", order=order)


@bp.route('/emergency-reset/<secret_key>')
def emergency_reset(secret_key):
    real_master_key = os.environ.get("MASTER_RESET_KEY")
    if not real_master_key or secret_key != real_master_key:
        return "Access Denied.", 403
    from app.models import User
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.password_hash = generate_password_hash('RescueMe2026!')
        db.session.commit()
        return "Emergency reset successful! You can now log in with the password: RescueMe2026!"
    return "Admin account not found.", 404
@bp.before_request
def block_old_doors():
    locked_routes = ['/admin/login', '/staff/login', '/staff/dashboard', '/admin/dashboard'] 
    if request.path in locked_routes:
        abort(404)
@bp.route('/tara', methods=['GET', 'POST'])
def admin_path():
    return admin_login()
@bp.route('/workers', methods=['GET', 'POST'])
def staff_way():
    return staff_login()
@bp.route('/tara-hood', methods=['GET', 'POST'])
def admin_doe():
    return admin_dashboard()
@bp.route('/workers-doe', methods=['GET', 'POST'])
def staff_hood():
    return staff_dashboard()

@bp.route('/emergency-db-fix')
def emergency_db_fix():
    if not current_user.is_authenticated or current_user.username != 'admin':
        return "Access Denied", 403
    try:
        flask_migrate.stamp()
        flask_migrate.upgrade()
        return "Database stamped and upgraded successfully! You can now delete this route."
    except Exception as e:
        return f"Error: {str(e)}"

@bp.route('/catalog')
def public_catalog():
    from app.models import Catalog
    projects = Catalog.query.order_by(Catalog.created_at.desc()).all()
    return render_template('catalog.html', projects=projects)

@bp.route('/admin/catalog', methods=['GET', 'POST'])
@login_required
def admin_catalog():
    if current_user.username != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    from app.models import Catalog

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_file = request.files.get('image')

        if not title or not image_file:
            flash("Title and Image are required.", "danger")
            return redirect(request.url)
        try:
            upload_result = upload(
                image_file,
                folder="heavenly_catalog",
                width=1080,
                height=1080,
                crop="limit",
                fetch_format="auto",
                quality="auto"
            )
            new_project = Catalog(
                title=title,
                description=description,
                image=upload_result['secure_url'],
                image_url=upload_result['secure_url'],
                show_on_home=True
            )
            db.session.add(new_project)
            db.session.commit()
            flash("Project successfully uploades!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error uploading image: {str(e)}", "danger")
        return redirect(url_for('main.admin_catalog'))
    projects = Catalog.query.order_by(Catalog.created_at.desc()).all()
    return render_template('admin/catalog.html', projects=projects)

@bp.route('/admin/catalog/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_catalog(id):
    if current_user.username != 'admin':
        return redirect(url_for('main.index'))

    from app.models import Catalog
    project = Catalog.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash("Project removed from catalog.", "info")
    return redirect(url_for('main.admin_catalog'))

@bp.route('/admin/catalog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_catalog(id):
    if current_user.username != 'admin':
        return redirect(url_for('main.index'))

    from app.models import Catalog
    project = Catalog.query.get_or_404(id)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_file = request.files.get('image')

        if title:
            project.title = title
        if description:
            project.description = description

        if image_file and image_file.filename != '':
            try:
                upload_result = upload(
                    image_file,
                    folder="heavenly_catalog",
                    width=1080,
                    height=1080,
                    crop="limit",
                    fetch_format="auto",
                    quality="auto"
                )
                project.image = upload_result['secure_url']
                project.image_url = upload_result['secure_url']
            except Exception as e:
                flash(f"Error uploading new image: {str(e)}", "danger")
                return redirect(request.url)

        db.session.commit()
        flash("Catalog project updated successfully!", "success")
        return redirect(url_for('main.admin_catalog'))

    return render_template('admin/edit_catalog.html', project=project)
