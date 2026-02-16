import os
import discord
from flask import Flask
from threading import Thread
from google import genai
from google.genai import types

# 1. HERZSCHLAG-SERVER
app = Flask('')
@app.route('/')
def home():
    return "AIDAN ONLINE"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. KONFIGURATION
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
G_KEY = os.getenv("G_KEY")
client = genai.Client(api_key=G_KEY)

# 3. BOT LOGIK
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ AIDAN ist online als {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=message.content,
                config=types.GenerateContentConfig(
                    system_instruction="Du bist AIDAN. Antworte kurz und hilfsbereit."
                )
            )
            await message.channel.send(response.text)
        except Exception as e:
            print(f"Fehler: {e}")

# 4. START
if __name__ == "__main__":
    keep_alive()
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("Fehler: Kein DISCORD_TOKEN gefunden!")
