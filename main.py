from keep_alive import keep_alive
import discord
from discord.ext import commands, tasks
import google.generativeai as genai
import os
import random
import asyncio
import yt_dlp
import warnings

warnings.filterwarnings("ignore")

# ==========================================
# 🔑 KEYS
# ==========================================
TOKEN = 'Nzc5NjQ0NTM3NTQ1OTQ5MTk3.GKqBfX.s5jUmDXHwa7HsV8VNjwkAk_zcwkgU4PRHBUJX4'
GEMINI_KEY = 'AIzaSyBnCyVP4sRflGfazQifoUfFO7s2_iyxNZI'

# ==========================================
# ⚙️ SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Must be ON in Dev Portal
intents.voice_states = True 

bot = commands.Bot(command_prefix="!", intents=intents)
bot.current_song = None 

# AI Setup
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    chat_session = model.start_chat(history=[])
except Exception as e:
    print(f"❌ AI ERROR: {e}")

# Music Setup
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', 
}
ffmpeg_options = {'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data: data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# ==========================================
# 🚀 EVENTS
# ==========================================

@bot.event
async def on_ready():
    print(f'🚀 Logged in as: {bot.user.name}')
    print("✅ System Status: ONLINE")
    change_status.start()

# --- WELCOME SYSTEM ---
@bot.event
async def on_member_join(member):
    await send_welcome_message(member)
    
    # GIVE ROLES
    role_names = ["♥️⇾｜members", "✅️⇾｜Verified"]
    roles_to_add = []
    for name in role_names:
        role = discord.utils.get(member.guild.roles, name=name)
        if role: roles_to_add.append(role)
    
    if roles_to_add:
        try:
            await member.add_roles(*roles_to_add)
            print(f"✅ Added roles to {member.name}")
        except:
            print("❌ Cannot give roles (Check Hierarchy)")

# --- DEBUG COMMANDS ---
@bot.command(name="checkroles")
async def check_roles(ctx):
    target_roles = ["♥️⇾｜members", "✅️⇾｜Verified"]
    bot_member = ctx.guild.me
    msg = "🔍 **Role System Check:**\n"
    for name in target_roles:
        role = discord.utils.get(ctx.guild.roles, name=name)
        if not role:
            msg += f"❌ **NOT FOUND:** `{name}`\n"
        elif role.position >= bot_member.top_role.position:
            msg += f"⚠️ **HIERARCHY ISSUE:** `{name}` is higher than Sugu!\n"
        else:
            msg += f"✅ **READY:** `{name}`\n"
    await ctx.send(msg)

@bot.command(name="testwelcome")
async def test_welcome(ctx):
    await ctx.send("🧪 Testing Welcome...")
    await send_welcome_message(ctx.author)

async def send_welcome_message(member):
    channel_name = "👋⇾｜ᴡᴇʟᴄᴏᴍᴇ"
    channel = discord.utils.get(member.guild.text_channels, name=channel_name)
    
    if not channel:
        print(f"❌ Channel '{channel_name}' not found!")
        return

    c_rules = discord.utils.get(member.guild.text_channels, name="📄⇾｜ʀᴜʟᴇꜱ")
    c_roles = discord.utils.get(member.guild.text_channels, name="✅⇾｜sᴇʟғ_ʀᴏʟᴇ")
    c_chat = discord.utils.get(member.guild.text_channels, name="👥⇾｜ɢᴇɴᴇʀᴀʟ_ᴄʜᴀᴛꜱ")
    c_music = discord.utils.get(member.guild.text_channels, name="🎵⇾｜ᴍᴜꜱɪᴄ_ʀᴇqᴜᴇꜱᴛ")

    link_rules = c_rules.mention if c_rules else "**📄⇾｜ʀᴜʟᴇꜱ**"
    link_roles = c_roles.mention if c_roles else "**✅⇾｜sᴇʟғ_ʀᴏʟᴇ**"
    link_chat = c_chat.mention if c_chat else "**👥⇾｜ɢᴇɴᴇʀᴀʟ_ᴄʜᴀᴛꜱ**"
    link_music = c_music.mention if c_music else "**🎵⇾｜ᴍᴜꜱɪᴄ_ʀᴇqᴜᴇꜱᴛ**"

    embed = discord.Embed(
        title="Welcome To Our Server KL 13 ( കണ്ണൂർ )",
        description=(
            f"You are number **{member.guild.member_count}**\n"
            f"----------------------------------------\n"
            f"Be sure to read  {link_rules}\n"
            f"Get your roles {link_roles}\n"
            f"Chat on general {link_chat}\n"
            f"Listen to Music  {link_music}\n"
            f"----------------------------------------"
        ),
        color=0x00ff00
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    
    # ✅ FIXED GIF LINK (The one you asked for)
    embed.set_image(url="https://apcp.es/wp-content/uploads/2021/12/banner-welcome.gif")

    await channel.send(f"Hey {member.mention} ,", embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    await bot.process_commands(message)

    if bot.user in message.mentions:
        async with message.channel.typing():
            clean_text = message.content.replace(f'<@{bot.user.id}>', '').strip()
            if not clean_text:
                await message.reply("Beep boop! 🤖")
                return
            try:
                response = chat_session.send_message(clean_text)
                await message.reply(response.text[:2000])
            except Exception:
                await message.reply("I had a glitch!")

# --- STATUS ---
@tasks.loop(seconds=60)
async def change_status():
    is_music_playing = False
    for vc in bot.voice_clients:
        if vc.is_playing():
            is_music_playing = True
            break
    
    if is_music_playing and bot.current_song:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=bot.current_song))
    else:
        status_list = [
            discord.Activity(type=discord.ActivityType.watching, name="u guys"),
            discord.Activity(type=discord.ActivityType.watching, name="admin trying to inspire"),
            discord.Game(name="CSE BTech"), 
            discord.Activity(type=discord.ActivityType.listening, name="you guyz"),
            discord.Activity(type=discord.ActivityType.watching, name="KL 13 Members"),
            discord.Activity(type=discord.ActivityType.watching, name="Thalassery Biryani cooking"),
            discord.Activity(type=discord.ActivityType.listening, name="Malayalam Hits"),
            discord.Game(name="Kannur Vibes"),
            discord.Game(name="With your feelings"),
            discord.Activity(type=discord.ActivityType.competing, name="Vadam Vali"),
        ]
        await bot.change_presence(activity=random.choice(status_list))

# --- MUSIC ---
@bot.command(name='join')
async def join(ctx):
    if not ctx.author.voice: return await ctx.send("❌ Join a voice channel first.")
    await ctx.author.voice.channel.connect()
    await ctx.send(f"🔊 Joined!")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client: 
        await ctx.voice_client.disconnect()
        bot.current_song = None
        await ctx.send("👋 Bye!")

@bot.command(name='play')
async def play(ctx, *, url):
    try:
        vc = ctx.voice_client
        if not vc:
            if ctx.author.voice: vc = await ctx.author.voice.channel.connect()
            else: return await ctx.send("Join a VC first!")
        
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            vc.play(player, after=lambda e: print(f'Err: {e}') if e else None)
            bot.current_song = player.title
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.title))
        await ctx.send(f'🎶 **Playing:** {player.title}')
    except Exception as e:
        await ctx.send("❌ Error! (Check FFmpeg)")
        print(f"Music Error: {e}")

bot.run(TOKEN)
=======
import discord
from discord.ext import commands, tasks
import google.generativeai as genai
import os
import random
import asyncio
import yt_dlp
import warnings
from dotenv import load_dotenv  # <--- NEW IMPORT

warnings.filterwarnings("ignore")

# ==========================================
# 🔐 SECURE KEYS SETUP
# ==========================================
# This loads the keys from your .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Safety check to ensure keys are loaded
if not TOKEN or not GEMINI_KEY:
    print("❌ ERROR: Keys not found! Make sure you created the .env file with DISCORD_TOKEN and GEMINI_API_KEY.")
    exit()

# ==========================================
# ⚙️ SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Must be ON in Dev Portal
intents.voice_states = True 

bot = commands.Bot(command_prefix="!", intents=intents)
bot.current_song = None 

# AI Setup
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    chat_session = model.start_chat(history=[])
except Exception as e:
    print(f"❌ AI ERROR: {e}")

# Music Setup
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', 
}
ffmpeg_options = {'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data: data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# ==========================================
# 🚀 EVENTS
# ==========================================

@bot.event
async def on_ready():
    print(f'🚀 Logged in as: {bot.user.name}')
    print("✅ System Status: ONLINE")
    change_status.start()

# --- WELCOME SYSTEM ---
@bot.event
async def on_member_join(member):
    await send_welcome_message(member)
    
    # GIVE ROLES
    role_names = ["♥️⇾｜members", "✅️⇾｜Verified"]
    roles_to_add = []
    for name in role_names:
        role = discord.utils.get(member.guild.roles, name=name)
        if role: roles_to_add.append(role)
    
    if roles_to_add:
        try:
            await member.add_roles(*roles_to_add)
            print(f"✅ Added roles to {member.name}")
        except:
            print("❌ Cannot give roles (Check Hierarchy)")

# --- DEBUG COMMANDS ---
@bot.command(name="checkroles")
async def check_roles(ctx):
    target_roles = ["♥️⇾｜members", "✅️⇾｜Verified"]
    bot_member = ctx.guild.me
    msg = "🔍 **Role System Check:**\n"
    for name in target_roles:
        role = discord.utils.get(ctx.guild.roles, name=name)
        if not role:
            msg += f"❌ **NOT FOUND:** `{name}`\n"
        elif role.position >= bot_member.top_role.position:
            msg += f"⚠️ **HIERARCHY ISSUE:** `{name}` is higher than Sugu!\n"
        else:
            msg += f"✅ **READY:** `{name}`\n"
    await ctx.send(msg)

@bot.command(name="testwelcome")
async def test_welcome(ctx):
    await ctx.send("🧪 Testing Welcome...")
    await send_welcome_message(ctx.author)

async def send_welcome_message(member):
    channel_name = "👋⇾｜ᴡᴇʟᴄᴏᴍᴇ"
    channel = discord.utils.get(member.guild.text_channels, name=channel_name)
    
    if not channel:
        print(f"❌ Channel '{channel_name}' not found!")
        return

    c_rules = discord.utils.get(member.guild.text_channels, name="📄⇾｜ʀᴜʟᴇꜱ")
    c_roles = discord.utils.get(member.guild.text_channels, name="✅⇾｜sᴇʟғ_ʀᴏʟᴇ")
    c_chat = discord.utils.get(member.guild.text_channels, name="👥⇾｜ɢᴇɴᴇʀᴀʟ_ᴄʜᴀᴛꜱ")
    c_music = discord.utils.get(member.guild.text_channels, name="🎵⇾｜ᴍᴜꜱɪᴄ_ʀᴇqᴜᴇꜱᴛ")

    link_rules = c_rules.mention if c_rules else "**📄⇾｜ʀᴜʟᴇꜱ**"
    link_roles = c_roles.mention if c_roles else "**✅⇾｜sᴇʟғ_ʀᴏʟᴇ**"
    link_chat = c_chat.mention if c_chat else "**👥⇾｜ɢᴇɴᴇʀᴀʟ_ᴄʜᴀᴛꜱ**"
    link_music = c_music.mention if c_music else "**🎵⇾｜ᴍᴜꜱɪᴄ_ʀᴇqᴜᴇꜱᴛ**"

    embed = discord.Embed(
        title="Welcome To Our Server KL 13 ( കണ്ണൂർ )",
        description=(
            f"You are number **{member.guild.member_count}**\n"
            f"----------------------------------------\n"
            f"Be sure to read  {link_rules}\n"
            f"Get your roles {link_roles}\n"
            f"Chat on general {link_chat}\n"
            f"Listen to Music  {link_music}\n"
            f"----------------------------------------"
        ),
        color=0x00ff00
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    
    # ✅ FIXED GIF LINK
    embed.set_image(url="https://apcp.es/wp-content/uploads/2021/12/banner-welcome.gif")

    await channel.send(f"Hey {member.mention} ,", embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    await bot.process_commands(message)

    if bot.user in message.mentions:
        async with message.channel.typing():
            clean_text = message.content.replace(f'<@{bot.user.id}>', '').strip()
            if not clean_text:
                await message.reply("Beep boop! 🤖")
                return
            try:
                response = chat_session.send_message(clean_text)
                await message.reply(response.text[:2000])
            except Exception:
                await message.reply("I had a glitch!")

# --- STATUS ---
@tasks.loop(seconds=60)
async def change_status():
    is_music_playing = False
    for vc in bot.voice_clients:
        if vc.is_playing():
            is_music_playing = True
            break
    
    if is_music_playing and bot.current_song:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=bot.current_song))
    else:
        status_list = [
            discord.Activity(type=discord.ActivityType.watching, name="u guys"),
            discord.Activity(type=discord.ActivityType.watching, name="admin trying to inspire"),
            discord.Game(name="CSE BTech"), 
            discord.Activity(type=discord.ActivityType.listening, name="you guyz"),
            discord.Activity(type=discord.ActivityType.watching, name="KL 13 Members"),
            discord.Activity(type=discord.ActivityType.watching, name="Thalassery Biryani cooking"),
            discord.Activity(type=discord.ActivityType.listening, name="Malayalam Hits"),
            discord.Game(name="Kannur Vibes"),
            discord.Game(name="With your feelings"),
            discord.Activity(type=discord.ActivityType.competing, name="Vadam Vali"),
        ]
        await bot.change_presence(activity=random.choice(status_list))

# --- MUSIC ---
@bot.command(name='join')
async def join(ctx):
    if not ctx.author.voice: return await ctx.send("❌ Join a voice channel first.")
    await ctx.author.voice.channel.connect()
    await ctx.send(f"🔊 Joined!")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client: 
        await ctx.voice_client.disconnect()
        bot.current_song = None
        await ctx.send("👋 Bye!")

@bot.command(name='play')
async def play(ctx, *, url):
    try:
        vc = ctx.voice_client
        if not vc:
            if ctx.author.voice: vc = await ctx.author.voice.channel.connect()
            else: return await ctx.send("Join a VC first!")
        
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            vc.play(player, after=lambda e: print(f'Err: {e}') if e else None)
            bot.current_song = player.title
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.title))
        await ctx.send(f'🎶 **Playing:** {player.title}')
    except Exception as e:
        await ctx.send("❌ Error! (Check FFmpeg)")
        print(f"Music Error: {e}")
on_ready(): keep_alive()
bot.run(TOKEN)
