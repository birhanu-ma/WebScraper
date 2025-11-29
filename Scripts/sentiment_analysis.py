
from transformers import pipeline
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
class SentimentAnalysis:
    def __init__(self):
        print("Initializing DistilBERT sentiment pipeline...")
        self.model = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )

    def analyze(self, text):
        try:
            result = self.model(text[:512])[0]
            return result['label'], result['score']
        except Exception:
            return "ERROR", 0.0

    # <-- instance method
    def extract_keywords(self, df, bank_col='bank_name', text_col='review_text', top_n=15, min_word_length=2):
          """
          Extract top meaningful keywords/phrases per bank using TF-IDF.
  
          Args:
              df: pandas DataFrame containing reviews.
              bank_col: column name for bank names.
              text_col: column name for review text.
              top_n: number of top keywords/phrases to return per bank.
              min_word_length: minimum number of words in a phrase (to prefer multi-word phrases).
  
          Returns:
              Dictionary with bank_name -> DataFrame of top keywords/phrases with TF-IDF scores.
          """
          bank_keywords = {}
          generic_words = {'app', 'bank', 'use', 'good', 'mobile', 'service', 'application'}
  
          for bank in df[bank_col].unique():
              bank_reviews = df[df[bank_col] == bank][text_col].values
  
              vectorizer = TfidfVectorizer(
                  stop_words='english',
                  ngram_range=(1, 3),  # unigrams, bigrams, trigrams
                  max_features=1000
              )
  
              X = vectorizer.fit_transform(bank_reviews)
              tfidf_scores = X.sum(axis=0).A1
              feature_names = vectorizer.get_feature_names_out()
  
              tfidf_df = pd.DataFrame({
                  'word': feature_names,
                  'tfidf': tfidf_scores
              }).sort_values(by='tfidf', ascending=False)
  
              # Filter out generic/common words
              tfidf_df = tfidf_df[~tfidf_df['word'].isin(generic_words)]
  
              # Keep only phrases with at least `min_word_length` words
              tfidf_df = tfidf_df[tfidf_df['word'].str.split().str.len() >= min_word_length]
  
              # Take top_n phrases
              tfidf_df = tfidf_df.head(top_n).reset_index(drop=True)
  
              bank_keywords[bank] = tfidf_df
  
          return bank_keywords