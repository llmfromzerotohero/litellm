# 🎓 Laboratório 01: Instalação e Inicialização do LiteLLM (Proxy & SDK)

## Curso: LLM From Zero To Hero — Unidade 2

Este laboratório prático guiará você nos primeiros passos com o **LiteLLM**, uma ferramenta poderosa que permite padronizar chamadas para centenas de provedores de LLMs (como OpenAI, Anthropic, Gemini e modelos locais do Ollama) utilizando o formato padrão da API da OpenAI.

Você aprenderá a instalar o LiteLLM (tanto como SDK quanto como Proxy/Gateway) e a realizar suas primeiras chamadas integradas com modelos locais rodando no Ollama.

---

### 📋 Pré-requisitos

Antes de começar, certifique-se de ter os seguintes requisitos configurados e ativos em sua máquina:

1. **Python 3.9+** instalado.
2. Um **Ambiente Virtual Python (venv)** criado e ativado.
3. **Ollama** instalado e em execução no seu sistema.
4. Modelos do Ollama baixados localmente (ex: `qwen3:1.7b`).

> [!TIP]
> Você pode verificar a versão e o funcionamento do Ollama rodando o seguinte comando no terminal (com seu ambiente virtual ativo):
>
> ```bash
> (venv) ollama --version
> ```

---

### 🛠️ Passos do Laboratório

#### Passo 1: Entendendo os Modos de Uso do LiteLLM

O LiteLLM pode ser operado de duas maneiras principais:

- **Como SDK Python:** Integrado diretamente no código da sua aplicação para padronizar chamadas a APIs de LLMs.
- **Como Gateway/Proxy:** Um servidor intermediário (proxy reverso) que expõe endpoints compatíveis com a OpenAI, ideal para gerenciar custos, logs, rotas de fallback e autenticação de forma centralizada e sem acoplamento de código.

---

#### Passo 2: Instalação do LiteLLM

No seu terminal, com o ambiente virtual ativo (`venv`), execute os comandos de instalação correspondentes ao seu caso de uso:

##### Opção A: Instalação Padrão (Apenas SDK)

Use esta opção se for utilizar o LiteLLM apenas como biblioteca dentro de scripts Python:

```bash
(venv) pip install litellm
```

##### Opção B: Instalação Completa (SDK + Proxy/Gateway)

Use esta opção para habilitar o servidor proxy do LiteLLM, que gerencia chaves, rotas e múltiplos modelos via API REST:

```bash
(venv) pip install "litellm[proxy]"
```

> [!NOTE]
> O sufixo `[proxy]` instala as dependências de rede e servidor web adicionais (como FastAPI, Uvicorn, etc.) que são cruciais para rodar o gateway local.

---

#### Passo 3: Iniciando o LiteLLM Proxy com Ollama

Com o serviço do Ollama em execução localmente em sua máquina, vamos iniciar o proxy do LiteLLM apontando para o modelo local `qwen3:1.7b` (ou outro de sua escolha):

```bash
(venv) litellm --model ollama/qwen3:1.7b \
               --api_base http://localhost:11434 \
               --port 4000
```

> [!IMPORTANT]
> Certifique-se de que o Ollama está ativo na porta padrão `11434` e que o modelo especificado já foi previamente baixado através de `ollama run qwen3:1.7b`.

---

#### Passo 4: Verificando o Status do Gateway

Abra uma **nova janela do terminal** (ou use seu navegador) para testar se o LiteLLM Proxy está operacional.

##### Verificação via API (cURL)

Solicite a lista de modelos disponíveis para garantir que o proxy está respondendo:

```bash
~$ curl http://localhost:4000/v1/models
```

##### Verificação via Navegador

Você também pode abrir o console administrativo e visualizador de rotas acessando o endereço abaixo no navegador:
👉 **[http://localhost:4000](http://localhost:4000)**

---

#### Passo 5: Realizando a Primeira Chamada ao LiteLLM Proxy (cURL)

Agora, vamos realizar nossa primeira chamada de geração de texto enviando uma pergunta para o modelo local através do proxy compatível com a API da OpenAI usando o terminal.

Execute o seguinte comando em seu terminal:

```bash
(venv) curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-YOUR_LITELLM_KEY" \
  -d '{
    "model": "ollama/qwen3:1.7b",
    "messages": [
      {"role": "user", "content": "O que é LLM?"}
    ]
  }'
```

> [!NOTE]
> Por padrão, se você não configurou chaves de segurança específicas em um arquivo `config.yaml` do LiteLLM Proxy, você pode usar qualquer valor fictício ou chave temporária no cabeçalho de `Authorization` para testes rápidos.

---

### 🏆 Conclusão & Próximos Passos

Parabéns! Você concluiu com sucesso este laboratório inicial do LiteLLM. Você aprendeu a:

1. Diferenciar a aplicação do LiteLLM como SDK e como Proxy.
2. Instalar a biblioteca e seus complementos de rede de maneira isolada com `pip install`.
3. Iniciar um servidor proxy unificado compatível com a API da OpenAI apontando para o seu LLM local no Ollama.
4. Consumir a API do LiteLLM utilizando requisições HTTP `curl` estruturadas no terminal.

No próximo laboratório, avançaremos para o **Roteamento e Fallback** automático entre múltiplos provedores!
