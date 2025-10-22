# Starts the voice capture (STT)
8. python stt_worker.py 
# Starts the screen capture
2. python recorder_host.py
# Starts the model
3. ollama serve
# Starts the ocr_worker
4. python ocr_worker.py
# Starts the RAG ingestion 
5. python rag_ingestion.py
# Starts the llm server (Logic that the web server talks to)
6. cd llm node server.js
# Starts the web server (Chats with the model to pull from the RAG)
7. cd web npm run dev
