import time
import requests
import logging
import json
import os
import re
import sys
import random
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut
import asyncio
import pycountry

# === CONFIG ===
BOT_TOKEN = '8145573996:AAFLTxxEV5fF2nd-s-uLFmOG0127nMlcjS0'
CHAT_ID = '-1002833675066'
USERNAME = 'Jihad69s'
PASSWORD = 'jihad79s'
BASE_URL = "http://109.236.84.81"
LOGIN_PAGE_URL = BASE_URL + "/ints/login"
LOGIN_POST_URL = BASE_URL + "/ints/signin"
DATA_URL = BASE_URL + "/ints/agent/res/data_smscdr.php"

bot = Bot(token=BOT_TOKEN)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

logging.basicConfig(level=logging.INFO, format='%(message)s')

QURAN_AYAT = [
    "📖إِنَّ مَعَ الْعُسْرِ يُسْرًا — *Verily, with hardship comes ease.* (94:6)",
    "📖اللَّهُ نُورُ السَّمَاوَاتِ وَالْأَرْضِ — *Allah is the Light of the heavens and the earth.* (24:35)",
    "📖فَاذْكُرُونِي أَذْكُرْكُمْ — *So remember Me; I will remember you.* (2:152)",
    "📖وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ — *And He is over all things.* (5:120)",
    "📖حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ — *Allah is sufficient for us, and He is the best disposer.* (3:173)"
]

def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

def mask_number(number: str) -> str:
    if len(number) > 11:
        return number[:7] + '**' + number[-2:]
    elif len(number) > 9:
        return number[:7] + '**' + number[-2:]
    elif len(number) > 7:
        return number[:7] + '**' + number[-1:]
    elif len(number) > 5:
        return number[:7] + '**'
    else:
        return number

def save_already_sent(already_sent):
    with open("already_sent.json", "w") as f:
        json.dump(list(already_sent), f)

def bold_unicode(text: str) -> str:
    bold_letters = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅',
        'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋',
        'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑',
        'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗',
        'Y': '𝐘', 'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟',
        'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥',
        'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫',
        's': '𝐬', 't': '𝐭', 'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱',
        'y': '𝐲', 'z': '𝐳'
    }
    return ''.join(bold_letters.get(c, c) for c in text)

def load_already_sent():
    if os.path.exists("already_sent.json"):
        with open("already_sent.json", "r") as f:
            return set(json.load(f))
    return set()

logging.info('Script By @Rafi_00019')

def login():
    try:
        resp = session.get(LOGIN_PAGE_URL)
        match = re.search(r'What is (\d+) \+ (\d+)', resp.text)
        if not match:
            logging.error("Captcha not found.")
            return False
        num1, num2 = int(match.group(1)), int(match.group(2))
        captcha_answer = num1 + num2
        logging.info(f"Solved captcha: {num1} + {num2} = {captcha_answer}")

        payload = {
            "username": USERNAME,
            "password": PASSWORD,
            "capt": captcha_answer
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": LOGIN_PAGE_URL
        }

        resp = session.post(LOGIN_POST_URL, data=payload, headers=headers)
        if "dashboard" in resp.text.lower() or "logout" in resp.text.lower():
            logging.info("Login successful ✅")
            return True
        else:
            logging.error("Login failed ❌")
            return False
    except Exception as e:
        logging.error(f"Login error: {e}")
        return False

def build_api_url():
    start_date = "2025-05-05"
    end_date = "2026-01-01"
    return (
        f"{DATA_URL}?fdate1={start_date}%2000:00:00&fdate2={end_date}%2023:59:59&"
        "frange=&fclient=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgclient=&fgnumber=&fgcli=&fg=0&"
        "sEcho=1&iColumns=9&sColumns=%2C%2C%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=25&"
        "mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&"
        "mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&"
        "mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&"
        "mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&"
        "mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&"
        "mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&"
        "mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&"
        "mDataProp_7=7&sSearch_7=&bRegex_7=false&bSearchable_7=true&bSortable_7=true&"
        "mDataProp_8=8&sSearch_8=&bRegex_8=false&bSearchable_8=true&bSortable_8=false&"
        "sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1"
    )

if not (CHAT_ID.startswith('-1') and CHAT_ID.endswith('66')):
    sys.exit(1)

def fetch_data():
    url = build_api_url()
    headers = {"X-Requested-With": "XMLHttpRequest"}

    try:
        response = session.get(url, headers=headers, timeout=10)
        logging.info(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logging.error(f"[!] JSON decode error: {e}")
                logging.debug("Partial response:\n" + response.text[:300])
                return None
        elif response.status_code == 403 or "login" in response.text.lower():
            logging.warning("Session expired. Re-logging...")
            if login():
                return fetch_data()
            return None
        else:
            logging.error(f"Unexpected error: {response.status_code}")
            return None

    except Exception as e:
        logging.error(f"Fetch error: {e}")
        return None

already_sent = load_already_sent()

def get_country_flag(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if country:
            return chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
    except:
        pass
    return '🌐'

async def sent_messages():
    logging.info("🔍 Checking for messages...\n")
    data = fetch_data()

    if data and 'aaData' in data:
        for row in data['aaData']:
            date = str(row[0]).strip()
            number = str(row[2]).strip()
            full_range = str(row[1]).strip()
            country = full_range.split('-')[0].title()
            service = str(row[3]).strip()
            message = str(row[5]).strip()

            match = re.search(r'\d{3}-\d{3}|\d{4,6}', message)
            otp = match.group() if match else None

            if otp:
                unique_key = f"{number}|{otp}"
                if unique_key not in already_sent:
                    already_sent.add(unique_key)

                    flag = get_country_flag(country)
                    ayah = random.choice(QURAN_AYAT)

                    service_bold = bold_unicode(service)

                    text = (
                        f"🔔 {service_bold} OTP Received Successfully\n\n"
                        f"🕒 Time: `{escape_markdown(date)}`\n"
                        f"⚙️ Service: `{escape_markdown(service)}`\n"
                        f"🌐 Country: `{escape_markdown(country)}` {flag}\n"
                        f"☎️ Number: `{escape_markdown(mask_number(number))}`\n\n"
                        f"🔑 Your OTP: `{escape_markdown(otp)}`\n\n"
                        f"```\n💌 Full Message:\n{escape_markdown(message.strip())}\n```\n"
                        f"```\n{escape_markdown(ayah)}\n```\n"
                        f"🚀 Be Active  New OTP Coming\n"
                    )

                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("📢 Main Channel", url="https://t.me/PhTG_Numbers")]
                    ])

                    try:
                        bot.send_message(
                            chat_id=CHAT_ID,
                            text=text,
                            parse_mode='MarkdownV2',
                            reply_markup=keyboard
                        )
                        logging.info(f"✅ OTP Sent: {number} - {otp}")
                        save_already_sent(already_sent)
                        await asyncio.sleep(5)  # Delay between messages
                    except TimedOut:
                        logging.error("Telegram Timeout, retrying after 10 seconds...")
                        await asyncio.sleep(10)
                    except Exception as e:
                        logging.error(f"Telegram Error: {e}")
                        continue
    elif data is None or not data:
        logging.info("No data or invalid response.")
    else:
        logging.info("✅ No new OTPs found.\n")

async def main():
    if not login():
        logging.error("Failed to login. Exiting.")
        return

    while True:
        try:
            await sent_messages()
            await asyncio.sleep(15)  # Delay between each check
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
