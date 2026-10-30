import sys
from pathlib import Path

# Let this file find risk_scoring.py in the same folder
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from risk_scoring import analyze_message, analyze_url  # loads both models

project_folder = Path(__file__).resolve().parent.parent

app = FastAPI(title="COGNISAFE API (draft v0.1)", version="0.1.0")

# Only these local addresses may call the API from a browser page.
# If your teammate's app uses another port, add it to this list.
ALLOWED_ORIGINS = [
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:8080", "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class MessageRequest(BaseModel):
    text: str


class UrlRequest(BaseModel):
    url: str


def bad_request(message):
    """Error format from API_CONTRACT.md"""
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "invalid_input", "message": message}},
    )


@app.exception_handler(RequestValidationError)
async def handle_bad_body(request, exc):
    return bad_request(
        'Request body must be JSON with a required text field, '
        'for example {"text": "..."} or {"url": "..."}, and the value must be a string.'
    )


@app.get("/", include_in_schema=False)
def demo_page():
    return FileResponse(project_folder / "web" / "demo.html")


@app.get("/health")
def health():
    # If this code is running, both models were loaded successfully
    return {"status": "ok", "models_loaded": True, "version": "0.1.0"}


@app.post("/api/v1/analyze/message")
def analyze_message_endpoint(body: MessageRequest):
    result = analyze_message(body.text)
    if "error" in result:
        return bad_request(result["error"])
    return result


@app.post("/api/v1/analyze/url")
def analyze_url_endpoint(body: UrlRequest):
    # The URL is only read as text. It is never opened.
    result = analyze_url(body.url)
    if "error" in result:
        return bad_request(result["error"])
    return result