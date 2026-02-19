import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mailman import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "main.admin_login"

    mail.init_app(app)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        from app.models import User
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(username="tara", email="admin@test.com")
            admin.set_password("myTara!")
            db.session.add(admin)
            db.session.commit()

    return app

