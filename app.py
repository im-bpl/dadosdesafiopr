import os
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import base64
from datetime import datetime
from melhorias_graficos import (
    criar_gauge_melhorado, 
    criar_grafico_nres_melhorado, 
    criar_grafico_alunos_nre_melhorado,
    criar_tabela_escolas_melhorada
)
from exportar_dados import criar_componentes_exportacao, registrar_callbacks_exportacao
from atualizar_dados_integrado import verificar_formato_planilha, atualizar_dados_dashboard, obter_historico_atualizacoes

# Inicializar a aplicação Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.15.4/css/all.css'],
    suppress_callback_exceptions=True,
    assets_folder='assets'
)

# Configurar o servidor para implantação
server = app.server

# Definir o título da aplicação
app.title = "Dashboard Desafio PR - NREs"

# Criar diretórios necessários se não existirem
os.makedirs('dados_processados', exist_ok=True)
os.makedirs('backup', exist_ok=True)

# Carregar dados iniciais ou criar dados de exemplo para implantação
try:
    with open('dados_processados/estrutura_dados.json', 'r', encoding='utf-8') as f:
        estrutura_dados = json.load(f)

    df_nre_metricas = pd.read_csv('dados_processados/nre_metricas.csv')
    df_escolas_metricas = pd.read_csv('dados_processados/escolas_metricas.csv')

    with open('dados_processados/lista_nres.json', 'r', encoding='utf-8') as f:
        lista_nres = json.load(f)

    with open('dados_processados/escolas_por_nre.json', 'r', encoding='utf-8') as f:
        escolas_por_nre = json.load(f)
except:
    print("Criando dados de exemplo para implantação...")
    estrutura_dados = {
        'total_nres': 5,
        'total_escolas': 100,
        'total_alunos': 10000,
        'total_professores': 500,
        'indice_respostas_geral': 0.75,
        'percentual_acertos_geral': 0.65,
        'semanas_atuais': 8,
        'questoes_por_semana': 30,
        'ultima_atualizacao': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    with open('dados_processados/estrutura_dados.json', 'w', encoding='utf-8') as f:
        json.dump(estrutura_dados, f, ensure_ascii=False, indent=4)

    df_nre_metricas = pd.DataFrame({
        'NRE': ['NRE 1', 'NRE 2', 'NRE 3', 'NRE 4', 'NRE 5'],
        'Alunos': [2000, 3000, 1500, 2500, 1000],
        'Professores': [100, 150, 75, 125, 50],
        'Atribuição Esperada': [480000, 720000, 360000, 600000, 240000],
        'Questões Respondidas': [360000, 540000, 270000, 450000, 180000],
        'Questões Corretas': [234000, 351000, 175500, 292500, 117000],
        'Número de Escolas': [20, 30, 15, 25, 10],
        'Índice de Respostas': [0.75]*5,
        'Percentual de acertos': [0.65]*5
    })

    df_nre_metricas.to_csv('dados_processados/nre_metricas.csv', index=False)

    df_escolas = []
    for nre in df_nre_metricas['NRE']:
        num_escolas = df_nre_metricas[df_nre_metricas['NRE'] == nre]['Número de Escolas'].values[0]
        for i in range(int(num_escolas)):
            df_escolas.append({
                'NRE': nre,
                'Escola': f'Escola {i+1} - {nre}',
                'Alunos': 100,
                'Professores': 5,
                'Atribuição Esperada': 24000,
                'Questões Respondidas': 18000,
                'Questões Corretas': 11700,
                'Índice de Respostas': 0.75,
                'Percentual de acertos': 0.65
            })

    df_escolas_metricas = pd.DataFrame(df_escolas)
    df_escolas_metricas.to_csv('dados_processados/escolas_metricas.csv', index=False)

    lista_nres = df_nre_metricas['NRE'].tolist()
    with open('dados_processados/lista_nres.json', 'w', encoding='utf-8') as f:
        json.dump(lista_nres, f, ensure_ascii=False)

    escolas_por_nre = {}
    for nre in lista_nres:
        escolas = df_escolas_metricas[df_escolas_metricas['NRE'] == nre]['Escola'].tolist()
        escolas_por_nre[nre] = escolas

    with open('dados_processados/escolas_por_nre.json', 'w', encoding='utf-8') as f:
        json.dump(escolas_por_nre, f, ensure_ascii=False, indent=4)

    with open('dados_processados/historico_atualizacoes.json', 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# Layout da aplicação
app.layout = html.Div([
    # Cabeçalho
    html.Div([
        html.Div([
            html.Img(src='/assets/logo.png', className='logo'),
            html.H1("Dashboard Desafio PR", className='dashboard-title'),
        ], className='header-left'),
        html.Div([
            html.Div([
                html.Span("Semana Atual: ", className='week-label'),
                html.Span(f"{estrutura_dados['semanas_atuais']}", className='current-week-highlight'),
            ], className='week-indicator'),
            html.Div([
                html.Span("Última Atualização: ", className='update-label'),
                html.Span(estrutura_dados['ultima_atualizacao'], className='update-date'),
            ], className='update-indicator'),
        ], className='header-right'),
    ], className='header'),

    # Filtros
    html.Div([
        html.Div([
            html.Label("Selecione o NRE:"),
            dcc.Dropdown(
                id='dropdown-nre',
                options=[{'label': nre, 'value': nre} for nre in lista_nres],
                placeholder="Todos os NREs",
                className='filter-dropdown'
            ),
        ], className='filter-item'),
        html.Div([
            html.Label("Selecione a Escola:"),
            dcc.Dropdown(
                id='dropdown-escola',
                placeholder="Selecione um NRE primeiro",
                disabled=True,
                className='filter-dropdown'
            ),
        ], className='filter-item'),
    ], className='filters-container'),

    # Gráficos e tabelas (aqui você adicionará os componentes visuais principais do seu dashboard)
    html.Div(id='conteudo-graficos', className='content-section'),

    # Exportação e Atualização
    html.Div([
        html.H4("Exportar / Atualizar Dados", className="section-title"),
        criar_componentes_exportacao()
    ], className='update-export-container'),
])

# Registrar os callbacks (essa linha é fundamental!)
registrar_callbacks_exportacao(app, df_nre_metricas, df_escolas_metricas)

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
