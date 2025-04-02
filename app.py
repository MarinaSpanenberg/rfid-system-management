from flask import Flask, request, jsonify
import sqlite3

from pubsub import AsyncConn

app = Flask(__name__)
pubnub = AsyncConn("Flask Application", "meu_canal")

# Função para conectar ao banco de dados SQLite
def connect_db():
    return sqlite3.connect('data.db')

# Função para criar a tabela se não existir
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            data_acesso DATETIME DEFAULT CURRENT_TIMESTAMP,
            tem_permissao BOOLEAN NOT NULL
        )"""
    )
    conn.commit()
    conn.close()

create_table()

def logs_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS logs_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id TEXT NOT NULL,
            colaborador_id INTEGER,
            acessou BOOLEAN NOT NULL,
            data_acesso DATETIME DEFAULT CURRENT_TIMESTAMP
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
        )"""
    )
    conn.commit()
    conn.close()

logs_data()

# def acessou_data():
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute(
#         """CREATE TABLE IF NOT EXISTS logs_acesso (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             FOREIGN KEY (id) REFERENCES colaboradores(id)    
#         )"""
#     )
#     conn.commit()
#     conn.close()

# acessou_data()

@app.route('/', methods=['POST', 'GET'])
def use_api():
    try:
        # Inicializa a tabela ao iniciar o aplicativo
        # ====== POST ==========================================================================
        if request.method == "POST":
            colaborador = request.json.get('colaborador')  # Recebe o valor do corpo da requisição JSON
            tem_permissao = request.json.get('tem_permissao') 
            tag_id = request.json.get('tag_id')

            if colaborador is None or tem_permissao is None or tag_id is None:
                return jsonify({"Erro": "Nenhum colaborador cadastrado"}), 400
        
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO colaboradores (colaborador, tag_id, tem_permissao) VALUES (?, ?, ?)', (colaborador, tag_id, tem_permissao))
                conn.commit()

            pubnub.publish({"nome": colaborador,
                            "conseguiu acessar?": tem_permissao})
            
            return jsonify({"Mensagem": "Valores adicionados com suceso"}), 201
        # ====== GET==========================================================================
        elif request.method == "GET":
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM colaboradores')
                rows = cursor.fetchall()

            values = [{"id": row[0], "colaborador": row[1], "tag_id": row[2], "tem_permissao": bool(row[3])} for row in rows]

            return jsonify(values), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dados/<int:dado_id>', methods=['PUT'])
def update_data(dado_id):
    colaborador = request.json.get('colaborador')  # Recebe o valor do corpo da requisição JSON
    tem_permissao = request.json.get('tem_permissao')
    tag_id = request.json.get('tag_id')

    if colaborador is None or tem_permissao is None or tag_id is None:
        return jsonify({"Erro": "Nome do colaborador é obrigatório!"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE colaboradores SET colaborador = ?, tem_permissao = ?, tag_id = ? WHERE id = ?', (colaborador, tem_permissao, tag_id, dado_id))
        conn.commit()

        return jsonify({'Mensagem': 'Dado atualizado com sucesso!'})
    except sqlite3.Error as e: 
        return jsonify({'Erro': str(e)}), 500
    finally:
        conn.close()
    
@app.route('/dados/<int:dado_id>', methods=['DELETE'])
def delete_data(dado_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM colaboradores WHERE id = ?', (dado_id))
        conn.commit()
        conn.close()

        return jsonify({'Mensagem': 'Dado deletado com sucesso!'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs_acesso')
            rows = cursor.fetchall()

            values = [{"id": row[0],  
                       "tag_id": row[1],  
                       "colaborador_id": row[2],
                       "acessou": bool(row[3]),
                       "data_acesso": row[4]
                       } for row in rows]
        return jsonify(values), 200

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
