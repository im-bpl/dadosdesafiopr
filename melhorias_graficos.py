import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def criar_gauge_melhorado(valor, titulo):
    """
    Cria um gráfico de gauge aprimorado para exibir percentuais
    
    Args:
        valor: Valor percentual (0-1)
        titulo: Título do gauge
        
    Returns:
        figura Plotly
    """
    # Determinar a cor principal e ícone baseados no valor
    if valor < 0.3:
        cor_principal = "#d32f2f"  # Vermelho
        icone = "⚠️"  # Ícone de alerta
        status_texto = "Atenção"
    elif valor < 0.7:
        cor_principal = "#fbc02d"  # Amarelo
        icone = "📈"  # Ícone de progresso
        status_texto = "Em progresso"
    else:
        cor_principal = "#388e3c"  # Verde
        icone = "🏆"  # Ícone de excelência
        status_texto = "Excelente"
    
    # Criar o gauge com design aprimorado
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"{icone} {titulo}", 
            'font': {'size': 18, 'color': '#333', 'family': 'Roboto, sans-serif'}
        },
        delta={'reference': 50, 'increasing': {'color': "#388e3c"}, 'decreasing': {'color': "#d32f2f"}},
        number={'font': {'size': 26, 'color': cor_principal, 'family': 'Roboto, sans-serif'}, 'suffix': "%"},
        gauge={
            'axis': {
                'range': [0, 100], 
                'tickwidth': 1, 
                'tickcolor': "#003366",
                'tickfont': {'size': 12, 'family': 'Roboto, sans-serif'}
            },
            'bar': {'color': cor_principal, 'thickness': 0.7},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#003366",
            'steps': [
                {'range': [0, 30], 'color': '#ffebee'},  # Fundo vermelho claro
                {'range': [30, 70], 'color': '#fffde7'},  # Fundo amarelo claro
                {'range': [70, 100], 'color': '#e8f5e9'}  # Fundo verde claro
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': valor * 100
            }
        }
    ))
    
    # Adicionar anotação de status
    fig.add_annotation(
        x=0.5,
        y=0.25,
        text=status_texto,
        showarrow=False,
        font=dict(
            family="Roboto, sans-serif",
            size=14,
            color=cor_principal
        )
    )
    
    # Melhorar o layout
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Roboto, sans-serif", size=12)
    )
    
    return fig

def criar_grafico_nres_melhorado(df):
    """
    Cria um gráfico de barras aprimorado para exibir o desempenho por NRE
    
    Args:
        df: DataFrame com os dados dos NREs
        
    Returns:
        figura Plotly
    """
    # Ordenar por percentual de acertos
    df_sorted = df.sort_values(by='Percentual de acertos', ascending=False)
    
    # Criar cores baseadas no valor
    colors = []
    hover_texts = []
    
    for valor in df_sorted['Percentual de acertos']:
        if valor < 0.3:
            colors.append('#d32f2f')  # Vermelho
            status = "Atenção"
        elif valor < 0.7:
            colors.append('#fbc02d')  # Amarelo
            status = "Em progresso"
        else:
            colors.append('#388e3c')  # Verde
            status = "Excelente"
        
        hover_texts.append(f"Status: {status}<br>Percentual: {valor:.1%}")
    
    # Criar gráfico com barras personalizadas
    fig = px.bar(
        df_sorted,
        x='NRE',
        y='Percentual de acertos',
        labels={'Percentual de acertos': 'Percentual de Acertos', 'NRE': 'NRE'},
        height=450,
        text=df_sorted['Percentual de acertos'].apply(lambda x: f"{x:.1%}")
    )
    
    # Atualizar cores das barras e adicionar hover personalizado
    fig.update_traces(
        marker_color=colors,
        hovertemplate='<b>%{x}</b><br>%{customdata}<extra></extra>',
        customdata=hover_texts,
        textposition='outside',
        textfont=dict(
            family="Roboto, sans-serif",
            size=12,
        )
    )
    
    # Adicionar linha de meta (70%)
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=0.7,
        x1=len(df_sorted)-0.5,
        y1=0.7,
        line=dict(
            color="#003366",
            width=2,
            dash="dash",
        )
    )
    
    # Adicionar anotação para a linha de meta
    fig.add_annotation(
        x=len(df_sorted)-1,
        y=0.72,
        text="Meta: 70%",
        showarrow=False,
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#003366"
        )
    )
    
    # Melhorar o layout
    fig.update_layout(
        xaxis={
            'categoryorder': 'total descending', 
            'tickangle': 45,
            'title': {'font': {'size': 14, 'family': 'Roboto, sans-serif'}},
            'tickfont': {'size': 12, 'family': 'Roboto, sans-serif'}
        },
        yaxis={
            'title': {'font': {'size': 14, 'family': 'Roboto, sans-serif'}},
            'tickfont': {'size': 12, 'family': 'Roboto, sans-serif'},
            'tickformat': '.0%',
            'range': [0, 1]
        },
        margin=dict(l=40, r=20, t=40, b=120),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Roboto, sans-serif", size=12),
        title={
            'text': 'Desempenho por NRE',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'family': 'Roboto, sans-serif', 'color': '#003366'}
        }
    )
    
    return fig

def criar_grafico_alunos_nre_melhorado(df):
    """
    Cria um gráfico de pizza aprimorado para exibir a distribuição de alunos por NRE
    
    Args:
        df: DataFrame com os dados dos NREs
        
    Returns:
        figura Plotly
    """
    # Ordenar por número de alunos
    df_sorted = df.sort_values(by='Alunos', ascending=False)
    
    # Pegar os 10 maiores NREs e agrupar o resto como "Outros"
    top_10 = df_sorted.head(10)
    outros = pd.DataFrame({
        'NRE': ['Outros'],
        'Alunos': [df_sorted.iloc[10:]['Alunos'].sum()]
    })
    df_plot = pd.concat([top_10, outros])
    
    # Criar gráfico de pizza aprimorado
    fig = px.pie(
        df_plot,
        values='Alunos',
        names='NRE',
        title='',
        height=450,
        color_discrete_sequence=px.colors.sequential.Blues_r,  # Usar tons de azul
        hole=0.4  # Criar um gráfico de donut
    )
    
    # Adicionar texto central
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"Total:<br>{df['Alunos'].sum():,}".replace(",", "."),
        font=dict(size=16, family="Roboto, sans-serif", color="#003366"),
        showarrow=False
    )
    
    # Melhorar o layout e formatação
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(size=12, family="Roboto, sans-serif"),
        hovertemplate='<b>%{label}</b><br>Alunos: %{value:,}<br>Percentual: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=12, family="Roboto, sans-serif")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': 'Distribuição de Alunos por NRE',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'family': 'Roboto, sans-serif', 'color': '#003366'}
        }
    )
    
    return fig

# Função para criar tabela de escolas com indicadores visuais melhorados
def criar_tabela_escolas_melhorada(df, nre=None):
    """
    Cria uma tabela HTML aprimorada para exibir as escolas
    
    Args:
        df: DataFrame com os dados das escolas
        nre: Filtro opcional por NRE
        
    Returns:
        componente HTML da tabela
    """
    from dash import html
    import dash_bootstrap_components as dbc
    
    if nre:
        df_filtered = df[df['NRE'] == nre]
    else:
        # Limitar a 20 escolas para não sobrecarregar a página
        df_filtered = df.head(20)
    
    # Ordenar por percentual de acertos
    df_filtered = df_filtered.sort_values(by='Percentual de acertos', ascending=False)
    
    # Formatar os valores para exibição
    df_display = df_filtered.copy()
    df_display['Índice de Respostas'] = df_display['Índice de Respostas'].apply(lambda x: f"{x:.1%}")
    df_display['Percentual de acertos'] = df_display['Percentual de acertos'].apply(lambda x: f"{x:.1%}")
    df_display['Atribuição Esperada'] = df_display['Atribuição Esperada'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    
    # Selecionar apenas as colunas relevantes
    colunas = ['Escola', 'Alunos', 'Professores', 'Atribuição Esperada', 'Questões Respondidas', 'Índice de Respostas', 'Percentual de acertos']
    df_display = df_display[colunas]
    
    # Criar a tabela HTML com indicadores visuais aprimorados
    header = html.Thead(html.Tr([html.Th(col, style={'background-color': '#003366', 'color': 'white'}) for col in colunas]))
    
    rows = []
    for i, row in df_display.iterrows():
        # Converter percentuais de string para float para comparação
        indice_resp = float(row['Índice de Respostas'].strip('%')) / 100
        perc_acertos = float(row['Percentual de acertos'].strip('%')) / 100
        
        # Determinar ícones, classes e cores baseados nos valores
        if indice_resp < 0.3:
            icone_resp = html.I(className="fas fa-exclamation-triangle status-icon", style={'color': '#d32f2f'})
            classe_resp = "status-red"
            cor_resp = "#ffebee"  # Fundo vermelho claro
        elif indice_resp < 0.7:
            icone_resp = html.I(className="fas fa-arrow-up status-icon", style={'color': '#fbc02d'})
            classe_resp = "status-yellow"
            cor_resp = "#fffde7"  # Fundo amarelo claro
        else:
            icone_resp = html.I(className="fas fa-trophy status-icon", style={'color': '#388e3c'})
            classe_resp = "status-green"
            cor_resp = "#e8f5e9"  # Fundo verde claro
            
        if perc_acertos < 0.3:
            icone_acertos = html.I(className="fas fa-exclamation-triangle status-icon", style={'color': '#d32f2f'})
            classe_acertos = "status-red"
            cor_acertos = "#ffebee"  # Fundo vermelho claro
        elif perc_acertos < 0.7:
            icone_acertos = html.I(className="fas fa-arrow-up status-icon", style={'color': '#fbc02d'})
            classe_acertos = "status-yellow"
            cor_acertos = "#fffde7"  # Fundo amarelo claro
        else:
            icone_acertos = html.I(className="fas fa-trophy status-icon", style={'color': '#388e3c'})
            classe_acertos = "status-green"
            cor_acertos = "#e8f5e9"  # Fundo verde claro
        
        # Criar linha com indicadores visuais aprimorados
        tr = html.Tr([
            html.Td(html.A(row['Escola'], href=f"#", id={'type': 'link-escola', 'index': i}, 
                          style={'font-weight': 'bold', 'color': '#003366'})),
            html.Td(row['Alunos']),
            html.Td(row['Professores']),
            html.Td(html.Div([
                row['Atribuição Esperada'],
                html.Div(className="expected-attribution", children=[
                    html.I(className="fas fa-calculator", style={'margin-right': '5px'}),
                    "Atribuição Esperada"
                ])
            ])),
            html.Td(row['Questões Respondidas']),
            html.Td(html.Div([
                row['Índice de Respostas'],
                html.Div(className=f"status-indicator {classe_resp}", children=[
                    icone_resp,
                    "Índice de Respostas"
                ])
            ], style={'background-color': cor_resp, 'padding': '5px', 'border-radius': '4px'})),
            html.Td(html.Div([
                row['Percentual de acertos'],
                html.Div(className=f"status-indicator {classe_acertos}", children=[
                    icone_acertos,
                    "Percentual de Acertos"
                ])
            ], style={'background-color': cor_acertos, 'padding': '5px', 'border-radius': '4px'})),
        ], style={'background-color': '#f9f9f9' if i % 2 == 0 else 'white'})
        rows.append(tr)
    
    body = html.Tbody(rows)
    
    table = dbc.Table(
        [header, body], 
        striped=True, 
        bordered=True, 
        hover=True, 
        responsive=True,
        className="table-hover table-bordered",
        style={'box-shadow': '0 4px 8px rgba(0,0,0,0.1)', 'border-radius': '8px'}
    )
    
    return table
