#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GURU + RGB MATCHING BOT - 1 MIN WINGO
🧠 GURU: Period Digit Sum Based
🎨 RGB: 12-Step Pattern (Time-based)
✅ MATCH = GURU + RGB মিললে প্রেডিকশন
❌ NO MATCH = শুধু রেজাল্ট দেখাবে
"""

import asyncio
import time
import requests
import os
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

try:
    from telegram import Bot
    from telegram.error import TelegramError, TimedOut, NetworkError
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install python-telegram-bot")
    exit(1)

# ==================== কনফিগ ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ==================== ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GURU + RGB MATCHING BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

def keep_alive():
    while True:
        try:
            time.sleep(600)
            port = int(os.environ.get("PORT", 8080))
            requests.get(f"http://localhost:{port}/", timeout=5)
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ==================== বট ====================
bot = Bot(token=BOT_TOKEN)

# ==================== ডেটা ====================
total_wins = 0
total_losses = 0
total_jackpots = 0
total_rounds = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0

# শুধু MATCH এর স্ট্যাটস
match_wins = 0
match_losses = 0
match_rounds = 0
no_match_rounds = 0

hourly_wins = 0
hourly_losses = 0
hourly_rounds = 0
hourly_best_win_streak = 0
hourly_worst_loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_match_status = None
prediction_sent_for_period = {}
last_result_sent = False

# ============================================================
# 🧠 GURU ENGINE
# ============================================================
def guru_engine(period_number):
    """
    GURU: Period number digit sum based
    - Digit sum % 10 >= 5 → BIG
    - Digit sum % 10 < 5  → SMALL
    """
    str_period = str(period_number)
    digit_sum = sum(int(c) for c in str_period if c.isdigit())
    remainder = digit_sum % 10
    pred = "BIG" if remainder >= 5 else "SMALL"
    
    # Confidence
    if pred == "BIG":
        conf = 70 + (remainder - 5) * 3
    else:
        conf = 70 + (4 - remainder) * 3
    conf = min(95, max(55, conf))
    
    # Number prediction
    if pred == "BIG":
        num = 5 + (remainder % 5)  # 5-9
    else:
        num = remainder % 5  # 0-4
    
    return {
        "prediction": pred,
        "number": num,
        "confidence": conf,
        "reason": f"GURU (Remainder: {remainder})",
        "digit_sum": digit_sum,
        "remainder": remainder
    }

# ============================================================
# 🎨 RGB ENGINE (12-Step Time Based Pattern)
# ============================================================
RGB_PATTERN = [
    {"s": "BIG",   "n": 7},   # 0
    {"s": "SMALL", "n": 2},   # 1
    {"s": "SMALL", "n": 4},   # 2
    {"s": "BIG",   "n": 9},   # 3
    {"s": "BIG",   "n": 6},   # 4
    {"s": "SMALL", "n": 0},   # 5
    {"s": "BIG",   "n": 8},   # 6
    {"s": "SMALL", "n": 3},   # 7
    {"s": "SMALL", "n": 1},   # 8
    {"s": "BIG",   "n": 5},   # 9
    {"s": "BIG",   "n": 7},   # 10
    {"s": "SMALL", "n": 4}    # 11
]

def rgb_engine():
    now = datetime.now(timezone.utc)
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
    diff_seconds = (now - midnight).total_seconds()
    period_index = int(diff_seconds // 60) + 1
    pattern_index = (period_index + 5) % 12
    pred = RGB_PATTERN[pattern_index]
    return {
        "prediction": pred["s"],
        "number": pred["n"],
        "confidence": 85,
        "reason": f"RGB (Idx: {pattern_index})",
        "pattern_index": pattern_index
    }

# ============================================================
# 🔥 MASTER MATCHING ENGINE (GURU + RGB)
# ============================================================
def master_matching_engine(period_number):
    guru = guru_engine(period_number)
    rgb = rgb_engine()

    if guru['prediction'] == rgb['prediction']:
        # MATCH!
        return {
            'matched': True,
            'prediction': guru['prediction'],
            'number': guru['number'],
            'confidence': int((guru['confidence'] + rgb['confidence']) / 2),
            'guru': guru,
            'rgb': rgb,
            'status': "✅ MATCH FOUND",
            'status_icon': "🟢"
        }
    else:
        # NO MATCH
        return {
            'matched': False,
            'prediction': guru['prediction'],
            'number': guru['number'],
            'confidence': guru['confidence'],
            'guru': guru,
            'rgb': rgb,
            'status': "❌ NO MATCH",
            'status_icon': "🔴"
        }

# ==================== API ====================
def fetch_api_data():
    try:
        url = API_URL + "?t=" + str(int(time.time() * 1000))
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"API Error: {e}")
    return []

# ==================== Telegram সেন্ড ====================
async def send_message(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False

# ==================== হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global total_wins, total_losses, total_rounds, total_jackpots
    global best_win_streak, worst_loss_streak
    global match_wins, match_losses, match_rounds, no_match_rounds

    if hourly_rounds == 0:
        return

    hourly_win_rate = (hourly_wins / hourly_rounds * 100) if hourly_rounds > 0 else 0
    total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
    match_win_rate = (match_wins / match_rounds * 100) if match_rounds > 0 else 0

    report_msg = (
        f"📊 *HOURLY REPORT - GURU + RGB*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *TIME:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *HOURLY ROUNDS:* `{hourly_rounds}`\n"
        f"✅ *HOURLY WINS:* `{hourly_wins}`\n"
        f"❌ *HOURLY LOSSES:* `{hourly_losses}`\n"
        f"📈 *HOURLY WIN RATE:* `{hourly_win_rate:.1f}%`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *MATCH ROUNDS:* `{match_rounds}`\n"
        f"✅ *MATCH WINS:* `{match_wins}`\n"
        f"❌ *MATCH LOSSES:* `{match_losses}`\n"
        f"📈 *MATCH WIN RATE:* `{match_win_rate:.1f}%`\n"
        f"❌ *NO MATCH ROUNDS:* `{no_match_rounds}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *TOTAL ROUNDS:* `{total_rounds}`\n"
        f"✅ *TOTAL WINS:* `{total_wins}`\n"
        f"❌ *TOTAL LOSSES:* `{total_losses}`\n"
        f"💎 *JACKPOTS:* `{total_jackpots}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ GURU + RGB BOT"
    )

    await send_message(report_msg)

    hourly_wins = 0
    hourly_losses = 0
    hourly_rounds = 0
    hourly_best_win_streak = 0
    hourly_worst_loss_streak = 0

# ==================== মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_jackpots, total_rounds
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global current_streak, best_win_streak, worst_loss_streak
    global last_predicted_period, last_predicted_signal, last_predicted_num
    global last_match_status, prediction_sent_for_period, last_result_sent
    global match_wins, match_losses, match_rounds, no_match_rounds

    print("🔥 GURU + RGB MATCHING BOT STARTED...")
    print("🧠 ENGINE 1: GURU (Period Digit Sum)")
    print("🎨 ENGINE 2: RGB 12-STEP PATTERN")
    print("✅ MATCH = Send Prediction + Result")
    print("❌ NO MATCH = Send Result Only")
    print("📡 MODE: 1 MIN WINGO")

    await send_message(
        "🔥 *GURU + RGB MATCHING BOT* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *GURU ENGINE:*\n"
        "📌 Period Digit Sum Based\n"
        "📌 Sum % 10 ≥ 5 = BIG\n"
        "📌 Sum % 10 < 5 = SMALL\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎨 *RGB ENGINE:* 12-Step Time Pattern\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *MATCH* = Send Prediction + Result\n"
        "❌ *NO MATCH* = Send Result Only\n"
        "📡 *MODE:* 1 MIN WINGO\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ WAITING FOR FIRST SIGNAL..."
    )

    last_hour_time = time.time()

    while True:
        try:
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 3
            await asyncio.sleep(sleep_time)

            raw_list = fetch_api_data()
            if not raw_list:
                print("⚠️ API ডেটা নেই")
                continue

            history_data = []
            for h in raw_list[:20]:
                num = int(h['number'])
                history_data.append({
                    'issueNumber': str(h['issueNumber']),
                    'number': num,
                    'side': "BIG" if num >= 5 else "SMALL"
                })

            latest = history_data[0]
            latest_issue = latest['issueNumber']
            actual_num = latest['number']
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            print(f"📡 PERIOD: {latest_issue}, NUMBER: {actual_num}")

            # ==================== RESULT CHECK ====================
            if last_predicted_period == latest_issue and not last_result_sent:

                if last_match_status == 'match' and last_predicted_signal is not None:
                    # ============ MATCH এর রেজাল্ট ============
                    is_win = (last_predicted_signal == actual_type)
                    is_jackpot = (last_predicted_num == actual_num)

                    if is_jackpot:
                        total_jackpots += 1
                        total_wins += 1
                        match_wins += 1
                        hourly_wins += 1
                        status = "💎 JACKPOT"
                        if current_streak >= 0:
                            current_streak += 1
                        else:
                            current_streak = 1
                    elif is_win:
                        total_wins += 1
                        match_wins += 1
                        hourly_wins += 1
                        status = "✅ WIN"
                        if current_streak >= 0:
                            current_streak += 1
                        else:
                            current_streak = 1
                    else:
                        total_losses += 1
                        match_losses += 1
                        hourly_losses += 1
                        status = "❌ LOSS"
                        if current_streak <= 0:
                            current_streak -= 1
                        else:
                            current_streak = -1

                    if current_streak > best_win_streak:
                        best_win_streak = current_streak
                    if current_streak > hourly_best_win_streak:
                        hourly_best_win_streak = current_streak
                    if abs(current_streak) > worst_loss_streak and current_streak < 0:
                        worst_loss_streak = abs(current_streak)
                    if abs(current_streak) > hourly_worst_loss_streak and current_streak < 0:
                        hourly_worst_loss_streak = abs(current_streak)

                    total_rounds += 1
                    match_rounds += 1
                    hourly_rounds += 1

                    total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
                    streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"

                    result_msg = (
                        f"🎯 *RESULT UPDATE (MATCH)*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                        f"🎯 PREDICTED: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"📌 RESULT: `{status}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 WIN RATE: `{total_win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                        f"💎 JACKPOTS: `{total_jackpots}`\n"
                        f"{streak_emoji} STREAK: `{current_streak:+d}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ GURU + RGB BOT"
                    )

                    await send_message(result_msg)
                    print(f"📊 MATCH Result: {status}")

                else:
                    # ============ NO MATCH এর রেজাল্ট ============
                    no_match_rounds += 1

                    result_msg = (
                        f"🎯 *RESULT (NO MATCH)*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ NO MATCH - Prediction Skipped\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ GURU + RGB BOT"
                    )

                    await send_message(result_msg)
                    print(f"📊 NO MATCH Result sent")

                last_result_sent = True
                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None
                last_match_status = None

                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    last_hour_time = time.time()

            # ==================== NEW PREDICTION ====================
            next_period = str(int(latest_issue) + 1)

            if not prediction_sent_for_period.get(next_period, False):
                pred = master_matching_engine(next_period)

                last_match_status = 'match' if pred['matched'] else 'no_match'

                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"

                if pred['matched']:
                    # ============ MATCH FOUND - প্রেডিকশন পাঠাবে ============
                    prediction_msg = (
                        f"🔥 *GURU + RGB - 1M WINGO* 🔥\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ *MATCH FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 PREDICTION: `{pred['prediction']}`\n"
                        f"🔢 TARGET NUMBER: `{pred['number']}`\n"
                        f"⚡ CONFIDENCE: `{pred['confidence']}%`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']['prediction']}` ({pred['guru']['reason']})\n"
                        f"🎨 RGB: `{pred['rgb']['prediction']}` ({pred['rgb']['reason']})\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 DIGIT SUM: `{pred['guru']['digit_sum']}` | REM: `{pred['guru']['remainder']}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"{streak_emoji} STREAK: `{current_streak:+d}`\n"
                        f"📈 WIN RATE: `{(total_wins/total_rounds*100) if total_rounds > 0 else 0:.1f}%`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏳ RESULT AWAITING...\n"
                        f"⚡ GURU + RGB BOT"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = pred['prediction']
                    last_predicted_num = pred['number']
                    prediction_sent_for_period[next_period] = True
                    last_result_sent = False

                    await send_message(prediction_msg)
                    print(f"✅ MATCH Prediction: {next_period} → {pred['prediction']} ({pred['number']})")

                else:
                    # ============ NO MATCH - প্রেডিকশন পাঠাবে না ============
                    no_match_msg = (
                        f"❌ *NO MATCH*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']['prediction']}` ({pred['guru']['reason']})\n"
                        f"🎨 RGB: `{pred['rgb']['prediction']}` ({pred['rgb']['reason']})\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ NO MATCH FOUND\n"
                        f"⏳ RESULT WILL BE SHOWN...\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ GURU + RGB BOT"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = None
                    last_predicted_num = None
                    prediction_sent_for_period[next_period] = True
                    last_result_sent = False

                    await send_message(no_match_msg)
                    print(f"❌ NO MATCH: {next_period}")

                if len(prediction_sent_for_period) > 10:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 GURU + RGB MATCHING BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 GURU: Period Digit Sum Based")
    print("🎨 RGB: 12-Step Pattern")
    print("✅ MATCH = Send Prediction + Result")
    print("❌ NO MATCH = Send Result Only")
    print("📡 MODE: 1 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    print(f"🤖 BOT: @rakiiibahmed")
    print(f"📡 CHAT ID: {CHAT_ID}")

    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")