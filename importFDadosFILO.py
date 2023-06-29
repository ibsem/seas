import pandas as pd
import pymysql

import os
caminhoApp = os.getcwd()

# Configurações do banco de dados MySQL
host = 'localhost'
port = 3306
database = 'seas'
username = 'root'
password = 'root'

# Caminho para o arquivo Excel
caminho_excel = '/seas/FontedeDadosSeas.xlsx'

# Nome da aba a ser importada
nome_aba = 'filo'

# Criar conexão com o banco de dados MySQL
conn = pymysql.connect(host=host, port=port, user=username, password=password, database=database)

# Ler a planilha do Excel
df = pd.read_excel(caminhoApp + caminho_excel, sheet_name=nome_aba)

print(df.head())

# Nome da tabela
nome_tabela = 'filo'

# Criar tabela 'filo' no banco de dados
criar_tabela = '''
CREATE TABLE IF NOT EXISTS filo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filo VARCHAR(255)
)
'''

# Executar comando SQL para criar a tabela
with conn.cursor() as cursor:
    cursor.execute(criar_tabela)

# Inserir dados na tabela 'pais'
with conn.cursor() as cursor:
    for index, row in df.iterrows():
        id_filo = row['id']  # Coluna 'id' no arquivo Excel
        nome_filo = row['filo']  # Coluna 'filo' no arquivo Excel
        
        # Comando SQL para inserir dados na tabela
        inserir_dados = f"INSERT INTO filo (id, filo) VALUES ({id_filo}, '{nome_filo}')"
        
        # Executar comando SQL para inserir os dados
        cursor.execute(inserir_dados)

# Confirmar as alterações no banco de dados
conn.commit()

# Fechar a conexão com o banco de dados
conn.close()