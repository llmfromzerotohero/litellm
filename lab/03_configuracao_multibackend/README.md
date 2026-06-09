# 🎓 Laboratório 02: Configuração Multi-Backend com LiteLLM

## Curso: LLM From Zero To Hero — Unidade 3

Neste laboratório, você aprenderá a configurar um ambiente híbrido e multi-backend utilizando o **LiteLLM**. Em cenários corporativos reais, as aplicações transitam entre modelos leves de desenvolvimento local, servidores de alta performance (como vLLM) e provedores comerciais na nuvem (como a OpenAI) para redundância e otimização.

Você aprenderá a centralizar, nomear e expor todos esses backends de forma unificada utilizando o arquivo de configuração `config.yaml`.

---

### 📋 Pré-requisitos & Inicialização com Docker Compose

Neste laboratório, não é necessário instalar ou rodar o Ollama e o vLLM manualmente na máquina host. Todo o ambiente (incluindo o banco de dados PostgreSQL, Ollama, vLLM e o próprio LiteLLM Proxy) já está devidamente configurado e orquestrado via **Docker Compose** na pasta raiz `/config`.

#### 1. Inicializar os Serviços via Docker Compose

Abra o terminal, navegue até a pasta de configurações do projeto (`/config`) e inicie os containers em segundo plano:

```bash
docker compose up -d
```

> [!NOTE]
> Este comando iniciará os seguintes serviços integrados na mesma rede virtual:
> - **PostgreSQL (`db`)** na porta `5432`
> - **Ollama (`ollama`)** na porta `11434`
> - **vLLM (`vllm`)** na porta `8000` (carregando o modelo `Qwen3.5-2B`)
> - **LiteLLM Proxy (`litellm`)** na porta `4000`

#### 2. Baixar o Modelo no Ollama (dentro do Container)

Como o Ollama está rodando de forma isolada dentro de um container Docker, precisamos baixar o modelo `qwen3:1.7b` diretamente nele:

```bash
docker exec -it ollama-service ollama pull qwen3:1.7b
```

---

### 🛠️ Passos do Laboratório

#### Passo 1: O Arquivo de Configuração Central (`config.yaml`)

A melhor prática absoluta para gerenciar múltiplos provedores e modelos é centralizá-los em um arquivo `config.yaml` unificado. O arquivo local [config.yaml](config.yaml) contém a seguinte definição teórica de backends:

```yaml
model_list:
  # Ollama (local)
  - model_name: qwen3:1.7b
    litellm_params:
      model: ollama/qwen3:1.7b
      api_base: http://ollama:11434

  # vLLM (local)
  - model_name: qwen3.5:2b
    litellm_params:
      model: openai/qwen3.5:9b
      api_base: http://vllm:8000/v1

  # Fallback (API Externa)
  - model_name: gpt_fallback
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
```

> [!NOTE]
> Os endereços de `api_base` (`http://ollama:11434` e `http://vllm:8000/v1`) utilizam os nomes dos serviços definidos no Docker Compose. A comunicação entre os containers ocorre de maneira interna e automática.

---

#### Passo 2: O LiteLLM Proxy no Docker Compose

Como o LiteLLM Proxy já foi iniciado automaticamente pelo Docker Compose, ele estará escutando na porta `4000` do seu host (mapeada para a porta interna do container) e carregando as configurações definidas no arquivo `/config/config.yaml` global.

> [!TIP]
> Caso queira executar o LiteLLM de forma manual e local fora do Docker (apenas para testar o arquivo `config.yaml` específico deste laboratório no terminal), certifique-se de ajustar os endereços de `api_base` para `localhost` (ex: `http://localhost:11434` e `http://localhost:8000/v1`), pois as URLs de rede interna do Docker (`http://ollama` e `http://vllm`) não resolvem no host. Para rodar localmente no terminal:
> ```bash
> (venv) litellm --config config.yaml --port 4000
> ```

---

#### Passo 3: Testando a Integração com o Ollama (Desenvolvimento)

Com o ambiente ativo, envie uma requisição para o modelo de desenvolvimento (`qwen3:1.7b`) usando o LiteLLM Proxy (porta 4000). 

Escolha o comando correspondente ao seu terminal/sistema operacional:

##### Linux/macOS:
```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-master-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:1.7b",
    "messages": [
      {"role": "user", "content": "Explique o que é IA Generativa"}
    ]
  }'
```

##### Windows (PowerShell):
```powershell
$body = '{"model": "qwen3:1.7b", "messages": [{"role": "user", "content": "Explique o que é IA Generativa"}]}'
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

$response = Invoke-RestMethod -Uri "http://localhost:4000/v1/chat/completions" `
  -Method Post `
  -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer sk-master-1234"
  } `
  -Body $bodyBytes

$response.choices[0].message.content
```

##### Windows (CMD):
```cmd
curl http://localhost:4000/v1/chat/completions ^
  -H "Authorization: Bearer sk-master-1234" ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"qwen3:1.7b\", \"messages\": [{\"role\": \"user\", \"content\": \"Explique o que é IA Generativa\"}]}"
```

> [!IMPORTANT]
> **Camada de Abstração:** Observe que a aplicação consumidora só conhece a porta `4000` (LiteLLM) e o nome do modelo `"qwen3:1.7b"`. O acesso físico ao Ollama fica totalmente transparente e blindado da aplicação cliente.

---

#### Passo 4: Testando a Integração com o vLLM (Produção)

Teste a chamada simulada de produção que aponta para o servidor vLLM rodando localmente no container Docker (`qwen3.5:2b`):

##### Linux/macOS:
```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-master-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5:2b",
    "messages": [
      {"role": "user", "content": "Explique o que é RAG (Retrieval-Augmented Generation)"}
    ]
  }'
```

##### Windows (PowerShell):
```powershell
$body = '{"model": "qwen3.5:2b", "messages": [{"role": "user", "content": "Explique o que é RAG (Retrieval-Augmented Generation)"}]}'
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

$response = Invoke-RestMethod -Uri "http://localhost:4000/v1/chat/completions" `
  -Method Post `
  -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer sk-master-1234"
  } `
  -Body $bodyBytes

# Nota: Modelos de raciocínio (como o Qwen 3.5 com reasoning parser no vLLM)
# retornam a resposta no campo 'reasoning_content' em vez de 'content'.
if ($response.choices[0].message.content) {
    $response.choices[0].message.content
} else {
    $response.choices[0].message.reasoning_content
}
```

##### Windows (CMD):
```cmd
curl http://localhost:4000/v1/chat/completions ^
  -H "Authorization: Bearer sk-master-1234" ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"qwen3.5:2b\", \"messages\": [{\"role\": \"user\", \"content\": \"Explique o que é RAG (Retrieval-Augmented Generation)\"}]}"
```

---

### 🏆 Conclusão & Próximos Passos

Você estruturou e implementou com sucesso um ambiente de orquestração multi-backend utilizando Docker!

Agora você compreende como:

1. Declarar múltiplos modelos e diferentes provedores (Ollama, vLLM e OpenAI) sob aliases lógicos.
2. Inicializar toda a infraestrutura do LiteLLM Proxy em conjunto com os backends via Docker Compose.
3. Consumir de forma centralizada rotas de desenvolvimento e produção com chaves seguras (Master Key).

No próximo laboratório, avançaremos para o **Roteamento Inteligente e Políticas de Fallback** automático caso um desses servidores fique indisponível!
