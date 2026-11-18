# Week 3 - MongoDB Connectivity and LLM Monitoring

This project sends a prompt to Ollama (or optional Gemini), records token counts, latency, estimated cost, attempts, status, and timestamp in MongoDB database `llm_monitoring`, collection `call_logs`.

## Requirements
- Python 3.10+
- Ollama installed with `llama3.2` downloaded
- MongoDB Community Server installed and running
- MongoDB Compass is optional; it provides a graphical way to inspect the database

## 1. Start/check Ollama (PowerShell)

```powershell
ollama --version
ollama pull llama3.2
ollama list
```

Open the Ollama desktop app if the local service is not already running.

## 2. Start/check MongoDB (Windows PowerShell)

```powershell
Get-Service MongoDB
```

If it is stopped, open PowerShell as Administrator and run:

```powershell
Start-Service MongoDB
```

MongoDB Compass can connect using:

```text
mongodb://localhost:27017/
```

The Python application creates the `llm_monitoring` database and `call_logs` collection automatically when the first log document is inserted. You can also create them manually in Compass as in the Week 3 handout.

## 3. Install Python packages

Open this folder in VS Code, then open its terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Run

```powershell
python main.py
```

Choose `2` for Ollama and enter a prompt. After the response, open Compass, refresh `llm_monitoring` > `call_logs` to see the saved record.

## 5. Verify MongoDB logging

In MongoDB Compass, connect to `mongodb://localhost:27017/`, then open:
- Database: `llm_monitoring`
- Collection: `call_logs`

Each successful or failed model call is recorded. Ollama's token counts come from its response metadata; its API cost is recorded as `0.0` because it runs locally.

## Troubleshooting
- `ServerSelectionTimeoutError`: MongoDB service is not running, or the URI/port is incorrect.
- `Connection refused` at Ollama: open the Ollama app and check `ollama list`.
- `model not found`: run `ollama pull llama3.2`.
- PowerShell blocks activation: run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate the environment again.
- If you only want to test Week 2, MongoDB is not required.
