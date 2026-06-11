# events.py
def event_surprise(actual, consensus):
    """Numeric surprise (actual - consensus)."""
    try:
        return float(actual) - float(consensus)
    except Exception:
        return 0.0

def event_signal(significance, surprise):
    """Map significance to multiplier and return signed component."""
    mult_map = {"low": 0.5, "med": 1.0, "high": 1.8}
    mult = mult_map.get(significance, 1.0)
    sign = 1 if surprise > 0 else -1 if surprise < 0 else 0
    return mult * sign * abs(surprise)