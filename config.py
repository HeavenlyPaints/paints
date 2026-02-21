import os
basedir = os.path.abspath(os.path.dirname(__file__))

database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = database_url or f"sqlite:///{os.path.join(basedir,'ecom.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(os.getcwd(),"app","static","uploads")
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
    PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")

    MAIL_SERVER = os.environ.get("MAIL_SERVER","smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT",587))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS","true").lower()=="true"
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER",MAIL_USERNAME)

    CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY")
