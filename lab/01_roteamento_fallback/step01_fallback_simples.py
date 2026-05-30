import os
from pathlib import Path
import requests


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


def get_chat_url() -> str:
    base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1").rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    return f"{base_url}/chat/completions"


def main() -> None:
    load_env_file()

    url = get_chat_url()
    model = "gemma3:1b"
    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-master-1234")

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Com quem estou falando?"}
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {master_key}",
    }

    response = requests.post(url, json=data, headers=headers, timeout=60)

    print("STATUS:", response.status_code)
    try:
        payload = response.json()
        response_model = payload.get("model")
        if response_model and response_model != model:
            print("FALLBACK_USED:", response_model)
        print(payload)
    except Exception:
        print(response.text)


if __name__ == "__main__":
    main()
