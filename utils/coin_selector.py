import requests

COINGECKO_API = "https://api.coingecko.com/api/v3"


def get_top_coins(limit=200):
    # Static fallback for major coins if rate limited
    return [
        {"symbol": "BTCUSDT", "coingecko_id": "bitcoin", "whale_symbol": "btc"},
        {"symbol": "ETHUSDT", "coingecko_id": "ethereum", "whale_symbol": "eth"},
        {"symbol": "SOLUSDT", "coingecko_id": "solana", "whale_symbol": "sol"},
        {"symbol": "LINKUSDT", "coingecko_id": "chainlink", "whale_symbol": "link"},
        {"symbol": "AVAXUSDT", "coingecko_id": "avalanche-2", "whale_symbol": "avax"}
    ]
