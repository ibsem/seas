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
    #print(pais_destino_id)
    #print(pais_origem_id)
    
    # CARGA DOS DADOS
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    # Consulta na tabela 'organismoVivo' com os parâmetros fornecidos
    cursor.execute('SELECT id, pais, speciesName, phylum FROM organismoVivo WHERE pais IN (%s)', (pais_origem_id))
    resultadosOrigem = cursor.fetchall()
    dfOrigem = pd.DataFrame(resultadosOrigem, columns=['id', 'pais', 'nomeEspecie', 'filo'])
    #print(dfOrigem.head())
    cursor.execute('SELECT id, pais, speciesName, phylum FROM organismoVivo WHERE pais IN (%s)', (pais_destino_id))
    resultadosDestino = cursor.fetchall()
    dfDestino = pd.DataFrame(resultadosDestino, columns=['id', 'pais', 'nomeEspecie', 'filo'])
    cursor.execute('SELECT id, filo FROM filo')
    resultadosFilo = cursor.fetchall()
    dfFilo = pd.DataFrame(resultadosFilo, columns=['id', 'filo'])
    dfFilo['id'] = dfFilo['id'].astype(str)
    #print(dfFilo.head())
    #TRATAMENTO DOS DADOS
    dfResultado = dfOrigem.loc[~dfOrigem['nomeEspecie'].isin(dfDestino['nomeEspecie'])]
    #print(dfResultado.head())

    # Agrupar por filo e contar as espécies
    df_agrupado = dfResultado.groupby('filo').count().reset_index()
    df_agrupado.rename(columns={'filo': 'idFilo'}, inplace=True)
    
    #print(dfFilo.columns)
    df_agrupadoComFilo = pd.merge(df_agrupado, dfFilo, how='inner', left_on='idFilo', right_on='id')

    df_agrupadoComFilo = df_agrupadoComFilo.drop(['idFilo', 'id_x', 'nomeEspecie', 'id_y'], axis=1)
    df_agrupadoComFilo.rename(columns={'pais': 'QuantidadeEspecies'}, inplace=True)

    df_agrupadoComFilo = df_agrupadoComFilo.reindex(columns=['filo', 'QuantidadeEspecies'])    
    df_agrupadoComFilo = df_agrupadoComFilo.sort_values(by='QuantidadeEspecies', ascending=False)
    print(df_agrupadoComFilo.columns)

    # Exibir o DataFrame agrupado    
    resultado = df_agrupadoComFilo.to_records(index=False)
    print(resultado)
    # Fechar a conexão com o banco de dados
    cursor.close()
    connection.close()

    # Renderizar o template HTML com os resultados da consulta
    return render_template('resultados.html', resultados=resultado)

@app.route('/enviar_resultados', methods=['POST'])
def enviar_resultados():
    resultados = []
    filos = request.form.getlist('filo')
    quantidades = request.form.getlist('quantidade')
    for filo, quantidade in zip(filos, quantidades):
        resultados.append((filo, quantidade))
    print(resultados)
    # criar a aba na planilha com as relacoes idsloucao e filo, a rotina para carregar a tabela no banco de dados 
    # e a rotina para carregar um dataframe com essas relacoes, que se chama dfRelacaoFiloSolucao
    dados = {
    'idSolucao': [1, 2, 3],
    'filo': ['Echinodermata', 'Arthropoda', 'Mollusca']}

# Criar o DataFrame dfRelacaoFiloSolucao
    dfRelacaoFiloSolucao = pd.DataFrame(dados)

    dfResultado = pd.DataFrame(resultados, columns=["filo", "quantidade"])

    dfResultadoFinal = pd.merge(dfResultado, dfRelacaoFiloSolucao, how="inner", left_on='filo', right_on='filo')

    print(dfResultadoFinal)

        # Resto do código
    return 'Valores recebidos com sucesso!'

if __name__ == '__main__':
    app.run(debug=True)
