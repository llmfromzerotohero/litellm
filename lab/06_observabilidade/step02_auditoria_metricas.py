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


def get_proxy_base_url() -> str:
    base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    return base_url.rstrip("/")


def format_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def print_title(text: str) -> None:
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def main() -> None:
    load_env_file()

    proxy_url = get_proxy_base_url()
    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-master-1234")
    team_id_estag = os.getenv("TEAM_ID_ESTAGIARIO", "")
    team_id_senior = os.getenv("TEAM_ID_SENIOR", "")

    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json"
    }

    url_logs = f"{proxy_url}/spend/logs?limit=50"

    print("=" * 60)
    print("LiteLLM - Painel de Observabilidade, Auditoria e Métricas")
    print(f"Buscando logs de: {url_logs}")
    print("=" * 60)

    try:
        resp = requests.get(url_logs, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[ERRO] Falha ao recuperar logs. Status: {resp.status_code}")
            print(resp.text)
            return
        
        logs_data = resp.json()
        data_list = logs_data if isinstance(logs_data, list) else logs_data.get("data", [])

        if not data_list:
            print("\n[AVISO] Nenhum log de requisição encontrado. Rode o gerador de tráfego primeiro!")
            return

        total_requests = len(data_list)
        total_spend = 0.0
        total_tokens = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0

        # Dicionários para agrupamento de dados
        model_latencies = {}   # model_name: [latencies]
        model_tokens = {}      # model_name: total_tokens
        model_requests = {}    # model_name: count
        
        team_spend = {
            "time-estagiario": 0.0,
            "time-senior": 0.0,
            "Sem Time / Master": 0.0
        }

        # Contadores de auditoria
        errors_401_403 = 0
        errors_429 = 0
        other_errors = 0
        success_count = 0

        for log in data_list:
            # Gastos gerais e tokens
            spend = float(log.get("spend") or 0.0)
            total_spend += spend
            
            p_tokens = int(log.get("prompt_tokens") or 0)
            c_tokens = int(log.get("completion_tokens") or 0)
            t_tokens = p_tokens + c_tokens
            total_prompt_tokens += p_tokens
            total_completion_tokens += c_tokens
            total_tokens += t_tokens

            # Identificação do time
            team_id = log.get("team_id")
            if team_id == team_id_estag:
                team_spend["time-estagiario"] += spend
            elif team_id == team_id_senior:
                team_spend["time-senior"] += spend
            else:
                # Também tenta verificar nas chaves de metadados
                meta_team = log.get("metadata", {}).get("user_api_key_team_id")
                if meta_team == team_id_estag:
                    team_spend["time-estagiario"] += spend
                elif meta_team == team_id_senior:
                    team_spend["time-senior"] += spend
                else:
                    team_spend["Sem Time / Master"] += spend

            # Status de Erros e Sucessos (LiteLLM usa 'status' como success/failure)
            status_str = log.get("status")
            if status_str == "success":
                status_int = 200
            else:
                err_info = log.get("metadata", {}).get("error_information") or {}
                err_code = err_info.get("error_code")
                try:
                    status_int = int(err_code) if err_code else 500
                except ValueError:
                    status_int = 500

            if status_int in (401, 403):
                errors_401_403 += 1
            elif status_int == 429:
                errors_429 += 1
            elif status_int >= 400:
                other_errors += 1
            else:
                success_count += 1

            # Latência e Throughput por Modelo (apenas requisições de sucesso que duraram > 0ms)
            # No banco do LiteLLM a latência é guardada em 'request_duration_ms'
            latency_ms = float(log.get("request_duration_ms") or 0.0)
            if status_int < 400 and latency_ms > 0:
                model_name = log.get("model", "Desconhecido")
                model_latencies.setdefault(model_name, []).append(latency_ms)
                model_tokens.setdefault(model_name, 0)
                model_tokens[model_name] += t_tokens
                model_requests.setdefault(model_name, 0)
                model_requests[model_name] += 1

        # --- 1. PAINEL DE MÉTRICAS FINANCEIRAS ---
        print_title("1. MÓDULO FINANCEIRO (Custos e Budgets)")
        print(f"Custo Total Estimado da Sessão: ${total_spend:.6f} USD")
        print("\nDistribuição de Custos por Time:")
        for team, spend in team_spend.items():
            print(f"  - {team.ljust(20)}: ${spend:.6f} USD")
        
        # --- 2. PAINEL DE PERFORMANCE (PILAR DE MÉTRICAS E TRACES) ---
        print_title("2. MÓDULO DE DESEMPENHO E PERFORMANCE")
        print("Métricas operacionais de sucesso:")
        if not model_latencies:
            print("  (Nenhuma métrica de latência disponível)")
        for model, latencies in model_latencies.items():
            avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
            reqs = model_requests.get(model, 0)
            toks = model_tokens.get(model, 0)
            # throughput = tokens / segundos totais (conversão de ms para s)
            total_sec = sum(latencies) / 1000.0
            throughput = toks / total_sec if total_sec > 0 else 0.0
            
            print(f"  * Modelo: {model}")
            print(f"    - Chamadas bem-sucedidas: {reqs}")
            print(f"    - Latência média:         {avg_lat:.2f} ms")
            print(f"    - Throughput médio:       {throughput:.2f} tokens/s")
            print(f"    - Total de tokens:        {toks}")

        # --- 3. AUDITORIA E SEGURANÇA (PILAR DE LOGS E COMPLIANCE) ---
        print_title("3. MÓDULO DE AUDITORIA E SEGURANÇA")
        print(f"Total de requisições analisadas: {total_requests}")
        print(f"  - Chamadas de Sucesso (200):   {success_count}")
        print(f"  - Chamadas Bloqueadas (401/403):{errors_401_403} (Tentativas não autorizadas)")
        print(f"  - Chamadas Rejeitadas (429):   {errors_429} (Estouro de Rate Limit)")
        print(f"  - Outros Erros Operacionais:   {other_errors}")

        # Taxas operacionais
        err_rate = ((errors_401_403 + errors_429 + other_errors) / total_requests) * 100
        print(f"\nTaxa de Erros Operacionais:     {err_rate:.1f}%")
        print("Nota: Chamadas de fallback bem-sucedidas são registradas sob o modelo final de resposta (ollama/qwen3:1.7b).")

        # --- 4. TRILHA DE LOGS DOS ÚLTIMOS EVENTOS ---
        print_title("4. TRILHA DE AUDITORIA (Logs Recentes)")
        for i, log in enumerate(data_list[:10], 1):
            req_model = log.get("model", "N/A")
            status_str = log.get("status")
            if status_str == "success":
                status_val = "200 OK"
            else:
                err_info = log.get("metadata", {}).get("error_information") or {}
                status_val = f"Erro {err_info.get('error_code', '500')}"
            
            api_key_pref = log.get("api_key")
            api_key_pref = f"{api_key_pref[:12]}..." if api_key_pref and api_key_pref != "None" else "Master/Anon"
            lat = log.get("request_duration_ms")
            lat_text = f"{lat}ms" if lat is not None else "N/A"
            
            print(f"[{i}] Chave: {api_key_pref.ljust(15)} | Modelo: {req_model.ljust(25)} | Status: {status_val.ljust(10)} | Latência: {lat_text}")

    except Exception as e:
        print(f"[ERRO] Ocorreu uma exceção ao tentar consultar as métricas: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print(" Dica de Boas Práticas (Slide 10): Evite logar o corpo do prompt no")
    print(" banco em produção para garantir conformidade de segurança e LGPD.")
    print("=" * 60)


if __name__ == "__main__":
    main()
