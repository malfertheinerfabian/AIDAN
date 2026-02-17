import os
import asyncio
import telebot
from flask import Flask
from threading import Thread
from anthropic import Anthropic

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

SYSTEM_PROMPT = """Du bist AIDAN Executive – ein proaktiver digitaler Chief of Staff.
Antworte auf Deutsch, präzise und professionell.
Keine Füllwörter. Maximal 3 Absätze pro Antwort.

WICHTIG: Du hast Zugriff auf Web-Suche für aktuelle Informationen.
Nutze sie proaktiv für: Wetter, News, Aktienkurse, Sportergebnisse."""

# --- 3. DAS GEHIRN (mit Web-Search) ---
async def ask_aidan(user_text: str) -> str:
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
    tg_bot.infinity_polling(timeout=60, long_polling_timeout=30)
```

---

### 3. Anthropic API Key holen:

1. Gehe zu [console.anthropic.com](https://console.anthropic.com)
2. **Get API Key** (Free Tier: $5 Guthaben gratis)
3. Kopiere den Key (beginnt mit `sk-ant-...`)

---

### 4. In Render eintragen:

**Environment Variables:**
```
TELEGRAM_TOKEN  = dein_telegram_token
ANTHROPIC_KEY   = sk-ant-api03-...  ← NEU
