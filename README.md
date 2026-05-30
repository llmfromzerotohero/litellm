# Orquestração e Governança Multi-Modelo de LLMs com LiteLLM

Projeto de demonstracao focado em orquestracao de multiplos modelos, roteamento, fallback e governanca via LiteLLM. Os labs desta pasta cobrem cenarios praticos para execucao durante a apresentacao.

## Estrutura do projeto

- [config](config): infraestrutura e configuracao central
	- [config/docker-compose.yml](config/docker-compose.yml): sobe Postgres, Ollama, vLLM e LiteLLM
	- [config/config.yaml](config/config.yaml): modelos, fallbacks e parametros do proxy
	- [config/.env](config/.env): variaveis de ambiente (master key, database, keys externas opcionais)
- [lab](lab): praticas organizadas por tema
	- [lab/README.md](lab/README.md): indice e pre-requisitos dos labs
- [requirements.txt](requirements.txt): dependencias Python para os scripts

## Requisitos

- Docker Desktop com Docker Compose ativo
- Portas livres: 4000 (LiteLLM), 5432 (Postgres), 11434 (Ollama), 8000 (vLLM)
- Python 3.11+ para executar os scripts de lab
- (Opcional) GPU NVIDIA + runtime do Docker para o vLLM

## Instalacao

1) Instale as dependencias Python:

```bash
pip install -r requirements.txt
```

2) Suba a infraestrutura do LiteLLM:

```bash
cd config
docker compose up -d
```

3) (Opcional) Ajuste as variaveis em [config/.env](config/.env) caso use APIs externas.

## Uso (labs)

1) Leia o guia principal dos labs em [lab/README.md](lab/README.md).
2) Entre na pasta do lab desejado e siga o README da pratica.
3) Execute os scripts na ordem sugerida para demonstrar roteamento, fallback e governanca.
