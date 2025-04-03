from flask import Flask, request, jsonify, render_template
import sqlite3

from pubsub import AsyncConn

app = Flask(__name__)
pubnub = AsyncConn("Flask Application", "meu_canal")

# Função para conectar ao banco de dados SQLite
def connect_db():
    return sqlite3.connect('data.db')

# Função para criar a tabela se não existir
def create_tables():
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
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS logs_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id TEXT NOT NULL,
            colaborador_id INTEGER,
            acessou BOOLEAN NOT NULL,
            data_acesso DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS controle_sala (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id TEXT NOT NULL,
            colaborador_id INTEGER,
            data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_saida DATETIME,
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
        )"""
    )
    conn.commit()
    conn.close()

create_tables()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/cadastro', methods=['POST'])
def register():
    try:
        usuario = request.json.get('usuario')
        senha = request.json.get('senha')

        if not usuario or not senha:
            return jsonify({"Erro": "Usuário e senha são obrigatórios!"}), 400

        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO usuarios (usuario, senha) VALUES (?, ?)', (usuario, senha))
            conn.commit()

        return jsonify({"Mensagem": "Usuário cadastrado com sucesso!"})

    except sqlite3.IntegrityError:
        return jsonify({"Erro": "Usuário já existe!"}), 400
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        usuario = request.json.get('usuario')
        senha = request.json.get('senha')
        if not [usuario, senha]:
            return jsonify({"Erro": "Usuário e senha são obrigatórios!"}), 400
     
        with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha))
                user = cursor.fetchone()

                if not user:
                    return jsonify({"Erro": "Usuário ou senha inválidos!"}), 401

                return jsonify({"Mensagem": "Login bem-sucedido!"})
    
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500 
    
@app.route('/dados', methods=['GET'])
def use_api():
    try:
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM colaboradores')
                rows = cursor.fetchall()

            values = [{"id": row[0], "colaborador": row[1], "tag_id": row[2], "tem_permissao": bool(row[4])} for row in rows]

            return jsonify(values), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/incluir', methods=['POST'])
def include_data():
    try:
        if request.method == "POST":
            colaborador = request.json.get('colaborador')  
            tem_permissao = request.json.get('tem_permissao') 
            tag_id = request.json.get('tag_id')

            if None in [colaborador, tem_permissao, tag_id]:
                return jsonify({"Erro": "Nenhum colaborador cadastrado"}), 400
        
            # tem_permissao = bool(int(tem_permissao))

            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO colaboradores (colaborador, tag_id, tem_permissao) VALUES (?, ?, ?)', (colaborador, tag_id, tem_permissao))
                conn.commit()

            pubnub.publish({"nome": colaborador,
                            "conseguiu acessar?": tem_permissao})
            
            return jsonify({"Mensagem": "Valores adicionados com suceso"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500    

@app.route('/dados/<int:dado_id>', methods=['PUT'])
def update_data(dado_id):
    colaborador = request.json.get('colaborador')  # Recebe o valor do corpo da requisição JSON
    tem_permissao = request.json.get('tem_permissao')
    tag_id = request.json.get('tag_id')

    if None in [colaborador, tem_permissao, tag_id]:
        return jsonify({"Erro": "Nome do colaborador é obrigatório!"}), 400

    try:
        # tem_permissao = bool(int(tem_permissao))

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
        cursor.execute('DELETE FROM colaboradores WHERE id = ?', (dado_id,))
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

@app.route('/sala', methods=['GET'])
def get_controle_sala():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM controle_sala')
            rows = cursor.fetchall()
            values = [{"id": row[0],  
                       "tag_id": row[1],  
                       "colaborador_id": row[2],
                       "data_entrada": row[3],
                       "data_saida": row[4],
                       } for row in rows]
        return jsonify(values), 200

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)