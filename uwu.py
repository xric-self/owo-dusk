# This file is part of owo-dusk.
#
# Copyright (c) 2024-present EchoQuill
#
# Portions of this file are based on code by EchoQuill, licensed under the
# GNU General Public License v3.0 (GPL-3.0).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import os
import sys
import subprocess

# ========================================================
# START: RAILWAY / SERVER ADAPTATION
# ========================================================

# If tokens.txt doesn't exist and we have environment variables, create it
if not os.path.exists("tokens.txt"):
    token = os.getenv("DISCORD_TOKEN")
    channel = os.getenv("CHANNEL_ID")
    if token and channel:
        with open("tokens.txt", "w", encoding="utf-8") as f:
            f.write(f"{token} {channel}\n")
        print("[✓] tokens.txt created from environment variables.")
    else:
        print("[!] No DISCORD_TOKEN or CHANNEL_ID environment variables set.")
        print("[!] Please set them in Railway's Variables tab.")
        sys.exit(1)

# ========================================================
# END: RAILWAY / SERVER ADAPTATION
# ========================================================

# Original imports (some may be unused, kept for compatibility)
import tomllib

import utils.system as syst
from utils.colors import COLORS

try:
    syst.system.clear()
except Exception:
    pass

def load_json_dict(file_path="config/captcha.toml"):
    with open(file_path, "rb") as config_file:
        return tomllib.load(config_file)

cap_cnf_dict = load_json_dict()

print(f"{COLORS.BOLD_GREEN}Welcome to OwO-Dusk\nThis setup will guide you through with the setup of OwO-Dusk\nThank you for your trust in OwO-Dusk <3{COLORS.RESET}")

# ========================================================
# Bypass interactive setup because we are on Railway
# ========================================================
print(f"{COLORS.BOLD_CYAN}[0]Running in server mode – skipping interactive setup.{COLORS.RESET}")

# Ensure tokens.txt is readable
try:
    with open("tokens.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        raise ValueError("tokens.txt is empty")
    print(f"{COLORS.BOLD_GREEN}[✓] tokens.txt loaded successfully.{COLORS.RESET}")
except Exception as e:
    print(f"{COLORS.BOLD_RED}[x] Failed to read tokens.txt: {e}{COLORS.RESET}")
    sys.exit(1)

# Now start the actual bot
# We need to import the bot's main function from the appropriate module.
# The original owo-dusk code likely has a function called `start_owodusk` or similar.
# Check if we can import from a module named `main` or `bot` or `core`.
# If not, we'll run a fallback simple bot.

try:
    # Attempt to import the main bot logic from the package
    # (The actual structure may vary; adjust these imports as needed)
    from core import start_bot  # common convention
except ImportError:
    try:
        from main import start_bot
    except ImportError:
        try:
            from bot import start_bot
        except ImportError:
            # If none exist, we'll define a minimal bot here
            print(f"{COLORS.BOLD_YELLOW}[!] Could not find a bot module. Running a minimal fallback bot.{COLORS.RESET}")
            import discord
            import asyncio

            client = discord.Client()

            @client.event
            async def on_ready():
                print(f"{COLORS.BOLD_GREEN}[✓] Fallback bot logged in as {client.user.name}{COLORS.RESET}")
                channel_id = None
                with open("tokens.txt", "r") as f:
                    line = f.readline().strip().split()
                    if len(line) >= 2:
                        channel_id = int(line[1])
                if channel_id:
                    channel = client.get_channel(channel_id)
                    if channel:
                        await channel.send("Bot is online (fallback mode).")
                    else:
                        print(f"{COLORS.BOLD_RED}[x] Could not find channel with ID {channel_id}{COLORS.RESET}")

            @client.event
            async def on_message(message):
                if message.author == client.user:
                    return
                # Basic echo for testing
                if message.content.startswith("!ping"):
                    await message.channel.send("Pong!")

            # Read token from tokens.txt
            with open("tokens.txt", "r") as f:
                token = f.readline().strip().split()[0]
            client.run(token)
            sys.exit(0)  # exit after bot runs (should never reach here)

# If we successfully imported a start_bot function, call it
def start_bot_from_module(start_func):
    try:
        # Read token and channel from tokens.txt for the bot module
        with open("tokens.txt", "r") as f:
            line = f.readline().strip().split()
            token = line[0]
            channel = int(line[1]) if len(line) > 1 else None
        # Pass these to the bot's start function if it expects them
        # Many bot modules read tokens internally, so we just call start_func()
        start_func()
    except Exception as e:
        print(f"{COLORS.BOLD_RED}[x] Error starting bot: {e}{COLORS.RESET}")
        sys.exit(1)

# If we reached here, we have start_bot from one of the imports
if 'start_bot' in locals():
    start_bot_from_module(start_bot)
else:
    # Shouldn't happen, but just in case
    print(f"{COLORS.BOLD_RED}[x] No start_bot function found. Exiting.{COLORS.RESET}")
    sys.exit(1)
