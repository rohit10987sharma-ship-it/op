"""
Script to generate realistic synthetic CSV and SQLite datasets for PrivLens.
Calibrated to the 5 Official PS-019 Personal Data Classes:
  1. Personal identity – name, date of birth, gender, age
  2. Contact information – email address, phone number
  3. Government identifiers – Aadhaar, PAN, passport, voter ID, driving licence numbers
  4. Financial information – bank account number, IFSC, card number, UPI ID
  5. Location / address – postal address, PIN code, geo-coordinates
  - not personal data (negative class)
"""

import os
import csv
import json
import sqlite3
import random

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "synthetic")
GROUND_TRUTH_PATH = os.path.join(BASE_DIR, "ground_truth.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

FIRST_NAMES = ["Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Sneha", "Aditya", "Neha", "Rahul", "Kavita", "Siddharth", "Pooja"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Singh", "Gupta", "Iyer", "Mehta", "Reddy", "Nair", "Deshmukh"]
DOMAINS = ["example.com", "company.org", "enterprise.net", "mailservice.io"]
STREETS = ["MG Road", "Brigade Road", "Park Street", "Connaught Place", "Banjara Hills", "Anna Salai", "Indiranagar 100ft Road"]
UPI_HANDLES = ["okhdfcbank", "okaxis", "oksbi", "okicici", "paytm", "ybl", "upi"]
IFSC_BANKS = ["HDFC", "SBIN", "ICIC", "UTIB", "KKBK", "PUNB"]
DEPARTMENTS = ["Engineering", "Product", "Sales", "Human Resources", "Finance", "Legal", "Operations"]

def random_aadhaar():
    """Generates 12-digit Aadhaar number formatted as XXXX XXXX XXXX."""
    return f"{random.randint(2, 9)}{random.randint(100, 999):03d} {random.randint(1000, 9999):04d} {random.randint(1000, 9999):04d}"

def random_pan():
    """Generates Indian 10-char alphanumeric PAN."""
    letters = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=5))
    digits = f"{random.randint(1000, 9999):04d}"
    last = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    return f"{letters}{digits}{last}"

def random_passport():
    """Generates standard passport number."""
    letter = random.choice("ABCDEFGHJKLMNPRSTUVWXYZ")
    digits = f"{random.randint(1000000, 9999999):07d}"
    return f"{letter}{digits}"

def random_voter_id():
    """Generates Indian Voter ID (EPIC number) e.g. ABC1234567."""
    code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=3))
    num = f"{random.randint(1000000, 9999999):07d}"
    return f"{code}{num}"

def random_driving_licence():
    """Generates Driving Licence number e.g. DL-0420180012345."""
    state = random.choice(["DL", "MH", "KA", "TN", "UP", "GJ"])
    rto = f"{random.randint(1, 14):02d}"
    year = random.randint(2010, 2024)
    num = f"{random.randint(1000000, 9999999):07d}"
    return f"{state}-{rto}{year}{num}"

def random_ifsc():
    """Generates 11-char Indian Financial System Code (IFSC)."""
    bank = random.choice(IFSC_BANKS)
    branch = f"{random.randint(100000, 999999):06d}"
    return f"{bank}0{branch}"

def random_upi_id(fn, ln):
    """Generates UPI ID / VPA."""
    handle = random.choice(UPI_HANDLES)
    return f"{fn.lower()}.{ln.lower()}{random.randint(1, 99)}@{handle}"

def random_bank_account():
    """Generates 9 to 16-digit bank account number."""
    return f"{random.randint(100000000, 999999999999999)}"

def random_luhn_credit_card():
    """Generates 16-digit credit card valid according to Luhn algorithm."""
    digits = [4] + [random.randint(0, 9) for _ in range(14)]
    total = 0
    for idx, d in enumerate(reversed(digits)):
        if idx % 2 == 0:
            doubled = d * 2
            total += (doubled - 9) if doubled > 9 else doubled
        else:
            total += d
    check_digit = (10 - (total % 10)) % 10
    digits.append(check_digit)
    s = "".join(str(d) for d in digits)
    return f"{s[:4]}-{s[4:8]}-{s[8:12]}-{s[12:]}"

def random_pin_code():
    """Generates 6-digit Indian Postal PIN code."""
    return str(random.randint(110001, 850000))

def random_geo_coords():
    """Generates Latitude, Longitude coordinates."""
    lat = round(random.uniform(8.4, 34.5), 6)
    lon = round(random.uniform(68.7, 92.5), 6)
    return f"{lat}, {lon}"

def random_dob():
    year = random.randint(1965, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"

def random_email(first, last):
    return f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(DOMAINS)}"

def random_phone():
    return f"+91-{random.randint(6, 9)}{random.randint(100000000, 999999999)}"

def random_address():
    return f"{random.randint(10, 999)}, {random.choice(STREETS)}, Sector {random.randint(1, 50)}"


def generate_customer_signups_csv():
    path = os.path.join(OUTPUT_DIR, "customer_signups.csv")
    rows = []
    headers = [
        "user_id", "customer_name", "email_address", "phone_number", 
        "date_of_birth", "gender", "residential_address", "pin_code", 
        "account_status"
    ]
    
    for i in range(1, 151):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        rows.append({
            "user_id": 1000 + i,
            "customer_name": f"{fn} {ln}",
            "email_address": random_email(fn, ln),
            "phone_number": random_phone(),
            "date_of_birth": random_dob(),
            "gender": random.choice(["Male", "Female", "Non-Binary", "Prefer_not_to_say"]),
            "residential_address": random_address(),
            "pin_code": random_pin_code(),
            "account_status": random.choice(["ACTIVE", "PENDING", "VERIFIED"])
        })
        
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {path} ({len(rows)} records)")


def generate_kyc_verification_csv():
    path = os.path.join(OUTPUT_DIR, "kyc_verification_records.csv")
    rows = []
    headers = [
        "verification_id", "aadhaar_number", "pan_number", "passport_number", 
        "voter_id", "driving_licence", "kyc_audit_flag"
    ]
    
    for i in range(1, 121):
        rows.append({
            "verification_id": f"KYC-{202600 + i}",
            "aadhaar_number": random_aadhaar(),
            "pan_number": random_pan(),
            "passport_number": random_passport(),
            "voter_id": random_voter_id(),
            "driving_licence": random_driving_licence(),
            "kyc_audit_flag": random.choice(["TIER_1_OK", "TIER_2_OK", "AUDIT_REVIEW"])
        })
        
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {path} ({len(rows)} records)")


def generate_digital_payments_csv():
    path = os.path.join(OUTPUT_DIR, "digital_payments_log.csv")
    rows = []
    headers = [
        "transaction_id", "bank_account_number", "ifsc_code", 
        "card_number", "upi_id", "amount_inr", "settlement_channel"
    ]
    
    for i in range(1, 101):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        rows.append({
            "transaction_id": f"TXN-IN-{90000 + i}",
            "bank_account_number": random_bank_account(),
            "ifsc_code": random_ifsc(),
            "card_number": random_luhn_credit_card(),
            "upi_id": random_upi_id(fn, ln),
            "amount_inr": random.randint(100, 75000),
            "settlement_channel": random.choice(["IMPS", "NEFT", "UPI", "NACH"])
        })
        
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {path} ({len(rows)} records)")


def generate_sqlite_database():
    db_path = os.path.join(OUTPUT_DIR, "enterprise_data.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Table employees
    cur.execute("""
    CREATE TABLE employees (
        emp_id INTEGER PRIMARY KEY,
        employee_name TEXT,
        age INTEGER,
        pan_card TEXT,
        salary_account_no TEXT,
        bank_ifsc TEXT,
        department TEXT
    )
    """)
    for i in range(1, 81):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        cur.execute("""
        INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            100 + i,
            f"{fn} {ln}",
            random.randint(22, 60),
            random_pan(),
            random_bank_account(),
            random_ifsc(),
            random.choice(DEPARTMENTS)
        ))
        
    # 2. Table delivery_dispatch
    cur.execute("""
    CREATE TABLE delivery_dispatch (
        dispatch_id TEXT PRIMARY KEY,
        delivery_address TEXT,
        postal_pin TEXT,
        geo_coords TEXT,
        order_upi TEXT,
        package_weight_kg REAL
    )
    """)
    for i in range(1, 91):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        cur.execute("""
        INSERT INTO delivery_dispatch VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"DISP-{random.randint(10000, 99999)}",
            random_address(),
            random_pin_code(),
            random_geo_coords(),
            random_upi_id(fn, ln),
            round(random.uniform(0.5, 12.0), 2)
        ))
        
    # 3. Table legacy_unindexed_vault (Unregistered Shadow data)
    cur.execute("""
    CREATE TABLE legacy_unindexed_vault (
        vault_id INTEGER PRIMARY KEY,
        aadhaar_card TEXT,
        caller_phone TEXT,
        contact_email TEXT,
        card_number TEXT,
        birth_date TEXT,
        geo_coordinates TEXT,
        http_code INTEGER
    )
    """)
    for i in range(1, 71):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        cur.execute("""
        INSERT INTO legacy_unindexed_vault VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            7000 + i,
            random_aadhaar(),
            random_phone(),
            random_email(fn, ln),
            random_luhn_credit_card(),
            random_dob(),
            random_geo_coords(),
            random.choice([200, 201, 400, 404, 500])
        ))
        
    conn.commit()
    conn.close()
    print(f"Generated SQLite database at {db_path} with 3 tables (employees, delivery_dispatch, legacy_unindexed_vault)")


def generate_ground_truth():
    """
    Creates a manually curated benchmark ground truth for the 5 PS-019 classes:
      - PID: Personal identity (name, date of birth, gender, age)
      - CNT: Contact information (email address, phone number)
      - GID: Government identifiers (Aadhaar, PAN, passport, voter ID, driving licence numbers)
      - FIN: Financial information (bank account number, IFSC, card number, UPI ID)
      - LOC: Location / address (postal address, PIN code, geo-coordinates)
      - not personal data: Negative class
    """
    ground_truth = {
        "metadata": {
            "description": "Benchmark ground truth for PS-019 5 Personal Data Classes evaluation",
            "version": "2.0.0",
            "classes": {
                "PID": "Personal identity",
                "CNT": "Contact information",
                "GID": "Government identifiers",
                "FIN": "Financial information",
                "LOC": "Location / address",
                "not personal data": "not personal data"
            }
        },
        "fields": [
            # customer_signups.csv (9 fields)
            {"source": "customer_signups.csv", "table": None, "column": "user_id", "is_pii": False, "true_class": "not personal data"},
            {"source": "customer_signups.csv", "table": None, "column": "customer_name", "is_pii": True, "true_class": "PID"},
            {"source": "customer_signups.csv", "table": None, "column": "email_address", "is_pii": True, "true_class": "CNT"},
            {"source": "customer_signups.csv", "table": None, "column": "phone_number", "is_pii": True, "true_class": "CNT"},
            {"source": "customer_signups.csv", "table": None, "column": "date_of_birth", "is_pii": True, "true_class": "PID"},
            {"source": "customer_signups.csv", "table": None, "column": "gender", "is_pii": True, "true_class": "PID"},
            {"source": "customer_signups.csv", "table": None, "column": "residential_address", "is_pii": True, "true_class": "LOC"},
            {"source": "customer_signups.csv", "table": None, "column": "pin_code", "is_pii": True, "true_class": "LOC"},
            {"source": "customer_signups.csv", "table": None, "column": "account_status", "is_pii": False, "true_class": "not personal data"},

            # kyc_verification_records.csv (7 fields)
            {"source": "kyc_verification_records.csv", "table": None, "column": "verification_id", "is_pii": False, "true_class": "not personal data"},
            {"source": "kyc_verification_records.csv", "table": None, "column": "aadhaar_number", "is_pii": True, "true_class": "GID"},
            {"source": "kyc_verification_records.csv", "table": None, "column": "pan_number", "is_pii": True, "true_class": "GID"},
            {"source": "kyc_verification_records.csv", "table": None, "column": "passport_number", "is_pii": True, "true_class": "GID"},
            {"source": "kyc_verification_records.csv", "table": None, "column": "voter_id", "is_pii": True, "true_class": "GID"},
            {"source": "kyc_verification_records.csv", "table": None, "column": "driving_licence", "is_pii": True, "true_class": "GID"},
            {"source": "kyc_verification_records.csv", "table": None, "column": "kyc_audit_flag", "is_pii": False, "true_class": "not personal data"},

            # digital_payments_log.csv (7 fields)
            {"source": "digital_payments_log.csv", "table": None, "column": "transaction_id", "is_pii": False, "true_class": "not personal data"},
            {"source": "digital_payments_log.csv", "table": None, "column": "bank_account_number", "is_pii": True, "true_class": "FIN"},
            {"source": "digital_payments_log.csv", "table": None, "column": "ifsc_code", "is_pii": True, "true_class": "FIN"},
            {"source": "digital_payments_log.csv", "table": None, "column": "card_number", "is_pii": True, "true_class": "FIN"},
            {"source": "digital_payments_log.csv", "table": None, "column": "upi_id", "is_pii": True, "true_class": "FIN"},
            {"source": "digital_payments_log.csv", "table": None, "column": "amount_inr", "is_pii": False, "true_class": "not personal data"},
            {"source": "digital_payments_log.csv", "table": None, "column": "settlement_channel", "is_pii": False, "true_class": "not personal data"},

            # enterprise_data.db:employees (7 fields)
            {"source": "enterprise_data.db", "table": "employees", "column": "emp_id", "is_pii": False, "true_class": "not personal data"},
            {"source": "enterprise_data.db", "table": "employees", "column": "employee_name", "is_pii": True, "true_class": "PID"},
            {"source": "enterprise_data.db", "table": "employees", "column": "age", "is_pii": True, "true_class": "PID"},
            {"source": "enterprise_data.db", "table": "employees", "column": "pan_card", "is_pii": True, "true_class": "GID"},
            {"source": "enterprise_data.db", "table": "employees", "column": "salary_account_no", "is_pii": True, "true_class": "FIN"},
            {"source": "enterprise_data.db", "table": "employees", "column": "bank_ifsc", "is_pii": True, "true_class": "FIN"},
            {"source": "enterprise_data.db", "table": "employees", "column": "department", "is_pii": False, "true_class": "not personal data"},

            # enterprise_data.db:delivery_dispatch (6 fields)
            {"source": "enterprise_data.db", "table": "delivery_dispatch", "column": "dispatch_id", "is_pii": False, "true_class": "not personal data"},
            {"source": "enterprise_data.db", "table": "delivery_dispatch", "column": "delivery_address", "is_pii": True, "true_class": "LOC"},
            {"source": "enterprise_data.db", "table": "delivery_dispatch", "column": "postal_pin", "is_pii": True, "true_class": "LOC"},
            {"source": "enterprise_data.db", "table": "delivery_dispatch", "column": "geo_coords", "is_pii": True, "true_class": "LOC"},
            {"source": "enterprise_data.db", "table": "delivery_dispatch", "column": "order_upi", "is_pii": True, "true_class": "FIN"},
            {"source": "enterprise_data.db", "table": "delivery_dispatch", "column": "package_weight_kg", "is_pii": False, "true_class": "not personal data"},

            # enterprise_data.db:legacy_unindexed_vault (8 fields)
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "vault_id", "is_pii": False, "true_class": "not personal data"},
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "aadhaar_card", "is_pii": True, "true_class": "GID"},
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "caller_phone", "is_pii": True, "true_class": "CNT"},
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "contact_email", "is_pii": True, "true_class": "CNT"},
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "card_number", "is_pii": True, "true_class": "FIN"},
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "birth_date", "is_pii": True, "true_class": "PID"},
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "geo_coordinates", "is_pii": True, "true_class": "LOC"},
            {"source": "enterprise_data.db", "table": "legacy_unindexed_vault", "column": "http_code", "is_pii": False, "true_class": "not personal data"}
        ]
    }
    
    with open(GROUND_TRUTH_PATH, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)
    print(f"Generated ground truth benchmark at {GROUND_TRUTH_PATH} ({len(ground_truth['fields'])} labeled fields)")

if __name__ == "__main__":
    generate_customer_signups_csv()
    generate_kyc_verification_csv()
    generate_digital_payments_csv()
    generate_sqlite_database()
    generate_ground_truth()
    print("All synthetic datasets and ground truth successfully generated.")
