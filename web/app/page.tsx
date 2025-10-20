"use client"
import { useState } from "react";

export default function Home() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (loading) return; // Prevent multiple clicks
    setLoading(true);
    setAnswer("Thinking...");
    try {
      const res = await fetch(`http://localhost:8000/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: q }),
      });
      const data = await res.json();
      setAnswer(data.response || data.error || "No response");
    } catch (error) {
      setAnswer("Error: " + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 40, fontFamily: "sans-serif" }}>
      <h1>🧠 Local Rewind POC</h1>
      <textarea 
        value={q} 
        onChange={e => setQ(e.target.value)} 
        placeholder="Ask about your recent screen..." 
        rows={4} 
        cols={60}
        disabled={loading}
      />
      <br/>
      <button onClick={ask} disabled={loading}>
        {loading ? "Loading..." : "Ask"}
      </button>
      <pre style={{ whiteSpace: "pre-wrap", marginTop: 20 }}>{answer}</pre>
    </div>
  );
}
