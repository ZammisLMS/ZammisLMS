# Personal Finance Telegram Bot

Este é um bot para Telegram em Python projetado para ajudar no controle financeiro pessoal. Ele permite que os usuários registrem despesas, visualizem resumos mensais, gerem gráficos de pizza de gastos por categoria e exportem dados.

## Funcionalidades

*   **Registro de Despesas:** Envie uma mensagem como "Café 5,50" e o bot extrairá a descrição e o valor.
*   **Categorização Automática:** As despesas são classificadas em categorias (Alimentação, Transporte, etc.) com base em palavras-chave.
*   **Armazenamento de Dados:** As despesas são salvas em um banco de dados SQLite local (ID do usuário, valor, descrição, categoria, data/hora).
*   **/start:** Inicia a interação com o bot e exibe a mensagem de boas-vindas.
*   **/resumo:** Exibe o total gasto por categoria no mês atual.
*   **/pizza:** Gera e envia um gráfico de pizza dos gastos por categoria no mês atual.
*   **/exportar:** Envia um arquivo CSV com os dados de despesas do mês atual.

## Tecnologias Utilizadas

*   Python 3.11+
*   `python-telegram-bot` (v20.x)
*   SQLite3
*   `matplotlib`

## Pré-requisitos

*   Python 3.11 ou superior
*   pip (gerenciador de pacotes Python)
*   Git (para clonar o repositório)

## Configuração do Bot Telegram

1.  **Crie um Bot no Telegram:**
    *   Converse com o [BotFather](https://t.me/BotFather) no Telegram.
    *   Use o comando `/newbot` para criar um novo bot.
    *   Siga as instruções e anote o **TOKEN** fornecido. Este token é essencial para o funcionamento do bot.

## Instalação (VPS Linux - Ubuntu)

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/username/repository.git # Substitua pela URL do seu repositório
    cd personal_finance_bot
    ```

2.  **(Opcional, mas recomendado) Crie e Ative um Ambiente Virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    (Para desativar o ambiente virtual, use `deactivate`)

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    (Se estiver usando o script `setup.sh`, ele pode auxiliar na instalação do Python/pip no sistema).

4.  **Configure o Token do Bot:**
    Crie uma variável de ambiente chamada `TELEGRAM_TOKEN` com o token que você obteve do BotFather.
    Você pode fazer isso de algumas maneiras:
    *   **Temporariamente no terminal (para a sessão atual):**
        ```bash
        export TELEGRAM_TOKEN="SEU_TOKEN_AQUI"
        ```
    *   **Adicionando ao `~/.bashrc` ou `~/.profile` (para persistência entre sessões):**
        Abra o arquivo (ex: `nano ~/.bashrc`) e adicione a linha:
        ```bash
        export TELEGRAM_TOKEN="SEU_TOKEN_AQUI"
        ```
        Depois, recarregue o arquivo: `source ~/.bashrc`
    *   **Usando um arquivo `.env` (Recomendado para desenvolvimento):**
        Crie um arquivo chamado `.env` na raiz do projeto (`personal_finance_bot/.env`) com o seguinte conteúdo:
        ```
        TELEGRAM_TOKEN="SEU_TOKEN_AQUI"
        ```
        O `main.py` tem um exemplo comentado de como carregar este arquivo usando `python-dotenv` (você precisaria adicionar `python-dotenv` ao `requirements.txt` e descomentar as linhas relevantes em `main.py`).

5.  **Banco de Dados:**
    O banco de dados SQLite (`finance_data.db`) será criado automaticamente no diretório raiz do projeto (`personal_finance_bot/finance_data.db`) na primeira vez que o bot for executado, graças à lógica no `database/db_handler.py`.

## Execução

Navegue até o diretório raiz do projeto (`personal_finance_bot`).

### 1. Usando Python Puro

*   **Execução (Recomendado para desenvolvimento/teste):**
    Certifique-se de que seu ambiente virtual está ativado e `TELEGRAM_TOKEN` está configurado (seja globalmente ou via `.env` se você adaptou o `main.py`).
    ```bash
    python -m bot.main
    ```
    Este comando executa o bot como um módulo a partir do diretório raiz do projeto, o que é ideal para o funcionamento correto dos imports.

*   **Execução em Background (para produção simples):**
    Para manter o bot rodando após fechar o terminal, você pode usar `screen` ou `nohup`.

    *   **Com `screen`:**
        ```bash
        screen -S financebot # Inicia uma nova sessão screen chamada financebot
        # Dentro da sessão screen (ative o venv se necessário):
        # source venv/bin/activate
        # export TELEGRAM_TOKEN="SEU_TOKEN_AQUI" # Se não estiver configurado de outra forma
        python -m bot.main
        # Pressione Ctrl+A e depois D para desanexar da sessão (o bot continua rodando)
        # Para reanexar: screen -r financebot
        ```

    *   **Com `nohup`:**
        ```bash
        # Ative o venv se necessário: source venv/bin/activate
        # export TELEGRAM_TOKEN="SEU_TOKEN_AQUI" # Se não estiver configurado de outra forma
        nohup python -m bot.main > bot.log 2>&1 &
        # O bot rodará em background, logs serão salvos em bot.log
        # Para parar o bot: ps aux | grep "python -m bot.main" (encontre o PID) e depois kill <PID>
        ```

### 2. Usando Docker

Certifique-se de ter o Docker instalado na sua VPS.

1.  **Construa a Imagem Docker:**
    No diretório raiz do projeto (`personal_finance_bot`), onde o `Dockerfile` está localizado:
    ```bash
    docker build -t finance-telegram-bot .
    ```

2.  **Execute o Container Docker:**
    Substitua `SEU_TOKEN_AQUI` pelo seu token do Telegram.
    ```bash
    docker run -d --restart always --env TELEGRAM_TOKEN="SEU_TOKEN_AQUI" --name finance-bot-container \
           -v $(pwd)/finance_data.db:/app/finance_data.db \
           finance-telegram-bot
    ```
    *   `-d`: Executa o container em modo detached (background).
    *   `--restart always`: Reinicia o container automaticamente se ele parar.
    *   `--env TELEGRAM_TOKEN="SEU_TOKEN_AQUI"`: Passa o token como variável de ambiente.
    *   `--name finance-bot-container`: Dá um nome ao container.
    *   `-v $(pwd)/finance_data.db:/app/finance_data.db`: **Importante!** Monta o arquivo do banco de dados do host para dentro do container. Isso garante que seus dados persistam mesmo se o container for recriado. Certifique-se de que `finance_data.db` exista no host ou seja criado corretamente na primeira execução. O Dockerfile deve colocar o app em `/app/`.

    Para ver os logs do container:
    ```bash
    docker logs finance-bot-container
    ```
    Para parar o container:
    ```bash
    docker stop finance-bot-container
    ```
    Para remover o container (os dados persistirão no host devido ao volume):
    ```bash
    docker rm finance-bot-container
    ```

## Estrutura do Projeto

```
personal_finance_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py             # Lógica principal do bot, handlers
│   └── categorizer.py      # Função de categorização
├── database/
│   ├── __init__.py
│   └── db_handler.py       # Interação com o banco de dados
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Funções utilitárias (parser, gráficos, CSV)
├── tests/
│   ├── __init__.py
│   └── test_categorizer.py # Exemplo de arquivo de teste
├── .env.example            # Exemplo de arquivo para variáveis de ambiente
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
├── setup.sh                # Script de setup (exemplo) para Ubuntu
└── finance_data.db         # Arquivo do banco de dados SQLite (criado automaticamente na raiz)
```

## (Opcional) Script de Setup (`setup.sh`)

O script `setup.sh` (exemplo, pode não estar no repositório ou precisar de ajustes) tenta automatizar a instalação do Python 3.11, pip e outras dependências do sistema em um ambiente Ubuntu.

Para usá-lo (se existir e for confiável):
```bash
chmod +x setup.sh
./setup.sh
```
Depois de executar, você provavelmente ainda precisará clonar o projeto (se o script não o fizer), configurar o ambiente virtual (recomendado) e instalar as dependências Python via `pip install -r requirements.txt`. Verifique o conteúdo do `setup.sh` para detalhes.

---

*Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.*
```
