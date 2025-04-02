import sqlite3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

leitorRfid = SimpleMFRC522()

# Conectar no bd
data = sqlite3.connect("data.db")
logs = sqlite3.connect("logs.db")
cursor_data = data.cursor()
cursor_logs = logs.cursor()

# cadastro = [
#     {"nome": "joao", "id": "2677980090", "auth": True},
#     {"nome": "marina", "id": "219403520343", "auth": False}
# ]

def validateIdAuthentication():
    print("Aguardando leitura da tag")
    tag, text = leitorRfid.read()

    try:
        # Buscar no banco se a tag existe
        cursor_data.execute("SELECT id, colaborador, tem_permissao FROM colaboradores WHERE tag_id = ?", (str(tag),))
        result = cursor_data.fetchone()

        if result:
            id, nome, tem_permissao = result
            cursor_logs.execute("INSERT INTO logs_acesso (id, colaborador_id, acessou, data_acesso) VALUES ( ?, ?, ? )", (id, str(tag),))
            result_logs = cursor_logs


            if tem_permissao == True:
                print(f"Acesso permitido para {nome}, com a tag {tag}")
            else:
                print(f"Acesso negado para {nome}, com a tag {tag}")
        else:
            print("Tag não cadastrada no sistema")  
            
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")

try:
    validateIdAuthentication()
finally:
    GPIO.cleanup()