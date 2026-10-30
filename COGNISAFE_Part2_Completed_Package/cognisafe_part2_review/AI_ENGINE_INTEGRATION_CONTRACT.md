# AI Engine Integration Contract (to agree with the model teammate)

Do not replace the current detector with guessed imports or guessed model APIs. First confirm the actual module, function name, dependencies, and expected input/output.

## Suggested interface
A detector should accept one message or URL and return a normalized result containing:
- `risk_score`: integer from 0 to 100
- `risk_level`: human-readable category
- `reasons`: list of strings explaining detected signals
- `recommendation`: user-facing safety advice
- `detection_method`: a value that identifies the actual engine used

## Integration requirements
- Validate the input before calling the engine.
- Handle engine exceptions without returning a traceback to the browser.
- Do not log full private messages or sensitive URL query parameters unnecessarily.
- Keep the API response field names stable so the frontend does not break.
- Add tests using representative expected results from the real model.
- Do not claim model accuracy or production readiness without evaluation data.
