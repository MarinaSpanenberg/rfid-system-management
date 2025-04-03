# **Sistema de Monitoramento de Acesso - Simples**

Este repositório trata-se de uma API desenvolvida para consumir dados de entrada e saída de pessoas e registra-as em um banco de dados. 
A aplicação foi feita no microcomputador **RaspBerry Pi 4** com **Python** junto com o microframework **Flask** e um sensor **RFID** para a leitura de dados.

### 1. Criar um ambiente virtual

```bash
python -m venv env
source env/bin/activate  # No Linux/macOS
env\Scripts\activate     # No Windows
```

### 2. Clonar o Repositório

Clone o projeto utilizando o comando:

```bash
git clone https://github.com/MarinaSpanenberg/rfid-system-management.git
cd seuRepositorio
```

### 3. Instalar as Dependências

Instale as dependências utilizando o comando:

```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação

Para executar a aplicação, utilize estes comandos:
```bash
python app.py
```

E depois:
```bash
python FRID.py
```

## E está pronto! 