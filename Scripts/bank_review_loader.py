import csv
import psycopg2
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

class BankReviewLoader:
    def __init__(self):
        # Database connection parameters from .env
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cur = self.conn.cursor()

    def load_banks_csv(self, csv_path):
        """Load banks CSV into the banks table"""
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                self.cur.execute("""
                    INSERT INTO banks (bank_name, app_name)
                    VALUES (%s, %s)
                """, (
                    row["bank_name"],
                    row["title"]  # mapped to app_name
                ))
                count += 1

        self.conn.commit()
        print(f"Inserted {count} rows into banks table.")

    def load_reviews_csv(self, csv_path):
        """Load reviews CSV into the reviews table"""
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            skipped = 0

            for row in reader:
                # Map bank_name to bank_id
                self.cur.execute(
                    "SELECT bank_id FROM banks WHERE bank_name = %s",
                    (row["bank_name"],)
                )
                result = self.cur.fetchone()

                if not result:
                    print(f"❌ Skipped review because bank '{row['bank_name']}' does not exist in banks table")
                    skipped += 1
                    continue

                bank_id = result[0]

                # Insert review
                self.cur.execute("""
                    INSERT INTO reviews (
                        bank_id, review_text, rating, review_date,
                        sentiment_label, sentiment_score, source
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    bank_id,
                    row.get("review_text"),
                    row.get("rating"),
                    row.get("review_date"),
                    row.get("sentiment_label"),
                    row.get("sentiment_score"),
                    row.get("source"),
                ))
                count += 1

        self.conn.commit()
        print(f"Inserted {count} reviews.")
        print(f"Skipped {skipped} reviews due to unknown bank.")

    def close(self):
        """Close database connection"""
        self.cur.close()
        self.conn.close()
        print("Database connection closed.")
