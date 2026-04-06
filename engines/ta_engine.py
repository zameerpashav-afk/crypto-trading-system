import requests
import pandas as pd
import ta

BINANCE_API = "https://api.binance.com/api/v3/klines"


def get_price_data(symbol="BTCUSDT", interval="5m", limit=100):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    data = requests.get(BINANCE_API, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df["close"] = df["close"].astype(float)
    return df


def compute_ta_score(symbol):
    df = get_price_data(symbol)

    # Indicators
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

    latest = df.iloc[-1]

    score = 0

    # RSI Logic
    if latest["rsi"] < 30:
        score += 0.4  # oversold (bullish)
    elif latest["rsi"] > 70:
        score -= 0.4  # overbought (bearish)

    # EMA Trend
    if latest["ema20"] > latest["ema50"]:
        score += 0.6  # bullish trend
    else:
        score -= 0.6  # bearish

    # Normalize score (0 to 1)
    score = (score + 1) / 2

    return {
        "score": round(score, 2),
        "confidence": 0.7,
        "signals": {
            "rsi": round(latest["rsi"], 2),
            "ema20": round(latest["ema20"], 2),
            "ema50": round(latest["ema50"], 2)
        }
    }


if __name__ == "__main__":
    result = compute_ta_score("BTCUSDT")
    print(result)