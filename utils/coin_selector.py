import requests

COINGECKO_API = "https://api.coingecko.com/api/v3"


def get_top_coins(limit=200):
    url = f"{COINGECKO_API}/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1
    }

    data = requests.get(url, params=params).json()

    coins = []

    for coin in data:
        coins.append({
            "symbol": coin["symbol"].upper() + "USDT",
            "coingecko_id": coin["id"],
            "whale_symbol": coin["symbol"]
        })

    return coins