import argparse
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
from openai import OpenAI


def _wait_for_proxy(base_url: str, api_key: str, timeout_s: int = 60) -> None:
    # Usar /v1/models (padrao OpenAI) para validar que o proxy esta no ar.
    # Em alguns setups, endpoints "health" podem exigir auth (401), entao tratamos isso como "proxy respondeu".
    models_url = f"{base_url}/models" if base_url.endswith("/v1") else f"{base_url}/v1/models"

    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            req = urllib.request.Request(
                models_url,
                headers={"Authorization": f"Bearer {api_key}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if 200 <= resp.status < 300:
                    return
        except urllib.error.HTTPError as e:
            # 401/403 = proxy respondeu, mas auth pode estar errada
            if e.code in (401, 403):
                return
            last_err = e
            time.sleep(1)
        except Exception as e:  # noqa: BLE001 - simples loop de espera
            last_err = e
            time.sleep(1)

    raise RuntimeError(
        f"LiteLLM proxy nao respondeu em {timeout_s}s: {models_url} ({last_err})"
    )


def _load_env_file() -> None:
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


def main() -> None:
    _load_env_file()
    parser = argparse.ArgumentParser(
        description=(
            "Faz uma pergunta simples via LiteLLM Proxy usando o modelo do vLLM (primario). "
            "Se o vLLM falhar, o LiteLLM Router deve fazer fallback para um modelo do Ollama (conforme config.yaml)."
        )
    )
    parser.add_argument(
        "--question",
        default="Responda em uma frase: o que e vLLM?",
        help="Pergunta a ser enviada ao modelo.",
    )
    parser.add_argument(
        "--model",
        default="qwen3.5:9b",
        help="Model name no LiteLLM (primario vLLM).",
    )
    args = parser.parse_args()

    base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1")
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    # Para LiteLLM Proxy, normalmente qualquer chave serve; aqui usamos o master key por padrao
    api_key = (
        os.getenv("LITELLM_API_KEY")
        or os.getenv("LITELLM_MASTER_KEY")
        or "sk-master-1234"
    )

    _wait_for_proxy(base_url, api_key)

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=60)

    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": args.question}],
        temperature=0.2,
    )

    content = resp.choices[0].message.content
    print("=== Resposta ===")
    print(content)
    print("\n=== Metadados ===")
    print(f"requested_model: {args.model}")
    print(f"response.model: {resp.model}")
    if resp.usage is not None:
        print(
            "usage: "
            f"prompt={resp.usage.prompt_tokens} "
            f"completion={resp.usage.completion_tokens} "
            f"total={resp.usage.total_tokens}"
        )


if __name__ == "__main__":
    main()
