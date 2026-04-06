import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WHALE_ALERT_API_KEY")

BASE_URL = "https://api.whale-alert.io/v1/transactions"


def get_whale_transactions(symbol="btc", min_value=500000):
    params = {
        "api_key": API_KEY,
        "min_value": min_value,
        "currency": symbol.lower(),
        "limit": 50
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    return data.get("transactions", [])


def compute_whale_score(symbol):
    txs = get_whale_transactions(symbol)

    inflow = 0
    outflow = 0

    for tx in txs:
        to_owner = tx.get("to", {}).get("owner_type", "")
        from_owner = tx.get("from", {}).get("owner_type", "")
        amount = tx.get("amount_usd", 0)

        # Exchange inflow = bearish
        if to_owner == "exchange":
            inflow += amount

        # Exchange outflow = bullish
        if from_owner == "exchange":
            outflow += amount

    total = inflow + outflow + 1e-9

    inflow_ratio = inflow / total
    outflow_ratio = outflow / total

    score = max(0, min(outflow_ratio - inflow_ratio + 0.5, 1))

    return {
        "score": score,
        "confidence": 0.75,
        "signals": {
            "inflow_usd": inflow,
            "outflow_usd": outflow
        }
    }
if __name__ == "__main__":
    result = compute_whale_score("btc")
    print(result)