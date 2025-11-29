import sys
import os

# -----------------------------
# Ensure project root is in sys.path
# -----------------------------
project_root = os.path.abspath(os.path.dirname(__file__))  # WebScraper folder
if project_root not in sys.path:
    sys.path.append(project_root)

# -----------------------------
# Imports
# -----------------------------
from models.tables import create_tables
from Scripts.csv_loader import BankReviewLoader

# -----------------------------
# Main function
# -----------------------------
def main():
    # Step 1: Create tables
    create_tables()

    # Step 2: Load CSV data
    loader = BankReviewLoader()
    loader.load_banks_csv(os.path.join(project_root, "data/raw/app_info.csv"))
    loader.load_reviews_csv(os.path.join(project_root, "data/final_reviews_analysis.csv"))
    loader.close()

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    main()
