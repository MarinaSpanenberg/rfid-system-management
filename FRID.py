import sqlite3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

leitorRfid = SimpleMFRC522()

# Conectar no bd
data = sqlite3.connect("data.db")
logs = sqlite3.connect("logs.db")
cursor_data = data.cursor()
cursor_logs = logs.cursor()

# tag_id_1 = 2677980090 -- cadastrado com permissão
# tag_id_2 = 219403520343 -- cadastrado sem permissão

def validateIdAuthentication():
    print("Aguardando leitura da tag")
    tag, text = leitorRfid.read()

    try:
        # Buscar no banco se a tag existe
        cursor_data.execute("SELECT id, colaborador, tem_permissao FROM colaboradores WHERE tag_id = ?", (str(tag),))
        result = cursor_data.fetchone()

        colaborador_id = None
        acessou = False

        if result:
            colaborador_id, nome, tem_permissao = result
            acessou = bool(tem_permissao)

            if tem_permissao == True:
                print(f"Acesso permitido para {nome}, com a tag {tag}")
            else:
                print(f"Acesso negado para {nome}, com a tag {tag}")
        else:
            print("Tag não cadastrada no sistema")  

        cursor_logs.execute(
            "INSERT INTO logs_acesso (tag_id, colaborador_id, acessou, data_acesso) VALUES ( ?, ?, ?, CURRENT_TIMESTAMP)",
            (str(tag), colaborador_id, acessou))

        logs.commit()       
            
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")

try:
    validateIdAuthentication()
finally:
    GPIO.cleanup()
