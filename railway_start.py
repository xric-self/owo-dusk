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

if not token or not channel_ids_str:
    print("[ERROR] DISCORD_TOKEN and CHANNEL_IDS must be set.")
    sys.exit(1)

channel_ids = [cid.strip() for cid in channel_ids_str.split(",") if cid.strip()]
if not channel_ids:
    print("[ERROR] No valid channel IDs.")
    sys.exit(1)

print(f"[INFO] Token: {token[:10]}... (truncated)")
print(f"[INFO] Channels: {channel_ids}")

# ============================================================
# STEP 2: Prepare tokens_and_channels
# ============================================================
tokens_and_channels = []
for cid in channel_ids:
    try:
        cid_int = int(cid)
        tokens_and_channels.append((token, cid_int))
    except ValueError:
        print(f"[ERROR] Invalid channel ID: {cid}")
        sys.exit(1)

print(f"[INFO] Prepared {len(tokens_and_channels)} pair(s).")

# ============================================================
# STEP 3: Write tokens.txt
# ============================================================
with open("tokens.txt", "w", encoding="utf-8") as f:
    for t, c in tokens_and_channels:
        f.write(f"{t} {c}\n")
print("[✓] tokens.txt written.")

# ============================================================
# STEP 4: Create the database with all required tables
# ============================================================
print("[INFO] Initializing database...")

# Ensure the utils/data directory exists
os.makedirs("utils/data", exist_ok=True)

db_path = "utils/data/db.sqlite"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Create all tables that the bot expects ---

    # 1. command_priority
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_priority (
            user_id TEXT,
            command_name TEXT,
            priority INTEGER,
            PRIMARY KEY (user_id, command_name)
        )
    ''')
    print("[✓] Table 'command_priority' created.")

    # 2. user_stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id TEXT PRIMARY KEY,
            daily INTEGER DEFAULT 0,
            lottery INTEGER DEFAULT 0,
            cookie INTEGER DEFAULT 0,
            giveaways INTEGER DEFAULT 0,
            captchas INTEGER DEFAULT 0,
            cowoncy INTEGER DEFAULT 0,
            boss INTEGER DEFAULT 0,
            boss_ticket INTEGER DEFAULT 0,
            pup INTEGER DEFAULT 0,
            piku INTEGER DEFAULT 0,
            army INTEGER DEFAULT 0
        )
    ''')
    print("[✓] Table 'user_stats' created.")

    # 3. cowoncy_earnings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cowoncy_earnings (
            user_id TEXT,
            hour INTEGER,
            earnings INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, hour)
        )
    ''')
    print("[✓] Table 'cowoncy_earnings' created.")

    # 4. meta_data (key-value store)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meta_data (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    print("[✓] Table 'meta_data' created.")

    # 5. gamble_entries (if needed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gamble_entries (
            user_id TEXT,
            gamble_id TEXT,
            amount INTEGER,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("[✓] Table 'gamble_entries' created.")

    # 6. lottery_entries (if needed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lottery_entries (
            user_id TEXT,
            lottery_id TEXT,
            tickets INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("[✓] Table 'lottery_entries' created.")

    # Insert some default meta_data values to avoid NULL errors
    cursor.execute('''
        INSERT OR IGNORE INTO meta_data (key, value)
        VALUES 
            ('cowoncy_earnings_last_checked', '0'),
            ('last_reset', '0'),
            ('boss_last_spawn', '0')
    ''')
    conn.commit()
    print("[✓] Default meta_data entries inserted.")

    conn.close()
    print(f"[✓] Database fully initialized at: {db_path}")

except Exception as e:
    print(f"[ERROR] Database initialization failed: {e}")
    sys.exit(1)

# ============================================================
# STEP 5: Import and run the bot
# ============================================================
try:
    from core.bot_runner import run_bots
    print("[✓] Imported run_bots successfully.")
    print("[INFO] Calling run_bots(tokens_and_channels)...")
    run_bots(tokens_and_channels)
    print("[✓] run_bots() returned (should not happen).")
except ImportError as e:
    print(f"[ERROR] Failed to import run_bots: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] run_bots crashed:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
