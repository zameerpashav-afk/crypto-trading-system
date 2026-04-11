# pipelines/run_pipeline.py

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import telegram

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Imports for engines
from engines.trend_engine import compute_trend_score
from engines.ta_engine import compute_ta_score
from engines.dex_scanner import compute_dex_score
from utils.coin_selector import get_top_coins

# -------------------------
# FILTER FUNCTION (UPDATED)
# -------------------------
def passes_filters(trend):
    whale = trend["components"]["whale"]["score"]
    dev = trend["components"]["dev"]["score"]
    unlock = trend["components"]["unlock"]["score"]

    # Weighted score instead of strict filtering
    filter_score = (
        whale * 0.4 +
        dev * 0.4 +
        unlock * 0.2
    )

    # Lower threshold → more signals
    return filter_score > 0.35


# -------------------------
# SIGNAL FUNCTION
# -------------------------
def generate_signal(combined_score):
    if combined_score > 0.7:
        return "BUY"
    elif combined_score > 0.55:
        return "WATCH"
    else:
        return "HOLD"


# -------------------------
# MAIN PIPELINE
# -------------------------
def run():
    candidates = []

    # Get top coins
    coins = get_top_coins(limit=100)

    for coin in coins:
        try:
            symbol = coin["symbol"]
            whale_symbol = coin["whale_symbol"]
            coin_id = coin["coingecko_id"]

            print(f"\nChecking {symbol}...")

            # TREND
            trend = compute_trend_score(symbol=whale_symbol, coin_id=coin_id)
            trend_score = trend["trend_score"]

            whale = trend["components"]["whale"]["score"]
            dev = trend["components"]["dev"]["score"]
            unlock = trend["components"]["unlock"]["score"]

            print(f"Scores → Whale: {whale} | Dev: {dev} | Unlock: {unlock}")

            # FILTER
            if not passes_filters(trend):
                print("❌ Skipped (low combined fundamentals)")
                continue

            # DEX (NO HARD FILTER)
            dex = compute_dex_score(whale_symbol)
            print(f"DEX Score → {dex['score']}")

            # TA
            ta = compute_ta_score(symbol)
            ta_score = ta["score"]

            # FINAL SCORE
            combined_score = (
                trend_score * 0.5 +
                ta_score * 0.3 +
                dex["score"] * 0.2
            )

            signal = generate_signal(combined_score)

            candidates.append({
                "symbol": symbol,
                "trend_score": round(trend_score, 2),
                "ta_score": round(ta_score, 2),
                "dex_score": round(dex["score"], 2),
                "combined_score": round(combined_score, 2),
                "signal": signal
            })

            print(f"✅ Candidate → Combined: {combined_score:.2f} | Signal: {signal}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    # -------------------------
    # TOP 5 RANKING
    # -------------------------
    top5 = sorted(candidates, key=lambda x: x["combined_score"], reverse=True)[:5]

    message = ""

    if not top5:
        print("\n⚠️ No strong coins found.")
        message = "⚠️ Bot running but no strong signals found (market quiet)"
    else:
        print("\n🔥 TOP 5 PICKS 🔥")
        message = "🔥 TOP 5 CRYPTO ALERTS 🔥\n"

        for coin in top5:
            line = (
                f"{coin['symbol']} | "
                f"Trend: {coin['trend_score']} | "
                f"TA: {coin['ta_score']} | "
                f"DEX: {coin['dex_score']} | "
                f"Signal: {coin['signal']}"
            )
            print(line)
            message += line + "\n"

    # -------------------------
    # TELEGRAM (SAFE SEND)
    # -------------------------
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Telegram sent")
    except Exception as e:
        print("❌ Telegram error:", e)

    # -------------------------
    # SAVE CSV
    # -------------------------
    if top5:
        filename = "top5_signals.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "datetime", "symbol", "trend_score",
                "ta_score", "dex_score", "combined_score", "signal"
            ])
            for coin in top5:
                writer.writerow([
                    datetime.now(),
                    coin["symbol"],
                    coin["trend_score"],
                    coin["ta_score"],
                    coin["dex_score"],
                    coin["combined_score"],
                    coin["signal"]
                ])


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    run()