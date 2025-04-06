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
    # Tentar carregar dados existentes
    with open('dados_processados/estrutura_dados.json', 'r', encoding='utf-8') as f:
        estrutura_dados = json.load(f)
    
    df_nre_metricas = pd.read_csv('dados_processados/nre_metricas.csv')
    df_escolas_metricas = pd.read_csv('dados_processados/escolas_metricas.csv')
    
    with open('dados_processados/lista_nres.json', 'r', encoding='utf-8') as f:
        lista_nres = json.load(f)
    
    with open('dados_processados/escolas_por_nre.json', 'r', encoding='utf-8') as f:
        escolas_por_nre = json.load(f)
except:
    # Criar dados de exemplo para implantação
    print("Criando dados de exemplo para implantação...")
    
    # Estrutura de dados básica
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
    
    # Salvar estrutura de dados
    with open('dados_processados/estrutura_dados.json', 'w', encoding='utf-8') as f:
        json.dump(estrutura_dados, f, ensure_ascii=False, indent=4)
    
    # Criar dados de NREs de exemplo
    df_nre_metricas = pd.DataFrame({
        'NRE': ['NRE 1', 'NRE 2', 'NRE 3', 'NRE 4', 'NRE 5'],
        'Alunos': [2000, 3000, 1500, 2500, 1000],
        'Professores': [100, 150, 75, 125, 50],
        'Atribuição Esperada': [480000, 720000, 360000, 600000, 240000],
        'Questões Respondidas': [360000, 540000, 270000, 450000, 180000],
        'Questões Corretas': [234000, 351000, 175500, 292500, 117000],
        'Número de Escolas': [20, 30, 15, 25, 10],
        'Índice de Respostas': [0.75, 0.75, 0.75, 0.75, 0.75],
        'Percentual de acertos': [0.65, 0.65, 0.65, 0.65, 0.65]
    })
    
    # Salvar dados de NREs
    df_nre_metricas.to_csv('dados_processados/nre_metricas.csv', index=False)
    
    # Criar dados de escolas de exemplo
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
    
    # Salvar dados de escolas
    df_escolas_metricas.to_csv('dados_processados/escolas_metricas.csv', index=False)
    
    # Criar lista de NREs
    lista_nres = df_nre_metricas['NRE'].tolist()
    with open('dados_processados/lista_nres.json', 'w', encoding='utf-8') as f:
        json.dump(lista_nres, f, ensure_ascii=False)
    
    # Criar mapeamento de escolas por NRE
    escolas_por_nre = {}
    for nre in lista_nres:
        escolas = df_escolas_metricas[df_escolas_metricas['NRE'] == nre]['Escola'].tolist()
        escolas_por_nre[nre] = escolas
    
    with open('dados_processados/escolas_por_nre.json', 'w', encoding='utf-8') as f:
        json.dump(escolas_por_nre, f, ensure_ascii=False, indent=4)
    
    # Inicializar o histórico de atualizações
    with open('dados_processados/historico_atualizacoes.json', 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# Resto do código da aplicação...
# [O código original continua aqui]

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
        html.Button("Limpar Filtros", id='btn-limpar', className='btn-limpar'),
    ], className='filters-container'),
    
    # Métricas principais
    html.Div([
        html.Div([
            html.H3("Total de NREs", className='card-title'),
            html.Div(estrutura_dados['total_nres'], className='card-value'),
            html.Div([html.I(className="fas fa-building")], className='card-icon'),
        ], className='metric-card'),
        html.Div([
            html.H3("Total de Escolas", className='card-title'),
            html.Div(estrutura_dados['total_escolas'], className='card-value'),
            html.Div([html.I(className="fas fa-school")], className='card-icon'),
        ], className='metric-card'),
        html.Div([
            html.H3("Total de Alunos", className='card-title'),
            html.Div(f"{estrutura_dados['total_alunos']:,}".replace(',', '.'), className='card-value'),
            html.Div([html.I(className="fas fa-user-graduate")], className='card-icon'),
        ], className='metric-card'),
        html.Div([
            html.H3("Total de Professores", className='card-title'),
            html.Div(f"{estrutura_dados['total_professores']:,}".replace(',', '.'), className='card-value'),
            html.Div([html.I(className="fas fa-chalkboard-teacher")], className='card-icon'),
        ], className='metric-card'),
    ], className='metrics-container'),
    
    # Gráficos de desempenho
    html.Div([
        html.Div([
            html.H3("Índice de Respostas", className='card-title'),
            dcc.Graph(
                id='gauge-respostas',
                figure=criar_gauge_melhorado(estrutura_dados['indice_respostas_geral'], "Índice de Respostas"),
                config={'displayModeBar': False},
                className='gauge-chart'
            ),
        ], className='performance-card'),
        html.Div([
            html.H3("Percentual de Acertos", className='card-title'),
            dcc.Graph(
                id='gauge-acertos',
                figure=criar_gauge_melhorado(estrutura_dados['percentual_acertos_geral'], "Percentual de Acertos"),
                config={'displayModeBar': False},
                className='gauge-chart'
            ),
        ], className='performance-card'),
    ], className='performance-container'),
    
    # Gráficos comparativos
    html.Div([
        html.H2("Comparativo entre NREs", className='section-title'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='grafico-nres',
                    figure=criar_grafico_nres_melhorado(df_nre_metricas),
                    config={'displayModeBar': True},
                    className='graph'
                ),
            ], className='graph-container'),
            html.Div([
                dcc.Graph(
                    id='grafico-alunos-nre',
                    figure=criar_grafico_alunos_nre_melhorado(df_nre_metricas),
                    config={'displayModeBar': True},
                    className='graph'
                ),
            ], className='graph-container'),
        ], className='graphs-row'),
    ], className='graphs-section'),
    
    # Tabela de escolas
    html.Div([
        html.H2("Principais Escolas", className='section-title'),
        html.Div(id='tabela-escolas', className='table-container'),
    ], className='table-section'),
    
    # Componentes de exportação
    criar_componentes_exportacao(),
    
    # Seção de atualização de dados
    html.Div([
        html.H2("Atualização de Dados", className='section-title'),
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Arraste e solte ou ',
                    html.A('selecione um arquivo Excel')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0'
                },
                multiple=False
            ),
            html.Div([
                html.Label("Semana Atual:"),
                dcc.Input(
                    id='input-semana',
                    type='number',
                    value=estrutura_dados['semanas_atuais'],
                    min=1,
                    max=52,
                    step=1,
                    className='update-input'
                ),
            ], className='update-field'),
            html.Div([
                html.Label("Questões por Semana:"),
                dcc.Input(
                    id='input-questoes',
                    type='number',
                    value=estrutura_dados['questoes_por_semana'],
                    min=1,
                    max=100,
                    step=1,
                    className='update-input'
                ),
            ], className='update-field'),
            html.Button('Atualizar Dados', id='btn-atualizar', className='btn-update'),
            html.Button('Recarregar Dashboard', id='btn-reload', className='btn-reload'),
            html.Div(id='output-data-upload', className='update-output'),
        ], className='update-container'),
        
        # Histórico de atualizações
        html.Div([
            html.H3("Histórico de Atualizações", className='section-title'),
            html.Div(id='historico-atualizacoes', className='historico-container'),
        ], className='historico-section'),
    ], className='update-section'),
    
    # Rodapé
    html.Footer([
        html.P("Dashboard Desafio PR © 2025 - Todos os direitos reservados"),
        html.P("Versão 2.0 - Atualizado em Abril/2025"),
    ], className='footer'),
    
    # Armazenamento de dados
    dcc.Store(id='store-nre-selecionado'),
    dcc.Store(id='store-escola-selecionada'),
    dcc.Store(id='store-dados-upload'),
    dcc.Location(id='url', refresh=False),
], className='dashboard-container')

# Callbacks da aplicação
@app.callback(
    [Output('dropdown-escola', 'options'),
     Output('dropdown-escola', 'disabled')],
    [Input('dropdown-nre', 'value')]
)
def atualizar_dropdown_escolas(nre_selecionado):
    if nre_selecionado:
        escolas = escolas_por_nre.get(nre_selecionado, [])
        return [{'label': escola, 'value': escola} for escola in escolas], False
    return [], True

@app.callback(
    [Output('dropdown-nre', 'value'),
     Output('dropdown-escola', 'value'),
     Output('store-nre-selecionado', 'data'),
     Output('store-escola-selecionada', 'data')],
    [Input('btn-limpar', 'n_clicks')],
    [State('dropdown-nre', 'value'),
     State('dropdown-escola', 'value')]
)
def limpar_filtros(n_clicks, nre_atual, escola_atual):
    if n_clicks:
        return None, None, None, None
    return nre_atual, escola_atual, nre_atual, escola_atual

@app.callback(
    [Output('gauge-respostas', 'figure'),
     Output('gauge-acertos', 'figure'),
     Output('grafico-nres', 'figure'),
     Output('grafico-alunos-nre', 'figure'),
     Output('tabela-escolas', 'children')],
    [Input('store-nre-selecionado', 'data'),
     Input('store-escola-selecionada', 'data'),
     Input('btn-reload', 'n_clicks')]
)
def atualizar_dashboard(nre_selecionado, escola_selecionada, n_clicks):
    # Filtrar dados com base nas seleções
    if nre_selecionado:
        df_nre_filtrado = df_nre_metricas[df_nre_metricas['NRE'] == nre_selecionado]
        df_escolas_filtrado = df_escolas_metricas[df_escolas_metricas['NRE'] == nre_selecionado]
        
        if escola_selecionada:
            df_escolas_filtrado = df_escolas_filtrado[df_escolas_filtrado['Escola'] == escola_selecionada]
            
        # Calcular métricas filtradas
        indice_respostas = df_escolas_filtrado['Questões Respondidas'].sum() / df_escolas_filtrado['Atribuição Esperada'].sum()
        percentual_acertos = df_escolas_filtrado['Questões Corretas'].sum() / df_escolas_filtrado['Questões Respondidas'].sum()
    else:
        df_nre_filtrado = df_nre_metricas
        df_escolas_filtrado = df_escolas_metricas
        indice_respostas = estrutura_dados['indice_respostas_geral']
        percentual_acertos = estrutura_dados['percentual_acertos_geral']
    
    # Criar gráficos atualizados
    fig_gauge_respostas = criar_gauge_melhorado(indice_respostas, "Índice de Respostas")
    fig_gauge_acertos = criar_gauge_melhorado(percentual_acertos, "Percentual de Acertos")
    fig_nres = criar_grafico_nres_melhorado(df_nre_filtrado)
    fig_alunos = criar_grafico_alunos_nre_melhorado(df_nre_filtrado)
    
    # Criar tabela de escolas
    tabela_escolas = criar_tabela_escolas_melhorada(df_escolas_filtrado)
    
    return fig_gauge_respostas, fig_gauge_acertos, fig_nres, fig_alunos, tabela_escolas

@app.callback(
    [Output('store-dados-upload', 'data'),
     Output('output-data-upload', 'children')],
    [Input('btn-atualizar', 'n_clicks')],
    [State('store-dados-upload', 'data'),
     State('input-semana', 'value'),
     State('input-questoes', 'value')]
)
def processar_atualizacao(n_clicks, dados_upload, semana_atual, questoes_por_semana):
    if n_clicks is None or dados_upload is None:
        return dados_upload, ""
    
    try:
        # Processar a atualização com os dados do upload
        arquivo_temp = dados_upload['arquivo_temp']
        resultado = atualizar_dados_dashboard(arquivo_temp, semana_atual, questoes_por_semana)
        
        return None, html.Div([
            html.H4("Resultado da Atualização", className="update-result-title"),
            html.Pre(resultado, className="update-result-text")
        ])
    except Exception as e:
        return dados_upload, html.Div([
            html.H4("Erro na Atualização", className="update-error-title"),
            html.Pre(str(e), className="update-error-text")
        ])

@app.callback(
    Output('historico-atualizacoes', 'children'),
    [Input('btn-reload', 'n_clicks')]
)
def atualizar_historico(n_clicks):
    try:
        historico = obter_historico_atualizacoes(5)
        if not historico:
            return html.P("Nenhuma atualização registrada.", className="historico-vazio")
        
        itens_historico = []
        for item in historico:
            itens_historico.append(html.Div([
                html.Div([
                    html.Span(item['data'], className="historico-data"),
                    html.Span(f"Arquivo: {item['arquivo']}", className="historico-arquivo"),
                ], className="historico-cabecalho"),
                html.Div([
                    html.Span(f"NREs: {item['metricas']['total_nres']}", className="historico-metricas"),
                    html.Span(f"Escolas: {item['metricas']['total_escolas']}", className="historico-metricas"),
                    html.Span(f"Alunos: {item['metricas']['total_alunos']:,}".replace(',', '.'), className="historico-metricas"),
                    html.Span(f"Índice: {item['metricas']['indice_respostas_geral']:.1%}", className="historico-metricas"),
                ], className="historico-detalhes"),
            ], className="historico-item"))
        
        return html.Div(itens_historico, className="historico-lista")
    except Exception as e:
        return html.P(f"Erro ao carregar histórico: {str(e)}", className="historico-erro")

@app.callback(
    Output('store-dados-upload', 'data', allow_duplicate=True),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')],
    prevent_initial_call=True
)
def armazenar_upload(contents, filename, date):
    if contents is None:
        return None
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Salvar o arquivo temporariamente
    arquivo_temp = f"upload_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    with open(arquivo_temp, 'wb') as f:
        f.write(decoded)
    
    # Verificar o formato do arquivo
    formato_valido, mensagem = verificar_formato_planilha(arquivo_temp)
    
    if formato_valido:
        return {
            'arquivo_temp': arquivo_temp,
            'filename': filename,
            'date': date
        }
    else:
        # Se o formato for inválido, excluir o arquivo temporário
        if os.path.exists(arquivo_temp):
            os.remove(arquivo_temp)
        
        return None

# Registrar callbacks de exportação
registrar_callbacks_exportacao(app)

# Executar o servidor
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)
