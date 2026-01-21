import os, requests, hmac, hashlib, json
import base64
from flask import current_app, url_for
from . import mail
from flask_mailman import EmailMessage
from werkzeug.utils import secure_filename
import uuid

def send_email(subject, recipients, html_body, text_body=None):
    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.info("Mail server not configured; cannot send email.")
        return False
    try:
        msg = EmailMessage(subject=subject, to=recipients, html=html_body)
        msg.send()
        return True
    except Exception as e:
        current_app.logger.error("Failed to send email: %s", e)
        return False

def initialize_paystack(reference, email, amount, callback_url):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {current_app.config['PAYSTACK_SECRET']}",
        "Content-Type": "application/json"
    }
    data = {
        "reference": reference,
        "amount": amount,
        "email": email,
        "callback_url": callback_url
    }
    r = requests.post(url, json=data, headers=headers, timeout=20)
    return r.json()

def verify_paystack_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {current_app.config['PAYSTACK_SECRET']}"}
    r = requests.get(url, headers=headers, timeout=20)
    return r.json()

def validate_paystack_webhook(request):
    secret = current_app.config.get('PAYSTACK_SECRET') or ''
    signature = request.headers.get('x-paystack-signature', '')
    body = request.get_data()
    computed = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(computed, signature)



def save_base64_image(image_data, folder="uploads"):
    if not image_data:
        return None

    header, encoded = image_data.split(",", 1)
    ext = header.split("/")[1].split(";")[0]

    filename = f"profile_{uuid.uuid4().hex}.{ext}"
    upload_folder = os.path.join(current_app.static_folder, folder)

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)

    with open(file_path, "wb") as f:
        f.write(base64.b64decode(encoded))

    return f"{folder}/{filename}"



def save_multiple_files(files, folder="documents"):
    if not files:
        return None

    saved_files = []

    upload_folder = os.path.join(current_app.static_folder, folder)
    os.makedirs(upload_folder, exist_ok=True)

    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1]
            new_name = f"{uuid.uuid4().hex}.{ext}"

            path = os.path.join(upload_folder, new_name)
            file.save(path)

            saved_files.append(f"{folder}/{new_name}")

    return ",".join(saved_files)
