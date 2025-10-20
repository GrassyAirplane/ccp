CREATE TABLE IF NOT EXISTS frames (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT,
  path TEXT,
  ocr_status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS ocr_results (
  frame_id INTEGER,
  text TEXT,
  FOREIGN KEY(frame_id) REFERENCES frames(id)
);
