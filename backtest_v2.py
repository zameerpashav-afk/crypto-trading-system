import pandas as pd
from engines.ta_engine import compute_ta_score, get_price_data

def run_backtest(symbol="SOLUSDT"):
    print(f"--- Backtesting V2 Logic for {symbol} ---")
    
    # Get 500 candles of data
    df = get_price_data(symbol, interval="1h", limit=500)
    
    if df is None:
        print("Failed to fetch data.")
        return

    # Simulate running the TA engine over historical data
    results = []
    
    # We need a rolling window to simulate "live" scores at each point in time
    for i in range(50, len(df)):
        window = df.iloc[i-50:i].copy()
        
        # We manually apply the logic from ta_engine (simplified for the backtest)
        import ta
        window["rsi"] = ta.momentum.RSIIndicator(window["close"], window=14).rsi()
        window["ema20"] = ta.trend.EMAIndicator(window["close"], window=20).ema_indicator()
        window["ema50"] = ta.trend.EMAIndicator(window["close"], window=50).ema_indicator()
        
        latest = window.iloc[-1]
        score = 0
        
        # V2 Logic
        if latest["rsi"] < 30: score += 0.4
        elif 50 < latest["rsi"] < 65: score += 0.5
        elif latest["rsi"] > 70: score -= 0.4
        
        if latest["ema20"] > latest["ema50"]: score += 0.6
        else: score -= 0.6
        
        if latest["close"] > latest["ema20"]: score += 0.3
            
        final_score = (score + 1) / 2.4
        
        # Check if this triggered a signal
        if final_score > 0.65: # BUY threshold
            # Check price 24h later (24 candles)
            if i + 24 < len(df):
                price_now = latest["close"]
                price_future = df.iloc[i + 24]["close"]
                perf = (price_future - price_now) / price_now * 100
                results.append(perf)
                print(f"Signal at {df.iloc[i]['close_time']}: Price {price_now:.2f} -> 24h Perf: {perf:.2f}%")

    if results:
        avg_perf = sum(results) / len(results)
        win_rate = len([r for r in results if r > 0]) / len(results) * 100
        print(f"\n--- Summary ---")
        print(f"Total Signals: {len(results)}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Avg 24h Performance: {avg_perf:.2f}%")
    else:
        print("No signals generated in this period.")

if __name__ == "__main__":
    run_backtest("SOLUSDT")
