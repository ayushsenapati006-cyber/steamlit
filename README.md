# LazyStudent — Your Morning Study Brief

A beginner-friendly local AI study planner built with Streamlit, Python, PDF text extraction, and Ollama.

## What it does
- Upload text-based assignment PDFs and extract their text locally.
- Add deadlines and study tasks manually.
- Ask a local Ollama model to prioritize tasks and create a time-blocked plan.
- Track tasks with a simple checklist.
- Download your study brief as a text file.

## Requirements
- Python 3.10 or newer
- Ollama installed and running: https://ollama.com
- A model such as `qwen2.5:3b`

## Run it on Windows
1. Install Python and Ollama.
2. Open PowerShell and download the model:

   ```powershell
   ollama pull qwen2.5:3b
   ```

3. Extract this ZIP, then open PowerShell in the `LazyStudent` folder.
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt instead:

   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   streamlit run app.py
   ```

7. Your browser should open the app, usually at `http://localhost:8501`.

## Troubleshooting
- **Can't connect to Ollama:** Start the Ollama app, then run `ollama list` in a terminal.
- **Model not found:** Run `ollama pull qwen2.5:3b` and check the model name in the app sidebar.
- **PDF text is blank:** The PDF may be scanned images rather than selectable text. OCR can be added in a later version.
- **Slow response:** Try a smaller model or upload shorter PDFs.

## Open innovation / privacy
The app uses a locally run model through Ollama rather than a paid hosted AI API. This can avoid per-request API fees and keep study documents on the student's machine. Local inference still uses the computer's CPU/GPU and memory. Check the model's license before redistribution or commercial use.

## Current prototype limitations
- Task data lives in the browser session and is not permanently saved.
- Deadline extraction from assignment text can be imperfect; verify the generated plan.
- Only text-based PDFs are supported; scanned PDFs need OCR.
- The generated plan is advisory, so confirm deadlines and requirements yourself.
