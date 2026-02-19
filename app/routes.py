import uuid
from functools import wraps
import random
import string
import requests
from .utils import generate_pickup_code
import secrets
from jinja2 import TemplateNotFound
from flask import render_template, session, abort
from flask_login import logout_user, login_required
from sqlalchemy.exc import IntegrityError
from flask import send_file, abort, current_app
import io
import os
from .models import OrderItem
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
from .models import Admin, Product, Order, Referer, Withdrawal, Rating
from .forms import AdminLoginForm, ProductForm, RefererApplyForm, CheckoutForm, WithdrawalForm, ChangeAdminForm
from .utils import initialize_paystack, verify_paystack_transaction, validate_paystack_webhook, send_email
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from flask import session,  abort
from app.models import Staff
import time
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from .utils import save_base64_image
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


@bp.route("/")
def index():
    from app.models import Product


    products = Product.query.order_by(Product.created_at.desc()).all()
    total_ordered = db.session.query(func.sum(Product.sold)).scalar() or 0
    total_delivered = db.session.query(func.sum(Product.delivered)).scalar() or 0

    return render_template(
        "index.html",
        products=products,
        total_ordered=total_ordered,
        total_delivered=total_delivered,
        paystack_public=current_app.config.get("PAYSTACK_PUBLIC"),
        current_year=datetime.now().year
    )


def staff_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            staff_id = session.get('staff_id')
            if not staff_id:
                flash("Please log in first.", "warning")
                return redirect(url_for('main.staff_login'))
            staff = Staff.query.get(staff_id)
            if not staff:
                flash("Staff not found.", "danger")
                return redirect(url_for('main.staff_login'))
            if role and staff.role.lower() != role.lower():
                flash("Access denied.", "danger")
                return redirect(url_for('main.staff_dashboard'))
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
    qty = int(payload.get("qty", 1))
    color_name = payload.get("color_name")
    color_hex = payload.get("color_hex")
    
    p = Product.query.get_or_404(pid)
    cart = _get_cart()

    cart.append({
    "product_id": pid,
    "name": p.name,
    "price": p.price,
    "qty": qty,
    "color_name": color_name,
    "color_hex": color_hex
})


    _save_cart(cart)
    return jsonify({"status": True, "cart": cart})



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
    return jsonify({"status": True, "cart": []})


@bp.route("/cart")
def cart_view():
    return jsonify({"cart": _get_cart()})


@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    form = CheckoutForm()
    cart = _get_cart()

    if not cart:
        flash("Cart is empty", "warning")
        return redirect(url_for("main.index"))

    amount = sum(it["price"] * it["qty"] for it in cart)
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
                quantity=item["qty"]
            )

            db.session.add(order_item)

    session["cart"] = []


    if order.ref_token:
        referrer = Referer.query.filter_by(token=order.ref_token, status="approved").first()
        if referrer:
            earn = int(order.amount * 0.09)
            referrer.earnings += earn
            referrer.referrals_count += 1
            db.session.commit()
            badge, pct = badge_for_count(referrer.referrals_count)
            if badge:
                send_email(
                    "Badge achieved",
                    [referrer.email or current_app.config.get('MAIL_USERNAME')],
                    f"<p>Congrats {referrer.name}, you earned {badge} badge ({pct}%)</p>"
                )

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

    send_email(
        "New order received",
        [current_app.config.get("MAIL_USERNAME")],
        f"<p>Order {order.reference} placed.</p>"
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


@bp.route('/apply-referer', methods=['GET', 'POST'])
def apply_referer():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        whatsapp = request.form.get("whatsapp_number")
        bank_name = request.form.get("bank")
        account_number = request.form.get("account_number")
        account_name = request.form.get("account_name")
        existing = Referer.query.filter_by(whatsapp=whatsapp).first()
        if existing:
            flash("You have already applied.", "warning")
            return redirect(url_for("main.referer_login"))

        bank = Bank.query.filter_by(name=bank_name).first()
        # generate a unique token for this referer
        token = uuid.uuid4().hex

        r = Referer(
            name=full_name,
            whatsapp=whatsapp,
            bank_id=bank.id if bank else None,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
            status="pending",
            earnings=0,
            referrals_count=0,
            token=token
        )
        db.session.add(r)
        db.session.commit()

        send_email(
            "New Referer Application",
            [current_app.config["MAIL_USERNAME"]],
            f"<h3>New Referer Application</h3>"
            f"<p>{r.name} ({r.whatsapp}) applied.</p>"
        )

        # redirect to pending page immediately
        return redirect(url_for("main.referer_pending", token=r.token))

    return render_template("apply_referer.html")





@bp.route("/generate_link/<token>")
def generate_link(token):
    r = Referer.query.filter_by(token=token, status="approved").first_or_404()
    link = f"{url_for('main.index', _external=True)}?ref={r.token}"
    return jsonify({"status": True, "link": link})



@bp.before_app_request
def capture_ref():
    ref = request.args.get("ref")
    if ref:
        session["ref_token"] = ref


@bp.route("/referer/withdraw", methods=["POST"])
def referer_withdraw():
    data = request.get_json(force=True)
    token = data.get("token")
    amount = int(data.get("amount", 0))
    account = data.get("account")

    if not all([token, amount, account]):
        return jsonify({"status": False, "message": "All fields are required"}), 400


    if amount < 20000:
        return jsonify({"status": False, "message": "Minimum withdrawal is ₦2,000"}), 400

    r = Referer.query.filter_by(token=token, status="approved").first_or_404()

    if amount > r.earnings:
        return jsonify({"status": False, "message": "Insufficient balance"}), 400

    r.earnings -= amount

    w = Withdrawal(
        referer_id=r.id,
        amount=amount,
        account_details=account,
        status="pending"
    )
    db.session.add(w)
    db.session.commit()

    send_email(
        "Withdrawal Request",
        [current_app.config["MAIL_USERNAME"]],
        f"<p>{r.name} requested a withdrawal of ₦{amount/100:.2f}</p>"
    )

    return jsonify({"status": True, "message": "Withdrawal submitted"})


@bp.route('/referer/pending/<token>')
def referer_pending(token):
    referer = Referer.query.filter_by(token=token).first_or_404()
    return render_template("referer_pending.html", referer=referer)


@bp.route("/referer/<token>/dashboard")
def referer_dashboard(token):
    referer = Referer.query.filter_by(token=token).first_or_404()

    if referer.status != "approved":
        return redirect(url_for("main.referer_pending", token=referer.token))

    badge, pct = badge_for_count(referer.referrals_count)

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

    return render_template(
        "referer/dashboard.html",
        referrer=referer,
        badge=badge,
        pct=pct,
        monthly_earnings=referer.earnings,
        total_withdrawn=total_withdrawn,
        pending_withdraw=pending_withdraw,
        monthly_withdrawn=monthly_withdrawn
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

        if referer.status == "pending":
            return redirect(url_for("main.referer_pending", token=referer.token))
        elif referer.status == "rejected":
            flash("Your application was rejected.", "danger")
            return redirect(url_for("main.referer_login"))

        # approved referers go to dashboard
        return redirect(url_for("main.referer_dashboard", token=referer.token))

    return render_template("referer_login.html")




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
    flash(f"{referer.name} approved.", "success")
    return redirect(url_for("main.referer_requests"))





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

    # **Automatically mark delivered if all items collected**
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
    # Expected format:
    # updates = [
    #   {"item_id": 1, "collect_qty": 2},
    #   {"item_id": 2, "collect_qty": 1}
    # ]

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

    # After updating items, check if fully collected
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
            return redirect(url_for("main.admin_dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("main.admin_login"))  # ✅ redirect triggers one-time flash

    return render_template("admin/login.html", form=form)





@bp.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.admin_login"))

@bp.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store,no-cache,must-revalidate,max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



@bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    # Only admin can access
    if current_user.username != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('main.index'))

    # Fetch products
    products = Product.query.all()

    # Fetch referrers by status
    pending_referers = Referer.query.filter_by(status="pending").all()
    approved_referers = Referer.query.filter_by(status="approved").all()
    rejected_referers = Referer.query.filter_by(status="rejected").all()

    # Fetch all orders (recent first)
    orders = Order.query.order_by(Order.created_at.desc()).all()

    # Monthly earnings calculation
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

    return render_template(
        "admin/dashboard.html",
        products=products,
        pending_referers=pending_referers,
        approved_referers=approved_referers,
        rejected_referers=rejected_referers,
        orders=orders,                 # pass orders for delivered/shipped display
        monthly_earnings=monthly_earnings,
        orders_count=orders_count,
        referrers_count=referrers_count
    )


def send_whatsapp_message(phone_number, message):
    api_key = current_app.config.get("CALLMEBOT_API_KEY")
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={message}&apikey={api_key}"
    try:
        requests.get(url)
    except Exception as e:
        print("WhatsApp message failed:", e)



@bp.route("/admin/product/add", methods=["GET","POST"])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        filename = None
        f = form.image.data
        if f:
            fname = secure_filename(f.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
            f.save(path)
            filename = fname
        p = Product(name=form.name.data, description=form.description.data, price=form.price.data, image=filename)
        db.session.add(p); db.session.commit()
        flash("Product added", "success")
        return redirect(url_for("main.admin_dashboard"))
    return render_template("admin/add_product.html", form=form)

@bp.route("/admin/product/delete/<int:pid>", methods=["POST"])
@login_required
def admin_delete_product(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p); db.session.commit()
    flash("Product deleted", "info")
    return redirect(url_for("main.admin_dashboard"))

@bp.route("/admin/referer-requests")
@login_required
def referer_requests():
    referer_requests = Referer.query.filter_by(status="pending").all()
    return render_template("admin/referer_requests.html", referer_requests=referer_requests)


def send_whatsapp_message(phone_number, message):
    """Send WhatsApp message using CallMeBot API (or your preferred provider)."""
    api_key = current_app.config.get("CALLMEBOT_API_KEY")
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={message}&apikey={api_key}"
    try:
        requests.get(url)
    except Exception as e:
        print("WhatsApp message failed:", e)



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
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def badge_for_count(count):
    if count >= 19: return ("Sapphire", 15)
    if count >= 15: return ("Platinum", 13)
    if count >= 11: return ("Gold", 12)
    if count >= 8: return ("Silver", 11)
    if count >= 5: return ("Wood", 10)
    return (None, 9)


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
            image = request.files['image']
            if image.filename != '':
                fname = image.filename
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
                image.save(path)
                product.image = fname
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('admin/edit_product.html', product=product)


@bp.route('/admin/delete_product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if current_user.username != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))


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


@bp.route("/admin/order/<int:order_id>/toggle_terminated", methods=["POST"])
@login_required
def admin_toggle_terminated(order_id):
    if current_user.username != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.get_or_404(order_id)

    if order.delivered and not order.terminated:
        flash("Cannot terminate a delivered order.", "danger")
        return redirect(url_for("main.admin_order_view", order_id=order_id))

    order.terminated = not order.terminated
    db.session.commit()

    flash(f"Order marked as {'terminated' if order.terminated else 'not terminated'}.", "warning")
    return redirect(url_for("main.admin_orders"))



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
            profile_image = save_base64_image(data['image'])

        documents = None
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
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('main.staff_login'))
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
            return redirect(url_for('main.staff_dashboard'))

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
        return redirect(url_for('main.staff_login'))

    return render_template('staff/forgot_password.html')

#@bp.route('/staff/reset-password/<token>', methods=['GET', 'POST'])
#def staff_reset_password(token):
 #   staff = Staff.query.filter_by(reset_token=token).first()

  #  if not staff or staff.reset_token_expires < datetime.utcnow():
   #     flash("Reset link is invalid or expired")
    #    return redirect(url_for('main.staff_login'))

#    if request.method == 'POST':
 #       new_password = request.form['password']
  #      staff.password = generate_password_hash(new_password)
   #     staff.reset_token = None
    #    staff.reset_token_expires = None
     #   db.session.commit()

      #  flash("Password updated. You can log in now.")
     #   return redirect(url_for('main.staff_login'))

   # return render_template('staff/reset_password.html')




@bp.route('/staff/reset-password/<token>', methods=['GET', 'POST'])
def staff_reset_password(token):
    staff = Staff.query.filter_by(reset_token=token).first()

    if not staff:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('main.staff_login'))

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
        return redirect(url_for('main.staff_login'))

    return render_template('staff/reset_password.html', token=token)


@bp.route('/staff/dashboard')
def staff_dashboard():
    if 'staff_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('main.staff_login'))

    staff = Staff.query.get_or_404(session['staff_id'])
    return render_template('staff/dashboard.html', staff=staff)



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
    flash(f"{staff.name} has been approved.", "success")
    return redirect(url_for('main.staff_verification'))


@bp.route('/admin/decline/<int:id>', methods=['POST'])
def decline_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.verification_status = 'declined'
    staff.verified = False
    db.session.commit()
    flash(f"{staff.name} has been declined.", "warning")
    return redirect(url_for('main.staff_verification'))


@bp.route('/admin/delete/<int:id>', methods=['POST'])
def delete_staff(id):
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

    db.session.delete(staff)
    db.session.commit()

    flash("Staff deleted successfully", "success")
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
        return redirect(url_for('main.staff_login'))

    staff = Staff.query.get_or_404(session['staff_id'])

    if staff.verification_status != "approved":
        flash("Your account is not approved yet.")
        return redirect(url_for('main.staff_dashboard'))
    if staff.role.lower() == "sales":
        return redirect(url_for('main.sales_dashboard'))
    template_path = f"roles/{staff.role.lower()}.html"
    try:
        return render_template(template_path, staff=staff)
    except:
        abort(404, description="Dashboard not available for your role yet.")



@bp.route('/staff/logout', methods=['POST'])
def staff_logout():
    session.pop('staff_id', None)
    flash('You have been logged out successfully.')
    return redirect(url_for('main.staff_login'))



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
@login_required
def staff_delete_product(id):
    staff = current_user

    if not hasattr(staff, "role") or staff.role != 'Sales':
        abort(403)

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
    staff = current_user

    if staff.role != 'Sales':
        abort(403)

    order = Order.query.get_or_404(order_id)

    if not order.paid:
        flash("Order not paid yet.", "warning")
        return redirect(url_for('main.sales_dashboard'))

    order.delivered = not order.delivered
    db.session.commit()

    flash(
        f"Order marked as {'shipped' if order.delivered else 'not shipped'}",
        "success"
    )
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
        for doc_path in doc_list:
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
