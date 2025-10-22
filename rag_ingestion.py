import sqlite3
import requests
import time
import json

DB_PATH = "data/db/localdb.sqlite"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"  # adjust to match your model

# Load the RAG prompt from file
with open("rag_prompt.txt", "r") as f:
    PROMPT = f.read()

def process_rag_frames():
    print("[RAG] Worker started")
    while True:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
        SELECT f.id, o.text, f.loaded_at
        FROM frames f
        JOIN ocr_results o ON f.id = o.frame_id
        LEFT JOIN rag_results r ON f.id = r.frame_id
        WHERE f.ocr_status='done' AND r.frame_id IS NULL
        ORDER BY f.loaded_at ASC
        LIMIT 1
        """)
        row = c.fetchone()
        if not row:
            conn.close()
            time.sleep(5)
            continue

        fid, text, loaded_at = row
        print(f"[RAG] Sending frame {fid} ({loaded_at}) to Ollama model…")
        full_prompt = PROMPT + "\n\n" + text

        try:
            # Non-streaming request
            resp = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": full_prompt, "stream": False},
                timeout=500
            )
            if resp.status_code != 200:
                print(f"[RAG ERROR] {resp.status_code}: {resp.text}")
                continue

            result = resp.json()
            json_data = result.get("response", "")

            # Save result
            c.execute(
                "INSERT INTO rag_results (frame_id, json_data) VALUES (?, ?)",
                (fid, json_data)
            )
            conn.commit()
            print(f"[RAG] Stored structured result for frame {fid}")

        except requests.Timeout:
            print(f"[RAG TIMEOUT] Model took too long for frame {fid}")
        except Exception as e:
            print(f"[RAG ERROR] {e}")
        finally:
            conn.close()
            time.sleep(2)


if __name__ == "__main__":
    try:
        process_rag_frames()
    except KeyboardInterrupt:
        print("\n[RAG] Worker stopped gracefully")
