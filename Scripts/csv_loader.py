import csv
import sys
import os

# Add project root (WebScraper) to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Import get_connection from db_config
from config.db_config import get_connection
class BankReviewLoader:
    def __init__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()

    def load_banks_csv(self, csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Insert banks safely
                self.cur.execute("""
                    INSERT INTO banks (bank_name, app_name)
                    VALUES (%s, %s)
                """, (
                    row["bank_name"],  # from your CSV
                    row["title"]       # mapped to app_name column
                ))
                count += 1
        self.conn.commit()
        print(f"Inserted {count} rows into banks table.")

    def load_reviews_csv(self, csv_path):
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
        self.cur.close()
        self.conn.close()

