import os
import asyncio
import telebot
from flask import Flask
from threading import Thread
from anthropic import Anthropic
from datetime import datetime

# --- 1. HERZSCHLAG FÜR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "AIDAN MULTI-CHANNEL ONLINE"

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
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_KEY")

claude_client = Anthropic(api_key=ANTHROPIC_KEY)

# Aktuelles Datum dynamisch generieren
CURRENT_DATE = datetime.now().strftime("%A, %d. %B %Y")

SYSTEM_PROMPT = f"""Du bist AIDAN Executive – ein proaktiver digitaler Chief of Staff.
Antworte auf Deutsch, präzise und professionell.
Keine Füllwörter. Maximal 3 Absätze pro Antwort.

AKTUELLES DATUM: {CURRENT_DATE}

WICHTIG: 
- Nutze Web-Suche für aktuelle Informationen (Wetter, News, Aktienkurse)
- Wenn nach dem Datum gefragt wird, antworte mit "Heute ist {CURRENT_DATE}"
- Bei zeitbezogenen Fragen: Beziehe dich auf dieses Datum als "jetzt"
"""

# --- 3. DAS GEHIRN (mit Web-Search) ---
async def ask_aidan(user_text: str) -> str:
    """Claude API Call mit automatischer Web-Suche wenn nötig."""
    try:
        loop = asyncio.get_event_loop()
        
        response = await loop.run_in_executor(
            None,
            lambda: claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_text
                }]
            )
        )
        
        # Claude gibt Content als Liste zurück
        return response.content[0].text
    
    except Exception as e:
        return f"⚠️ AIDAN Error: {str(e)}"

# --- 4. TELEGRAM HANDLER ---
tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None)

@tg_bot.message_handler(func=lambda message: True)
def handle_tg(message):
    """Empfängt Telegram-Nachrichten und antwortet mit Claude."""
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
    print("🚀 AIDAN (powered by Claude) startet...")
    print(f"📅 Aktuelles Datum: {CURRENT_DATE}")
    tg_bot.infinity_polling(timeout=60, long_polling_timeout=30)
