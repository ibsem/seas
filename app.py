from flask import Flask, render_template, request
import pymysql
import os
import pandas as pd

caminhoApp = os.getcwd() + "/seas/"

print(caminhoApp)
app = Flask(__name__)

# Configurações do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'seas',
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obter os dados do formulário
        pais_origem = request.form['pais_origem']
        pais_destino = request.form['pais_destino']

        # Conectar ao banco de dados
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # Executar uma ação com os dados (por exemplo, inserir em outra tabela)
        # Aqui, estou apenas imprimindo os dados para fins de demonstração
        print('País de origem:', pais_origem)
        print('País de destino:', pais_destino)

        # Fechar a conexão com o banco de dados
        cursor.close()
        connection.close()

    # Carregar os países da tabela 'pais' do banco de dados
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('SELECT id, nomePais FROM pais')
    paises = cursor.fetchall()

    # Renderizar o template HTML com os países
    return render_template('index.html', paises=paises)

@app.route('/pesquisa_rota', methods=['POST'])
def pesquisa_rota():
    pais_origem_id = request.form['pais_origem']
    pais_destino_id = request.form['pais_destino']
    print(pais_destino_id)
    print(pais_origem_id)
    # Conectar ao banco de dados
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    # Consulta na tabela 'organismoVivo' com os parâmetros fornecidos
    cursor.execute('SELECT id, pais, speciesName, phylum FROM organismoVivo WHERE pais IN (%s)', (pais_origem_id))
    resultadosOrigem = cursor.fetchall()
    dfOrigem = pd.DataFrame(resultadosOrigem, columns=['id', 'pais', 'nomeEspecie', 'filo'])
    print(dfOrigem.head())
    cursor.execute('SELECT id, pais, speciesName, phylum FROM organismoVivo WHERE pais IN (%s)', (pais_destino_id))
    resultadosDestino = cursor.fetchall()
    dfDestino = pd.DataFrame(resultadosOrigem, columns=['id', 'pais', 'nomeEspecie', 'filo'])
    print(dfDestino.head())
    # Fechar a conexão com o banco de dados
    cursor.close()
    connection.close()

    # Renderizar o template HTML com os resultados da consulta
    return render_template('resultados.html', resultados=resultadosOrigem)


if __name__ == '__main__':
    app.run(debug=True)
