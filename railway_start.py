import os
import sys
import sqlite3
import subprocess

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)

print("[START] railway_start.py is executing...")

# ============================================================
# Install all required packages
# ============================================================
required_packages = [
    "numpy",
    "Pillow",
    "onnxruntime",
    "playsound3",
    "plyer"
]

missing = []
for pkg in required_packages:
    try:
        if pkg == "Pillow":
            import PIL
        elif pkg == "onnxruntime":
            import onnxruntime
        elif pkg == "playsound3":
            import playsound3
        elif pkg == "plyer":
            import plyer
        else:
            import numpy
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"[INFO] Installing missing packages: {', '.join(missing)}")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    print("[✓] Missing packages installed.")
else:
    print("[✓] All required packages are already installed.")

# ============================================================
# Read environment variables
# ============================================================
token = os.getenv("DISCORD_TOKEN")
channel_ids_str = os.getenv("CHANNEL_IDS")
if not token or not channel_ids_str:
    print("[ERROR] DISCORD_TOKEN and CHANNEL_IDS required.")
    sys.exit(1)
channel_ids = [cid.strip() for cid in channel_ids_str.split(",") if cid.strip()]
if not channel_ids:
    print("[ERROR] No valid channel IDs.")
    sys.exit(1)

print(f"[INFO] Token: {token[:10]}...")
print(f"[INFO] Channels: {channel_ids}")

# tokens.txt
tokens_and_channels = []
for cid in channel_ids:
    try:
        tokens_and_channels.append((token, int(cid)))
    except ValueError:
        print(f"[ERROR] Invalid channel ID: {cid}")
        sys.exit(1)
with open("tokens.txt", "w") as f:
    for t, c in tokens_and_channels:
        f.write(f"{t} {c}\n")
print("[✓] tokens.txt written.")

# ============================================================
# Database setup (same as before, with ALTER TABLE)
# ============================================================
print("[INFO] Initializing database...")
os.makedirs("utils/data", exist_ok=True)
db_path = "utils/data/db.sqlite"

def add_column_if_not_exists(cursor, table, column, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"[✓] Added column '{column}' to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS command_priority (
        user_id TEXT, command_name TEXT, priority INTEGER,
        PRIMARY KEY (user_id, command_name)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id TEXT PRIMARY KEY, name TEXT,
        daily INTEGER DEFAULT 0, lottery INTEGER DEFAULT 0,
        cookie INTEGER DEFAULT 0, giveaways INTEGER DEFAULT 0,
        captchas INTEGER DEFAULT 0, cowoncy INTEGER DEFAULT 0,
        boss INTEGER DEFAULT 0, boss_ticket INTEGER DEFAULT 0,
        pup INTEGER DEFAULT 0, piku INTEGER DEFAULT 0,
        army INTEGER DEFAULT 0
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cowoncy_earnings (
        user_id TEXT, hour INTEGER, earnings INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, hour)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS meta_data (
        key TEXT PRIMARY KEY, value TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gamble_entries (
        user_id TEXT, gamble_id TEXT, amount INTEGER,
        result TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lottery_entries (
        user_id TEXT, lottery_id TEXT, tickets INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gamble_winrate (
        user_id TEXT, command_name TEXT,
        wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0,
        total_gambles INTEGER DEFAULT 0,
        net INTEGER DEFAULT 0, count INTEGER DEFAULT 0,
        hour INTEGER DEFAULT 0, name TEXT,
        PRIMARY KEY (user_id, command_name)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT, command_name TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        count INTEGER DEFAULT 1, net INTEGER DEFAULT 0,
        hour INTEGER DEFAULT 0, name TEXT
    )
''')

# Add missing columns
add_column_if_not_exists(cursor, "user_stats", "name", "TEXT")
add_column_if_not_exists(cursor, "gamble_winrate", "hour", "INTEGER")
add_column_if_not_exists(cursor, "gamble_winrate", "name", "TEXT")
add_column_if_not_exists(cursor, "gamble_winrate", "net", "INTEGER")
add_column_if_not_exists(cursor, "gamble_winrate", "count", "INTEGER")
add_column_if_not_exists(cursor, "commands", "hour", "INTEGER")
add_column_if_not_exists(cursor, "commands", "name", "TEXT")
add_column_if_not_exists(cursor, "commands", "net", "INTEGER")

cursor.execute('''
    INSERT OR IGNORE INTO meta_data (key, value)
    VALUES
        ('cowoncy_earnings_last_checked', '0'),
        ('last_reset', '0'),
        ('boss_last_spawn', '0')
''')
conn.commit()
conn.close()
print("[✓] Database fully initialized.")

# ============================================================
# Start the bot
# ============================================================
try:
    from core.bot_runner import run_bots
    print("[✓] Imported run_bots successfully.")
    run_bots(tokens_and_channels)
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
