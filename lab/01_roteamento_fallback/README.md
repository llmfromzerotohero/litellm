# Roteamento e fallback

Este lab cobre roteamento baseado em regras no cliente e fallback automatico no LiteLLM. Ele assume que a infraestrutura do lab ja esta em execucao conforme o README principal.

- Infraestrutura e configuracao: [lab/README.md](../README.md)
- Config do LiteLLM: [config/config.yaml](../../config/config.yaml)

## Objetivo

- Demonstrar fallback automatico quando o modelo primario falha.
- Demonstrar roteamento por regras no cliente (palavras-chave e tamanho do prompt).

## Sequencia sugerida

### 1) Fallback simples

```bash
python step01_fallback_simples.py
```

Esse script chama `gemma3:1b` (com `api_base` invalido no config) e confirma o fallback para `qwen3:1.7b`.

### 2) Fallback via vLLM (primario) -> Ollama (fallback)

```bash
python step02_vllm_fallback.py --question "O que e vLLM?"
```

Se o vLLM estiver indisponivel, o LiteLLM aciona o fallback para um modelo Ollama configurado.

### 3) Roteamento por regras (cliente)

```bash
python step03_router_regras.py
```

Regras aplicadas:

- palavras-chave de tecnologia -> `qwen3.5:4b`
- prompt curto -> `qwen3:1.7b`
- prompt longo -> `qwen3.5:2b`

### 4) Roteamento + fallback interativo

```bash
python step04_router_interativo.py
```

Esse fluxo usa as mesmas regras da etapa 3 e imprime `FALLBACK_USED` quando o proxy entrega um modelo diferente do solicitado.
