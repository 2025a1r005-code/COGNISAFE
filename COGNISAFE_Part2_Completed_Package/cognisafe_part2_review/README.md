# COGNISAFE — Part 2 application layer

This project currently contains a FastAPI backend and an HTML/CSS/JavaScript frontend.
The detector functions in `main.py` are rule-based placeholders for application
integration; they are not the other team member's trained AI model.

## 1. Create and activate a virtual environment (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Run the backend

```powershell
python -m uvicorn main:app --reload
```

Health check: `http://127.0.0.1:8000/health`
API documentation: `http://127.0.0.1:8000/docs`

## 3. Run the frontend

Open a second PowerShell terminal from the project root:

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500/`.

## 4. Run automated tests

Stop neither server is required for these in-process API tests. From the project root:

```powershell
pytest -q
```

The tests check the health endpoint, response structure, message scoring behavior,
and invalid input handling. Test results must be confirmed on your computer after
installing the listed dependencies.

## Important limitations

- Current detection is rule-based, not a real AI prediction or live threat-intelligence lookup.
- A low score does not guarantee a message or URL is safe.
- Do not automatically visit suspicious URLs.
- Agree on the API contract and detector function interface with the AI-engine teammate
  before replacing the rule-based functions.
- This is the existing HTML frontend. If Streamlit is a strict project requirement,
  implement and test it as a separate frontend rather than silently replacing this one.

## Additional handover documents
- `PROJECT_REPORT.md`: project summary and current status.
- `MANUAL_TEST_CHECKLIST.md`: browser/API checks for the demo.
- `AI_ENGINE_INTEGRATION_CONTRACT.md`: interface checklist to agree with the teammate providing the actual model.
