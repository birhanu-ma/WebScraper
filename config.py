"""
Configuration file for Bank Reviews Analysis Project
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Play Store App IDs
APP_IDS = {
# env
    'CBE': os.getenv('CBE_APP_ID', 'com.combanketh.mobilebanking'),
    'Dashen': os.getenv('DASHEN_APP_ID', 'com.dashen.dashensuperapp'),
    'Abyssinia': os.getenv('BOA_APP_ID', 'com.boa.boaMobileBanking')

}

# Bank Names Mapping
BANK_NAMES = {
    'CBE': 'Commercial Bank of Ethiopia',
    'Dashen': 'Dashen Bank',
    'Abyssinia': 'Abyssinia'
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'reviews_per_bank': None,  # None means fetch all reviews
    'max_retries': int(os.getenv('MAX_RETRIES', 3)),
    'lang': 'en',
    'country': 'et'  # Ethiopia
}


# File Paths
DATA_PATHS = {
    'raw': 'data/raw',
    'processed': 'data/processed',
    'raw_reviews': 'data/raw/reviews_raw.csv',
    'processed_reviews': 'data/processed/reviews_processed.csv',
    'sentiment_results': 'data/processed/reviews_with_sentiment.csv',
    'final_results': 'data/processed/reviews_final.csv'
}









