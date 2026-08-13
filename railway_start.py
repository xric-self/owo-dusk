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
# STEP 2: Prepare tokens_and_channels list
# ============================================================
tokens_and_channels = []
for cid in channel_ids:
    try:
        cid_int = int(cid)
        tokens_and_channels.append((token, cid_int))
    except ValueError:
        print(f"[ERROR] Invalid channel ID (must be integer): {cid}")
        sys.exit(1)

print(f"[INFO] Prepared {len(tokens_and_channels)} token-channel pair(s).")

# ============================================================
# STEP 3: Optionally write tokens.txt (some bots expect it)
# ============================================================
try:
    with open("tokens.txt", "w", encoding="utf-8") as f:
        for t, c in tokens_and_channels:
            f.write(f"{t} {c}\n")
    print("[✓] tokens.txt written successfully.")
except Exception as e:
    print(f"[WARN] Could not write tokens.txt: {e}")

# ============================================================
# STEP 4: Import and call run_bots with the list
# ============================================================
try:
    from core.bot_runner import run_bots
    print("[✓] Imported run_bots successfully.")

    print("[INFO] Calling run_bots(tokens_and_channels)...")
    run_bots(tokens_and_channels)
    print("[✓] run_bots() returned (should not happen unless it exits)")

except ImportError as e:
    print(f"[ERROR] Failed to import run_bots: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] run_bots crashed:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
