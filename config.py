import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'ecom.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    PAYSTACK_PUBLIC = "pk_live_5f798f462459c01c0edd2c7e723350bb86271014"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USERNAME = "heavenlypaints33@gmail.com"
    MAIL_PASSWORD = "08122889225aA"
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = "heavenlypaints33@gmail.com"
    CALLMEBOT_API_KEY = "4916867"
