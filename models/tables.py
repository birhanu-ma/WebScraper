from config.db_config import get_connection

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS banks (
        bank_id SERIAL PRIMARY KEY,
        bank_name VARCHAR(255) NOT NULL,
        app_name VARCHAR(255)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id SERIAL PRIMARY KEY,
        bank_id INT NOT NULL REFERENCES banks(bank_id) ON DELETE CASCADE,
        review_text TEXT,
        rating NUMERIC(2,1),
        review_date DATE,
        sentiment_label VARCHAR(20),
        sentiment_score NUMERIC(3,2),
        theme VARCHAR(50),
        source VARCHAR(50)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Tables 'banks' and 'reviews' created successfully!")
