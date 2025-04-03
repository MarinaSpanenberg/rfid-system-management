import sqlite3
import pandas as pd

# Ler os logs do banco de dados
conn = sqlite3.connect('../data.db')
df = pd.read_sql_query("SELECT * FROM controle_sala", conn)
conn.close()

print(df.head())

# Converter datas
df['data_entrada'] = pd.to_datetime(df['data_entrada'])
df['data_saida'] = pd.to_datetime(df['data_saida'])
df['date'] = df['data_entrada'].dt.date

# Exemplo: contar registros por dia
entradas_por_dia = df.groupby('date')['id'].count().reset_index()
entradas_por_dia.columns = ['date', 'count']

print("Total de entradas por dia:")
print(entradas_por_dia)

# Calcular o tempo total dentro da sala para um colaborador específico
def calcular_tempo_total(colaborador_id):
    # Filtrar os registros para o colaborador
    colaborador_data = df[df['colaborador_id'] == colaborador_id]
    colaborador_data['tempo_sala'] = (colaborador_data['data_saida'] - colaborador_data['data_entrada']).dt.total_seconds() / 3600
    return colaborador_data['tempo_sala'].sum()

# Exemplo de uso
colaborador_id = 1
tempo_total = calcular_tempo_total(colaborador_id)

print(f"O colaborador com ID {colaborador_id} permaneceu na sala por {tempo_total:.2f} horas.")

