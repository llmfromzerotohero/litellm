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

    api_key = os.getenv("SK_SENIOR")
    chat_url = get_chat_url()

    if not api_key:
        print("[ERRO] Chave SK_SENIOR não encontrada. Execute step01_setup_governanca.py primeiro!")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    print("=" * 60)
    print("LiteLLM - Testes do Time Sênior (Acesso Livre e Fallback)")
    print(f"URL de Chat: {chat_url}")
    print(f"Usando chave do Sênior: {api_key[:12]}...")
    print("=" * 60)

    # --- CENÁRIO D: Privilégio Senior ---
    print("\n--- Cenário D — Privilégio Senior [ACESSO LIVRE] ---")
    print("Ação 1: Chamar modelo premium/vLLM ('qwen3.5:2b')")
    
    data_d1 = {
        "model": "qwen3.5:2b",
        "messages": [{"role": "user", "content": "Diga 'Olá do vLLM' em uma frase curta."}]
    }

    try:
        response = requests.post(chat_url, headers=headers, json=data_d1, timeout=60)
        print(f"Status HTTP: {response.status_code} (Esperado: 200)")
        if response.status_code == 200:
            payload = response.json()
            msg_obj = payload['choices'][0]['message']
            content = msg_obj.get('content') or msg_obj.get('reasoning_content')
            print(f"Resposta: {content}")
        else:
            print(f"Falha: {response.text}")
    except Exception as e:
        print(f"[ERRO] Falha na conexão: {e}")

    print("\nAção 2: Duas chamadas seguidas rápidas (Sênior não sofre rate limit de 1 RPM)")
    data_d2 = {
        "model": "qwen3:0.6b",
        "messages": [{"role": "user", "content": "Ping"}]
    }

    for i in range(1, 3):
        print(f"Chamada {i}/2 imediata...")
        try:
            response = requests.post(chat_url, headers=headers, json=data_d2, timeout=60)
            print(f"Status HTTP Chamada {i}: {response.status_code} (Esperado: 200)")
            if response.status_code == 200:
                payload = response.json()
                msg_obj = payload['choices'][0]['message']
                content = msg_obj.get('content') or msg_obj.get('reasoning_content')
                print(f" -> Resposta: {content}")
            else:
                print(f" -> Falha: {response.text}")
        except Exception as e:
            print(f"[ERRO] Falha na conexão: {e}")

    # --- CENÁRIO E: Fallback Automático ---
    print("\n--- Cenário E — Fallback Automático [CHAVEAMENTO] ---")
    print("Ação: Chamar modelo 'gemma3:1b' que está configurado com porta com erro.")
    print("LiteLLM Proxy deve detectar o erro de conexão e acionar o fallback para 'qwen3:1.7b'.")
    
    data_e = {
        "model": "gemma3:1b",
        "messages": [{"role": "user", "content": "Identifique-se de forma resumida."}]
    }

    print("Enviando requisição...")
    try:
        start_time = time.time()
        response = requests.post(chat_url, headers=headers, json=data_e, timeout=60)
        duration = time.time() - start_time
        print(f"Status HTTP: {response.status_code} (Esperado: 200, com tempo adicional de tentativa de conexão)")
        print(f"Tempo de requisição: {duration:.2f} segundos")
        
        if response.status_code == 200:
            payload = response.json()
            model_retornado = payload.get("model", "")
            print("\nResultado:")
            print(f" -> Modelo Solicitado: gemma3:1b")
            print(f" -> Modelo Retornado:  {model_retornado}")
            if model_retornado != "gemma3:1b":
                print(" -> [FALLBACK RECONHECIDO] O proxy fez o chaveamento automático para o modelo alternativo!")
            msg_obj = payload['choices'][0]['message']
            content = msg_obj.get('content') or msg_obj.get('reasoning_content')
            print(f" -> Resposta do modelo: {content}")
        else:
            print(f"Falha na requisição: {response.text}")
    except Exception as e:
        print(f"[ERRO] Falha na conexão: {e}")

    print("\n[INFO] Fim dos testes do Sênior. Prossiga para o passo 4 de auditoria.")


if __name__ == "__main__":
    main()
