import sqlite3
import pandas as pd

conn = sqlite3.connect('../data.db')
df = pd.read_sql_query("SELECT * FROM controle_sala", conn)
conn.close()

print(df.head())

df['data_entrada'] = pd.to_datetime(df['data_entrada'])
df['data_saida'] = pd.to_datetime(df['data_saida'])
df['date'] = df['data_entrada'].dt.date

entradas_por_dia = df.groupby('date')['id'].count().reset_index()
entradas_por_dia.columns = ['date', 'count']

print("Total de entradas por dia:")
print(entradas_por_dia)

def calcular_tempo_total(colaborador_id):
    colaborador_data = df[df['colaborador_id'] == colaborador_id]
    colaborador_data['tempo_sala'] = (colaborador_data['data_saida'] - colaborador_data['data_entrada']).dt.total_seconds() / 3600
    return colaborador_data['tempo_sala'].sum()


