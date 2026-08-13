import os
import sys

token = os.getenv("DISCORD_TOKEN")
channel_ids_str = os.getenv("CHANNEL_IDS")

if not token or not channel_ids_str:
    print("[ERROR] DISCORD_TOKEN and CHANNEL_IDS must be set.")
    sys.exit(1)

channel_ids = [cid.strip() for cid in channel_ids_str.split(",") if cid.strip()]
if not channel_ids:
    print("[ERROR] No valid channel IDs.")
    sys.exit(1)

with open("tokens.txt", "w", encoding="utf-8") as f:
    for cid in channel_ids:
        f.write(f"{token} {cid}\n")

print(f"[✓] tokens.txt created with {len(channel_ids)} channel(s).")

from core.bot_runner import run_bot
run_bot()
