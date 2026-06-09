import os
from pathlib import Path
import re
import requests

MODEL_CODE = "qwen3.5:2b"
MODEL_SHORT = "qwen3:0.6b"
MODEL_LONG = "qwen3:1.7b"

TOKEN_THRESHOLD = 50

KEYWORDS = {
    "python",
    "javascript",
    "java",
    "c#",
    "csharp",
    "c++",
    "cpp",
    "golang",
    "rust",
    "kotlin",
    "swift",
    "php",
    "ruby",
    "typescript",
    "programacao",
    "programming",
    "nodejs",
    "react",
    "angular",
    "sql",
    "database",
    "api",
    "backend",
    "frontend",
}


def load_env_file() -> None:
    # Minimal .env loader to avoid external dependencies.
    candidates = [
        Path(".env"),
        Path(__file__).resolve().parents[1] / "config" / ".env",
    ]

    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
        break


def estimate_tokens(text: str) -> int:
    # Rough estimate: 1 token ~ 4 chars.
    if not text:
        return 0
    return max(1, len(text) // 4)


def extract_terms(text: str):
    normalized = text.lower().replace("node.js", "nodejs")
    return set(re.findall(r"[a-z0-9\+#]+", normalized))


def route_model(messages):
    content = " ".join(message.get("content", "") for message in messages)
    terms = extract_terms(content)

    if KEYWORDS.intersection(terms):
        return MODEL_CODE, "keyword"

    tokens = estimate_tokens(content)
    if tokens <= TOKEN_THRESHOLD:
        return MODEL_SHORT, f"short:{tokens}"

    return MODEL_LONG, f"long:{tokens}"


def get_chat_url() -> str:
    base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1").rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    return f"{base_url}/chat/completions"


def main() -> None:
    load_env_file()

    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-master-1234")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {master_key}",
    }

    chat_url = get_chat_url()

    print("LiteLLM rule-based routing (blank line to quit)")

    while True:
        user_input = input("Prompt: ").strip()
        if not user_input:
            break

        messages = [
            {
                "role": "system",
                "content": "Responda de forma concisa.",
            },
            {"role": "user", "content": user_input},
        ]

        model, reason = route_model(messages)

        data = {
            "model": model,
            "messages": messages,
        }

        print(f"Enviando request ao modelo: {model}")
        print(f"URL: {chat_url}")
        response = requests.post(chat_url, headers=headers, json=data, timeout=300)
        print("Request concluído. Status:", response.status_code)

        print("ROUTE_REASON:", reason)
        print("MODEL:", model)
        print("STATUS:", response.status_code)

        try:
            payload = response.json()
            response_model = payload.get("model")
            if response_model and response_model != model:
                print("FALLBACK_USED:", response_model)
            print(payload)
        except Exception:
            print(response.text)

        print("-" * 50)


if __name__ == "__main__":
    main()
