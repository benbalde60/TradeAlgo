# aggregator.py
import time
from collections import deque
import numpy as np
from sentiment import score_text
from filter import is_bot_like, credibility_score

WINDOW_SECONDS = 30 * 60  # 30 minutes

class SentimentWindow:
    def __init__(self, window_seconds=WINDOW_SECONDS):
        self.window = window_seconds
        self.buffer = deque()  # (timestamp, score, cred, author_id)

    def add_post(self, text, account_meta, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        if is_bot_like(account_meta):
            return
        s = score_text(text)
        cred = credibility_score(account_meta)
        aid = account_meta.get("author_id", None)
        self.buffer.append((timestamp, s, cred, aid))
        self._evict_old(timestamp)

    def _evict_old(self, now):
        cutoff = now - self.window
        while self.buffer and self.buffer[0][0] < cutoff:
            self.buffer.popleft()

    def aggregate(self, now=None):
        if now is None:
            now = self.buffer[-1][0] if self.buffer else time.time()

        self._evict_old(now)

        if not self.buffer:
            return 0.0, 0

        scores = []
        weights = []
        authors = set()

        for ts, s, cred, aid in self.buffer:
            scores.append(s * cred)
            weights.append(cred)
            authors.add(aid)

        scores = np.array(scores)
        weights = np.array(weights) + 1e-9

        vw = float(scores.sum() / weights.sum())

        return vw, len(authors)