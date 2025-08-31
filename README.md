# Minecraft Server Info Discord Bot

![Discord](https://img.shields.io/badge/Platform-Discord-7289DA?style=flat&logo=discord)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python)
![Requests](https://img.shields.io/badge/Requests-2.31.0-orange?style=flat)

A **Discord bot** that fetches Minecraft server information, including players online, version, and server icon, and sends it as an embed message.

---

## Features

- Fetches **Minecraft server status** via `mcsrvstat.us` API.
- Displays **online/offline status**.
- Shows **players online** with a character limit safeguard.
- Sends **server icon** as an embed thumbnail.
- **Ping command** to check bot latency.
- Fully **ephemeral responses** for privacy.

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/minecraft-server-discord-bot.git
cd minecraft-server-discord-bot
pip install -r requirements.txt
python Bot.py
