import os
import sys
import time

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)

print("[START] railway_start.py is executing...")

# ============================================================
# STEP 1: Read environment variables
# ============================================================
token = os.getenv("DISCORD_TOKEN")
channel_ids_str = os.getenv("CHANNEL_IDS")

if not token:
    print("[ERROR] DISCORD_TOKEN environment variable is not set.")
    sys.exit(1)

if not channel_ids_str:
    print("[ERROR] CHANNEL_IDS environment variable is not set.")
    sys.exit(1)

channel_ids = [cid.strip() for cid in channel_ids_str.split(",") if cid.strip()]
if not channel_ids:
    print("[ERROR] No valid channel IDs found.")
    sys.exit(1)

print(f"[INFO] Token: {token[:10]}... (truncated)")
print(f"[INFO] Channels: {channel_ids}")

# ============================================================
# STEP 2: Create tokens.txt
# ============================================================
try:
    with open("tokens.txt", "w", encoding="utf-8") as f:
        for cid in channel_ids:
            f.write(f"{token} {cid}\n")
    print("[✓] tokens.txt written successfully.")
except Exception as e:
    print(f"[ERROR] Could not write tokens.txt: {e}")
    sys.exit(1)

# ============================================================
# STEP 3: Launch the bot using run_bots() (reads tokens.txt)
# ============================================================
try:
    # Import the correct function that reads tokens.txt and starts threads
    from core.bot_runner import run_bots  # Note: plural 'run_bots'
    print("[✓] Imported run_bots successfully.")

    # run_bots() reads tokens.txt automatically and starts all threads
    print("[INFO] Calling run_bots()...")
    run_bots()
    print("[✓] run_bots() returned (should not happen unless it exits)")

except ImportError as e:
    print(f"[ERROR] Failed to import run_bots: {e}")
    print("Check that core/bot_runner.py exists and contains run_bots.")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] run_bots crashed:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
