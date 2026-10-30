const API_BASE = "http://127.0.0.1:8000/api/v1/analyze";

const urlForm = document.getElementById("urlForm");
const messageForm = document.getElementById("messageForm");

const urlInput = document.getElementById("urlInput");
const messageInput = document.getElementById("messageInput");

const urlButton = document.getElementById("analyzeBtn");
const messageButton = document.getElementById("analyzeMessageBtn");

const urlModeBtn = document.getElementById("urlModeBtn");
const messageModeBtn = document.getElementById("messageModeBtn");

console.log("CogniSafe JavaScript loaded");
console.log("URL button:", urlModeBtn);
console.log("Message button:", messageModeBtn);

const errorMessage = document.getElementById("errorMessage");
const result = document.getElementById("result");

let currentMode = "url";

// Switch between URL and message analysis.
urlModeBtn.addEventListener("click", () => switchMode("url"));
messageModeBtn.addEventListener("click", () => switchMode("message"));

function switchMode(mode) {
    currentMode = mode;

    const isUrl = mode === "url";

    urlForm.classList.toggle("hidden", !isUrl);
    messageForm.classList.toggle("hidden", isUrl);

    urlModeBtn.classList.toggle("active", isUrl);
    messageModeBtn.classList.toggle("active", !isUrl);

    urlModeBtn.setAttribute("aria-pressed", String(isUrl));
    messageModeBtn.setAttribute("aria-pressed", String(!isUrl));

    clearMessages();
}

// URL analysis.
urlForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const url = urlInput.value.trim();

    clearMessages();

    if (!url) {
        showError("Please enter a URL.");
        return;
    }

    try {
        const parsedUrl = new URL(url);

        if (!["http:", "https:"].includes(parsedUrl.protocol)) {
            showError("Please enter an HTTP or HTTPS URL.");
            return;
        }

        if (!parsedUrl.hostname || !parsedUrl.hostname.includes(".")) {
            showError("Please enter a complete website URL.");
            return;
        }
    } catch {
        showError("Enter a valid URL, including https:// or http://.");
        return;
    }

    await analyze(
        `${API_BASE}/url`,
        { url },
        urlButton,
        "Analyze URL ↗"
    );
});

// Message analysis.
messageForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const text = messageInput.value.trim();

    clearMessages();

    if (!text) {
        showError("Please enter a message to analyze.");
        return;
    }

    if (text.length > 10000) {
        showError("The message must not exceed 10,000 characters.");
        return;
    }

    await analyze(
        `${API_BASE}/message`,
        { text },
        messageButton,
        "Analyze Message ↗"
    );
});

// Send a request to the backend.
async function analyze(endpoint, payload, button, originalLabel) {
    button.disabled = true;
    button.textContent = "Analyzing...";

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            let message = "The server could not analyze your input.";

            if (typeof data.detail === "string") {
                message = data.detail;
            } else if (Array.isArray(data.detail)) {
                message = data.detail
                    .map((item) => item.msg || "Invalid input")
                    .join("; ");
            }

            throw new Error(message);
        }

        displayResults(data);

    } catch (error) {
        if (error instanceof TypeError) {
            showError(
                "Cannot connect to the API. Check that FastAPI is running and CORS is configured."
            );
        } else {
            showError(error.message || "Something went wrong.");
        }
    } finally {
        button.disabled = false;
        button.textContent = originalLabel;
    }
}

// Display the backend's structured response.
function displayResults(data) {
    const score = Number(data.risk_score);

    if (
        !Number.isFinite(score) ||
        score < 0 ||
        score > 100
    ) {
        showError("The API returned an invalid risk score.");
        return;
    }

    const level = String(data.risk_level || "Unknown");
    const normalizedLevel = level.toLowerCase();

    document.getElementById("riskScore").textContent = score;


const riskBadge = document.getElementById("riskLevel");
riskBadge.textContent = level;
riskBadge.className = "risk-badge";

const scoreIcon = document.getElementById("scoreIcon");

if (normalizedLevel === "critical" || normalizedLevel === "high") {
    riskBadge.classList.add("high");
    scoreIcon.textContent = "✕";
    scoreIcon.style.background = "#ffebeb";
    scoreIcon.style.color = "#b52e2e";

} else if (normalizedLevel === "medium") {
    riskBadge.classList.add("medium");
    scoreIcon.textContent = "!";
    scoreIcon.style.background = "#fff4d9";
    scoreIcon.style.color = "#956400";

} else if (normalizedLevel === "low") {
    riskBadge.classList.add("low");
    scoreIcon.textContent = "!";
    scoreIcon.style.background = "#fff4d9";
    scoreIcon.style.color = "#956400";

} else {
    scoreIcon.textContent = "✓";
    scoreIcon.style.background = "#ddf6e8";
    scoreIcon.style.color = "#16824d";
}



    const reasonsList = document.getElementById("reasonsList");
    reasonsList.replaceChildren();

    const reasons = Array.isArray(data.reasons) ? data.reasons : [];

    if (reasons.length === 0) {
        const item = document.createElement("li");
        item.textContent = "No specific indicators were returned.";
        reasonsList.appendChild(item);
    } else {
        reasons.forEach((reason) => {
            const item = document.createElement("li");
            item.textContent = String(reason);
            reasonsList.appendChild(item);
        });
    }

    document.getElementById("recommendationText").textContent =
        data.recommendation ||
        "Verify the source independently before sharing sensitive information.";

    // Clearly label mock results if the backend provides this field.
    const resultSource = document.getElementById("resultSource");

    if (resultSource) {
        if (data.is_mock === true) {
            resultSource.textContent =
                "Development mode: this is a mock result, not a real AI prediction.";
        } else if (data.detection_method) {
            resultSource.textContent =
                `Detection method: ${String(data.detection_method)}`;
        } else {
            resultSource.textContent = "";
        }
    }

    result.classList.remove("hidden");
    result.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}

function clearMessages() {
    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
    result.classList.add("hidden");
}