# 🎓 Laboratório 02: Configuração Multi-Backend com LiteLLM

## Curso: LLM From Zero To Hero — Unidade 2

Neste laboratório, você aprenderá a configurar um ambiente híbrido e multi-backend utilizando o **LiteLLM**. Em cenários corporativos reais, as aplicações transitam entre modelos leves de desenvolvimento local, servidores de alta performance (como vLLM) e provedores comerciais na nuvem (como a OpenAI) para redundância e otimização.

Você aprenderá a centralizar, nomear e expor todos esses backends de forma unificada utilizando o arquivo de configuração `config.yaml`.

---

### 📋 Pré-requisitos & Instalações

#### 1. Ollama (Ambiente Local / Desenvolvimento)

Certifique-se de que o Ollama está operacional em seu sistema.

- **Instalação (se necessário):**
  ```bash
  ~$ curl -fsSL https://ollama.com | sh
  ```
- **Verificação de versão:**
  ```bash
  ~$ ollama --version
  ```
- **Download do modelo:**
  Baixe o modelo leve localmente para garantir sua disponibilidade:
  ```bash
  ~$ ollama pull qwen3:1.7b
  ```

---

#### 2. vLLM (Ambiente Otimizado / Produção)

O **vLLM** é uma biblioteca de alta performance projetada para servir modelos localmente de forma extremamente rápida.

- **Inicialização do servidor compatível OpenAI com vLLM:**
  Para subir o servidor do vLLM apontando para o modelo Qwen na porta `8000`, utilize:
  ```bash
  ~$ python -m vllm.entrypoints.openai.api_server \
       --model meta-llama/Llama-3-8B \
       --port 8000
  ```

---

### 🛠️ Passos do Laboratório

#### Passo 1: O Arquivo de Configuração Central (`config.yaml`)

A melhor prática absoluta para gerenciar múltiplos provedores e modelos é centralizá-los em um arquivo `config.yaml` unificado. Criamos o arquivo [config.yaml](config.yaml) na pasta deste laboratório com a seguinte definição:

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
> Usando `os.environ/OPENAI_API_KEY`, o LiteLLM lê automaticamente a credencial diretamente das variáveis de ambiente do seu sistema, evitando o vazamento de chaves secretas no código.

---

#### Passo 2: Iniciando o LiteLLM Proxy com o arquivo de configuração

Em vez de passar parâmetros gigantescos na linha de comando, inicie o proxy apontando diretamente para o arquivo de configuração:

```bash
(venv) litellm --config config.yaml --port 4000
```

---

#### Passo 3: Testando a Integração com o Ollama (Desenvolvimento)

Com o LiteLLM Proxy rodando na porta 4000, envie uma requisição para o modelo de desenvolvimento (`qwen3:1.7b`):

```bash
~$ curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-local" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:1.7b",
    "messages": [
      {"role": "user", "content": "Explique o que é IA Generativa"}
    ]
  }'
```

> [!IMPORTANT]
> **Camada de Abstração:** Observe que a aplicação que consome o modelo só conhece a porta `4000` (LiteLLM) e o nome lógico `"qwen3:1.7b"`. O acesso físico ao Ollama (`http://ollama:11434`) fica totalmente transparente e blindado da aplicação cliente.

---

#### Passo 4: Testando a Integração com o vLLM (Produção)

Teste a chamada simulada de produção que aponta para o servidor vLLM otimizado rodando localmente na porta `8000` (`qwen3.5:2b`):

```bash
~$ curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-local" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5:2b",
    "messages": [
      {"role": "user", "content": "Explique o que é RAG (Retrieval-Augmented Generation)"}
    ]
  }'
```

---

### 🏆 Conclusão & Próximos Passos

Você estruturou e implementou com sucesso um ambiente de orquestração multi-backend!

Agora você compreende como:

1. Declarar múltiplos modelos e diferentes provedores (Ollama, vLLM e OpenAI) sob aliases lógicos.
2. Inicializar o LiteLLM Proxy a partir de um arquivo estruturado `config.yaml`.
3. Oferecer aos seus clientes uma única API padronizada contendo rotas de desenvolvimento, produção e segurança.

No próximo laboratório, avançaremos para o **Roteamento Inteligente e Políticas de Fallback** automático caso um desses servidores fique indisponível!
