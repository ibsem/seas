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
#caminho_excel = 'https://docs.google.com/spreadsheets/d/1q22d8qauLHFaFJlwcP4bBzPaRURwa40gJsiWacerkm0/edit?usp=drive_link'
# Nome da aba a ser importada
nome_aba = 'organismoVivo'

# Criar conexão com o banco de dados MySQL
conn = pymysql.connect(host=host, port=port, user=username, password=password, database=database)

# Ler a planilha do Excel
df = pd.read_excel(caminhoApp + caminho_excel, sheet_name=nome_aba)

print(df.head())

nome_tabela = 'organismoVivo'

# Criar tabela 'organismoVivo' no banco de dados
criar_tabela = '''
CREATE TABLE IF NOT EXISTS organismoVivo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pais VARCHAR(255),
    speciesName VARCHAR(255),
    phylum VARCHAR(255),
    class VARCHAR(255),
    ordem VARCHAR(255),
    family VARCHAR(255),
    occurrence VARCHAR(255)
)
'''

# Executar comando SQL para criar a tabela
with conn.cursor() as cursor:
    cursor.execute(criar_tabela)

# Inserir dados na tabela 'organismoVivo'
with conn.cursor() as cursor:
    for index, row in df.iterrows():
        #id_organismo = row['id']  # Coluna 'id' no arquivo Excel
        pais = row['pais']  # Coluna 'pais' no arquivo Excel
        species_name = row['speciesName']  # Coluna 'speciesName' no arquivo Excel
        phylum = row['phylum']  # Coluna 'phylum' no arquivo Excel
        class_name = row['class']  # Coluna 'class' no arquivo Excel
        order_name = row['order']  # Coluna 'order' no arquivo Excel
        family = row['family']  # Coluna 'family' no arquivo Excel
        occurrence = row['occurrence']  # Coluna 'occurrence' no arquivo Excel
        
        # Comando SQL para inserir dados na tabela
        inserir_dados = f"INSERT INTO organismoVivo ( pais, speciesName, phylum, class, ordem, family, occurrence) VALUES ('{pais}', '{species_name}', '{phylum}', '{class_name}', '{order_name}', '{family}', '{occurrence}')"
        
        # Executar comando SQL para inserir os dados
        cursor.execute(inserir_dados)

# Confirmar as alterações no banco de dados
conn.commit()

# Fechar a conexão com o banco de dados
conn.close()