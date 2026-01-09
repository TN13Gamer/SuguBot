import google.generativeai as genai

# Your Key
KEY = 'AIzaSyAGa4Ro0Ic22Ifcms47bYi2rMcuIR8tfJA'
genai.configure(api_key=KEY)

print("--- SEARCHING FOR AVAILABLE MODELS ---")

try:
    # This asks Google: "What models can I use?"
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
            available_models.append(m.name)

    if not available_models:
        print("❌ No chat models found. Your key might be restricted.")
        
except Exception as e:
    print(f"❌ Error: {e}")

import discord
from discord.ext import commands
import google.generativeai as genai
import os

# ==========================================
# 1. PASTE TOKEN HERE
# ==========================================
TOKEN = 'Nzc5NjQ0NTM3NTQ1OTQ5MTk3.GKqBfX.s5jUmDXHwa7HsV8VNjwkAk_zcwkgU4PRHBUJX4'

# ==========================================
# 2. PASTE GOOGLE KEY HERE
# ==========================================
GEMINI_KEY = 'AIzaSyBnCyVP4sRflGfazQifoUfFO7s2_iyxNZI' 

# --- SETUP ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configure AI directly
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    print("✅ AI LOADED SUCCESSFULY")
except Exception as e:
    print(f"❌ AI FAILED: {e}")

@bot.event
async def on_ready():
    print(f"✅ BOT SIGNED IN AS: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Simple check: Reply to ANY mention
    if bot.user in message.mentions:
        print(f"📩 Message received from {message.author}: {message.content}")
        async with message.channel.typing():
            try:
                response = chat.send_message(message.content)
                await message.reply(response.text)
                print("📤 Sent reply!")
            except Exception as e:
                print(f"❌ Error sending reply: {e}")
                await message.reply("My brain is broken right now.")

bot.run(TOKEN)