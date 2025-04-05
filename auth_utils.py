import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rajkumar@2004",
        database="resource_optimization"
    )

def register_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
    conn.commit()
    conn.close()
    return True

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None
