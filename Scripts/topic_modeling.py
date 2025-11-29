import pandas as pd
import nltk
from nltk.corpus import stopwords
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel

nltk.download("stopwords")


class TopicModeling:
    """
    Handles:
    - text cleaning
    - tokenization + stopword removal
    - LDA topic modeling
    - auto-assigning 5 predefined themes per review
    """

    def __init__(self, num_topics=3, num_words=10):
        self.num_topics = num_topics
        self.num_words = num_words
        self.stop_words = set(stopwords.words("english"))
        self.dictionary = None
        self.lda_model = None

        # ---------------------------------------------------------
        # NEW: predefined themes + their keyword grouping logic
        # ---------------------------------------------------------
        self.theme_keywords = {
            "Account Access Issues": [
                "login", "log", "crash", "crashes", "error", "issue",
                "doesn", "work", "working", "not working", "fail",
                "open", "connect", "unable", "developer", "problem"
            ],
            "Transaction Performance": [
                "money", "transfer", "transaction", "send", "receive",
                "history", "slow", "processing", "telebirr", "payment"
            ],
            "User Interface & Experience": [
                "easy", "user", "friendly", "interface", "design",
                "navigation", "layout", "feature", "good app",
                "nice app", "mobile banking", "ui"
            ],
            "Customer Support": [
                "support", "help", "service", "customer", "complain",
                "contact", "response", "solve", "agent", "staff"
            ],
            "Feature Requests / General Satisfaction": [
                "best", "super", "love", "amazing", "great",
                "recommend", "request", "need", "feature",
                "option", "improve", "update"
            ],
        }

    # ---------------------------------------------------------
    # 1. CLEAN TEXT → lowercase, tokenize, remove stopwords
    # ---------------------------------------------------------
    def preprocess(self, df, text_col="review_text"):
        df["clean_text"] = df[text_col].str.lower()
        df["tokens"] = df["clean_text"].str.split()
        df["tokens_nostop"] = df["tokens"].apply(
            lambda words: [w for w in words if w not in self.stop_words]
        )
        return df

    # ---------------------------------------------------------
    # 2. Train LDA Topic Model
    # ---------------------------------------------------------
    def fit_lda(self, df):
        tokens = df["tokens_nostop"].tolist()
        self.dictionary = Dictionary(tokens)
        corpus = [self.dictionary.doc2bow(tok) for tok in tokens]

        self.lda_model = LdaModel(
            corpus=corpus,
            id2word=self.dictionary,
            num_topics=self.num_topics,
            passes=10,
            random_state=42,
        )

        return self.lda_model

    # ---------------------------------------------------------
    # 3. Return readable LDA topics with top words
    # ---------------------------------------------------------
    def get_topics(self):
        topics = self.lda_model.show_topics(
            num_topics=self.num_topics,
            num_words=self.num_words,
            formatted=False
        )

        output = {}
        for topic_id, words in topics:
            output[f"Topic_{topic_id}"] = [
                (word, float(weight)) for word, weight in words
            ]
        return output

    # ---------------------------------------------------------
    # 4. Assign LDA topic to each review
    # ---------------------------------------------------------
    def assign_review_topics(self, df):
        tokens = df["tokens_nostop"].tolist()
        corpus = [self.dictionary.doc2bow(tok) for tok in tokens]

        dominant_topics = []
        for bow in corpus:
            topic_probs = self.lda_model.get_document_topics(bow)
            dominant_topic = max(topic_probs, key=lambda x: x[1])[0]
            dominant_topics.append(dominant_topic)

        df["topic_id"] = dominant_topics
        return df

    # ---------------------------------------------------------
    # 5. NEW: Assign one of the 5 main human themes
    # ---------------------------------------------------------
    def map_to_theme(self, tokens):
        """
        Assign the theme that best matches the review tokens.
        """
        text = " ".join(tokens)

        for theme, keywords in self.theme_keywords.items():
            for k in keywords:
                if k in text:
                    return theme

        return "Other"

    # ---------------------------------------------------------
    # 6. NEW: Apply themes to all reviews
    # ---------------------------------------------------------
    def assign_themes(self, df):
        df["theme"] = df["tokens_nostop"].apply(self.map_to_theme)
        return df

    # ---------------------------------------------------------
    # 7. OPTIONAL: Attach custom names to LDA topics
    # ---------------------------------------------------------
    def label_topics(self, df, name_mapping: dict):
        df["topic_name"] = df["topic_id"].map(name_mapping)
        return df
