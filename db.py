import os
import bcrypt
import psycopg

# Connection string, e.g. postgresql://user:password@db:5432/appdb
# In Docker Compose this is set for you (see compose.yaml).
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Example: "
        "postgresql://appuser:password@localhost:5432/appdb"
    )


def get_conn():
    # Used as `with get_conn() as conn:` -> commits on success, rolls back on
    # error, and closes the connection when the block ends.
    return psycopg.connect(DATABASE_URL)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    DOB TEXT NOT NULL,
                    gender TEXT NOT NULL
                )
            """)

            # Seed default admin if no users exist
            cur.execute("SELECT COUNT(*) FROM admin_users")
            if cur.fetchone()[0] == 0:
                admin_password = os.environ.get("ADMIN_PASSWORD")
                if not admin_password:
                    raise RuntimeError("ADMIN_PASSWORD must be set to create the first admin user.")
                cur.execute(
                    "INSERT INTO admin_users (username, name, email, password_hash) "
                    "VALUES (%s, %s, %s, %s)",
                    ("admin", "Admin User", "", hash_password(admin_password)),
                )


def get_authenticator_credentials():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username, name, email, password_hash FROM admin_users")
            rows = cur.fetchall()

    usernames_dict = {}
    for row in rows:
        usernames_dict[row[0]] = {
            "name": row[1],
            "email": row[2],
            "password": row[3],
        }
    return {"usernames": usernames_dict}


def insert_user(first_name, last_name, DOB, gender):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (first_name, last_name, DOB, gender) "
                "VALUES (%s, %s, %s, %s)",
                (first_name, last_name, str(DOB), gender),
            )


def get_all_users():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, first_name, last_name, DOB, gender FROM users ORDER BY id"
            )
            rows = cur.fetchall()

    return [
        {
            "ID": row[0],
            "First Name": row[1],
            "Last Name": row[2],
            "Date of Birth": row[3],
            "Gender": row[4],
        }
        for row in rows
    ]


def update_user(user_id, first_name, last_name, DOB, gender):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET first_name=%s, last_name=%s, DOB=%s, gender=%s
                WHERE id=%s
                """,
                (first_name, last_name, str(DOB), gender, user_id),
            )


def delete_user(id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id=%s", (id,))