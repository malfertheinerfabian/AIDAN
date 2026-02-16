import os, discord
from flask import Flask
from threading import Thread

# Webserver für Render
app = Flask('')
@app.route('/')
def home(): return "STILL ALIVE"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))))
    t.start()

# Minimaler Bot-Check
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Eingeloggt als {self.user}')
        # Versucht in den ersten verfügbaren Kanal zu schreiben
        for guild in self.guilds:
            for channel in guild.text_channels:
                try:
                    await channel.send("🚀 AIDAN meldet sich zum Dienst! Wenn du das siehst, steht die Verbindung.")
                    break
                except: continue

if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    MyClient(intents=discord.Intents.all()).run(token)
