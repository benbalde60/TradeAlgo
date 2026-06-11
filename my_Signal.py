# signal.py
def compute_S(event_comp, vw_sentiment, novelty, tech_conf, weights=None):
    """
    Combine components into composite S.
    event_comp: numeric (signed)
    vw_sentiment: in [-1,1]
    novelty: >=0 (recommend scaling to [0,1])
    tech_conf: -1,0,1
    """
    if weights is None:
        weights = {"w1": 0.45, "w2": 0.25, "w3": 0.15, "w4": 0.15}
    # normalize event to [-1,1] heuristically (user should calibrate)
    e = max(min(event_comp, 1.0), -1.0)
    s = max(min(vw_sentiment, 1.0), -1.0)
    n = max(min(novelty, 1.0), 0.0)
    t = max(min(tech_conf, 1), -1)
    S = weights["w1"] * e + weights["w2"] * s + weights["w3"] * n + weights["w4"] * t
    return S

def decision_from_S(S, threshold=0.0001):
    if S > threshold:
        return "BUY", S
    if S < -threshold:
        return "SELL", S
    return "HOLD", S