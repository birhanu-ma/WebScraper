"""
Google Play Store Review Scraper
Target: 400+ meaningful English reviews per bank
"""

import sys
import os
import re
from langdetect import detect, LangDetectException
from google_play_scraper import app, reviews_all
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from config import APP_IDS, BANK_NAMES, SCRAPING_CONFIG, DATA_PATHS
import time


class PlayStoreScraper:
    """Scraper class for Google Play Store reviews"""

    def __init__(self):
        self.app_ids = APP_IDS
        self.bank_names = BANK_NAMES
        self.min_reviews_per_bank = SCRAPING_CONFIG['reviews_per_bank'] or 400
        self.lang = SCRAPING_CONFIG['lang']
        self.country = SCRAPING_CONFIG['country']

    # -----------------------------
    # Text Cleaning
    # -----------------------------
    def clean_text(self, text):
        """Remove non-ASCII characters and extra whitespace"""
        text = re.sub(r"[^\x00-\x7F]+", " ", text)  # remove emojis and foreign chars
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # -----------------------------
    # Check if English and meaningful
    # -----------------------------
    def is_meaningful_english(self, text):
        """Return True if the text is English and meaningful"""
        text = self.clean_text(text)
        if len(text) < 8:  # skip very short reviews
            return False
        try:
            return detect(text) == "en"
        except LangDetectException:
            return False

    # -----------------------------
    # Fetch App Info
    # -----------------------------
    def get_app_info(self, app_id):
        try:
            result = app(app_id, lang=self.lang, country=self.country)
            return {
                'app_id': app_id,
                'title': result.get('title', 'N/A'),
                'score': result.get('score', 0),
                'ratings': result.get('ratings', 0),
                'reviews': result.get('reviews', 0),
                'installs': result.get('installs', 'N/A')
            }
        except Exception as e:
            print(f"Error getting app info for {app_id}: {e}")
            return None

    # -----------------------------
    # Scrape meaningful English reviews for a bank
    # -----------------------------
    def scrape_reviews_for_bank(self, app_id, bank_code):
        print(f"\n🔍 Scraping reviews for {self.bank_names[bank_code]}...")

        collected = []

        try:
            all_reviews = reviews_all(app_id, lang=self.lang, country=self.country)
            print(f"Total raw reviews fetched: {len(all_reviews)}")

            for review in all_reviews:
                text = review.get("content", "")
                if not self.is_meaningful_english(text):
                    continue

                collected.append({
                    'review_id': review.get('reviewId'),
                    'review_text': self.clean_text(text),
                    'rating': review.get('score', 0),
                    'review_date': review.get('at', datetime.now()),
                    'user_name': review.get('userName', 'Anonymous'),
                    'thumbs_up': review.get('thumbsUpCount', 0),
                    'reply_content': review.get('replyContent', None),
                    'bank_code': bank_code,
                    'bank_name': self.bank_names[bank_code],
                    'app_version': review.get('reviewCreatedVersion', 'N/A'),
                    'source': 'Google Play'
                    
                })

                if len(collected) >= self.min_reviews_per_bank:
                    break  # stop when we reach target

            print(f"✅ Collected {len(collected)} meaningful English reviews for {self.bank_names[bank_code]}")
            return collected

        except Exception as e:
            print(f"Error scraping {self.bank_names[bank_code]}: {e}")
            return []

    # -----------------------------
    # Scrape all banks
    # -----------------------------
    def scrape_all_banks(self):
        final_reviews = []
        app_info_list = []

        print("\n==============================================")
        print("Starting Google Play Review Scraper")
        print("==============================================\n")

        # Fetch app info
        print("[1/2] Fetching app info...")
        for bank_code, app_id in self.app_ids.items():
            info = self.get_app_info(app_id)
            if info:
                info['bank_code'] = bank_code
                info['bank_name'] = self.bank_names[bank_code]
                app_info_list.append(info)

        if app_info_list:
            os.makedirs(DATA_PATHS['raw'], exist_ok=True)
            pd.DataFrame(app_info_list).to_csv(f"{DATA_PATHS['raw']}/app_info.csv", index=False)
            print("App info saved.\n")

        # Scrape reviews
        print("[2/2] Scraping reviews...")
        for bank_code, app_id in tqdm(self.app_ids.items(), desc="Banks"):
            reviews_list = self.scrape_reviews_for_bank(app_id, bank_code)
            final_reviews.extend(reviews_list)
            time.sleep(2)  # polite delay

        # Save all reviews
        if final_reviews:
            df = pd.DataFrame(final_reviews)
            os.makedirs(DATA_PATHS['raw'], exist_ok=True)
            df.to_csv(DATA_PATHS['raw_reviews'], index=False)
            print("\n==============================================")
            print("Scraping Completed!")
            print("Total English reviews collected:", len(df))
            print("==============================================\n")
            return df

        print("ERROR: No reviews collected!")
        return pd.DataFrame()

    # -----------------------------
    # Display sample reviews
    # -----------------------------
    def display_sample_reviews(self, df, n=3):
        print("\n==============================================")
        print("Sample Reviews")
        print("==============================================")
        for bank_code in self.bank_names:
            bank_df = df[df['bank_code'] == bank_code]
            if not bank_df.empty:
                print(f"\n{self.bank_names[bank_code]}")
                print("-" * 60)
                for _, row in bank_df.head(n).iterrows():
                    print(f"\n⭐ Rating: {row['rating']}")
                    print(f"Review: {row['review_text'][:200]}...")
                    print(f"Date: {row['review_date']}")


# -----------------------------
# Main
# -----------------------------
def main():
    scraper = PlayStoreScraper()
    df = scraper.scrape_all_banks()
    if not df.empty:
        scraper.display_sample_reviews(df)
    return df


if __name__ == "__main__":
    main()
