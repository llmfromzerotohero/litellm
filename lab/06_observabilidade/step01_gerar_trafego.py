import os
from pathlib import Path
import requests
import time
import sys

# Garante que o console use UTF-8 no Windows para evitar UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def load_env_file() -> None:
    # Busca .env local, da pasta 05 ou da config geral
    candidates = [
        Path(".env"),
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parents[1] / "05_governanca" / ".env",
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

    sk_estagiario = os.getenv("SK_ESTAGIARIO")
    sk_senior = os.getenv("SK_SENIOR")
    chat_url = get_chat_url()

    if not sk_estagiario or not sk_senior:
        print("[ERRO] Chaves SK_ESTAGIARIO ou SK_SENIOR não encontradas.")
        print("Certifique-se de executar step01_setup_governanca.py na pasta 05_governanca primeiro!")
        return

    print("=" * 60)
    print("LiteLLM - Gerador de Tráfego Operacional para Observabilidade")
    print(f"Chat URL: {chat_url}")
    print("=" * 60)

    # 1. Requisição de Sucesso (Sênior chamando vLLM qwen3.5:2b)
    print("\n[Tráfego 1] Sênior acessa modelo premium qwen3.5:2b...")
    headers_senior = {"Authorization": f"Bearer {sk_senior}", "Content-Type": "application/json"}
    try:
        resp = requests.post(chat_url, headers=headers_senior, json={
            "model": "qwen3.5:2b",
            "messages": [{"role": "user", "content": "Explique brevemente o que é auditoria de sistemas."}]
        }, timeout=30)
        print(f" -> Status: {resp.status_code}")
    except Exception as e:
        print(f" -> Erro: {e}")

    # 2. Requisição de Sucesso (Estagiário chamando Ollama qwen3:0.6b)
    print("\n[Tráfego 2] Estagiário acessa modelo leve qwen3:0.6b...")
    headers_estag = {"Authorization": f"Bearer {sk_estagiario}", "Content-Type": "application/json"}
    try:
        resp = requests.post(chat_url, headers=headers_estag, json={
            "model": "qwen3:0.6b",
            "messages": [{"role": "user", "content": "Olá, me dê uma dica rápida de produtividade."}]
        }, timeout=30)
        print(f" -> Status: {resp.status_code}")
    except Exception as e:
        print(f" -> Erro: {e}")

    # 3. Requisição Proibida (Estagiário chamando qwen3.5:2b) -> Gerar 401/403 no log
    print("\n[Tráfego 3] Estagiário tenta acessar modelo premium proibido (qwen3.5:2b) -> Esperado bloqueio...")
    try:
        resp = requests.post(chat_url, headers=headers_estag, json={
            "model": "qwen3.5:2b",
            "messages": [{"role": "user", "content": "Me dê acesso a este modelo."}]
        }, timeout=30)
        print(f" -> Status: {resp.status_code} (Bloqueio registrado)")
    except Exception as e:
        print(f" -> Erro: {e}")

    # 4. Requisições Rápidas (Estagiário gerando Rate Limit) -> Gerar 429 no log
    print("\n[Tráfego 4] Gerando disparos rápidos com estagiário para estourar RPM=1 -> Esperado 429...")
    for i in range(2):
        try:
            resp = requests.post(chat_url, headers=headers_estag, json={
                "model": "qwen3:0.6b",
                "messages": [{"role": "user", "content": "Ping rápido"}]
            }, timeout=30)
            print(f"   -> Disparo {i+1} Status: {resp.status_code}")
        except Exception as e:
            print(f"   -> Disparo {i+1} Erro: {e}")

    # 5. Requisição que provoca Fallback (Sênior chamando gemma3:1b -> vai falhar e usar qwen3:1.7b)
    print("\n[Tráfego 5] Sênior chama gemma3:1b (porta errada) -> Forçar Fallback automático...")
    try:
        start_time = time.time()
        resp = requests.post(chat_url, headers=headers_senior, json={
            "model": "gemma3:1b",
            "messages": [{"role": "user", "content": "Diga seu nome."}]
        }, timeout=30)
        duration = time.time() - start_time
        print(f" -> Status: {resp.status_code} (Completo em {duration:.2f}s)")
        if resp.status_code == 200:
            payload = resp.json()
            print(f" -> Modelo Solicitado: gemma3:1b | Respondido: {payload.get('model')}")
    except Exception as e:
        print(f" -> Erro: {e}")

    print("\n[SUCESSO] Tráfego de teste gerado com sucesso!")
    print("Agora execute python step02_auditoria_metricas.py para extrair e consolidar as métricas.")


if __name__ == "__main__":
    main()
