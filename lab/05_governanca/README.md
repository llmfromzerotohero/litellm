# Governança: Controle de Acesso, Rate Limiting e Auditoria

Este lab cobre a configuração de controle de acesso via times, restrição de modelos, rate limiting e auditoria no LiteLLM Proxy. Ele assume que a infraestrutura do lab já está em execução conforme o README principal.

- Infraestrutura e configuração: [lab/README.md](../README.md)
- Config do LiteLLM: [config/config.yaml](../../config/config.yaml)

## Objetivo

- Configurar times (`time-estagiario` e `time-senior`) e chaves virtuais no LiteLLM.
- Demonstrar restrição de acesso por modelo (HTTP 403) e limites de requisições por minuto (HTTP 429) no time estagiário.
- Demonstrar acesso total e fallback automático no time sênior.

## Sequência sugerida

### 1) Configuração de Governança

```bash
python step01_setup_governanca.py
```

Esse script cria os times e gera as chaves necessárias para os testes, salvando-as automaticamente em um arquivo `.env` local para as etapas seguintes.

### 2) Testes do Estagiário (Cenários A, B e C)

```bash
python step02_testes_estagiario.py
```

Roda o cenário feliz (acesso a `qwen3:0.6b`), o bloqueio de modelo proibido (acesso a `qwen3.5:2b` retornando 401/403) e o rate limit (requisição repetida em menos de 1 minuto retornando 429).

### 3) Testes do Sênior e Fallback (Cenários D e E)

```bash
python step03_testes_senior.py
```

Demonstra que a chave sênior possui acesso livre a qualquer modelo sem rate limits e demonstra o fallback automático em caso de falha física do backend.

