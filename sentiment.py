# sentiment.py
from transformers import pipeline

# Lightweight sentiment pipeline; swap model for a finance-finetuned one if available.
# Note: first run will download model weights.
sentiment_pipe = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

def score_text(text):
    """Return sentiment score in [-1,1]."""
    if not text:
        return 0.0

    try:
        r = sentiment_pipe(text[:512])[0]
        label = r["label"]

        score = float(r["score"])

        if label == "LABEL_0":
            return -score
        elif label == "LABEL_2":
            return score
        else:
            return 0.0

    except Exception:
        return 0.0