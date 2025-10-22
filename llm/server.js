import express from 'express';
import cors from 'cors';
import sqlite3 from 'sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());
app.use(cors({
  origin: "http://localhost:3000",
  credentials: true
}));

const DB_PATH = path.join(__dirname, '..', 'data', 'db', 'localdb.sqlite');

// Endpoint to get RAG data
app.get('/api/rag', async (req, res) => {
  const db = new sqlite3.Database(DB_PATH);
  db.all("SELECT json_data FROM rag_results", [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    const contexts = rows.map(row => row.json_data).join('\n');
    res.json({ contexts });
  });
  db.close();
});

// Endpoint to chat
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  console.log(`[CHAT] Received request: "${message}"`);
  try {
    // Get RAG contexts
    const db = new sqlite3.Database(DB_PATH);
    db.all("SELECT json_data FROM rag_results", [], async (err, rows) => {
      if (err) {
        console.error('[CHAT] DB error:', err.message);
        res.status(500).json({ error: err.message });
        db.close();
        return;
      }
      const contexts = rows.map(row => row.json_data).join('\n');
      console.log(`[CHAT] Retrieved ${rows.length} RAG contexts`);
      const prompt = `Based on the following context:\n${contexts}\n\nAnswer the question: ${message}`;
      
      try {
        console.log('[CHAT] Sending to Ollama...');
        const response = await fetch('http://localhost:11434/api/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'llama3:latest',
            prompt: prompt,
            stream: false
          })
        });
        
        if (!response.ok) {
          throw new Error(`Ollama error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('[CHAT] Received response from Ollama');
        res.json({ response: result.response });
      } catch (fetchError) {
        console.error('[CHAT] Ollama fetch error:', fetchError);
        res.status(500).json({ error: 'Failed to connect to Ollama. Ensure Ollama is running with the model loaded.' });
      }
      db.close();
    });
  } catch (error) {
    console.error('[CHAT] Error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(8000, () => {
  console.log('LLM Server running on port 8000');
});