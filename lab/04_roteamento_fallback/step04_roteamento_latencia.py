import os
from pathlib import Path
import time
import requests

MODEL_LATENCY = "modelo-latencia"


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

    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-master-1234")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {master_key}",
    }

    chat_url = get_chat_url()

    print("=== Demonstração de Roteamento por Latência Mínima (LiteLLM Native) ===")
    print(f"Modelo requisitado: '{MODEL_LATENCY}'")
    print(f"URL do Proxy: {chat_url}\n")
    print("Enviando uma série de 6 requisições para observar a escolha de rotas...")
    print("O LiteLLM rastreia as latências e prioriza o deployment mais rápido.")
    print("-" * 70)

    prompts = [
        "O que é o sol? Responda em uma frase.",
        "Qual a capital da França? Responda em uma frase.",
        "O que é água? Responda em uma frase.",
        "Quem descobriu a gravidade? Responda em uma frase.",
        "O que é fotossíntese? Responda em uma frase.",
        "Quantos planetas existem no sistema solar? Responda em uma frase."
    ]

    for i, prompt in enumerate(prompts, 1):
        data = {
            "model": MODEL_LATENCY,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        print(f"Requisição {i}/{len(prompts)}")
        print(f"Prompt: {prompt}")

        start_time = time.time()
        try:
            response = requests.post(chat_url, headers=headers, json=data, timeout=30)
            latency = time.time() - start_time
            response.raise_for_status()

            payload = response.json()
            response_text = payload["choices"][0]["message"]["content"].strip()

            # Cabeçalhos especiais do LiteLLM Proxy para identificar a rota real
            model_id = response.headers.get("x-litellm-model-id", "N/A")
            api_base = response.headers.get("x-litellm-model-api-base", "N/A")

            print(f"-> Tempo de resposta (latência): {latency:.3f}s")
            print(f"-> Deployment selecionado (x-litellm-model-id): {model_id}")
            print(f"-> Base URL correspondente: {api_base}")
            print(f"-> Resposta: {response_text}")

        except Exception as e:
            print(f"Erro ao enviar requisição: {e}")

        print("-" * 70)
        # Pequena pausa para evitar sobrecarga e simular requisições normais
        time.sleep(1)


if __name__ == "__main__":
    main()
