import sqlite3
import time
from datetime import datetime
import numpy as np
from stt.recorder import FasterWhisperRecorder

DB_PATH = "data/db/localdb.sqlite"

def init_stt_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS stt_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        text TEXT,
        loaded_at TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("[STT] Database initialized")

def batch_transcription():
    recorder = FasterWhisperRecorder(
        model_size="base.en",
        device="cpu",
        aggressiveness=3,
        silence_duration=0.5,
        min_audio_length=0.4,
    )

    print("[STT] Starting batch transcription (60s intervals)...")
    
    # Start stream ONCE at the beginning
    recorder.start_stream()
    
    try:
        while True:
            start_time = time.time()
            frames = []
            print("[STT] Recording... (live transcript below)")
            live_audio = b""
            
            # Collect audio for 60 seconds
            while time.time() - start_time < 60:
                try:
                    frame = recorder.buffer_queue.get(timeout=1)
                    frames.append(frame)
                    live_audio += frame
                    
                    # Live transcript every ~2 seconds (40 frames at 30ms each)
                    if len(frames) % 40 == 0:
                        audio_np = np.frombuffer(live_audio, np.int16).astype(np.float32) / 32768.0
                        partial = recorder.transcribe(audio_np)
                        if partial:
                            print(f"[LIVE] {partial}")
                except:
                    continue
            
            if frames:
                # Combine frames into audio
                audio_data = b"".join(frames)
                audio_np = np.frombuffer(audio_data, np.int16).astype(np.float32) / 32768.0
                
                # Transcribe
                final_text = recorder.transcribe(audio_np)
                
                if final_text:
                    # Store in DB
                    ts = datetime.utcnow().isoformat()
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("INSERT INTO stt_results (created_at, text, loaded_at) VALUES (?, ?, ?)", 
                             (ts, final_text, ts))
                    conn.commit()
                    conn.close()
                    print(f"[STT] Transcribed and stored: {final_text[:50]}...")
                else:
                    print("[STT] No speech detected in batch")
            else:
                print("[STT] No audio frames collected")
                
            # Brief pause before next batch
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[STT] Stopping batch transcription...")
    finally:
        # Stop stream ONCE at the end
        recorder.stop_stream()

if __name__ == "__main__":
    init_stt_table()
    batch_transcription()
