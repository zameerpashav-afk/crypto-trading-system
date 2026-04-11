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

# Safety check (GitHub Actions safe fail)
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Missing Telegram credentials")
    exit()

bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Engines
from engines.trend_engine import compute_trend_score
from engines.ta_engine import compute_ta_score
from engines.dex_scanner import compute_dex_score
from utils.coin_selector import get_top_coins


# -------------------------
# FILTER FUNCTION (IMPROVED)
# -------------------------
def passes_filters(whale, dev, unlock):
    filter_score = (
        whale * 0.4 +
        dev * 0.4 +
        unlock * 0.2
    )
    return filter_score > 0.35


# -------------------------
# SIGNAL FUNCTION
# -------------------------
def generate_signal(score):
    if score > 0.8:
        return "STRONG BUY"
    elif score > 0.7:
        return "BUY"
    elif score > 0.55:
        return "WATCH"
    else:
        return "HOLD"


# -------------------------
# MAIN PIPELINE
# -------------------------
def run():
    candidates = []

    coins = get_top_coins(limit=50)

    for coin in coins:
        try:
            symbol = coin["symbol"]
            whale_symbol = coin["whale_symbol"]
            coin_id = coin["coingecko_id"]

            print(f"\nChecking {symbol}...")

            # -------------------------
            # TREND ENGINE
            # -------------------------
            trend = compute_trend_score(symbol=whale_symbol, coin_id=coin_id)

            trend_score = trend["trend_score"]

            whale = trend["components"]["whale"]["score"]
            dev = trend["components"]["dev"]["score"]
            unlock = trend["components"]["unlock"]["score"]

            print(f"Scores → Whale: {whale:.2f} | Dev: {dev:.2f} | Unlock: {unlock:.2f}")

            # -------------------------
            # FILTERING (SOFT)
            # -------------------------
            if not passes_filters(whale, dev, unlock):
                print("❌ Skipped (weak fundamentals)")
                continue

            # -------------------------
            # DEX SCANNER
            # -------------------------
            try:
                dex = compute_dex_score(whale_symbol)
                dex_score = dex["score"]
            except Exception as e:
                print("DEX error:", e)
                dex_score = 0

            print(f"DEX Score → {dex_score:.2f}")

            # Soft DEX requirement (NOT strict)
            if dex_score < 0.15:
                print("❌ Skipped (low DEX activity)")
                continue

            # -------------------------
            # TECHNICAL ANALYSIS
            # -------------------------
            ta = compute_ta_score(symbol)
            ta_score = ta["score"]

            # -------------------------
            # COMBINED SCORE (IMPROVED)
            # -------------------------
            combined_score = (
                trend_score * 0.45 +
                ta_score * 0.30 +
                dex_score * 0.15 +
                unlock * 0.10
            )

            # Momentum boost
            if trend_score > 0.6 and ta_score > 0.6:
                combined_score += 0.05

            combined_score = min(combined_score, 1)

            signal = generate_signal(combined_score)

            print(f"✅ Candidate → Score: {combined_score:.2f} | Signal: {signal}")

            candidates.append({
                "symbol": symbol,
                "trend_score": round(trend_score, 2),
                "ta_score": round(ta_score, 2),
                "dex_score": round(dex_score, 2),
                "unlock_score": round(unlock, 2),
                "combined_score": round(combined_score, 2),
                "signal": signal
            })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    # -------------------------
    # SORT + TOP 5
    # -------------------------
    candidates = sorted(candidates, key=lambda x: x["combined_score"], reverse=True)
    top5 = candidates[:5]

    print("\n==============================")

    # -------------------------
    # TELEGRAM MESSAGE
    # -------------------------
    if not top5:
        message = "⚠️ Bot running but no strong signals found (market quiet)"
        print(message)
    else:
        print("🔥 TOP 5 PICKS 🔥")

        message = "🚀 TOP CRYPTO SIGNALS 🚀\n\n"

        for i, coin in enumerate(top5, 1):
            line = (
                f"{i}. {coin['symbol']}\n"
                f"Score: {coin['combined_score']} | Signal: {coin['signal']}\n"
                f"Trend: {coin['trend_score']} | TA: {coin['ta_score']} | "
                f"DEX: {coin['dex_score']} | Unlock: {coin['unlock_score']}\n"
                "-------------------------\n"
            )

            print(line)
            message += line

    # Trim message for Telegram safety
    message = message[:4000]

    # -------------------------
    # SEND TELEGRAM
    # -------------------------
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Telegram sent")
    except Exception as e:
        print("❌ Telegram error:", e)

    # -------------------------
    # SAVE TOP 5
    # -------------------------
    if top5:
        with open("top5_signals.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "datetime", "symbol", "trend_score",
                "ta_score", "dex_score", "unlock_score",
                "combined_score", "signal"
            ])
            for coin in top5:
                writer.writerow([
                    datetime.now(),
                    coin["symbol"],
                    coin["trend_score"],
                    coin["ta_score"],
                    coin["dex_score"],
                    coin["unlock_score"],
                    coin["combined_score"],
                    coin["signal"]
                ])


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    run()