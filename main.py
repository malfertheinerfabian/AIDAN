import os
import asyncio
import telebot
from flask import Flask
from threading import Thread
from google import genai
from google.genai import types

# --- 1. HERZSCHLAG FÜR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "AIDAN TELEGRAM ONLINE"

def keep_alive():
    t = Thread(
        target=lambda: app.run(
            host='0.0.0.0',
            port=int(os.environ.get("PORT", 8080))
        )
    )
    t.daemon = True
    t.start()

# --- 2. KONFIGURATION ---
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN")
G_KEY           = os.getenv("G_KEY")

ai_client = genai.Client(api_key=G_KEY)

SYSTEM_PROMPT = """Du bist AIDAN Executive – ein proaktiver digitaler Chief of Staff.
Antworte präzise, professionell und lösungsorientiert.
Keine Füllwörter. Maximal 3 Absätze pro Antwort."""

# --- 3. DAS GEMEINSAME GEHIRN ---
async def ask_aidan(user_text: str) -> str:
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )
        )
        return response.text
    except Exception as e:
        return f"⚠️ AIDAN Brain-Error: {e}"

# --- 4. TELEGRAM LOGIK ---
tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None)

@tg_bot.message_handler(func=lambda message: True)
def handle_tg(message):
    try:
        loop = asyncio.new_event_loop()
        reply = loop.run_until_complete(ask_aidan(message.text))
        loop.close()
    except Exception as e:
        reply = f"⚠️ Fehler: {e}"
    
    tg_bot.reply_to(message, reply)

# --- 5. START ---
if __name__ == "__main__":
    keep_alive()
    print("🚀 AIDAN Telegram startet...")
    tg_bot.infinity_polling(timeout=60, long_polling_timeout=30)
