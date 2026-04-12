# pipelines/run_pipeline.py

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import telegram

# Load env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
# FILTER (soft scoring)
# -------------------------
def passes_filters(whale, dev, unlock):
    filter_score = (
        whale * 0.5 +
        dev * 0.3 +
        unlock * 0.2
    )
    return filter_score > 0.25


# -------------------------
# SIGNAL ENGINE
# -------------------------
def generate_signal(score):
    if score > 0.75:
        return "STRONG BUY"
    elif score > 0.65:
        return "BUY"
    elif score > 0.50:
        return "WATCH"
    return "HOLD"


# -------------------------
# MAIN PIPELINE
# -------------------------
def run():

    coins = get_top_coins(limit=200)
    candidates = []

    print(f"\n🚀 Starting scan at {datetime.now()}")
    print(f"Scanning {len(coins)} coins...\n")

    for coin in coins:
        try:
            symbol = coin["symbol"]
            whale_symbol = coin["whale_symbol"]
            coin_id = coin["coingecko_id"]

            print(f"Checking {symbol}...")

            # -------------------------
            # TREND
            # -------------------------
            trend = compute_trend_score(symbol=whale_symbol, coin_id=coin_id)

            trend_score = trend["trend_score"]
            whale = trend["components"]["whale"]["score"]
            dev = trend["components"]["dev"]["score"]
            unlock = trend["components"]["unlock"]["score"]

            print(f"Scores → W:{whale:.2f} D:{dev:.2f} U:{unlock:.2f}")

            # Soft filter
            if not passes_filters(whale, dev, unlock):
                print("❌ Skipped (fundamentals weak)")
                continue

            # -------------------------
            # DEX
            # -------------------------
            dex = compute_dex_score(whale_symbol)
            dex_score = dex["score"]

            if dex_score < 0.1:
                print("❌ Skipped (DEX too low)")
                continue

            # -------------------------
            # TA (SAFE)
            # -------------------------
            ta = compute_ta_score(symbol)
            ta_score = ta["score"]

            # -------------------------
            # COMBINED SCORE
            # -------------------------
            combined_score = (
                trend_score * 0.45 +
                ta_score * 0.30 +
                dex_score * 0.15 +
                unlock * 0.10
            )

            # momentum boost
            if trend_score > 0.6 and ta_score > 0.6:
                combined_score += 0.05

            combined_score = min(combined_score, 1)

            signal = generate_signal(combined_score)

            print(f"✅ {symbol} → {combined_score:.2f} | {signal}")

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
            print(f"Error {symbol}: {e}")

    # -------------------------
    # TOP 5
    # -------------------------
    candidates = sorted(candidates, key=lambda x: x["combined_score"], reverse=True)
    top5 = candidates[:5]

    # BUY ONLY LIST
    buy_coins = [c for c in top5 if c["signal"] in ["BUY", "STRONG BUY"]]

    # -------------------------
    # TELEGRAM MESSAGE (ALWAYS SENT)
    # -------------------------
    message = f"""
📊 CRYPTO SCAN COMPLETE

Time: {datetime.now()}
Coins scanned: {len(coins)}
Candidates found: {len(candidates)}
Top 5: {len(top5)}
BUY signals: {len(buy_coins)}

-------------------------
"""

    if len(top5) > 0:
        message += "\n🔥 TOP 5 PICKS 🔥\n\n"
        for i, c in enumerate(top5, 1):
            message += (
                f"{i}. {c['symbol']}\n"
                f"Score: {c['combined_score']} | {c['signal']}\n"
                f"TA:{c['ta_score']} DEX:{c['dex_score']} UNLOCK:{c['unlock_score']}\n"
                "-------------------\n"
            )
    else:
        message += "\n⚠️ No valid coins found in this scan.\n"

    if len(buy_coins) > 0:
        message += "\n🚀 BUY SIGNALS 🚀\n\n"
        for c in buy_coins:
            message += f"{c['symbol']} → {c['combined_score']} ({c['signal']})\n"
    else:
        message += "\n⚠️ No BUY signals in this cycle.\nMarket is neutral.\n"

    # -------------------------
    # SEND TELEGRAM (ALWAYS)
    # -------------------------
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message[:4000])
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

            for c in top5:
                writer.writerow([
                    datetime.now(),
                    c["symbol"],
                    c["trend_score"],
                    c["ta_score"],
                    c["dex_score"],
                    c["unlock_score"],
                    c["combined_score"],
                    c["signal"]
                ])


# ENTRY
if __name__ == "__main__":
    run()