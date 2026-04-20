#from app import create_app, db

#app = create_app()

#with app.app_context():
#    db.create_all()

#if __name__ == "__main__":
#    app.run(debug=True)


















#import os
#from dotenv import load_dotenv
#from app import create_app, db

#load_dotenv()

#app = create_app()

#with app.app_context():
#    db.create_all()

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 5000))
#    app.run(host="0.0.0.0", port=port)

from app import create_app, db
from flask_migrate import upgrade, stamp
import os

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        try:
            print("Checking database migrations...")
            stamp() 
            upgrade()
            print("Database is up to date!")
        except Exception as e:
            print(f"Migration skipped or already done: {e}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
