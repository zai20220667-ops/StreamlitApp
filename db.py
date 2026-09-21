import sqlite3
import bcrypt
import os

DATABASE = os.environ.get("DATABASE_PATH", "database.db")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            DOB TEXT NOT NULL,
            gender TEXT NOT NULL
        )
    ''')

    # Seed default admin if no users exist
    cur.execute("SELECT COUNT(*) FROM admin_users")
    if cur.fetchone()[0] == 0:
        default_hash = hash_password("admin123")
        cur.execute(
            "INSERT INTO admin_users (username, name, email, password_hash) VALUES (?, ?, ?, ?)",
            ("admin", "Admin User", "", default_hash)
        )
    conn.commit()
    conn.close()



def get_authenticator_credentials():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT username, name, email, password_hash FROM admin_users")
    rows = cur.fetchall()
    conn.close()

    usernames_dict = {}
    for row in rows:
        usernames_dict[row[0]] = {
            "name": row[1],
            "email": row[2],
            "password": row[3]
        }
    return {"usernames": usernames_dict}

def insert_user(first_name, last_name, DOB, gender):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (first_name, last_name, DOB, gender) VALUES (?, ?, ?, ?)",
        (first_name, last_name, str(DOB), gender)
    )
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, DOB, gender FROM users")
    rows = cur.fetchall()
    conn.close()
    return [{
        "ID": row[0],
        "First Name": row[1],
        "Last Name": row[2],
        "Date of Birth": row[3],
        "Gender": row[4]
    } for row in rows]

def update_user(user_id, first_name, last_name, DOB, gender):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        UPDATE users 
        SET first_name=?, last_name=?, DOB=?, gender=?
        WHERE id=?
    ''', (first_name, last_name, str(DOB), gender, user_id))
    conn.commit()
    conn.close()

def delete_user(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()