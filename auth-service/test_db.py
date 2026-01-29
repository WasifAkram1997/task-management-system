import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5433,  # ← Changed to 5433
        database="auth_db",
        user="postgres",
        password="auth_secure_pass_2024_xyz"
    )
    print("✅ SUCCESS!")
    conn.close()
except Exception as e:
    print(f"❌ Failed: {e}")