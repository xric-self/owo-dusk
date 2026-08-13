import os
import sys
import sqlite3
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
# STEP 3: Write tokens.txt
# ============================================================
try:
    with open("tokens.txt", "w", encoding="utf-8") as f:
        for t, c in tokens_and_channels:
            f.write(f"{t} {c}\n")
    print("[✓] tokens.txt written successfully.")
except Exception as e:
    print(f"[WARN] Could not write tokens.txt: {e}")

# ============================================================
# STEP 4: Initialize SQLite database (fix missing table)
# ============================================================
print("[INFO] Checking database and creating missing tables if needed...")
try:
    # The bot likely uses a database file in the current directory.
    # We'll look for the most common name: owo.db, dusk.db, or bot.db.
    # If not found, we'll create a default one.
    db_path = None
    for f in os.listdir("."):
        if f.endswith(".db"):
            db_path = f
            break
    if not db_path:
        # Default name used in the bot (common)
        db_path = "owo.db"
        print(f"[INFO] No existing .db file found. Will create {db_path}.")
    
    # Connect to the database (creates if not exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the command_priority table if it doesn't exist
    # The bot queries: SELECT * FROM command_priority WHERE user_id = ?
    # So we need at least a user_id column. We'll add a priority column as well.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_priority (
            user_id TEXT PRIMARY KEY,
            priority INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    print(f"[✓] Database table 'command_priority' created (if not existed).")
    
    # Optionally, we could check if other tables exist, but we'll stop here.
    conn.close()
    print("[✓] Database initialization complete.")
    
except Exception as e:
    print(f"[ERROR] Database initialization failed: {e}")
    # Continue anyway – the bot might handle it gracefully, but we'll proceed.

# ============================================================
# STEP 5: Import and call run_bots with the list
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
