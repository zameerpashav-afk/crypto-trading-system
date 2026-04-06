import requests

def get_unlock_data(symbol):
    """
    Using CryptoRank public API (no key required for basic use)
    """
    url = "https://api.cryptorank.io/v1/currencies"
    
    params = {
        "limit": 100
    }

    data = requests.get(url, params=params).json()

    for coin in data.get("data", []):
        if coin["symbol"].lower() == symbol.lower():
            return {
                "unlock_percentage": coin.get("circulatingSupply", 0) / 
                                     (coin.get("totalSupply", 1) + 1e-9)
            }

    return {"unlock_percentage": 0}


def compute_unlock_score(symbol):
    data = get_unlock_data(symbol)

    unlock_pct = data["unlock_percentage"]

    if unlock_pct < 0.5:
        score = 0.8
    elif unlock_pct < 0.8:
        score = 0.5
    else:
        score = 0.2

    return {
        "score": score,
        "confidence": 0.65,
        "signals": data
    }
if __name__ == "__main__":
    result = compute_unlock_score("BTC")
    print(result)