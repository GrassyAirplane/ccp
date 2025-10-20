import time, os, sqlite3, requests
from datetime import datetime
import subprocess

# Use macOS screencapture instead of mss
os.makedirs("data/screenshots", exist_ok=True)
os.makedirs("data/db", exist_ok=True)

CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", "60"))
DB_PATH = "data/db/localdb.sqlite"

# Ensure DB exists
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS frames (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT,
  path TEXT,
  ocr_status TEXT DEFAULT 'pending',
  loaded_at TEXT
)
""")
conn.commit()
conn.close()

def capture_screen():
    ts = datetime.utcnow().isoformat()
    filename = f"data/screenshots/{ts}.png"
    
    # Use macOS built-in screencapture command
    subprocess.run(["screencapture", "-x", filename], check=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO frames (created_at, path, loaded_at) VALUES (?, ?, ?)", (ts, f"data/screenshots/{ts}.png", ts))
    conn.commit()
    conn.close()
    print(f"[RECORDER] Captured {filename}")

if __name__ == "__main__":
    print("Starting macOS screen recorder...")
    while True:
        try:
            capture_screen()
            time.sleep(CAPTURE_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopping recorder...")
            break
        except Exception as e:
            print(f"Error capturing screen: {e}")
            time.sleep(CAPTURE_INTERVAL)