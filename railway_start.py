# ... (same imports and env vars as before)

# ============================================================
# STEP 4: Initialize database with ALL required tables
# ============================================================
print("[INFO] Initializing database...")
os.makedirs("utils/data", exist_ok=True)
db_path = "utils/data/db.sqlite"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Table: command_priority ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_priority (
            user_id TEXT,
            command_name TEXT,
            priority INTEGER,
            PRIMARY KEY (user_id, command_name)
        )
    ''')
    print("[✓] Table 'command_priority' created/verified.")

    # --- Table: user_stats ---
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
    print("[✓] Table 'user_stats' created/verified.")

    # --- Table: cowoncy_earnings ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cowoncy_earnings (
            user_id TEXT,
            hour INTEGER,
            earnings INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, hour)
        )
    ''')
    print("[✓] Table 'cowoncy_earnings' created/verified.")

    # --- Table: meta_data ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meta_data (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    print("[✓] Table 'meta_data' created/verified.")

    # --- Table: gamble_entries ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gamble_entries (
            user_id TEXT,
            gamble_id TEXT,
            amount INTEGER,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("[✓] Table 'gamble_entries' created/verified.")

    # --- Table: lottery_entries ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lottery_entries (
            user_id TEXT,
            lottery_id TEXT,
            tickets INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("[✓] Table 'lottery_entries' created/verified.")

    # --- Table: gamble_winrate ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gamble_winrate (
            user_id TEXT,
            command_name TEXT,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            total_gambles INTEGER DEFAULT 0,
            net INTEGER DEFAULT 0,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, command_name)
        )
    ''')
    print("[✓] Table 'gamble_winrate' created/verified.")

    # --- Table: commands (with count and net) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            command_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            count INTEGER DEFAULT 1,
            net INTEGER DEFAULT 0
        )
    ''')
    print("[✓] Table 'commands' created/verified.")

    # Insert default meta_data entries
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

# ... (rest of the code: import and run_bots)
