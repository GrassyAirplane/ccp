# CCP - Comprehensive Capture and Processing System

## Description

CCP is a multi-modal AI-powered system that integrates voice capture (STT), screen recording, OCR, RAG (Retrieval-Augmented Generation), and a web interface for interacting with large language models.

## Features

- Voice capture and speech-to-text (STT)
- Screen recording
- Optical Character Recognition (OCR)
- RAG ingestion for document processing
- LLM server for model interactions
- Web interface for user interaction

## Prerequisites

- Python 3.x
- Node.js
- Ollama (for running the language model)
- npm or yarn

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GrassyAirplane/ccp.git
   cd ccp
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies for the web app:
   ```bash
   cd web
   npm install
   cd ..
   ```

4. Install dependencies for the LLM server:
   ```bash
   cd llm
   npm install
   cd ..
   ```

5. Ensure Ollama is installed and running.

## Usage

To run the entire system, start the components in the following order:

1. Start the voice capture (STT):
   ```bash
   python stt_worker.py
   ```

2. Start the screen capture:
   ```bash
   python recorder_host.py
   ```

3. Start the model (Ollama):
   ```bash
   ollama serve
   ```

4. Start the OCR worker:
   ```bash
   python ocr_worker.py
   ```

5. Start the RAG ingestion:
   ```bash
   python rag_ingestion.py
   ```

6. Start the LLM server:
   ```bash
   cd llm
   node server.js
   ```

7. Start the web server:
   ```bash
   cd web
   npm run dev
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
