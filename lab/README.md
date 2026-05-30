# Lab de praticas LiteLLM

Esta pasta concentra as praticas usadas durante a apresentacao do LiteLLM. Cada subpasta representa um tema (roteamento e fallback, custos, observabilidade, etc.) e contem scripts e um roteiro de execucao.

## Pre-requisitos

- Docker Desktop com Docker Compose ativo.
- Portas livres: 4000 (LiteLLM), 5432 (Postgres), 11434 (Ollama), 8000 (vLLM).
- Python 3.11+ para rodar os scripts de cada pratica.
- Instalar as dependencias do Python (via `requirements.txt`)
- (Opcional) GPU NVIDIA + runtime do Docker para o vLLM. Sem GPU, o servico vLLM pode falhar ao subir.

## Configuracao central

Todas as praticas usam a pasta config como base de infraestrutura e configuracao:

- [config/docker-compose.yml](../config/docker-compose.yml): sobe Postgres, Ollama, vLLM e o proxy do LiteLLM.
- [config/config.yaml](../config/config.yaml): lista de modelos, fallbacks e configuracoes do LiteLLM.
- [config/.env](../config/.env): variaveis do banco e do LiteLLM (master key). Chaves de API externas sao opcionais.

Antes de iniciar as praticas, verifique se a .env esta correta e se as portas estao livres.

## Como iniciar (resumo)

1) A partir de [config](../config), suba os containers:

```bash
docker compose up -d
```

2) Baixe os modelos no Ollama (se necessario):

```bash
docker exec -it ollama-service ollama pull qwen3:1.7b
docker exec -it ollama-service ollama pull qwen3.5:4b
docker exec -it ollama-service ollama pull gemma3:1b
...
```

3) Execute a pratica desejada dentro da subpasta correspondente.
