# engines/trend_engine.py
from .whale_tracker import compute_whale_score
from .dev_activity import compute_dev_score
from .unlock_tracker import compute_unlock_score

def compute_trend_score(symbol, coin_id):
    """
    symbol: e.g. 'btc' for whale tracker
    coin_id: e.g. 'bitcoin' for dev activity / unlock tracker
    """
    # Get scores from engines
    whale_result = compute_whale_score(symbol)
    dev_result = compute_dev_score(coin_id)
    unlock_result = compute_unlock_score(symbol)

    # Extract numeric scores (adjust keys if needed)
    whale_score = whale_result.get("score", 0)
    dev_score = dev_result.get("score", 0)
    unlock_score = unlock_result.get("score", 0)

    # Compute weighted trend score
    trend_score = whale_score * 0.4 + dev_score * 0.4 + unlock_score * 0.2

    # Return results
    return {
        "trend_score": trend_score,
        "components": {
            "whale": whale_result,
            "dev": dev_result,
            "unlock": unlock_result
        }
    }

# Optional: quick test
if __name__ == "__main__":
    result = compute_trend_score("btc", "bitcoin")
    print(result)