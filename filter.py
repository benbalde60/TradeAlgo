# filter.py
def is_bot_like(account_meta):
    """Basic bot heuristics."""
    posts_per_day = account_meta.get("posts_per_day", 0)
    followers = account_meta.get("followers", 0)
    return posts_per_day > 200 or followers < 2

def credibility_score(account_meta):
    """Simple 0..1 credibility score."""
    followers = account_meta.get("followers", 0)
    account_age_days = account_meta.get("account_age_days", 0)
    verified = account_meta.get("verified", False)
    f = min(followers / 10000.0, 1.0)
    age = min(account_age_days / 3650.0, 1.0)
    v = 1.0 if verified else 0.0
    return 0.5 * f + 0.4 * age + 0.1 * v