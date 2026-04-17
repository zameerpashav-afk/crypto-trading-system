import requests
import pandas as pd
import ta

BINANCE_API = "https://api.binance.com/api/v3/klines"


# -------------------------
# GET PRICE DATA (SAFE)
# -------------------------
def get_price_data(symbol="BTCUSDT", interval="5m", limit=100):
    try:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        data = requests.get(BINANCE_API, params=params, timeout=10).json()

        # 🚨 Safety check: API failure
        if not isinstance(data, list):
            return None

        if len(data) < 50:
            return None

        df = pd.DataFrame(data, columns=[
            "time","open","high","low","close","volume",
            "close_time","qav","trades","tbbav","tbqav","ignore"
        ])

        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df = df.dropna()

        if len(df) < 50:
            return None

        return df

    except Exception as e:
        print(f"Price data error for {symbol}: {e}")
        return None


# -------------------------
# TA SCORE ENGINE (SAFE)
# -------------------------
def compute_ta_score(symbol):
    df = get_price_data(symbol)

    # 🚨 Prevent crash
    if df is None or len(df) < 50:
        return {
            "score": 0,
            "confidence": 0,
            "signals": {
                "rsi": 0,
                "ema20": 0,
                "ema50": 0
            }
        }

    try:
        # Indicators
        df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
        df["ema20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
        df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

        df = df.dropna()

        latest = df.iloc[-1]

        score = 0

        # RSI Logic
        # V2 Improvement: Add points for bullish momentum (RSI > 50) 
        # instead of just looking for oversold (< 30)
        if latest["rsi"] < 30:
            score += 0.4
        elif 50 < latest["rsi"] < 65:
            score += 0.5  # Momentum zone
        elif latest["rsi"] > 70:
            score -= 0.4

        # EMA Trend
        if latest["ema20"] > latest["ema50"]:
            score += 0.6
        else:
            score -= 0.6

        # V2 Improvement: Price over EMA20 is a strong breakout signal
        if latest["close"] > latest["ema20"]:
            score += 0.3
        
        # Normalize (-1 → 1.4) into (0 → 1)
        # Max theoretical score is now 0.5 (RSI) + 0.6 (EMA) + 0.3 (Price) = 1.4
        score = (score + 1) / 2.4
        score = max(0, min(1, score))

        return {
            "score": round(score, 2),
            "confidence": 0.7,
            "signals": {
                "rsi": round(latest["rsi"], 2),
                "ema20": round(latest["ema20"], 2),
                "ema50": round(latest["ema50"], 2)
            }
        }

    except Exception as e:
        print(f"TA computation error for {symbol}: {e}")
        return {
            "score": 0,
            "confidence": 0,
            "signals": {}
        }


# -------------------------
# TEST ONLY (SAFE)
# -------------------------
if __name__ == "__main__":
    print(compute_ta_score("BTCUSDT"))