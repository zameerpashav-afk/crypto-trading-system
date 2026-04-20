import requests

COINGECKO_API = "https://api.coingecko.com/api/v3"


def get_top_coins(limit=200):
    # 1. First, try to get Binance Top Gainers/Active coins to catch "hot" opportunities
    try:
        binance_data = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
        # Filter for USDT pairs and sort by priceChangePercent
        hot_coins = [
            {
                "symbol": t["symbol"],
                "coingecko_id": t["symbol"].replace("USDT", "").lower(), # Heuristic
                "whale_symbol": t["symbol"].replace("USDT", "").lower()
            }
            for t in binance_data 
            if t["symbol"].endswith("USDT") and float(t["quoteVolume"]) > 1000000
        ]
        hot_coins = sorted(hot_coins, key=lambda x: next(t["priceChangePercent"] for t in binance_data if t["symbol"] == x["symbol"]), reverse=True)
        # We take the top 20 hot coins to prioritize
        hot_list = hot_coins[:20]
    except Exception as e:
        print(f"⚠️ Binance hot-scan error: {e}")
        hot_list = []

    # 2. Then try CoinGecko for market cap depth
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
            coins = hot_list # Start with hot coins
            seen = {c["symbol"] for c in coins}
            for coin in data:
                sym = coin["symbol"].upper() + "USDT"
                if sym not in seen:
                    coins.append({
                        "symbol": sym,
                        "coingecko_id": coin["id"],
                        "whale_symbol": coin["symbol"]
                    })
                    seen.add(sym)
            return coins[:limit]
        
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
