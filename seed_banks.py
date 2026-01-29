from app import create_app, db
from flask_migrate import Migrate
from app.models import Bank

app = create_app()

banks = [
    # --- COMMERCIAL BANKS ---
    "Access Bank Plc",
    "Fidelity Bank Plc",
    "First Bank Nigeria Ltd",
    "First City Monument Bank Plc (FCMB)",
    "Guaranty Trust Bank Plc (GTBank)",
    "United Bank for Africa Plc (UBA)",
    "Zenith Bank Plc",
    "Union Bank of Nigeria Plc",
    "Sterling Bank Plc",
    "Stanbic IBTC Bank Plc",
    "Wema Bank Plc",
    "Unity Bank Plc",
    "Ecobank Nigeria Plc",
    "Polaris Bank Plc",
    "Keystone Bank Ltd",
    "Providus Bank Ltd",
    "Parallex Bank Ltd",
    "SunTrust Bank Nigeria Ltd",
    "Titan Trust Bank Ltd",
    "Signature Bank Ltd",
    "Taj Bank Ltd",
    "Citibank Nigeria Ltd",
    "Standard Chartered Bank Nigeria Ltd",

    # --- POPULAR MICROFINANCE BANKS ---
    "LAPO Microfinance Bank",
    "AB Microfinance Bank",
    "Accion Microfinance Bank",
    "Addosser Microfinance Bank",
    "Advans La Fayette Microfinance Bank",
    "NPF Microfinance Bank",
    "Peace Microfinance Bank",
    "Hasal Microfinance Bank",
    "BoI Microfinance Bank",
    "Sparkle Microfinance Bank",
    "VFD Microfinance Bank",
    "Shepherd Trust Microfinance Bank",
    "Rephidim Microfinance Bank",
    "Carbon Microfinance Bank",
    "FairMoney Microfinance Bank",
    "Opay Microfinance Bank",

]

app = create_app()

with app.app_context():
    for name in banks:
        if not Bank.query.filter_by(name=name).first():
            db.session.add(Bank(name=name))
    db.session.commit()

print("Banks seeded successfully")
