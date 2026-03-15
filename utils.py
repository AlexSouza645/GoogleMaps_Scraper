import pandas as pd
import os
import re

def limpar_telefone(telefone_sujo):
    """
    Remove caracteres especiais e garante o formato brasileiro.
    Exemplo: (11) 98888-7777 -> 11988887777
    """
    if not telefone_sujo or telefone_sujo == "N/A":
        return "N/A"
    
    # Remove tudo o que não for número usando Regex
    apenas_numeros = re.sub(r'\D', '', telefone_sujo)
    
    # Se o número for brasileiro e faltar o DDI (55), podemos adicionar
    if len(apenas_numeros) >= 10 and not apenas_numeros.startswith('55'):
        return f"55{apenas_numeros}"
    
    return apenas_numeros

def salvar_excel(lista_leads, nicho, cidade):
    """
    Recebe a lista de dicionários e converte para uma planilha profissional.
    """
    # Cria a pasta 'data' se não existir (Boa prática!)
    if not os.path.exists('data'):
        os.makedirs('data')

    df = pd.DataFrame(lista_leads)

    # Aplica a limpeza na coluna de Telefone (Passagem de variável!)
    if 'Telefone' in df.columns:
        df['Telefone'] = df['Telefone'].apply(limpar_telefone)

    # Remove duplicatas baseadas no Nome e Telefone
    df = df.drop_duplicates(subset=['Nome', 'Telefone'])

    nome_arquivo = f"data/leads_{nicho}_{cidade}.xlsx"
    df.to_excel(nome_arquivo, index=False)
    print(f"✅ Dados guardados com sucesso em: {nome_arquivo}")

def registrar_log(mensagem):
    """
    Cria um histórico da execução do robô.
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    with open("logs/execucao.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")