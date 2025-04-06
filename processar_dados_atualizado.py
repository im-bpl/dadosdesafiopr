import pandas as pd
import numpy as np
import json
import os
import shutil
from datetime import datetime

def extrair_dados_planilhas():
    """
    Extrai os dados das planilhas e os estrutura para uso no dashboard
    """
    # Caminho das planilhas
    modelo_path = '/home/ubuntu/upload/MODELO DADOS DESAFIO PR.xlsx'
    dados_path = '/home/ubuntu/upload/_DADOS DESAFIO PR - NRES.xlsx'
    
    # Criar diretório para armazenar os dados processados
    os.makedirs('dados_processados', exist_ok=True)
    
    # Extrair dados da planilha modelo
    df_modelo_nre = pd.read_excel(modelo_path, sheet_name='NRE DOIS VIZINHOS GERAL')
    df_modelo_prof = pd.read_excel(modelo_path, sheet_name='PROFESSORES ATIVOS')
    
    # Extrair dados da planilha de dados
    df_desafio = pd.read_excel(dados_path, sheet_name='DESAFIO PR - NRE')
    df_raiz = pd.read_excel(dados_path, sheet_name='RAIZ')
    
    # Obter lista de todos os NREs
    nres = sorted(df_desafio['NRE'].dropna().unique())
    
    # Extrair dados de cada NRE
    dados_nres = {}
    for nre in nres:
        try:
            # Tentar ler a aba específica do NRE
            sheet_name = nre.strip()
            df_nre = pd.read_excel(dados_path, sheet_name=sheet_name)
            dados_nres[nre] = df_nre
        except Exception as e:
            print(f"Erro ao ler dados do NRE {nre}: {e}")
    
    # Processar dados para o dashboard
    
    # 1. Dados gerais por NRE
    df_nre_geral = df_desafio.copy()
    # Remover a primeira linha que contém totais
    if pd.isna(df_nre_geral.iloc[0]['NRE']):
        df_nre_geral = df_nre_geral.iloc[1:].reset_index(drop=True)
    
    # Calcular métricas agregadas por NRE
    nre_metricas = df_nre_geral.groupby('NRE').agg({
        'Alunos': 'sum',
        'Atribuição Esperada': 'sum',
        'Questões Respondidas': 'sum',
        'Questões Corretas': 'sum',
        'Professores': 'sum',
        'Escola': 'count'
    }).reset_index()
    
    # Calcular índices
    nre_metricas['Índice de Respostas'] = nre_metricas['Questões Respondidas'] / nre_metricas['Atribuição Esperada']
    nre_metricas['Percentual de acertos'] = nre_metricas['Questões Corretas'] / nre_metricas['Questões Respondidas']
    nre_metricas.rename(columns={'Escola': 'Número de Escolas'}, inplace=True)
    
    # 2. Dados por escola
    escolas_metricas = df_nre_geral.copy()
    
    # 3. Dados de professores (da planilha modelo)
    professores_metricas = df_modelo_prof.copy()
    
    # Salvar dados processados
    nre_metricas.to_csv('dados_processados/nre_metricas.csv', index=False)
    escolas_metricas.to_csv('dados_processados/escolas_metricas.csv', index=False)
    professores_metricas.to_csv('dados_processados/professores_metricas.csv', index=False)
    
    # Salvar lista de NREs
    with open('dados_processados/lista_nres.json', 'w', encoding='utf-8') as f:
        json.dump(list(nres), f, ensure_ascii=False)
    
    # Criar estrutura de dados para o dashboard
    estrutura_dados = {
        'nres': list(nres),
        'total_nres': len(nres),
        'total_escolas': len(escolas_metricas),
        'total_alunos': int(escolas_metricas['Alunos'].sum()),
        'total_professores': int(escolas_metricas['Professores'].sum()),
        'indice_respostas_geral': float(escolas_metricas['Questões Respondidas'].sum() / escolas_metricas['Atribuição Esperada'].sum()),
        'percentual_acertos_geral': float(escolas_metricas['Questões Corretas'].sum() / escolas_metricas['Questões Respondidas'].sum()),
        'ultima_atualizacao': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'semanas_atuais': 8,  # Valor padrão
        'questoes_por_semana': 30  # Valor padrão
    }
    
    # Salvar estrutura de dados
    with open('dados_processados/estrutura_dados.json', 'w', encoding='utf-8') as f:
        json.dump(estrutura_dados, f, ensure_ascii=False, indent=4)
    
    # Criar mapeamento de escolas por NRE
    escolas_por_nre = {}
    for nre in nres:
        escolas = df_nre_geral[df_nre_geral['NRE'] == nre]['Escola'].tolist()
        escolas_por_nre[nre] = escolas
    
    # Salvar mapeamento de escolas por NRE
    with open('dados_processados/escolas_por_nre.json', 'w', encoding='utf-8') as f:
        json.dump(escolas_por_nre, f, ensure_ascii=False, indent=4)
    
    # Criar mapeamento de professores por escola (da planilha modelo)
    professores_por_escola = {}
    for escola in professores_metricas['Escola'].unique():
        profs = professores_metricas[professores_metricas['Escola'] == escola]['E-mail do Professor'].tolist()
        professores_por_escola[escola] = profs
    
    # Salvar mapeamento de professores por escola
    with open('dados_processados/professores_por_escola.json', 'w', encoding='utf-8') as f:
        json.dump(professores_por_escola, f, ensure_ascii=False, indent=4)
    
    # Inicializar o histórico de atualizações se não existir
    historico_file = 'dados_processados/historico_atualizacoes.json'
    if not os.path.exists(historico_file):
        with open(historico_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    
    return {
        'nre_metricas': nre_metricas,
        'escolas_metricas': escolas_metricas,
        'professores_metricas': professores_metricas,
        'estrutura_dados': estrutura_dados,
        'escolas_por_nre': escolas_por_nre,
        'professores_por_escola': professores_por_escola
    }

def criar_funcoes_atualizacao():
    """
    Cria funções para atualização dos dados a partir de novas planilhas
    
    Returns:
        dict: Dicionário com as funções de atualização
    """
    def verificar_formato_planilha(arquivo_excel):
        """
        Verifica se a planilha tem o formato esperado para atualização
        
        Args:
            arquivo_excel: Caminho para o arquivo Excel
            
        Returns:
            tuple: (bool, str) indicando se o formato é válido e uma mensagem
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo_excel):
                return False, f"Arquivo {arquivo_excel} não encontrado."
            
            # Verificar se o arquivo tem a aba RAIZ
            try:
                xls = pd.ExcelFile(arquivo_excel)
                if 'RAIZ' not in xls.sheet_names:
                    return False, "A planilha não contém a aba 'RAIZ' necessária para atualização."
                
                # Ler a aba RAIZ
                df_raiz = pd.read_excel(arquivo_excel, sheet_name='RAIZ')
                
                # Verificar se as colunas necessárias estão presentes
                colunas_necessarias = ['NRE', 'Escola', 'Alunos', 'Questões Respondidas', 
                                      'Questões Corretas', 'Professores']
                
                colunas_faltantes = []
                for coluna in colunas_necessarias:
                    if coluna not in df_raiz.columns:
                        colunas_faltantes.append(coluna)
                
                if colunas_faltantes:
                    return False, f"Colunas faltantes na aba RAIZ: {', '.join(colunas_faltantes)}"
                
                # Verificar se há dados
                if len(df_raiz) < 2:  # Considerando que pode haver uma linha de total
                    return False, "A planilha não contém dados suficientes na aba RAIZ."
                
                return True, "A planilha tem o formato correto para atualização."
                
            except Exception as e:
                return False, f"Erro ao verificar a estrutura da planilha: {str(e)}"
            
        except Exception as e:
            return False, f"Erro ao verificar o formato da planilha: {str(e)}"
    
    def atualizar_dados_dashboard(arquivo_excel, semanas_atuais=8, questoes_por_semana=30):
        """
        Atualiza os dados do dashboard a partir de um novo arquivo Excel
        
        Args:
            arquivo_excel: Caminho para o arquivo Excel com novos dados
            semanas_atuais: Número atual de semanas (padrão: 8)
            questoes_por_semana: Número de questões por semana (padrão: 30)
            
        Returns:
            str: Mensagem com o resultado da atualização
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo_excel):
                return f"Erro: Arquivo {arquivo_excel} não encontrado."
            
            # Verificar se o arquivo tem a estrutura esperada
            formato_valido, mensagem = verificar_formato_planilha(arquivo_excel)
            if not formato_valido:
                return f"Erro: {mensagem}"
            
            # Fazer backup dos dados atuais
            if not os.path.exists('backup'):
                os.makedirs('backup')
                
            # Criar um timestamp para o backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup/dados_{timestamp}"
            os.makedirs(backup_dir)
            
            # Copiar os arquivos de dados para o backup
            if os.path.exists('dados_processados'):
                for arquivo in os.listdir('dados_processados'):
                    shutil.copy(f"dados_processados/{arquivo}", f"{backup_dir}/{arquivo}")
            
            # Processar os novos dados
            print("Processando novos dados...")
            
            # Extrair dados da planilha
            df_desafio = pd.read_excel(arquivo_excel, sheet_name='RAIZ')
            
            # Remover a primeira linha se for um total
            if pd.isna(df_desafio.iloc[0]['NRE']):
                df_desafio = df_desafio.iloc[1:].reset_index(drop=True)
            
            # Calcular a Atribuição Esperada com a fórmula correta: Alunos × questões_por_semana × semanas_atuais
            df_desafio['Atribuição Esperada'] = df_desafio['Alunos'] * questoes_por_semana * semanas_atuais
            
            # Calcular o índice de respostas
            df_desafio['Índice de Respostas'] = df_desafio['Questões Respondidas'] / df_desafio['Atribuição Esperada']
            
            # Calcular o percentual de acertos se não estiver presente
            if 'Percentual de acertos' not in df_desafio.columns or df_desafio['Percentual de acertos'].isna().all():
                df_desafio['Percentual de acertos'] = df_desafio['Questões Corretas'] / df_desafio['Questões Respondidas']
            
            # Obter lista de todos os NREs
            nres = sorted(df_desafio['NRE'].dropna().unique())
            
            # Calcular métricas agregadas por NRE
            nre_metricas = df_desafio.groupby('NRE').agg({
                'Alunos': 'sum',
                'Atribuição Esperada': 'sum',
                'Questões Respondidas': 'sum',
                'Questões Corretas': 'sum',
                'Professores': 'sum',
                'Escola': 'count'
            }).reset_index()
            
            # Calcular índices
            nre_metricas['Índice de Respostas'] = nre_metricas['Questões Respondidas'] / nre_metricas['Atribuição Esperada']
            nre_metricas['Percentual de acertos'] = nre_metricas['Questões Corretas'] / nre_metricas['Questões Respondidas']
            nre_metricas.rename(columns={'Escola': 'Número de Escolas'}, inplace=True)
            
            # Dados por escola
            escolas_metricas = df_desafio.copy()
            
            # Criar estrutura de dados para o dashboard
            estrutura_dados = {
                'nres': list(nres),
                'total_nres': len(nres),
                'total_escolas': len(escolas_metricas),
                'total_alunos': int(escolas_metricas['Alunos'].sum()),
                'total_professores': int(escolas_metricas['Professores'].sum()),
                'indice_respostas_geral': float(escolas_metricas['Questões Respondidas'].sum() / escolas_metricas['Atribuição Esperada'].sum()),
                'percentual_acertos_geral': float(escolas_metricas['Questões Corretas'].sum() / escolas_metricas['Questões Respondidas'].sum()),
                'ultima_atualizacao': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'semanas_atuais': semanas_atuais,
                'questoes_por_semana': questoes_por_semana
            }
            
            # Criar mapeamento de escolas por NRE
            escolas_por_nre = {}
            for nre in nres:
                escolas = df_desafio[df_desafio['NRE'] == nre]['Escola'].tolist()
                escolas_por_nre[nre] = escolas
            
            # Salvar os dados processados
            os.makedirs('dados_processados', exist_ok=True)
            
            nre_metricas.to_csv('dados_processados/nre_metricas.csv', index=False)
            escolas_metricas.to_csv('dados_processados/escolas_metricas.csv', index=False)
            
            with open('dados_processados/lista_nres.json', 'w', encoding='utf-8') as f:
                json.dump(list(nres), f, ensure_ascii=False)
                
            with open('dados_processados/estrutura_dados.json', 'w', encoding='utf-8') as f:
                json.dump(estrutura_dados, f, ensure_ascii=False, indent=4)
                
            with open('dados_processados/escolas_por_nre.json', 'w', encoding='utf-8') as f:
                json.dump(escolas_por_nre, f, ensure_ascii=False, indent=4)
            
            # Registrar o histórico de atualizações
            historico_file = 'dados_processados/historico_atualizacoes.json'
            if os.path.exists(historico_file):
                with open(historico_file, 'r', encoding='utf-8') as f:
                    try:
                        historico = json.load(f)
                    except:
                        historico = []
            else:
                historico = []
            
            # Adicionar nova atualização ao histórico
            historico.append({
                'data': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'arquivo': os.path.basename(arquivo_excel),
                'backup': backup_dir,
                'semanas': semanas_atuais,
                'metricas': {
                    'total_nres': estrutura_dados['total_nres'],
                    'total_escolas': estrutura_dados['total_escolas'],
                    'total_alunos': estrutura_dados['total_alunos'],
                    'total_professores': estrutura_dados['total_professores'],
                    'indice_respostas_geral': estrutura_dados['indice_respostas_geral'],
                    'percentual_acertos_geral': estrutura_dados['percentual_acertos_geral']
                }
            })
            
            # Salvar histórico atualizado
            with open(historico_file, 'w', encoding='utf-8') as f:
                json.dump(historico, f, ensure_ascii=False, indent=4)
            
            return f"""
            Dados atualizados com sucesso!
            
            Resumo da atualização:
            - Semana atual: {semanas_atuais}
            - Questões por semana: {questoes_por_semana}
            - Total de NREs: {estrutura_dados['total_nres']}
            - Total de escolas: {estrutura_dados['total_escolas']}
            - Total de alunos: {estrutura_dados['total_alunos']:,}
            - Total de professores: {estrutura_dados['total_professores']:,}
            - Índice de respostas geral: {estrutura_dados['indice_respostas_geral']:.1%}
            - Percentual de acertos geral: {estrutura_dados['percentual_acertos_geral']:.1%}
            
            Backup dos dados anteriores salvo em: {backup_dir}
            Histórico de atualizações registrado.
            
            Para visualizar as alterações, clique em "Recarregar Dashboard".
            """
            
        except Exception as e:
            return f"Erro durante a atualização dos dados: {str(e)}"
    
    def obter_historico_atualizacoes(limite=5):
        """
        Obtém o histórico de atualizações
        
        Args:
            limite: Número máximo de registros a retornar (padrão: 5)
            
        Returns:
            list: Lista com os registros de atualização
        """
        historico_file = 'dados_processados/historico_atualizacoes.json'
        if os.path.exists(historico_file):
            with open(historico_file, 'r', encoding='utf-8') as f:
                try:
                    historico = json.load(f)
                    return historico[:limite]
                except:
                    return []
        return []
    
    def validar_dados_entrada(df):
        """
        Valida os dados de entrada para garantir consistência
        
        Args:
            df: DataFrame com os dados a serem validados
            
        Returns:
            tuple: (bool, str) indicando se os dados são válidos e uma mensagem
        """
        try:
            # Verificar valores negativos
            for coluna in ['Alunos', 'Questões Respondidas', 'Questões Corretas', 'Professores']:
                if (df[coluna] < 0).any():
                    return False, f"Existem valores negativos na coluna {coluna}"
            
            # Verificar inconsistências lógicas
            if (df['Questões Corretas'] > df['Questões Respondidas']).any():
                return False, "Existem escolas com mais questões corretas do que respondidas"
            
            # Verificar valores zerados que podem causar divisão por zero
            if (df['Questões Respondidas'] == 0).any():
                # Não é um erro crítico, apenas um aviso
                print("Aviso: Existem escolas sem questões respondidas")
            
            # Verificar duplicatas de escolas
            if df['Escola'].duplicated().any():
                escolas_duplicadas = df[df['Escola'].duplicated()]['Escola'].tolist()
                return False, f"Existem escolas duplicadas: {', '.join(escolas_duplicadas)}"
            
            return True, "Dados válidos"
            
        except Exception as e:
            return False, f"Erro ao validar dados: {str(e)}"
    
    # Retornar as funções criadas
    return {
        'verificar_formato_planilha': verificar_formato_planilha,
        'atualizar_dados_dashboard': atualizar_dados_dashboard,
        'obter_historico_atualizacoes': obter_historico_atualizacoes,
        'validar_dados_entrada': validar_dados_entrada
    }

if __name__ == "__main__":
    print("Iniciando extração e processamento dos dados...")
    dados = extrair_dados_planilhas()
    print("Dados extraídos e processados com sucesso!")
    print(f"Total de NREs: {dados['estrutura_dados']['total_nres']}")
    print(f"Total de escolas: {dados['estrutura_dados']['total_escolas']}")
    print(f"Total de alunos: {dados['estrutura_dados']['total_alunos']}")
    print(f"Total de professores: {dados['estrutura_dados']['total_professores']}")
    print(f"Índice de respostas geral: {dados['estrutura_dados']['indice_respostas_geral']:.2%}")
    print(f"Percentual de acertos geral: {dados['estrutura_dados']['percentual_acertos_geral']:.2%}")
    print("Arquivos salvos no diretório 'dados_processados'")
    
    print("\nCriando funções de atualização...")
    funcoes = criar_funcoes_atualizacao()
    print("Funções de atualização criadas com sucesso!")
