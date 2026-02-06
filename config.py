import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'ecom.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024
    PAYSTACK_SECRET = "sk_test_256a9fcacfac205e8315233f487878eb153d0190"
    PAYSTACK_PUBLIC = "pk_test_0c58adaa4cef7b1e8ee6879c797597f6c5ae2da8"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USERNAME = "heavenlypaints33@gmail.com"
    MAIL_PASSWORD = "08122889225aA"
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = "heavenlypaints33@gmail.com"
    CALLMEBOT_API_KEY = "4916867"
    api_key = ("CALLMEBOT_API_KEY")
