import pandas as pd
import json
import os
import shutil
import datetime
from processar_dados_atualizado import criar_funcoes_atualizacao

def verificar_formato_planilha(arquivo_excel):
    """
    Verifica se a planilha tem o formato esperado para atualização
    
    Args:
        arquivo_excel: Caminho para o arquivo Excel
        
    Returns:
        tuple: (bool, str) indicando se o formato é válido e uma mensagem
    """
    # Obter as funções de atualização
    funcoes = criar_funcoes_atualizacao()
    return funcoes['verificar_formato_planilha'](arquivo_excel)

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
    # Obter as funções de atualização
    funcoes = criar_funcoes_atualizacao()
    return funcoes['atualizar_dados_dashboard'](arquivo_excel, semanas_atuais, questoes_por_semana)

def obter_historico_atualizacoes(limite=5):
    """
    Obtém o histórico de atualizações
    
    Args:
        limite: Número máximo de registros a retornar (padrão: 5)
        
    Returns:
        list: Lista com os registros de atualização
    """
    # Obter as funções de atualização
    funcoes = criar_funcoes_atualizacao()
    return funcoes['obter_historico_atualizacoes'](limite)

def validar_dados_entrada(df):
    """
    Valida os dados de entrada para garantir consistência
    
    Args:
        df: DataFrame com os dados a serem validados
        
    Returns:
        tuple: (bool, str) indicando se os dados são válidos e uma mensagem
    """
    # Obter as funções de atualização
    funcoes = criar_funcoes_atualizacao()
    return funcoes['validar_dados_entrada'](df)

if __name__ == "__main__":
    # Teste da função
    resultado = atualizar_dados_dashboard('/home/ubuntu/upload/_DADOS DESAFIO PR - NRES.xlsx')
    print(resultado)
