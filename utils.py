import pandas as pd
import os
import re

def limpar_telefone(telefone_sujo):
    """
    Remove caracteres especiais, limpa zeros do DDD e cria hiperlink do WhatsApp com ícone.
    """
    if not telefone_sujo or telefone_sujo == "N/A":
        return "N/A"
    
    # Remove tudo o que não for número usando Regex
    apenas_numeros = re.sub(r'\D', '', telefone_sujo)
    
    # Remove o DDI 55 caso exista para evitar duplicidade ou zeros indesejados
    if apenas_numeros.startswith('55') and len(apenas_numeros) >= 12:
        apenas_numeros = apenas_numeros[2:]
        
    # Remove zeros soltos que as vezes o telefone traz antes do DDD (ex: 011)
    apenas_numeros = apenas_numeros.lstrip('0')
    
    # Se for muito curto para ser telefone, retorna como está
    if len(apenas_numeros) < 10:
        return apenas_numeros
        
    # Remonta o número certinho garantindo que só tem 55 + DDD limpo + Numero
    numero_wa = f"55{apenas_numeros}"
    
    # Retorna com o próprio número e um ícone de celular visível e clicável!
    return f'=HYPERLINK("https://wa.me/{numero_wa}", "📱 {numero_wa}")'

import sys

def get_base_path():
    """Retorna o diretório base onde está o script ou o .exe"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        # Se o executável estiver rodando de dentro da pasta "dist", 
        # volta um nível para salvar na pasta "data" raiz do projeto.
        if os.path.basename(exe_dir).lower() == 'dist':
            return os.path.dirname(exe_dir)
        return exe_dir
    return os.path.dirname(os.path.abspath(__file__))

def salvar_excel(lista_leads, nicho, cidade):
    """
    Recebe a lista de dicionários e converte para uma planilha profissional.
    """
    base = get_base_path()
    pasta_data = os.path.join(base, 'data')
    
    # Cria a pasta 'data' se não existir (Boa prática!)
    if not os.path.exists(pasta_data):
        os.makedirs(pasta_data)

    df = pd.DataFrame(lista_leads)

    # Aplica a limpeza na coluna de Telefone para transformá-la diretamente no Hyperlink do WhatsApp
    if 'Telefone' in df.columns:
        df['Telefone'] = df['Telefone'].apply(limpar_telefone)

    # Reordena as colunas para o Status vir primeiro e sem coluna avulsa do WhatsApp
    colunas_ordem = ["Status do Lead", "Nome", "E-mail", "Telefone", "Site", "Presença Digital", "Link do Maps"]
    # Seleciona apenas as colunas que realmente existem (evita erros se algo não for coletado)
    colunas_ordem = [col for col in colunas_ordem if col in df.columns]
    df = df[colunas_ordem]

    # Remove duplicatas baseadas no Nome e Telefone
    df = df.drop_duplicates(subset=['Nome', 'Telefone'])

    nome_arquivo = os.path.join(pasta_data, f"leads_{nicho}_{cidade}.xlsx")
    df.to_excel(nome_arquivo, index=False)
    print(f"✅ Dados guardados com sucesso em: {nome_arquivo}")

def registrar_log(mensagem):
    """
    Cria um histórico da execução do robô.
    """
    base = get_base_path()
    pasta_logs = os.path.join(base, 'logs')
    
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    arquivo_log = os.path.join(pasta_logs, "execucao.txt")
    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")