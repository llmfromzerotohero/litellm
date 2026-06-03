import os
from pathlib import Path
import requests
import json
import sys

# Garante que o console use UTF-8 no Windows para evitar UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def load_env_file() -> None:
    # Procura pelo .env no diretório atual e no diretório de configuração central.
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


def get_proxy_base_url() -> str:
    # URL base do proxy LiteLLM (gerenciamento usa a raiz do proxy, não /v1)
    base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
    # Remove /v1 se estiver no final para chamadas administrativas
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    return base_url.rstrip("/")


def save_local_env(env_data: dict) -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    lines = []
    for k, v in env_data.items():
        lines.append(f"{k}={v}")
    
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[INFO] Chaves salvas localmente em: {env_path.name}")


def clean_previous_setup(proxy_url: str, headers: dict) -> None:
    local_env_path = Path(__file__).resolve().parent / ".env"
    if not local_env_path.exists():
        return

    print("\n[INFO] Detectado setup anterior. Tentando limpar chaves e times antigos...")
    old_vars = {}
    for line in local_env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        old_vars[k.strip()] = v.strip()

    # 1. Deletar chaves antigas
    keys_to_delete = []
    if "SK_ESTAGIARIO" in old_vars:
        keys_to_delete.append(old_vars["SK_ESTAGIARIO"])
    if "SK_SENIOR" in old_vars:
        keys_to_delete.append(old_vars["SK_SENIOR"])

    if keys_to_delete:
        try:
            print(f"-> Deletando chaves virtuais antigas: {keys_to_delete}")
            resp = requests.post(
                f"{proxy_url}/key/delete",
                headers=headers,
                json={"keys": keys_to_delete},
                timeout=10
            )
            if resp.status_code == 200:
                print("   Chaves deletadas com sucesso.")
            else:
                print(f"   Falha ao deletar chaves: {resp.text}")
        except Exception as e:
            print(f"   Erro ao tentar conectar para deletar chaves: {e}")

    # 2. Deletar times antigos
    teams_to_delete = []
    if "TEAM_ID_ESTAGIARIO" in old_vars:
        teams_to_delete.append(old_vars["TEAM_ID_ESTAGIARIO"])
    if "TEAM_ID_SENIOR" in old_vars:
        teams_to_delete.append(old_vars["TEAM_ID_SENIOR"])

    if teams_to_delete:
        try:
            print(f"-> Deletando times antigos: {teams_to_delete}")
            resp = requests.post(
                f"{proxy_url}/team/delete",
                headers=headers,
                json={"team_ids": teams_to_delete},
                timeout=10
            )
            if resp.status_code == 200:
                print("   Times deletados com sucesso.")
            else:
                print(f"   Falha ao deletar times: {resp.text}")
        except Exception as e:
            print(f"   Erro ao tentar conectar para deletar times: {e}")


def main() -> None:
    load_env_file()
    
    proxy_url = get_proxy_base_url()
    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-master-1234")
    
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json"
    }

    print("=" * 60)
    print("LiteLLM - Configuração da Governança (Times e Chaves)")
    print(f"Proxy URL: {proxy_url}")
    print("=" * 60)

    # Limpa o setup anterior se existir localmente
    clean_previous_setup(proxy_url, headers)

    # --- 1. Criar Time Estagiário ---
    print("\n1. Criando o Time Estagiário...")
    time_estagiario_payload = {
        "team_alias": "time-estagiario",
        "models": ["qwen3:1.7b", "qwen3:0.6b"],
        "rpm_limit": 1,
        "max_budget": 0.10,
        "budget_duration": "1d"
    }

    try:
        resp = requests.post(
            f"{proxy_url}/team/new",
            headers=headers,
            json=time_estagiario_payload,
            timeout=15
        )
        if resp.status_code not in (200, 201):
            print(f"[ERRO] Falha ao criar time estagiário. Status: {resp.status_code}")
            print(resp.text)
            return
        
        time_estagiario_data = resp.json()
        team_id_estagiario = time_estagiario_data.get("team_id")
        print(f"-> Time Estagiário criado! ID: {team_id_estagiario}")
    except Exception as e:
        print(f"[ERRO] Conexão com o proxy falhou: {e}")
        return

    # --- 2. Gerar Chave Virtual para o Estagiário ---
    print("\n2. Gerando Chave Virtual para o Estagiário...")
    chave_estagiario_payload = {
        "team_id": team_id_estagiario,
        "key_alias": "chave-estagiario",
        "models": ["qwen3:1.7b", "qwen3:0.6b"],
        "rpm_limit": 1,
        "duration": "24h"
    }

    resp = requests.post(
        f"{proxy_url}/key/generate",
        headers=headers,
        json=chave_estagiario_payload,
        timeout=15
    )
    if resp.status_code not in (200, 201):
        print(f"[ERRO] Falha ao gerar chave para estagiário. Status: {resp.status_code}")
        print(resp.text)
        return
    
    key_estagiario = resp.json().get("key")
    print(f"-> Chave do Estagiário gerada: {key_estagiario}")

    # --- 3. Criar Time Sênior ---
    print("\n3. Criando o Time Sênior...")
    time_senior_payload = {
        "team_alias": "time-senior",
        "models": []  # Todos os modelos liberados
    }

    resp = requests.post(
        f"{proxy_url}/team/new",
        headers=headers,
        json=time_senior_payload,
        timeout=15
    )
    if resp.status_code not in (200, 201):
        print(f"[ERRO] Falha ao criar time sênior. Status: {resp.status_code}")
        print(resp.text)
        return
    
    time_senior_data = resp.json()
    team_id_senior = time_senior_data.get("team_id")
    print(f"-> Time Sênior criado! ID: {team_id_senior}")

    # --- 4. Gerar Chave Virtual para o Sênior ---
    print("\n4. Gerando Chave Virtual para o Sênior...")
    chave_senior_payload = {
        "team_id": team_id_senior,
        "key_alias": "chave-senior",
        "duration": "24h"
    }

    resp = requests.post(
        f"{proxy_url}/key/generate",
        headers=headers,
        json=chave_senior_payload,
        timeout=15
    )
    if resp.status_code not in (200, 201):
        print(f"[ERRO] Falha ao gerar chave para sênior. Status: {resp.status_code}")
        print(resp.text)
        return
    
    key_senior = resp.json().get("key")
    print(f"-> Chave do Sênior gerada: {key_senior}")

    # Salva as chaves no .env local do lab
    save_local_env({
        "SK_ESTAGIARIO": key_estagiario,
        "SK_SENIOR": key_senior,
        "TEAM_ID_ESTAGIARIO": team_id_estagiario,
        "TEAM_ID_SENIOR": team_id_senior,
        "LITELLM_BASE_URL": f"{proxy_url}/v1",
        "LITELLM_MASTER_KEY": master_key
    })

    print("\n[SUCESSO] Setup de Governança concluído! Avance para o passo 2.")


if __name__ == "__main__":
    main()
