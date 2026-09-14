#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 PATTERN MATCHER + REAL VIP V3 - 3M WINGO
🎯 MATCH হলে → MATCH FOUND Prediction
🎯 NO MATCH হলে → Real VIP V3 Prediction
🤖 @rakiiibahmed
"""

import asyncio
import time
import requests
import os
import random
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from telegram import Bot
    from telegram.error import TelegramError, TimedOut, NetworkError
except ImportError:
    print("❌ python-telegram-bot ইনস্টল নেই!")
    exit(1)

# ==================== 📌 কনফিগারেশন ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"

API_URLS = [
    "https://draw.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
    "https://api.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
]

# ==================== 🌐 ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MATCH/NO MATCH BOT is running!")

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

# ==================== 📊 বট ইনিশিয়ালাইজ ====================
try:
    bot = Bot(token=BOT_TOKEN)
    logger.info("✅ বট ইনিশিয়ালাইজেশন সফল!")
except Exception as e:
    logger.error(f"❌ বট ইনিশিয়ালাইজেশন ব্যর্থ: {e}")
    exit(1)

# ==================== গ্লোবাল ভেরিয়েবল ====================
total_wins = 0
total_losses = 0
total_rounds = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0

match_count = 0
no_match_count = 0

hourly_wins = 0
hourly_losses = 0
hourly_rounds = 0
hourly_best_win_streak = 0
hourly_worst_loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
prediction_sent_for_period = {}
last_result_sent = False

# ============================================================
#  📚 PATTERN DATABASE (PDF 1)
# ============================================================
PATTERNS_5 = {
    "SSBSS": "S", "BBSBS": "S", "SBBBS": "B", "BSBBB": "S",
    "BBBBS": "B", "BBBSB": "B", "SSBSB": "B",
    "SBSBS": "B", "SBSBB": "B", "SSSBB": "B", "BSSBS": "S",
    "SBBSB": "S", "BSBSB": "S", "SBSSB": "S",
    "BSSSB": "S", "BBSBB": "B", "SBBBB": "B",
    "SBSSBB": "B", "BBSSSB": "B", "BSSBSB": "S",
}

PATTERNS_6 = {
    "BSBBSS": "S", "BSBSSS": "S", "SSSBBB": "B", "SSSBBS": "B",
    "SSBBBS": "B", "BSBSSB": "S", "BSSSBS": "B", "SSSSSS": "B",
    "SSSSSB": "B", "BBSBSB": "S", "BBBBSB": "S", "SBBBBB": "S",
    "SBBBBS": "S", "BBSBBB": "S", "BSBSBB": "S", "SSSSBS": "B",
    "SSBBSB": "B", "SBSSSB": "B", "BSBBBS": "S", "SSSBSB": "B",
}

PATTERNS_7 = {
    "SSBBBS": "B", "BSSSSB": "S", "BSSSBB": "S", "SBBBBS": "S",
    "SSSBBB": "B", "BSSBBB": "S", "SSSSBB": "B", "SSSSSSB": "B",
    "SSSSSB": "B", "BSBSBSB": "S", "BSSBSBS": "S",
    "SBSBSB": "B", "BSBSBSS": "B", "SSSBSB": "B", "BBSBSB": "S",
    "BBSBSBS": "B", "SBSBSBS": "S", "BSSBSBS": "B", "SSSSSSS": "B",
    "BBBBBBS": "S", "SBBBBBB": "S", "BSBBBSB": "S",
    "SSSBBSB": "B", "BBSBBBS": "S",
}

# ============================================================
#  🧠 ENGINE 1: PATTERN MATCHER
# ============================================================
def pattern_matcher(data):
    """PATTERN MATCHER - PDF 1"""
    if len(data) < 5:
        return {"prediction": "BIG", "confidence": 50, "reason": "INSUFFICIENT DATA", "pattern": None, "pattern_type": "NONE"}
    
    sides = [d['side'][0] for d in data]
    
    # 7-digit
    if len(sides) >= 7:
        pattern_7 = ''.join(sides[:7])
        if pattern_7 in PATTERNS_7:
            pred_letter = PATTERNS_7[pattern_7]
            pred = "BIG" if pred_letter == "B" else "SMALL"
            return {
                "prediction": pred, "confidence": 80,
                "reason": f"7-DIGIT MATCH ({pattern_7})",
                "pattern": pattern_7, "pattern_type": "7-DIGIT"
            }
    
    # 6-digit
    if len(sides) >= 6:
        pattern_6 = ''.join(sides[:6])
        if pattern_6 in PATTERNS_6:
            pred_letter = PATTERNS_6[pattern_6]
            pred = "BIG" if pred_letter == "B" else "SMALL"
            return {
                "prediction": pred, "confidence": 75,
                "reason": f"6-DIGIT MATCH ({pattern_6})",
                "pattern": pattern_6, "pattern_type": "6-DIGIT"
            }
    
    # 5-digit
    if len(sides) >= 5:
        pattern_5 = ''.join(sides[:5])
        if pattern_5 in PATTERNS_5:
            pred_letter = PATTERNS_5[pattern_5]
            pred = "BIG" if pred_letter == "B" else "SMALL"
            return {
                "prediction": pred, "confidence": 70,
                "reason": f"5-DIGIT MATCH ({pattern_5})",
                "pattern": pattern_5, "pattern_type": "5-DIGIT"
            }
    
    # Majority Vote
    recent5 = sides[:5]
    big_count = recent5.count("B")
    small_count = recent5.count("S")
    pred = "BIG" if big_count >= small_count else "SMALL"
    
    return {
        "prediction": pred, "confidence": 55,
        "reason": f"MAJORITY ({big_count}B-{small_count}S)",
        "pattern": None, "pattern_type": "MAJORITY"
    }

# ============================================================
#  🧠 ENGINE 2: REAL VIP V3 (NEURAL)
# ============================================================
def real_vip_v3_engine(data):
    """REAL VIP V3 - Anti-Dragon + Mirror + Twin + Majority"""
    if len(data) < 10:
        return {"pred": "BIG", "conf": "STABILIZING", "nums": [5, 7], "reason": "INSUFFICIENT DATA"}
    
    results = []
    for d in data[:10]:
        num = d['number']
        results.append({
            "num": num,
            "size": "BIG" if num >= 5 else "SMALL"
        })
    
    sizes = [r["size"] for r in results]
    
    # Dragon Count
    dragon = 1
    for i in range(len(sizes) - 1):
        if sizes[i] == sizes[i+1]:
            dragon += 1
        else:
            break
    
    pred = ""
    conf = ""
    reason = ""
    
    # Anti-Dragon
    if dragon >= 4:
        pred = "SMALL" if sizes[0] == "BIG" else "BIG"
        conf = "ULTRA 🔥 (BREAK)"
        reason = f"ANTI-DRAGON ({dragon}টি টানা {sizes[0]})"
    
    # 1-1 Mirror
    elif sizes[0] != sizes[1] and sizes[1] != sizes[2]:
        pred = "SMALL" if sizes[0] == "BIG" else "BIG"
        conf = "EXTREME 🚀 (MIRROR)"
        reason = f"1-1 MIRROR ({sizes[0]}-{sizes[1]}-{sizes[2]})"
    
    # 2-2 Twin
    elif sizes[0] == sizes[1] and sizes[2] == sizes[3]:
        pred = "SMALL" if sizes[0] == "BIG" else "BIG"
        conf = "HIGH ⚡ (TWIN)"
        reason = f"2-2 TWIN ({sizes[0]}{sizes[1]}-{sizes[2]}{sizes[3]})"
    
    # Majority
    else:
        bigs = sizes[:6].count("BIG")
        pred = "BIG" if bigs >= 3 else "SMALL"
        conf = "NORMAL ⚡"
        reason = f"MAJORITY (শেষ ৬টিতে {bigs}B-{6-bigs}S)"
    
    # Smart Number Selection
    recent_nums = set(r["num"] for r in results[:8])
    pool = [5, 6, 7, 8, 9] if pred == "BIG" else [0, 1, 2, 3, 4]
    smart_nums = [n for n in pool if n not in recent_nums]
    
    if len(smart_nums) < 2:
        smart_nums = random.sample(pool, 2)
    else:
        smart_nums = random.sample(smart_nums, 2)
    
    smart_nums = sorted(smart_nums)
    
    return {
        "pred": pred,
        "conf": conf,
        "nums": smart_nums,
        "reason": reason,
        "dragon": dragon
    }

# ==================== 📡 API ফেচ ====================
def fetch_api_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
    }
    
    for api_url in API_URLS:
        try:
            url = api_url + "?t=" + str(int(time.time() * 1000))
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                list_data = data.get("data", {}).get("list", [])
                if list_data and len(list_data) > 0:
                    return list_data
            else:
                logger.warning(f"⚠️ {api_url} → HTTP {res.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ {api_url} → এরর: {e}")
    
    return []

# ==================== 📤 মেসেজ সেন্ড ====================
async def send_message(text, parse_mode="Markdown", retry_count=3):
    for attempt in range(retry_count):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
            return True
        except (TimedOut, NetworkError):
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"❌ টেলিগ্রাম এরর: {e}")
            break
    return False

# ==================== 📊 হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global total_wins, total_losses, total_rounds
    global best_win_streak, worst_loss_streak
    global match_count, no_match_count
    
    if hourly_rounds == 0:
        return
    
    hourly_win_rate = (hourly_wins / hourly_rounds * 100) if hourly_rounds > 0 else 0
    total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
    
    report_msg = (
        f"📊 *আওয়ারলি রিপোর্ট - MATCH/NO MATCH*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *সময়:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *এই ঘন্টায় রাউন্ড:* `{hourly_rounds}`\n"
        f"✅ *এই ঘন্টায় জয়:* `{hourly_wins}`\n"
        f"❌ *এই ঘন্টায় হার:* `{hourly_losses}`\n"
        f"📈 *এই ঘন্টায় হার:* `{hourly_win_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{hourly_best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{hourly_worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *মোট রাউন্ড:* `{total_rounds}`\n"
        f"✅ *মোট জয়:* `{total_wins}`\n"
        f"❌ *মোট হার:* `{total_losses}`\n"
        f"📈 *মোট জয়ের হার:* `{total_win_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *মোট Match:* `{match_count}`\n"
        f"⚠️ *মোট No Match:* `{no_match_count}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 @rakiiibahmed"
    )
    
    await send_message(report_msg)
    
    hourly_wins = 0
    hourly_losses = 0
    hourly_rounds = 0
    hourly_best_win_streak = 0
    hourly_worst_loss_streak = 0

# ==================== 🚀 মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global current_streak, best_win_streak, worst_loss_streak
    global match_count, no_match_count
    global last_predicted_period, last_predicted_signal
    global prediction_sent_for_period, last_result_sent

    logger.info("🔥 MATCH/NO MATCH বট স্টার্ট...")

    await send_message(
        "🔥 *MATCH / NO MATCH BOT - 3M* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *2 Engines:*\n"
        "1️⃣ PATTERN MATCHER (PDF 1)\n"
        "2️⃣ REAL VIP V3 (Neural)\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *MATCH* = দুই ইঞ্জিন একমত\n"
        "⚠️ *NO MATCH* = REAL VIP V3 প্রেডিকশন\n"
        "📡 *মোড:* 3 MIN WINGO\n"
        "🤖 *বট:* @rakiiibahmed\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
    )

    last_hour_time = time.time()

    while True:
        try:
            current_sec = int(time.time()) % 180
            sleep_time = 180 - current_sec + 5
            await asyncio.sleep(sleep_time)

            raw_list = fetch_api_data()
            if not raw_list:
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

            logger.info(f"📡 পিরিয়ড: {latest_issue}, নাম্বার: {actual_num} ({actual_type})")

            # ===== রেজাল্ট চেক =====
            if last_predicted_period == latest_issue and last_predicted_signal is not None and not last_result_sent:
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    hourly_wins += 1
                    
                    if current_streak >= 0:
                        current_streak += 1
                    else:
                        current_streak = 1
                    
                    if current_streak > best_win_streak:
                        best_win_streak = current_streak
                    if current_streak > hourly_best_win_streak:
                        hourly_best_win_streak = current_streak
                    
                    status = "✅ জয় 🎉"
                else:
                    total_losses += 1
                    hourly_losses += 1
                    
                    if current_streak <= 0:
                        current_streak -= 1
                    else:
                        current_streak = -1
                    
                    if abs(current_streak) > worst_loss_streak:
                        worst_loss_streak = abs(current_streak)
                    if abs(current_streak) > hourly_worst_loss_streak:
                        hourly_worst_loss_streak = abs(current_streak)
                    
                    status = "❌ হার"

                total_rounds += 1
                hourly_rounds += 1
                
                total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"

                result_msg = (
                    f"🎯 *রেজাল্ট আপডেট*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{latest_issue[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔮 প্রেডিকশন: `{last_predicted_signal}`\n"
                    f"🎰 একচুয়াল: `{actual_num}` → `{actual_type}`\n"
                    f"📌 রেজাল্ট: `{status}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 জয়ের হার: `{total_win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 @rakiiibahmed"
                )

                await send_message(result_msg)
                last_result_sent = True

                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    last_hour_time = time.time()

            # ===== নতুন প্রেডিকশন =====
            next_period = str(int(latest_issue) + 1)
            
            if not prediction_sent_for_period.get(next_period, False):
                
                # 🔥 ENGINE 1: PATTERN MATCHER
                pattern_result = pattern_matcher(history_data)
                pattern_pred = pattern_result['prediction']
                
                # 🔥 ENGINE 2: REAL VIP V3
                vip_result = real_vip_v3_engine(history_data)
                vip_pred = vip_result['pred']
                vip_nums = vip_result['nums']
                
                logger.info(f"🔍 Pattern: {pattern_pred} | VIP: {vip_pred}")
                
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                
                # ✅ MATCH Check
                if pattern_pred == vip_pred:
                    # MATCH FOUND
                    match_count += 1
                    final_pred = pattern_pred
                    
                    prediction_msg = (
                        f"🔥 *MATCH FOUND - 3M WINGO* 🔥\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ *MATCH FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 প্রেডিকশন: `{final_pred}`\n"
                        f"⚡ কনফিডেন্স: `{pattern_result['confidence']}%`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 *Pattern Matcher:* `{pattern_pred}`\n"
                        f"📊 ইঞ্জিন: {pattern_result['reason']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 *REAL VIP V3:* `{vip_pred}`\n"
                        f"🎰 টার্গেট: `{', '.join(map(str, vip_nums))}`\n"
                        f"📊 ইঞ্জিন: {vip_result['reason']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏳ রেজাল্টের জন্য অপেক্ষা...\n"
                        f"🤖 @rakiiibahmed"
                    )
                    logger.info(f"✅ MATCH: {next_period} → {final_pred}")
                
                else:
                    # NO MATCH → Real VIP V3 প্রেডিকশন
                    no_match_count += 1
                    final_pred = vip_pred
                    
                    prediction_msg = (
                        f"⚠️ *NO MATCH - 3M WINGO* ⚠️\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ *NO MATCH*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 প্রেডিকশন (VIP V3): `{final_pred}`\n"
                        f"🎰 টার্গেট নম্বর: `{', '.join(map(str, vip_nums))}`\n"
                        f"⚡ কনফিডেন্স: `{vip_result['conf']}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 *Pattern Matcher:* `{pattern_pred}`\n"
                        f"📊 ইঞ্জিন: {pattern_result['reason']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 *REAL VIP V3:* `{vip_pred}`\n"
                        f"📊 ইঞ্জিন: {vip_result['reason']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏳ রেজাল্টের জন্য অপেক্ষা...\n"
                        f"🤖 @rakiiibahmed"
                    )
                    logger.info(f"⚠️ NO MATCH: {next_period} → VIP V3 = {final_pred}")
                
                last_predicted_period = next_period
                last_predicted_signal = final_pred
                prediction_sent_for_period[next_period] = True
                last_result_sent = False
                
                await send_message(prediction_msg)
                
                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            logger.error(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 MATCH / NO MATCH BOT - 3M WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 2 Engines:")
    print("   1. PATTERN MATCHER (PDF 1)")
    print("   2. REAL VIP V3 (Neural)")
    print("✅ MATCH = দুই ইঞ্জিন একমত")
    print("⚠️ NO MATCH = REAL VIP V3 প্রেডিকশন")
    print("📡 MODE: 3 MIN WINGO")
    print("🤖 BOT: @rakiiibahmed")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")
