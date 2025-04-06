import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import base64
import io
import json
import os
from datetime import datetime

def criar_funcao_exportacao():
    """
    Cria funções para exportação de dados do dashboard
    
    Returns:
        dict: Dicionário com as funções de exportação
    """
    def exportar_para_excel(df, nome_arquivo="dados_exportados.xlsx"):
        """
        Exporta um DataFrame para um arquivo Excel
        
        Args:
            df: DataFrame a ser exportado
            nome_arquivo: Nome do arquivo Excel (padrão: dados_exportados.xlsx)
            
        Returns:
            bytes: Conteúdo do arquivo Excel em bytes
        """
        # Criar um buffer em memória
        output = io.BytesIO()
        
        # Criar um writer do Excel
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        # Escrever o DataFrame no Excel
        df.to_excel(writer, index=False, sheet_name='Dados')
        
        # Salvar o arquivo
        writer.close()
        
        # Retornar o conteúdo do buffer
        output.seek(0)
        return output.getvalue()
    
    def exportar_para_csv(df, nome_arquivo="dados_exportados.csv"):
        """
        Exporta um DataFrame para um arquivo CSV
        
        Args:
            df: DataFrame a ser exportado
            nome_arquivo: Nome do arquivo CSV (padrão: dados_exportados.csv)
            
        Returns:
            bytes: Conteúdo do arquivo CSV em bytes
        """
        # Criar um buffer em memória
        output = io.StringIO()
        
        # Escrever o DataFrame no CSV
        df.to_csv(output, index=False, encoding='utf-8-sig')
        
        # Retornar o conteúdo do buffer
        output.seek(0)
        return output.getvalue().encode('utf-8-sig')
    
    def gerar_link_download(conteudo, nome_arquivo):
        """
        Gera um link de download para um conteúdo
        
        Args:
            conteudo: Conteúdo do arquivo em bytes
            nome_arquivo: Nome do arquivo
            
        Returns:
            str: Link de download em formato data URL
        """
        # Codificar o conteúdo em base64
        b64 = base64.b64encode(conteudo).decode()
        
        # Determinar o tipo MIME com base na extensão do arquivo
        if nome_arquivo.endswith('.xlsx'):
            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif nome_arquivo.endswith('.csv'):
            mime = 'text/csv'
        else:
            mime = 'application/octet-stream'
        
        # Criar o link de download
        href = f'data:{mime};base64,{b64}'
        
        return href
    
    def exportar_grafico_para_imagem(fig, formato='png'):
        """
        Exporta um gráfico Plotly para uma imagem
        
        Args:
            fig: Figura Plotly
            formato: Formato da imagem (padrão: png)
            
        Returns:
            bytes: Conteúdo da imagem em bytes
        """
        # Exportar a figura para o formato especificado
        img_bytes = fig.to_image(format=formato, scale=2)
        
        return img_bytes
    
    def exportar_dashboard_para_pdf(figs, nome_arquivo="dashboard_exportado.pdf"):
        """
        Exporta múltiplos gráficos para um único arquivo PDF
        
        Args:
            figs: Lista de figuras Plotly
            nome_arquivo: Nome do arquivo PDF (padrão: dashboard_exportado.pdf)
            
        Returns:
            bytes: Conteúdo do arquivo PDF em bytes
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            import tempfile
            
            # Criar um buffer em memória para o PDF
            buffer = io.BytesIO()
            
            # Criar um documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            
            # Lista de elementos para o PDF
            elements = []
            
            # Adicionar título
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"Dashboard Desafio PR - Exportado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Title']))
            elements.append(Spacer(1, 0.25*inch))
            
            # Adicionar cada figura como uma imagem
            for i, fig in enumerate(figs):
                # Salvar a figura temporariamente
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_filename = tmp.name
                    fig.write_image(tmp_filename, scale=2)
                
                # Adicionar a imagem ao PDF
                img = Image(tmp_filename, width=7*inch, height=5*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.25*inch))
                
                # Remover o arquivo temporário
                os.unlink(tmp_filename)
            
            # Construir o PDF
            doc.build(elements)
            
            # Retornar o conteúdo do buffer
            buffer.seek(0)
            return buffer.getvalue()
            
        except ImportError:
            # Se reportlab não estiver instalado
            return None
    
    # Retornar as funções criadas
    return {
        'exportar_para_excel': exportar_para_excel,
        'exportar_para_csv': exportar_para_csv,
        'gerar_link_download': gerar_link_download,
        'exportar_grafico_para_imagem': exportar_grafico_para_imagem,
        'exportar_dashboard_para_pdf': exportar_dashboard_para_pdf
    }

def criar_componentes_exportacao():
    """
    Cria componentes Dash para exportação de dados
    
    Returns:
        html.Div: Componente Dash com os botões de exportação
    """
    componente = html.Div([
        html.H3("Exportar Dados", className="section-title"),
        html.Div([
            html.Div([
                html.H5("Exportar Tabelas", className="export-subtitle"),
                html.Div([
                    dbc.Button("Exportar NREs (Excel)", id="btn-export-nre-excel", color="primary", className="export-button"),
                    dbc.Button("Exportar NREs (CSV)", id="btn-export-nre-csv", color="primary", className="export-button"),
                ], className="export-button-group"),
                html.Div([
                    dbc.Button("Exportar Escolas (Excel)", id="btn-export-escolas-excel", color="primary", className="export-button"),
                    dbc.Button("Exportar Escolas (CSV)", id="btn-export-escolas-csv", color="primary", className="export-button"),
                ], className="export-button-group"),
                # Links de download (inicialmente vazios)
                html.Div([
                    html.A(id="download-nre-excel", download="nres_metricas.xlsx"),
                    html.A(id="download-nre-csv", download="nres_metricas.csv"),
                    html.A(id="download-escolas-excel", download="escolas_metricas.xlsx"),
                    html.A(id="download-escolas-csv", download="escolas_metricas.csv"),
                ], style={"display": "none"}),
            ], className="export-section"),
            
            html.Div([
                html.H5("Exportar Gráficos", className="export-subtitle"),
                html.Div([
                    dbc.Button("Exportar Gráfico NREs (PNG)", id="btn-export-grafico-nre", color="primary", className="export-button"),
                    dbc.Button("Exportar Gráfico Alunos (PNG)", id="btn-export-grafico-alunos", color="primary", className="export-button"),
                ], className="export-button-group"),
                html.Div([
                    dbc.Button("Exportar Dashboard Completo (PDF)", id="btn-export-dashboard-pdf", color="primary", className="export-button"),
                ], className="export-button-group"),
                # Links de download para gráficos (inicialmente vazios)
                html.Div([
                    html.A(id="download-grafico-nre", download="grafico_nres.png"),
                    html.A(id="download-grafico-alunos", download="grafico_alunos.png"),
                    html.A(id="download-dashboard-pdf", download="dashboard_completo.pdf"),
                ], style={"display": "none"}),
            ], className="export-section"),
        ], className="export-container"),
        
        # Feedback de exportação
        dbc.Alert(
            "Exportação concluída com sucesso!",
            id="alert-export",
            color="success",
            dismissable=True,
            is_open=False,
            duration=4000,
        ),
    ], className="export-section-container")
    
    return componente

def registrar_callbacks_exportacao(app):
    """
    Registra os callbacks para os botões de exportação
    
    Args:
        app: Aplicação Dash
    """
    # Obter as funções de exportação
    funcoes_exportacao = criar_funcao_exportacao()
    
    # Callback para exportar NREs para Excel
    @app.callback(
        [Output("download-nre-excel", "href"),
         Output("download-nre-excel", "children")],
        [Input("btn-export-nre-excel", "n_clicks")],
        prevent_initial_call=True
    )
    def exportar_nre_excel(n_clicks):
        if n_clicks:
            # Carregar dados
            df_nre_metricas = pd.read_csv('dados_processados/nre_metricas.csv')
            
            # Exportar para Excel
            excel_bytes = funcoes_exportacao['exportar_para_excel'](df_nre_metricas, "nres_metricas.xlsx")
            
            # Gerar link de download
            href = funcoes_exportacao['gerar_link_download'](excel_bytes, "nres_metricas.xlsx")
            
            # Simular clique no link de download
            return href, html.Script("document.getElementById('download-nre-excel').click();")
        
        return "", ""
    
    # Callback para exportar NREs para CSV
    @app.callback(
        [Output("download-nre-csv", "href"),
         Output("download-nre-csv", "children")],
        [Input("btn-export-nre-csv", "n_clicks")],
        prevent_initial_call=True
    )
    def exportar_nre_csv(n_clicks):
        if n_clicks:
            # Carregar dados
            df_nre_metricas = pd.read_csv('dados_processados/nre_metricas.csv')
            
            # Exportar para CSV
            csv_bytes = funcoes_exportacao['exportar_para_csv'](df_nre_metricas, "nres_metricas.csv")
            
            # Gerar link de download
            href = funcoes_exportacao['gerar_link_download'](csv_bytes, "nres_metricas.csv")
            
            # Simular clique no link de download
            return href, html.Script("document.getElementById('download-nre-csv').click();")
        
        return "", ""
    
    # Callback para exportar Escolas para Excel
    @app.callback(
        [Output("download-escolas-excel", "href"),
         Output("download-escolas-excel", "children")],
        [Input("btn-export-escolas-excel", "n_clicks")],
        prevent_initial_call=True
    )
    def exportar_escolas_excel(n_clicks):
        if n_clicks:
            # Carregar dados
            df_escolas_metricas = pd.read_csv('dados_processados/escolas_metricas.csv')
            
            # Exportar para Excel
            excel_bytes = funcoes_exportacao['exportar_para_excel'](df_escolas_metricas, "escolas_metricas.xlsx")
            
            # Gerar link de download
            href = funcoes_exportacao['gerar_link_download'](excel_bytes, "escolas_metricas.xlsx")
            
            # Simular clique no link de download
            return href, html.Script("document.getElementById('download-escolas-excel').click();")
        
        return "", ""
    
    # Callback para exportar Escolas para CSV
    @app.callback(
        [Output("download-escolas-csv", "href"),
         Output("download-escolas-csv", "children")],
        [Input("btn-export-escolas-csv", "n_clicks")],
        prevent_initial_call=True
    )
    def exportar_escolas_csv(n_clicks):
        if n_clicks:
            # Carregar dados
            df_escolas_metricas = pd.read_csv('dados_processados/escolas_metricas.csv')
            
            # Exportar para CSV
            csv_bytes = funcoes_exportacao['exportar_para_csv'](df_escolas_metricas, "escolas_metricas.csv")
            
            # Gerar link de download
            href = funcoes_exportacao['gerar_link_download'](csv_bytes, "escolas_metricas.csv")
            
            # Simular clique no link de download
            return href, html.Script("document.getElementById('download-escolas-csv').click();")
        
        return "", ""
    
    # Callback para exportar gráfico de NREs
    @app.callback(
        [Output("download-grafico-nre", "href"),
         Output("download-grafico-nre", "children")],
        [Input("btn-export-grafico-nre", "n_clicks")],
        [State("grafico-nres", "figure")],
        prevent_initial_call=True
    )
    def exportar_grafico_nre(n_clicks, figura):
        if n_clicks and figura:
            # Criar figura a partir dos dados
            fig = go.Figure(figura)
            
            # Exportar para PNG
            img_bytes = funcoes_exportacao['exportar_grafico_para_imagem'](fig, 'png')
            
            # Gerar link de download
            href = funcoes_exportacao['gerar_link_download'](img_bytes, "grafico_nres.png")
            
            # Simular clique no link de download
            return href, html.Script("document.getElementById('download-grafico-nre').click();")
        
        return "", ""
    
    # Callback para exportar gráfico de Alunos
    @app.callback(
        [Output("download-grafico-alunos", "href"),
         Output("download-grafico-alunos", "children")],
        [Input("btn-export-grafico-alunos", "n_clicks")],
        [State("grafico-alunos-nre", "figure")],
        prevent_initial_call=True
    )
    def exportar_grafico_alunos(n_clicks, figura):
        if n_clicks and figura:
            # Criar figura a partir dos dados
            fig = go.Figure(figura)
            
            # Exportar para PNG
            img_bytes = funcoes_exportacao['exportar_grafico_para_imagem'](fig, 'png')
            
            # Gerar link de download
            href = funcoes_exportacao['gerar_link_download'](img_bytes, "grafico_alunos.png")
            
            # Simular clique no link de download
            return href, html.Script("document.getElementById('download-grafico-alunos').click();")
        
        return "", ""
    
    # Callback para exportar dashboard completo para PDF
    @app.callback(
        [Output("download-dashboard-pdf", "href"),
         Output("download-dashboard-pdf", "children"),
         Output("alert-export", "is_open")],
        [Input("btn-export-dashboard-pdf", "n_clicks")],
        [State("grafico-nres", "figure"),
         State("grafico-alunos-nre", "figure"),
         State("gauge-respostas", "figure"),
         State("gauge-acertos", "figure")],
        prevent_initial_call=True
    )
    def exportar_dashboard_pdf(n_clicks, fig_nres, fig_alunos, fig_respostas, fig_acertos):
        if n_clicks and all([fig_nres, fig_alunos, fig_respostas, fig_acertos]):
            # Criar figuras a partir dos dados
            figuras = [
                go.Figure(fig_nres),
                go.Figure(fig_alunos),
                go.Figure(fig_respostas),
                go.Figure(fig_acertos)
            ]
            
            # Exportar para PDF
            pdf_bytes = funcoes_exportacao['exportar_dashboard_para_pdf'](figuras, "dashboard_completo.pdf")
            
            if pdf_bytes:
                # Gerar link de download
                href = funcoes_exportacao['gerar_link_download'](pdf_bytes, "dashboard_completo.pdf")
                
                # Simular clique no link de download
                return href, html.Script("document.getElementById('download-dashboard-pdf').click();"), True
            else:
                # Se não foi possível gerar o PDF (reportlab não instalado)
                return "", "", False
        
        return "", "", False

if __name__ == "__main__":
    # Teste das funções
    funcoes = criar_funcao_exportacao()
    print("Funções de exportação criadas com sucesso!")
    
    # Criar um DataFrame de teste
    df_teste = pd.DataFrame({
        'NRE': ['NRE 1', 'NRE 2', 'NRE 3'],
        'Alunos': [1000, 2000, 3000],
        'Professores': [50, 100, 150]
    })
    
    # Testar exportação para Excel
    excel_bytes = funcoes['exportar_para_excel'](df_teste)
    print(f"Tamanho do arquivo Excel: {len(excel_bytes)} bytes")
    
    # Testar exportação para CSV
    csv_bytes = funcoes['exportar_para_csv'](df_teste)
    print(f"Tamanho do arquivo CSV: {len(csv_bytes)} bytes")
