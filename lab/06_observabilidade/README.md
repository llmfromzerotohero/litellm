# Observabilidade e Auditoria em Sistemas de LLM

Este lab cobre a coleta de logs de requisições, cálculo de métricas de desempenho (latência e vazão de tokens) e custos, além de auditoria de uso e rastreabilidade utilizando a API do LiteLLM Proxy. Ele assume que você já configurou as chaves virtuais no laboratório anterior (05_governanca).

- Config do LiteLLM: [config/config.yaml](../../config/config.yaml)
- Laboratório de Governança (pre-requisito): [lab/05_governanca](../05_governanca/README.md)

## Objetivo

- Gerar tráfego operacional real simulando diversos cenários de uso (sucesso, bloqueios e fallbacks).
- Consumir e analisar os logs estruturados no LiteLLM Proxy.
- Extrair métricas operacionais chave: latência média por modelo, throughput (tokens/segundo) e taxas de erro/bloqueio.
- Avaliar a governança financeira analisando o custo total estimado e por time.

## Sequência sugerida

### 1) Gerar tráfego operacional

```bash
python step01_gerar_trafego.py
```

Esse script executa uma bateria de chamadas ao proxy simulando requisições corretas (sênior e estagiário), requisições que causam erros (401/403/429) e requisições que forçam o chaveamento de fallback (gemma3:1b). Isso preenche o banco de dados de auditoria com dados realistas.

### 2) Extrair auditoria e métricas de desempenho

```bash
python step02_auditoria_metricas.py
```

Este script lê e processa a API administrativa `/spend/logs` do LiteLLM, gerando um dashboard completo com latências de rede, throughput, taxas de erro e consumo financeiro agrupado por time e modelo.
