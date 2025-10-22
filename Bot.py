import os
import base64
import orjson
import asyncio
import discord
import requests
import argparse
from discord.ext import tasks
from dotenv import load_dotenv, dotenv_values
from discord import app_commands, Interaction, Embed, File

# Setup Credentials
load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MINECRAFT_SERVER_IP = os.getenv("MINECRAFT_SERVER_IP")

# Setup
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

def get_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return {}
    else:
        with open(WATCHLIST_FILE, 'rb') as f:
            return orjson.load(f)

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, 'wb') as f:
        f.write(orjson.dumps(watchlist, option=orjson.OPT_INDENT_2))

@tasks.loop(minutes=1)
async def auto_message():
    try:
        url = f"https://api.mcsrvstat.us/2/{MINECRAFT_SERVER_IP}"
        response = requests.get(url)
        data = orjson.loads(response.text)
        watchlist = get_watchlist()
    except Exception as e:
        print(f"An Error Has Occurred: {e}")
    player_list = data.get("players", {}).get("list", [])
    for player in player_list:
        if player in watchlist:
            for user_id in watchlist[player]:
                user = await client.fetch_user(int(user_id))
                try:
                    embed = discord.Embed(title="Player is Online", color=discord.Color.dark_green())
                    embed.add_field(name="", value=f"Player **{player}** is online", inline=False)
                    embed.set_thumbnail(url=f"https://mc-heads.net/avatar/{player}")
                    await user.send(embed=embed)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"An Error Has Occurred: {e}")
                watchlist[player].remove(user_id)
    save_watchlist(watchlist)

@client.event
async def on_ready():
    global WATCHLIST_FILE
    WATCHLIST_FILE = 'watchlist.json'
    if not os.path.exists(WATCHLIST_FILE):
        open(WATCHLIST_FILE, 'w').close()
    print(f"Bot is ready. Logged in as {client.user} (ID: {client.user.id})")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    auto_message.start()

# Commands
@tree.command(name="ping", description="sends ping of bot", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    latency = client.latency * 1000  # Convert to ms
    await interaction.response.send_message(f'Pong! `{latency:.2f}ms`', ephemeral=True)

@tree.command(name="info", description="sends server info", guild=discord.Object(id=GUILD_ID))
async def get_sever_info(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        url = f"https://api.mcsrvstat.us/2/{MINECRAFT_SERVER_IP}"
        response = requests.get(url)
        data = response.orjson()
    except Exception as e:
        print(f"An Error Has Occurred: {e}")

    # Server info
    version = data.get("version")
    online = data.get("online")

    # Players
    player_list = data.get("players", {}).get("list", [])
    players_online = len(player_list)
    players_max = data.get("players", {}).get("max", 0)

    # Download and decord thumbnail
    base64_string = data["icon"].split(",")[1]
    with open("server_icon.png", "wb") as image_file:
        image_file.write(base64.b64decode(base64_string))
    shortened_list = ''
    overflown_usernames_count = 0

    for player in player_list:
        if (len(player) + len(shortened_list)) < 1800:
            shortened_list += f'{player}, '
        else:
            overflown_usernames_count += 1

    if overflown_usernames_count > 0:
        shortened_list += f'+{overflown_usernames_count} other people, '

    async def info_command(interaction: discord.Interaction):
        if online is True:
            embed = discord.Embed(title="Server Info", color=discord.Color.dark_green())
        elif online is False:
            embed = discord.Embed(title="Server Info", color=discord.Color.dark_red())
        else:
            embed = discord.Embed(title="Server Info", color=discord.Color.light_gray())
        embed.set_thumbnail(url="attachment://server_icon.png")
        embed.add_field(name="Players", value=f"{players_online}/{players_max}", inline=False)
        embed.add_field(name="Player List:", value=shortened_list[0:-2], inline=False)

        if online is True:
            embed.set_footer(text="Online 🟢")
        elif online is False:
            embed.set_footer(text="Offline 🔴")
        else:
            embed.set_footer(text="Error Getting Status")
        file = File("server_icon.png", filename="server_icon.png")
        await interaction.followup.send(embed=embed, file=file)
    await info_command(interaction)
    os.remove('server_icon.png')

@tree.command(name="watch", description="DMs you when a certin player gets online", guild=discord.Object(id=GUILD_ID))
async def watchlist(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)
    data = get_watchlist()
    if username not in data:
        data[username] = []
    if username not in data[username]:
        data[username].append(user_id)
    save_watchlist(data)
    await interaction.response.send_message(f"You’ll be notified in DMs when {username} logs on.", ephemeral=True)

client.run(BOT_TOKEN)
