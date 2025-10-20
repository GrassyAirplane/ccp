import sqlite3
import pytesseract
import os
import time
from PIL import Image
from datetime import datetime

DB_PATH = "data/db/localdb.sqlite"

# --------------------------------------
# Database initialization
# --------------------------------------
def init_database():
    os.makedirs("data/db", exist_ok=True)
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
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS ocr_results (
        frame_id INTEGER,
        text TEXT,
        loaded_at TEXT,
        FOREIGN KEY(frame_id) REFERENCES frames(id)
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS rag_results (
        frame_id INTEGER,
        json_data TEXT,
        FOREIGN KEY(frame_id) REFERENCES frames(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("[OCR] Database initialized")

# --------------------------------------
# OCR Processing Loop
# --------------------------------------
def process_frames():
    print("[OCR] Worker started")
    
    while True:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get the oldest pending frame
        c.execute("""
            SELECT id, path, loaded_at FROM frames
            WHERE ocr_status = 'pending'
            ORDER BY loaded_at ASC LIMIT 1
        """)
        row = c.fetchone()

        if not row:
            conn.close()
            time.sleep(3)
            continue

        fid, path, loaded_at = row

        try:
            # Lock frame to prevent double work
            c.execute("UPDATE frames SET ocr_status='processing' WHERE id=?", (fid,))
            conn.commit()

            # Perform OCR
            text = pytesseract.image_to_string(Image.open(path))

            # Store result
            c.execute("INSERT INTO ocr_results (frame_id, text, loaded_at) VALUES (?, ?, ?)", (fid, text, loaded_at))
            c.execute("UPDATE frames SET ocr_status='done' WHERE id=?", (fid,))
            conn.commit()

            print(f"[OCR] Extracted text from {path}")

        except Exception as e:
            print(f"[OCR ERROR] Failed on {path}: {e}")
            c.execute("UPDATE frames SET ocr_status='error' WHERE id=?", (fid,))
            conn.commit()

        finally:
            conn.close()
            time.sleep(2)

# --------------------------------------
# Entrypoint
# --------------------------------------
if __name__ == "__main__":
    try:
        init_database()
        process_frames()
    except KeyboardInterrupt:
        print("\n[OCR] Stopping worker gracefully...")
    except Exception as e:
        print(f"[OCR] Fatal error: {e}")
