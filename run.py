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


#below is the old run
#import os
#from app import create_app, db
#from sqlalchemy import text

#app = create_app()

#with app.app_context():
#    try:
#        db.session.execute(text('ALTER TABLE product ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
#        db.session.commit()
#        print("Successfully added missing is_active column.")
#    except Exception as e:
#        db.session.rollback()
#        print("Database structure is already correct.")

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 5000))
#    app.run(host="0.0.0.0", port=port)





#below is the current one

import os
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        print("Running database structure verification...")
        db.session.execute(text('ALTER TABLE product ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE'))
        db.session.execute(text('ALTER TABLE catalog ADD COLUMN IF NOT EXISTS description TEXT'))
        db.session.execute(text('ALTER TABLE catalog ADD COLUMN IF NOT EXISTS image VARCHAR(255)'))
        db.session.execute(text('ALTER TABLE catalog ADD COLUMN IF NOT EXISTS image_url VARCHAR(255)'))
        db.session.commit()
        print("Database structure verified and patched successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Database sync note: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
