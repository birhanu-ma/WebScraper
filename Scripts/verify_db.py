# verify_db.py
import sys, os
project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_root)
from config.db_config import get_connection

def verifyDb():
    conn = get_connection()
    cur = conn.cursor()

    print("\n--- Verification Report ---\n")

    # 1. Count rows in banks table
    cur.execute("SELECT COUNT(*) FROM banks;")
    bank_count = cur.fetchone()[0]
    print(f"Total banks: {bank_count}")

    # 2. Count rows in reviews table
    cur.execute("SELECT COUNT(*) FROM reviews;")
    review_count = cur.fetchone()[0]
    print(f"Total reviews: {review_count}")

    # 3. Count reviews per bank
    cur.execute("""
        SELECT b.bank_name, COUNT(r.review_id) AS review_count
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_name;
    """)
    print("\nReviews per bank:")
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} reviews")

    # 4. Check for null sentiment labels
    cur.execute("SELECT COUNT(*) FROM reviews WHERE sentiment_label IS NULL;")
    null_sentiment = cur.fetchone()[0]
    print(f"\nReviews with NULL sentiment_label: {null_sentiment}")

    # 5. Check for reviews with invalid bank_id (foreign key consistency)
    cur.execute("""
        SELECT COUNT(*)
        FROM reviews r
        LEFT JOIN banks b ON r.bank_id = b.bank_id
        WHERE b.bank_id IS NULL;
    """)
    invalid_fk = cur.fetchone()[0]
    print(f"Reviews with invalid bank_id (FK violation): {invalid_fk}")

    # 6. Optional: Check for duplicate reviews (same text for same bank)
    cur.execute("""
        SELECT bank_id, review_text, COUNT(*)
        FROM reviews
        GROUP BY bank_id, review_text
        HAVING COUNT(*) > 1;
    """)
    duplicates = cur.fetchall()
    if duplicates:
        print("\nDuplicate reviews found:")
        for dup in duplicates:
            print(f"Bank ID {dup[0]}: '{dup[1]}' appears {dup[2]} times")
    else:
        print("\nNo duplicate reviews found.")

    # Close connections
    cur.close()
    conn.close()
    print("\n--- Verification Completed ---\n")

if __name__ == "__main__":
    verifyDb()
