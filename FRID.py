import sqlite3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from datetime import datetime

leitorRfid = SimpleMFRC522()

# Conectar no bd
conn = sqlite3.connect("data.db")
cursor = conn.cursor()


def validateIdAuthentication():
    print("Aguardando leitura da tag")
    tag, text = leitorRfid.read()
    tag_id = str(tag)

    try:
        cursor.execute("SELECT id, colaborador, tem_permissao FROM colaboradores WHERE tag_id = ?", (tag_id,))
        result = cursor.fetchone()

        colaborador_id = None
        acessou = False

        if result:
            colaborador_id, nome, tem_permissao = result
            acessou = bool(tem_permissao)
            status_msg = f"Acesso {'permitido' if tem_permissao else 'negado'} para {nome}, com a tag {tag_id}"
        else:
            status_msg = f"Tag {tag_id} não cadastrada no sistema"

        print(status_msg)

        cursor.execute(
            """INSERT INTO logs_acesso (tag_id, colaborador_id, acessou, data_acesso) 
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (tag_id, colaborador_id, acessou)
        )
        conn.commit()

        if not acessou:
            return

        cursor.execute("""
            SELECT data_entrada FROM controle_sala
            WHERE tag_id = ? AND data_saida IS NULL
        """, (tag_id,))
        entrada_existente = cursor.fetchone()

        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if entrada_existente:
            data_entrada = entrada_existente[0]
            print(f"Saída registrada para {nome}. Entrada: {data_entrada}, Saída: {agora}")

            cursor.execute("""
                UPDATE controle_sala
                SET data_saida = ?
                WHERE tag_id = ? AND data_saida IS NULL
            """, (agora, tag_id))

        else:
            print(f"Entrada registrada para {nome} às {agora}")

            cursor.execute("""
                INSERT INTO controle_sala (tag_id, colaborador_id, data_entrada)
                VALUES (?, ?, ?)
            """, (tag_id, colaborador_id, agora))

        conn.commit()
            
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")

try:
    validateIdAuthentication()
finally:
    GPIO.cleanup()