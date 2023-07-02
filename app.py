from flask import Flask, render_template, request
import pymysql
import os
import pandas as pd

caminhoApp = os.getcwd() + "/seas/"

# DADOS DO BANCO DE PRODUCAO



print(caminhoApp)
app = Flask(__name__)

db_config = {
    'host': 'db4free.net',
    'user': 'vitorufsc',
    'password': 'root2808',
    'database': 'seasufsc',
}

# Configurações do banco de dados para uso local
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
    ########## RECEBE OS DADOS DA REQUISICAO##############
    pais_origem_id = request.form['pais_origem']
    pais_destino_id = request.form['pais_destino']
    ################ CARGA DOS DADOS TABELAS PARA OS DF###############
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    #Carrega dfOrigem
    cursor.execute('SELECT id, pais, speciesName, phylum FROM organismoVivo WHERE pais IN (%s)', (pais_origem_id))
    resultadosOrigem = cursor.fetchall()
    dfOrigem = pd.DataFrame(resultadosOrigem, columns=['id', 'pais', 'nomeEspecie', 'filo'])
    #carrega dfDestino
    cursor.execute('SELECT id, pais, speciesName, phylum FROM organismoVivo WHERE pais IN (%s)', (pais_destino_id))
    resultadosDestino = cursor.fetchall()
    dfDestino = pd.DataFrame(resultadosDestino, columns=['id', 'pais', 'nomeEspecie', 'filo'])
    #Carrega dffilos
    cursor.execute('SELECT id, filo FROM filo')
    resultadosFilo = cursor.fetchall()
    dfFilo = pd.DataFrame(resultadosFilo, columns=['id', 'filo'])
    dfFilo['id'] = dfFilo['id'].astype(str)
    cursor.close()
    connection.close()
    ###############TRATAMENTO DOS DADOS#####################
    dfResultado = dfOrigem.loc[~dfOrigem['nomeEspecie'].isin(dfDestino['nomeEspecie'])]
    df_agrupado = dfResultado.groupby('filo').count().reset_index()
    df_agrupado.rename(columns={'filo': 'idFilo'}, inplace=True)
    df_agrupadoComFilo = pd.merge(df_agrupado, dfFilo, how='inner', left_on='idFilo', right_on='id')
    df_agrupadoComFilo = df_agrupadoComFilo.drop(['idFilo', 'id_x', 'nomeEspecie', 'id_y'], axis=1)
    df_agrupadoComFilo.rename(columns={'pais': 'QuantidadeEspecies'}, inplace=True)
    df_agrupadoComFilo = df_agrupadoComFilo.reindex(columns=['filo', 'QuantidadeEspecies'])    
    df_agrupadoComFilo = df_agrupadoComFilo.sort_values(by='QuantidadeEspecies', ascending=False)
    ################CARREGAR RESPOSTA ################  
    resultado = df_agrupadoComFilo.to_records(index=False)
    return render_template('resultados.html', resultados=resultado)

@app.route('/enviar_resultados', methods=['POST'])
def enviar_resultados():
    ########## RECEBE OS DADOS DA REQUISICAO##############
    resultados = []
    filos = request.form.getlist('filo')
    quantidades = request.form.getlist('quantidade')
    for filo, quantidade in zip(filos, quantidades):
        resultados.append((filo, quantidade))
    ###############CARGA DADOS DAS TABELAS PARA OS DATAFRAMES##################
    #Carrega dfRelacaoSolucaoFilo
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('SELECT idSolucao, filo, outrosFilos FROM relacaoFiloSolucao')
    resultadosRelacaoSolucoesFilos = cursor.fetchall()
    dfRelSolucaoFilo = pd.DataFrame(resultadosRelacaoSolucoesFilos, columns=['idSolucao','filo','outrosfilos'])
    #Carrega dfSolucaoFilo
    cursor.execute('SELECT id, nomeSolucao, descricao, refBibliografica FROM solucaoFilo')
    resultadosSolucoes = cursor.fetchall()
    dfSolucao = pd.DataFrame(resultadosSolucoes, columns=['id', 'nomeSolucao', 'descricao', 'refBibliografica'])
    print(dfSolucao.head())
    cursor.close()
    connection.close()
    ################TRATAMENTO DADOS###############
    dfResultado = pd.DataFrame(resultados, columns=["filo", "quantidade"])
    dfResultadoFinal = pd.merge(dfResultado, dfRelSolucaoFilo , how="inner", left_on='filo', right_on='filo')
    dfResultadoFinalComSolucao = pd.merge(dfResultadoFinal,dfSolucao,how="inner", left_on='idSolucao', right_on='id')
    dfResultadoFinalComSolucao = dfResultadoFinalComSolucao.drop(['outrosfilos', 'idSolucao', 'id'], axis=1)

    colunas = ['nomeSolucao', 'descricao', 'refBibliografica', 'filo', 'quantidade']
    dfResultadoFinalComSolucao = dfResultadoFinalComSolucao.reindex(columns=colunas)

    dfResultadoFinalComSolucaoAgrupado = dfResultadoFinalComSolucao.groupby(['nomeSolucao', 'descricao', 'refBibliografica']).agg({'filo': ', '.join, 'quantidade': lambda x: ', '.join(map(str, x))}).reset_index()
    print(dfResultadoFinalComSolucaoAgrupado)

    dfResultadoFinalComSolucaoAgrupadoFiltrado = dfResultadoFinalComSolucaoAgrupado.sort_values(by='filo', key=lambda x: x.str.len(), ascending=False)

    print(dfResultadoFinalComSolucaoAgrupadoFiltrado)
    ################CARREGAR RESPOSTA ################
    resposta = dfResultadoFinalComSolucaoAgrupadoFiltrado.to_dict('records')
    return render_template('solucoes.html', resultados=resposta)

if __name__ == '__main__':
    app.run(debug=True)
