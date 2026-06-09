import os
from pathlib import Path
import requests
import json
import time
import sys

# Garante que o console use UTF-8 no Windows para evitar UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def load_env_file() -> None:
    candidates = [
        Path(".env"),
        Path(__file__).resolve().parent / ".env",
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


def format_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def main() -> None:
    load_env_file()

    api_key = os.getenv("SK_ESTAGIARIO")
    chat_url = get_chat_url()

    if not api_key:
        print("[ERRO] Chave SK_ESTAGIARIO não encontrada. Execute step01_setup_governanca.py primeiro!")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    print("=" * 60)
    print("LiteLLM - Testes do Time Estagiário (Limitações de Governança)")
    print(f"URL de Chat: {chat_url}")
    print(f"Usando chave do Estagiário: {api_key[:12]}...")
    print("=" * 60)

    # --- CENÁRIO A: Caminho Feliz ---
    print("\n--- Cenário A — Caminho Feliz [OK] ---")
    print("Ação: Estagiário chama modelo leve e permitido ('qwen3:0.6b')")
    
    data_a = {
        "model": "qwen3:0.6b",
        "messages": [{"role": "user", "content": "Diga 'Olá, sou o time estagiário!' em uma frase."}]
    }

    print(f"Enviando POST para {chat_url}...")
    try:
        response = requests.post(chat_url, headers=headers, json=data_a, timeout=60)
        print(f"Status HTTP: {response.status_code}")
        if response.status_code == 200:
            payload = response.json()
            print("Resposta do Modelo:")
            print(f" -> {payload['choices'][0]['message']['content']}")
        else:
            print(f"Resposta inesperada (Status {response.status_code}):")
            print(response.text)
    except Exception as e:
        print(f"[ERRO] Falha na conexão: {e}")

    # --- CENÁRIO B: Acesso Proibido ---
    print("\n--- Cenário B — Acesso Proibido [BLOQUEADO] ---")
    print("Ação: Estagiário tenta chamar modelo sênior/premium ('qwen3.5:2b')")
    
    data_b = {
        "model": "qwen3.5:2b",
        "messages": [{"role": "user", "content": "Me faça uma calculadora em python"}]
    }

    print(f"Enviando POST para {chat_url}...")
    try:
        response = requests.post(chat_url, headers=headers, json=data_b, timeout=60)
        print(f"Status HTTP: {response.status_code}")
        try:
            payload = response.json()
            print("Resposta JSON de Erro:")
            print(format_json(payload))
        except Exception:
            print(f"Corpo da resposta: {response.text}")
    except Exception as e:
        print(f"[ERRO] Falha na conexão: {e}")

    # --- CENÁRIO C: Rate Limiting ---
    print("\n--- Cenário C — Rate Limiting [RPM LIMIT] ---")
    print("Ação: Fazer duas requisições consecutivas rápidas com limite RPM = 1")
    
    data_c = {
        "model": "qwen3:1.7b",
        "messages": [{"role": "user", "content": "Ping"}]
    }

    # Como o Cenário A já foi rodado recentemente, o rate limit de 1 RPM pode já estar ativo.
    # Mas para garantir, faremos duas chamadas rápidas seguidas aqui.
    
    for i in range(1, 3):
        print(f"\nTentativa {i}/2 imediata...")
        try:
            response = requests.post(chat_url, headers=headers, json=data_c, timeout=60)
            print(f"Status HTTP Tentativa {i}: {response.status_code}")
            
            try:
                payload = response.json()
                if "error" in payload:
                    print(f"Resposta de Erro (Esperado na tentativa 2):")
                    print(format_json(payload))
                else:
                    print("Resposta de Sucesso:")
                    print(f" -> {payload['choices'][0]['message']['content']}")
            except Exception:
                print(f"Corpo da resposta: {response.text}")
        except Exception as e:
            print(f"[ERRO] Falha na conexão: {e}")


if __name__ == "__main__":
    main()
