import requests

DEX_API = "https://api.dexscreener.com/latest/dex/search"


def get_dex_data(query="usdt"):
    url = f"{DEX_API}?q={query}"
    data = requests.get(url).json()
    return data.get("pairs", [])


def compute_dex_score(symbol):
    pairs = get_dex_data(symbol)

    if not pairs:
        return {"score": 0, "confidence": 0, "signals": {}}

    # Take top pair
    pair = pairs[0]

    volume = float(pair.get("volume", {}).get("h24", 0))
    liquidity = float(pair.get("liquidity", {}).get("usd", 0))
    price_change = float(pair.get("priceChange", {}).get("h24", 0))

    score = 0

    # Volume spike
    if volume > 1_000_000:
        score += 0.4

    # Liquidity strength
    if liquidity > 500_000:
        score += 0.3

    # Price momentum
    if price_change > 5:
        score += 0.3

    return {
        "score": min(score, 1),
        "confidence": 0.7,
        "signals": {
            "volume": volume,
            "liquidity": liquidity,
            "price_change": price_change
        }
    }


if __name__ == "__main__":
    print(compute_dex_score("ETH"))