# Roteamento e fallback

Este lab cobre roteamento baseado em regras no cliente e fallback automatico no LiteLLM. Ele assume que a infraestrutura do lab ja esta em execucao conforme o README principal.

- Infraestrutura e configuracao: [lab/README.md](../README.md)
- Config do LiteLLM: [config/config.yaml](../../config/config.yaml)

## Objetivo

- Demonstrar fallback automático quando o modelo primário falha.
- Demonstrar roteamento por regras no cliente (palavras-chave e tamanho do prompt).
- Demonstrar roteamento inteligente nativo por latência mínima (`latency-based-routing`) no proxy LiteLLM.

## Sequência sugerida

### 1) Fallback simples

```bash
python step01_fallback_simples.py
```

Esse script chama `gemma3:1b` (com `api_base` inválido no config) e confirma o fallback para `qwen3:1.7b`.

### 2) Fallback via vLLM (primário) -> Ollama (fallback)

```bash
python step02_vllm_fallback.py --question "O que é vLLM?"
```

Se o vLLM estiver indisponível, o LiteLLM aciona o fallback para um modelo Ollama configurado.

### 3) Roteamento por regras (cliente)

```bash
python step03_router_regras.py
```

Regras aplicadas no lado do cliente com exemplos de prompts:
- **Palavras-chave de tecnologia** -> Roteado para `qwen3.5:2b`
  * *Exemplo de prompt:* `"Como criar uma API REST em Python?"` (contém as palavras-chave `"api"` e `"python"`).
- **Prompt curto** (sem palavras-chave e estimado em <= 100 tokens / ~400 caracteres) -> Roteado para `qwen3:0.6b`
  * *Exemplo de prompt:* `"Qual é a capital do Brasil?"`
- **Prompt longo** (sem palavras-chave e estimado em > 100 tokens / ~400 caracteres) -> Roteado para `qwen3:1.7b`
  * *Exemplo de prompt:* `"Escreva um ensaio detalhado sobre os impactos da Revolução Industrial na sociedade moderna, abordando as transformações urbanas, a criação de novas classes sociais, a mudança nos meios de transporte e as consequências ecológicas a longo prazo que enfrentamos hoje."`

### 4) Roteamento por Latência Mínima (LiteLLM Native)

```bash
python step04_roteamento_latencia.py
```

Esse fluxo demonstra o roteamento inteligente no LiteLLM Proxy. Ao agrupar múltiplos modelos sob o alias `modelo-latencia` e configurar a estratégia `latency-based-routing` no `config.yaml`, o proxy monitora o tempo de resposta e direciona as requisições para o deployment mais rápido.

O script executa 6 requisições consecutivas e exibe os seguintes cabeçalhos retornados pelo proxy para validar o comportamento:
- `x-litellm-model-id`: Mostra qual modelo resolveu a requisição (espera-se que priorize `qwen3-0.6b-fast` por ser menor e mais rápido que `qwen3-1.7b-slow`).
- `x-litellm-model-api-base`: Endpoint correspondente utilizado.
