import sqlite3

# Bazani ulash
db = sqlite3.connect("database.db")
cursor = db.cursor()

# Jadval yaratish funksiyasi
def create_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        points INTEGER DEFAULT 0
    )
    """)
    db.commit()

# Foydalanuvchini qo'shish funksiyasi
def add_user(user_id, full_name, username):
    cursor.execute("""
    INSERT OR IGNORE INTO users (id, full_name, username) VALUES (?, ?, ?)
    """, (user_id, full_name, username))
    db.commit()

# Foydalanuvchini ballini yangilash funksiyasi
def update_points(user_id, points):
    cursor.execute("UPDATE users SET points = points + ? WHERE id = ?", (points, user_id))
    db.commit()

# Foydalanuvchilarni olish funksiyasi
def get_all_users():
    cursor.execute("SELECT full_name, username, points FROM users")
    return cursor.fetchall()
