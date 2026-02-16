import os
import discord
import asyncio
from flask import Flask
from threading import Thread
from google import genai
from google.genai import types
from discord.ext import commands

# ==========================================
# 1. HERZSCHLAG-SERVER (Hält Render wach)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "AIDAN Executive is online and heartbeat is active!"

def run_webserver():
    # Render vergibt den Port automatisch über Umgebungsvariablen
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_webserver)
    t.start()

# ==========================================
# 2. KONFIGURATION
# ==========================================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
G_KEY = os.getenv("G_KEY")

client = genai.Client(api_key=G_KEY)
MODEL_ID = "gemini-2.0-flash"

# ==========================================
# 3. BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 AIDAN v42.4 ist live auf dem Server!")
    print(f"Eingeloggt als: {bot.user.name}")

# ==========================================
# 4. EXECUTIVE LOGIK & BRAIN
# ==========================================
async def aidan_brain(user_text, user_name):
    # Hier können wir später die Tools für Outlook/Gmail wieder einfügen
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=f"Du bist AIDAN Executive. Antworte {user_name} präzise und professionell."
            )
        )
        return response.text
    except Exception as e:
        return f"System-Fehler: {str(e)}"

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        reply = await aidan_brain(message.content, message.author.name)
        await message.reply(reply)

# ==========================================
# 5. STARTPROZESS
# ==========================================
if __name__ == "__main__":
    #
