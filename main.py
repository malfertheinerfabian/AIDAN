import os
import asyncio
import discord
import telebot
from flask import Flask
from threading import Thread
from google import genai
from google.genai import types

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
DISCORD_TOKEN   = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN")
G_KEY           = os.getenv("G_KEY")

ai_client = genai.Client(api_key=G_KEY)

SYSTEM_PROMPT = """Du bist AIDAN Executive – ein proaktiver digitaler Chief of Staff.
Antworte präzise, professionell und lösungsorientiert.
Keine Füllwörter. Maximal 3 Absätze pro Antwort."""

# --- 3. DAS GEMEINSAME GEHIRN (jetzt async) ---
async def ask_aidan(user_text: str) -> str:
    """Async Wrapper – blockiert den Event Loop nicht mehr."""
    try:
        loop = asyncio.get_event_loop()
        
        # Synchronen SDK-Call in ThreadPool auslagern
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
    """Telegram läuft synchron – eigener Thread, kein Konflikt."""
    try:
        # Neuen Event Loop für diesen Thread erstellen
        loop = asyncio.new_event_loop()
        reply = loop.run_until_complete(ask_aidan(message.text))
        loop.close()
    except Exception as e:
        reply = f"⚠️ Fehler: {e}"
    
    tg_bot.reply_to(message, reply)

# --- 5. DISCORD LOGIK ---
intents = discord.Intents.default()
intents.message_content = True  # Explizit erforderlich ab Discord.py 2.0
ds_client = discord.Client(intents=intents)

@ds_client.event
async def on_ready():
    print(f'✅ Discord: {ds_client.user} online')
    print(f'📡 Server: {[g.name for g in ds_client.guilds]}')

@ds_client.event
async def on_message(message):
    # Bot-Nachrichten ignorieren
    if message.author == ds_client.user:
        return
    
    # ✅ NUR antworten wenn Bot erwähnt wird
    # Entferne diese Bedingung für Antwort auf ALLE Nachrichten
    if ds_client.user not in message.mentions:
        return

    async with message.channel.typing():
        reply = await ask_aidan(message.content)  # Jetzt echtes await
        
        # Discord 2000-Zeichen Limit absichern
        if len(reply) > 1900:
            reply = reply[:1900] + "\n\n_[Antwort gekürzt]_"
        
        await message.channel.send(reply)

# --- 6. DER MULTI-START ---
def run_telegram():
    print("🚀 Telegram Bot startet...")
    tg_bot.infinity_polling(timeout=60, long_polling_timeout=30)

if __name__ == "__main__":
    keep_alive()
    Thread(target=run_telegram, daemon=True).start()
    
    if DISCORD_TOKEN:
        print("🚀 Discord Bot startet...")
        ds_client.run(DISCORD_TOKEN)
    else:
        print("❌ DISCORD_TOKEN fehlt in Environment Variables")
