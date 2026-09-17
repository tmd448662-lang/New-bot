#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GURU + RGB + DARK X V3 + SHIKAARI - MAJORITY VOTE BOT
🧠 ENGINE 1: GURU (Period Digit Sum)
🎨 ENGINE 2: RGB (12-Step Pattern)
🔥 ENGINE 3: DARK X V3 (Hybrid)
🎯 ENGINE 4: SHIKAARI BOSS (Last-1 / 11-Last)
🗳️ MAJORITY VOTE: 2/4 → Send Prediction
⏭️ TIE (2-2) → SKIP
📊 HOURLY REPORT
"""

import asyncio
import time
import requests
import os
import random
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
        self.wfile.write(b"4-ENGINE MAJORITY VOTE BOT is running!")

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
total_skips = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0
current_level = 1
consecutive_losses = 0

# Hourly Stats
hourly_wins = 0
hourly_losses = 0
hourly_rounds = 0
hourly_skips = 0
hourly_best_win_streak = 0
hourly_worst_loss_streak = 0
hourly_current_streak = 0
hourly_current_streak_type = "WIN"
hourly_jackpots = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_skip_status = False
prediction_sent_for_period = {}
last_result_sent = False
last_hour_report_time = time.time()

# ============================================================
# 🧠 ENGINE 1: GURU
# ============================================================
def guru_engine(period_number):
    str_period = str(period_number)
    digit_sum = sum(int(c) for c in str_period if c.isdigit())
    remainder = digit_sum % 10
    pred = "BIG" if remainder >= 5 else "SMALL"
    
    if pred == "BIG":
        conf = 70 + (remainder - 5) * 3
        num = 5 + (remainder % 5)
    else:
        conf = 70 + (4 - remainder) * 3
        num = remainder % 5
    
    conf = min(95, max(55, conf))
    
    return {
        "prediction": pred,
        "number": num,
        "confidence": conf,
        "reason": f"GURU (Rem: {remainder})"
    }

# ============================================================
# 🎨 ENGINE 2: RGB
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
        "reason": f"RGB (Idx: {pattern_index})"
    }

# ============================================================
# 🔥 ENGINE 3: DARK X V3
# ============================================================
def alternating_engine(types):
    if len(types) < 4:
        return None
    last4 = types[:4]
    if last4 == ["BIG", "SMALL", "BIG", "SMALL"]:
        return {"prediction": "BIG", "confidence": 88, "reason": "DARKX-ALT"}
    elif last4 == ["SMALL", "BIG", "SMALL", "BIG"]:
        return {"prediction": "SMALL", "confidence": 88, "reason": "DARKX-ALT"}
    return None

def trend_engine(types):
    if len(types) < 5:
        return None
    recent5 = types[:5]
    big_count = recent5.count("BIG")
    small_count = recent5.count("SMALL")
    if big_count >= 4:
        return {"prediction": "BIG", "confidence": 85 if big_count == 5 else 80,
                "reason": f"DARKX-TREND ({big_count}B-{small_count}S)"}
    elif small_count >= 4:
        return {"prediction": "SMALL", "confidence": 85 if small_count == 5 else 80,
                "reason": f"DARKX-TREND ({big_count}B-{small_count}S)"}
    return None

def markov_engine(data, level):
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50, "number": 7, "reason": "DARKX-MARKOV"}
    types = [d['side'] for d in data[:10]]
    last1 = types[0] if len(types) > 0 else "BIG"
    last2 = types[1] if len(types) > 1 else "BIG"
    
    if last1 == "SMALL":
        pred, conf = "BIG", 75
    else:
        pred, conf = "SMALL", 60
    
    if last1 == "BIG" and last2 == "BIG":
        pred, conf = "SMALL", 90
    elif last1 == "SMALL" and last2 == "SMALL":
        pred, conf = "BIG", 95
    elif last1 == "SMALL" and last2 == "BIG":
        pred, conf = "BIG", 70
    elif last1 == "BIG" and last2 == "SMALL":
        pred, conf = "BIG", 85
    
    if level >= 3 and len(data) > 0:
        latest_num = data[0]['number']
        pred = "SMALL" if latest_num >= 5 else "BIG"
        conf = 99
    
    num = random.randint(5, 9) if pred == "BIG" else random.randint(0, 4)
    return {"prediction": pred, "confidence": conf, "number": num, "reason": "DARKX-MARKOV"}

def loss_breaker_engine(data, level, consec_losses):
    if consec_losses < 3:
        return None
    markov = markov_engine(data, level)
    if consec_losses % 2 == 1:
        pred = "SMALL" if markov['prediction'] == "BIG" else "BIG"
        reason = f"DARKX-LOSSBREAKER"
    else:
        pred = markov['prediction']
        reason = f"DARKX-LOSSBREAKER"
    
    num = random.randint(5, 9) if pred == "BIG" else random.randint(0, 4)
    return {"prediction": pred, "confidence": min(99, markov['confidence'] + 5),
            "number": num, "reason": reason}

def dark_x_engine(data, level, consec_losses):
    if len(data) < 3:
        num = random.randint(5, 9)
        return {"prediction": "BIG", "confidence": 50, "number": num, "reason": "DARKX-INIT"}
    
    types = [d['side'] for d in data]
    
    alt = alternating_engine(types)
    if alt:
        num = random.randint(5, 9) if alt['prediction'] == "BIG" else random.randint(0, 4)
        return {"prediction": alt['prediction'], "confidence": alt['confidence'],
                "number": num, "reason": alt['reason']}
    
    trend = trend_engine(types)
    if trend:
        num = random.randint(5, 9) if trend['prediction'] == "BIG" else random.randint(0, 4)
        return {"prediction": trend['prediction'], "confidence": trend['confidence'],
                "number": num, "reason": trend['reason']}
    
    if consec_losses >= 3:
        lb = loss_breaker_engine(data, level, consec_losses)
        if lb:
            return lb
    
    return markov_engine(data, level)

# ============================================================
# 🎯 ENGINE 4: SHIKAARI BOSS
# ============================================================
def shikaari_engine(history_numbers):
    if len(history_numbers) < 2:
        return {
            "prediction": "BIG",
            "number": 7,
            "confidence": 50,
            "reason": "SHIKAARI (Init)"
        }
    
    last = history_numbers[0]
    prev = history_numbers[1]
    
    if last == prev:
        result = 11 - last
        if result > 9:
            result = result - 10
        rule = "SHIKAARI-REPEAT (11-L)"
    else:
        result = last - 1
        if result < 0:
            result = 9
        rule = "SHIKAARI-NORMAL (L-1)"
    
    return {
        "prediction": "BIG" if result >= 5 else "SMALL",
        "number": result,
        "confidence": 80,
        "reason": rule,
        "last": last,
        "prev": prev
    }

# ============================================================
# 🗳️ MAJORITY VOTE SYSTEM (4 ENGINES)
# ============================================================
def majority_vote_engine(period_number, data, level, consec_losses, history_numbers):
    guru = guru_engine(period_number)
    rgb = rgb_engine()
    dark_x = dark_x_engine(data, level, consec_losses)
    shikaari = shikaari_engine(history_numbers)
    
    # ভোট
    votes = {"BIG": 0, "SMALL": 0}
    votes[guru['prediction']] += 1
    votes[rgb['prediction']] += 1
    votes[dark_x['prediction']] += 1
    votes[shikaari['prediction']] += 1
    
    # Tie Check (2-2)
    is_tie = (votes["BIG"] == 2 and votes["SMALL"] == 2)
    
    if is_tie:
        return {
            'skip': True,
            'votes': votes,
            'guru': guru,
            'rgb': rgb,
            'dark_x': dark_x,
            'shikaari': shikaari,
            'prediction': None,
            'number': None,
            'confidence': 0
        }
    
    # Majority Winner
    if votes["BIG"] > votes["SMALL"]:
        final_pred = "BIG"
    else:
        final_pred = "SMALL"
    
    # Confidence
    if votes[final_pred] == 4:
        final_conf = 95
    elif votes[final_pred] == 3:
        final_conf = 88
    else:
        final_conf = 75
    
    # Number Selection
    num_candidates = []
    if guru['prediction'] == final_pred:
        num_candidates.append(guru['number'])
    if rgb['prediction'] == final_pred:
        num_candidates.append(rgb['number'])
    if dark_x['prediction'] == final_pred:
        num_candidates.append(dark_x['number'])
    if shikaari['prediction'] == final_pred:
        num_candidates.append(shikaari['number'])
    
    final_num = num_candidates[0] if num_candidates else guru['number']
    
    return {
        'skip': False,
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'votes': votes,
        'guru': guru,
        'rgb': rgb,
        'dark_x': dark_x,
        'shikaari': shikaari
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
    global hourly_wins, hourly_losses, hourly_rounds, hourly_skips
    global hourly_best_win_streak, hourly_worst_loss_streak
    global hourly_current_streak, hourly_current_streak_type, hourly_jackpots
    global total_wins, total_losses, total_rounds, total_jackpots, total_skips
    global best_win_streak, worst_loss_streak
    global last_hour_report_time

    if hourly_rounds == 0 and hourly_skips == 0:
        return

    hourly_win_rate = (hourly_wins / hourly_rounds * 100) if hourly_rounds > 0 else 0
    total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0

    report_msg = (
        f"📊 *HOURLY REPORT - GURU+RGB+DARKX+SHIKAARI (1M)*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *TIME:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *HOURLY ROUNDS:* `{hourly_rounds}`\n"
        f"✅ *HOURLY WINS:* `{hourly_wins}`\n"
        f"❌ *HOURLY LOSSES:* `{hourly_losses}`\n"
        f"📈 *HOURLY WIN RATE:* `{hourly_win_rate:.1f}%`\n"
        f"🔥 *BEST WIN STREAK:* `{hourly_best_win_streak}x`\n"
        f"📉 *WORST LOSS STREAK:* `{hourly_worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *TOTAL ROUNDS:* `{total_rounds}`\n"
        f"✅ *TOTAL WINS:* `{total_wins}`\n"
        f"❌ *TOTAL LOSSES:* `{total_losses}`\n"
        f"💎 *JACKPOTS:* `{total_jackpots}`\n"
        f"📈 *TOTAL WIN RATE:* `{total_win_rate:.1f}%`\n"
        f"🔥 *BEST WIN STREAK:* `{best_win_streak}x`\n"
        f"📉 *WORST LOSS STREAK:* `{worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ GURU + RGB + DARK X V3 + SHIKAARI"
    )

    await send_message(report_msg)

    hourly_wins = 0
    hourly_losses = 0
    hourly_rounds = 0
    hourly_skips = 0
    hourly_best_win_streak = 0
    hourly_worst_loss_streak = 0
    hourly_current_streak = 0
    hourly_current_streak_type = "WIN"
    hourly_jackpots = 0
    last_hour_report_time = time.time()

# ==================== মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_jackpots, total_rounds, total_skips
    global hourly_wins, hourly_losses, hourly_rounds, hourly_skips
    global hourly_best_win_streak, hourly_worst_loss_streak
    global hourly_current_streak, hourly_current_streak_type, hourly_jackpots
    global current_streak, best_win_streak, worst_loss_streak
    global current_level, consecutive_losses
    global last_predicted_period, last_predicted_signal, last_predicted_num
    global last_skip_status, prediction_sent_for_period, last_result_sent
    global last_hour_report_time

    print("🔥 4-ENGINE MAJORITY VOTE BOT STARTED...")
    print("🧠 ENGINE 1: GURU")
    print("🎨 ENGINE 2: RGB")
    print("🔥 ENGINE 3: DARK X V3")
    print("🎯 ENGINE 4: SHIKAARI BOSS")
    print("🗳️ MAJORITY VOTE: 2/4")
    print("⏭️ TIE (2-2) → SKIP")
    print("📊 HOURLY REPORT: ENABLED")
    print("📡 MODE: 1 MIN WINGO")

    await send_message(
        "🔥 *4-ENGINE MAJORITY VOTE BOT* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *ENGINE 1:* GURU\n"
        "🎨 *ENGINE 2:* RGB\n"
        "🔥 *ENGINE 3:* DARK X V3\n"
        "🎯 *ENGINE 4:* SHIKAARI BOSS\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🗳️ *MAJORITY VOTE:* 2/4\n"
        "⏭️ *TIE (2-2):* SKIP\n"
        "📊 *HOURLY REPORT:* ENABLED\n"
        "📡 *MODE:* 1 MIN WINGO\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ WAITING FOR FIRST SIGNAL..."
    )

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
            history_numbers = []
            for h in raw_list[:20]:
                num = int(h['number'])
                history_data.append({
                    'issueNumber': str(h['issueNumber']),
                    'number': num,
                    'side': "BIG" if num >= 5 else "SMALL"
                })
                history_numbers.append(num)

            latest = history_data[0]
            latest_issue = latest['issueNumber']
            actual_num = latest['number']
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            print(f"📡 PERIOD: {latest_issue}, NUMBER: {actual_num}")

            # ==================== RESULT CHECK ====================
            if last_predicted_period == latest_issue and not last_result_sent:
                if last_skip_status:
                    total_skips += 1
                    hourly_skips += 1
                    print(f"⏭️ Skip Round Complete: {latest_issue}")
                
                elif last_predicted_signal is not None:
                    is_win = (last_predicted_signal == actual_type)
                    is_jackpot = (last_predicted_num == actual_num)

                    if is_jackpot:
                        total_jackpots += 1
                        total_wins += 1
                        hourly_wins += 1
                        hourly_jackpots += 1
                        consecutive_losses = 0
                        current_level = 1
                        status = "💎 JACKPOT"
                        is_win = True
                    elif is_win:
                        total_wins += 1
                        hourly_wins += 1
                        consecutive_losses = 0
                        current_level = 1
                        status = "✅ WIN"
                    else:
                        total_losses += 1
                        hourly_losses += 1
                        consecutive_losses += 1
                        current_level = min(3, current_level + 1)
                        status = "❌ LOSS"

                    if is_win:
                        if current_streak >= 0:
                            current_streak += 1
                        else:
                            current_streak = 1
                    else:
                        if current_streak <= 0:
                            current_streak -= 1
                        else:
                            current_streak = -1

                    if current_streak > best_win_streak:
                        best_win_streak = current_streak
                    if abs(current_streak) > worst_loss_streak and current_streak < 0:
                        worst_loss_streak = abs(current_streak)

                    if is_win:
                        if hourly_current_streak_type == "WIN":
                            hourly_current_streak += 1
                        else:
                            hourly_current_streak = 1
                            hourly_current_streak_type = "WIN"
                        if hourly_current_streak > hourly_best_win_streak:
                            hourly_best_win_streak = hourly_current_streak
                    else:
                        if hourly_current_streak_type == "LOSS":
                            hourly_current_streak += 1
                        else:
                            hourly_current_streak = 1
                            hourly_current_streak_type = "LOSS"
                        if hourly_current_streak > hourly_worst_loss_streak:
                            hourly_worst_loss_streak = hourly_current_streak

                    total_rounds += 1
                    hourly_rounds += 1

                    total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
                    streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                    level_emoji = "🟢" if current_level == 1 else ("🟡" if current_level == 2 else "🔴")

                    result_msg = (
                        f"🎯 *RESULT UPDATE*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                        f"🎯 PREDICTED: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"📌 RESULT: `{status}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 WIN RATE: `{total_win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                        f"💎 JACKPOTS: `{total_jackpots}`\n"
                        f"{streak_emoji} STREAK: `{current_streak:+d}`\n"
                        f"{level_emoji} LEVEL: `{current_level}` ({current_level}x)\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ 4-ENGINE MAJORITY"
                    )

                    await send_message(result_msg)
                    print(f"📊 Result: {status}")

                last_result_sent = True
                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None
                last_skip_status = False

                if time.time() - last_hour_report_time >= 3600:
                    await send_hourly_report()

            # ==================== NEW PREDICTION ====================
            next_period = str(int(latest_issue) + 1)

            if not prediction_sent_for_period.get(next_period, False):
                pred = majority_vote_engine(next_period, history_data, current_level, consecutive_losses, history_numbers)

                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                level_emoji = "🟢" if current_level == 1 else ("🟡" if current_level == 2 else "🔴")
                vote_text = f"BIG: {pred['votes']['BIG']} | SMALL: {pred['votes']['SMALL']}"

                if pred['skip']:
                    skip_msg = (
                        f"⏭️ *TIE - SKIP*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚖️ *VOTES ARE TIED (2-2)*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']['prediction']}`\n"
                        f"🎨 RGB: `{pred['rgb']['prediction']}`\n"
                        f"🔥 DARK X: `{pred['dark_x']['prediction']}`\n"
                        f"🎯 SHIKAARI: `{pred['shikaari']['prediction']}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🗳️ VOTES: `{vote_text}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏭️ *SKIP - No Clear Winner*\n"
                        f"⏳ RESULT AWAITING...\n"
                        f"⚡ 4-ENGINE MAJORITY"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = None
                    last_predicted_num = None
                    last_skip_status = True
                    prediction_sent_for_period[next_period] = True
                    last_result_sent = False

                    await send_message(skip_msg)
                    print(f"⏭️ SKIP (Tie): {next_period}")

                else:
                    prediction_msg = (
                        f"🔥 *4-ENGINE MAJORITY* 🔥\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 PREDICTION: `{pred['prediction']}`\n"
                        f"🔢 TARGET NUMBER: `{pred['number']}`\n"
                        f"⚡ CONFIDENCE: `{pred['confidence']}%`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']['prediction']}`\n"
                        f"🎨 RGB: `{pred['rgb']['prediction']}`\n"
                        f"🔥 DARK X: `{pred['dark_x']['prediction']}`\n"
                        f"🎯 SHIKAARI: `{pred['shikaari']['prediction']}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🗳️ VOTES: `{vote_text}`\n"
                        f"{level_emoji} LEVEL: `{current_level}` ({current_level}x)\n"
                        f"{streak_emoji} STREAK: `{current_streak:+d}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏳ RESULT AWAITING...\n"
                        f"⚡ 4-ENGINE MAJORITY"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = pred['prediction']
                    last_predicted_num = pred['number']
                    last_skip_status = False
                    prediction_sent_for_period[next_period] = True
                    last_result_sent = False

                    await send_message(prediction_msg)
                    print(f"✅ Prediction: {next_period} → {pred['prediction']} ({pred['number']}) [{vote_text}]")

                if len(prediction_sent_for_period) > 10:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 4-ENGINE MAJORITY VOTE BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINE 1: GURU")
    print("🎨 ENGINE 2: RGB")
    print("🔥 ENGINE 3: DARK X V3")
    print("🎯 ENGINE 4: SHIKAARI BOSS")
    print("🗳️ MAJORITY VOTE: 2/4")
    print("⏭️ TIE (2-2) → SKIP")
    print("📊 HOURLY REPORT: ENABLED")
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