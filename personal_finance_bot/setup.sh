#!/bin/bash

# Script para configurar o ambiente para o Personal Finance Telegram Bot em Ubuntu

echo "Iniciando configuração do ambiente para o Personal Finance Bot..."

# Atualizar lista de pacotes
echo "Atualizando lista de pacotes..."
sudo apt-get update -y

# Instalar dependências básicas (git, curl, software-properties-common)
# build-essential: Compiladores C/C++ e ferramentas relacionadas.
# libssl-dev, zlib1g-dev, libbz2-dev, libreadline-dev, libsqlite3-dev: Headers para compilar Python e alguns módulos.
# wget, llvm, libncurses5-dev, libncursesw5-dev, xz-utils, tk-dev, libffi-dev, liblzma-dev: Outras dependências comuns para Python.
# python3-openssl: Pode ser necessário para algumas interações SSL do Python.
echo "Instalando dependências básicas e de compilação Python..."
sudo apt-get install -y git curl software-properties-common build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl

# Instalar Python 3.11
# Adicionar deadsnakes PPA para versões mais recentes do Python
echo "Configurando PPA para Python 3.11 (deadsnakes)..."
# Prevenir prompts interativos durante a adição do PPA
sudo DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update -y

echo "Instalando Python 3.11, python3.11-venv e python3.11-pip..."
# Tenta instalar python3.11-pip diretamente se disponível. python3-pip é um fallback.
sudo apt-get install -y python3.11 python3.11-venv python3.11-pip python3-pip

# Configurar python3.11 como 'python3' e pip3.11 como 'pip3' (opcional, mas pode ser conveniente)
# Comentado por padrão para evitar conflitos com Python do sistema se não desejado.
# echo "Configurando alternativas para python3 e pip3 (opcional)..."
# sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
# if command -v pip3.11 &> /dev/null; then
#   sudo update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
# fi

# Verificar a instalação do Python
echo "Verificando a instalação do Python..."
if command -v python3.11 &> /dev/null
then
    python3.11 --version
else
    echo "Python 3.11 não parece ter sido instalado corretamente."
    echo "Verifique se o PPA deadsnakes foi adicionado corretamente e se 'sudo apt-get update' foi executado."
fi

# Verificar pip (tentar pip para python3.11 se existir, senão pip3 geral)
echo "Verificando a instalação do pip..."
PIP_COMMAND=""
if command -v python3.11 &> /dev/null && python3.11 -m pip --version &> /dev/null; then
    PIP_COMMAND="python3.11 -m pip"
    echo "Usando 'python3.11 -m pip':"
    $PIP_COMMAND --version
elif command -v pip3 &> /dev/null; then
    PIP_COMMAND="pip3" # Might be system's pip3 or linked to an older python
    echo "Usando 'pip3' (pode ser o pip do sistema ou de outra versão Python):"
    $PIP_COMMAND --version
    echo "Certifique-se de que 'pip3' esteja associado ao Python 3.11 ou use 'python3.11 -m pip'."
else
    echo "pip não parece estar instalado ou acessível."
fi


# Instalar dependências do matplotlib que podem ser necessárias
echo "Instalando dependências de sistema para o Matplotlib..."
sudo apt-get install -y libfreetype6-dev libpng-dev pkg-config

echo ""
echo "---------------------------------------------------------------------"
echo "Configuração básica do ambiente concluída."
echo "Próximos passos sugeridos:"
echo "1. Clone o repositório do projeto (se ainda não o fez):"
echo "   git clone <URL_DO_SEU_REPOSITORIO_GIT_AQUI>"
echo "   cd personal_finance_bot"
echo "2. (Recomendado) Crie e ative um ambiente virtual:"
echo "   python3.11 -m venv venv"
echo "   source venv/bin/activate"
echo "3. Instale as dependências Python do projeto (dentro do venv):"
echo "   python3.11 -m pip install -r requirements.txt"
echo "   (Ou use 'pip install -r requirements.txt' se 'pip' estiver corretamente linkado ao Python 3.11 do venv)"
echo "4. Configure a variável de ambiente TELEGRAM_TOKEN:"
echo "   export TELEGRAM_TOKEN='SEU_TOKEN_AQUI'"
echo "   (Considere adicionar ao seu ~/.bashrc, ~/.profile, ou usar um arquivo .env com python-dotenv)"
echo "5. Execute o bot (dentro do venv):"
echo "   python3.11 -m bot.main"
echo "---------------------------------------------------------------------"
echo ""
