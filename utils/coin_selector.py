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

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # Check if we got a list of coins (success) or an error dict
        if isinstance(data, list):
            coins = []
            for coin in data:
                coins.append({
                    "symbol": coin["symbol"].upper() + "USDT",
                    "coingecko_id": coin["id"],
                    "whale_symbol": coin["symbol"]
                })
            return coins
        
        print(f"⚠️ CoinGecko API busy (Rate Limited). Using major coin fallback...")
    except Exception as e:
        print(f"⚠️ Connection error: {e}. Using major coin fallback...")

    # Static fallback for major coins if API fails or rate limits
    return [
        {"symbol": "BTCUSDT", "coingecko_id": "bitcoin", "whale_symbol": "btc"},
        {"symbol": "ETHUSDT", "coingecko_id": "ethereum", "whale_symbol": "eth"},
        {"symbol": "SOLUSDT", "coingecko_id": "solana", "whale_symbol": "sol"},
        {"symbol": "LINKUSDT", "coingecko_id": "chainlink", "whale_symbol": "link"},
        {"symbol": "AVAXUSDT", "coingecko_id": "avalanche-2", "whale_symbol": "avax"},
        {"symbol": "BNBUSDT", "coingecko_id": "binancecoin", "whale_symbol": "bnb"},
        {"symbol": "ADAUSDT", "coingecko_id": "cardano", "whale_symbol": "ada"},
        {"symbol": "DOTUSDT", "coingecko_id": "polkadot", "whale_symbol": "dot"},
        {"symbol": "NEARUSDT", "coingecko_id": "near", "whale_symbol": "near"},
        {"symbol": "SUIUSDT", "coingecko_id": "sui", "whale_symbol": "sui"}
    ]
