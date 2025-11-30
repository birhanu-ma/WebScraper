import pandas as pd
import sys, os
from config.db_config import get_connection

# go 1 level up: notebooks → project root
project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_root)

def load_reviews():
    conn = get_connection()

    query = """
    SELECT 
        r.review_id,
        r.bank_id,
        b.bank_name,
        b.app_name,
        r.review_text,
        r.rating,
        r.review_date,
        r.sentiment_label,
        r.sentiment_score,
        r.source,
        r.themes   -- if you stored themes
    FROM reviews r
    JOIN banks b ON r.bank_id = b.bank_id
    ORDER BY r.review_id;
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df
