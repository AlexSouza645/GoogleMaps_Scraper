import pandas as pd
import os
import re
import sqlite3
import logging

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

def get_db_path():
    base = get_base_path()
    pasta_data = os.path.join(base, 'data')
    if not os.path.exists(pasta_data):
        os.makedirs(pasta_data)
    return os.path.join(pasta_data, "historico.db")

def inicializar_banco():
    con = sqlite3.connect(get_db_path())
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            nome TEXT,
            telefone TEXT,
            UNIQUE(nome, telefone)
        )
    """)
    con.commit()
    con.close()

def lead_existe(nome, telefone):
    inicializar_banco()
    con = sqlite3.connect(get_db_path())
    cur = con.cursor()
    cur.execute("SELECT 1 FROM leads WHERE nome = ? AND telefone = ?", (nome, telefone))
    existe = cur.fetchone() is not None
    con.close()
    return existe

def salvar_lead_historico(nome, telefone):
    try:
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO leads (nome, telefone) VALUES (?, ?)", (nome, telefone))
        con.commit()
        con.close()
    except Exception:
        pass

def enviar_para_crm(lista_leads):
    """
    Mock/Simulador de envio para CRM (ex: PipeDrive, RD Station).
    No futuro, integramos a API de POST aqui.
    """
    print(f"   🚀 [API CRM] Disparando {len(lista_leads)} leads automaticamente para o CRM do cliente...")
    # Simula um delay de rede
    import time
    time.sleep(1)
    print("   ✅ [API CRM] Leads enviados com sucesso ao PipeDrive/RD Station!")

def salvar_excel(lista_leads, nicho, cidade, plano="ENTERPRISE"):
    """
    Recebe a lista de dicionários e converte para uma planilha ajustando ao plano do cliente.
    """
    base = get_base_path()
    pasta_data = os.path.join(base, 'data')
    
    # Cria a pasta 'data' se não existir (Boa prática!)
    if not os.path.exists(pasta_data):
        os.makedirs(pasta_data)

    df = pd.DataFrame(lista_leads)

    # Aplica a limpeza na coluna de Telefone para transformá-la diretamente no Hyperlink do WhatsApp
    # Plano START recebe o numero cru (sem hiperlink de WA)
    if 'Telefone' in df.columns and plano in ["PRO", "ENTERPRISE"]:
        df['Telefone'] = df['Telefone'].apply(limpar_telefone)

    # Reordena as colunas para o Status vir primeiro dependendo do plano
    if plano == "START":
        colunas_ordem = ["Nome", "Telefone", "Link do Maps"]
    elif plano == "PRO":
        colunas_ordem = ["Nome", "Telefone", "Site", "Presença Digital", "Link do Maps"]
    else: # ENTERPRISE
        colunas_ordem = ["Status do Lead", "Prioridade", "Nome", "E-mail", "Instagram", "Facebook", "LinkedIn", "Telefone", "Site", "Status do Site", "Presença Digital", "Link do Maps"]
        
    # Seleciona apenas as colunas que realmente existem (evita erros se algo não for coletado)
    colunas_ordem = [col for col in colunas_ordem if col in df.columns]
    df = df[colunas_ordem]

    # Remove duplicatas baseadas no Nome e Telefone
    if 'Nome' in df.columns and 'Telefone' in df.columns:
        df = df.drop_duplicates(subset=['Nome', 'Telefone'])
    
    # Plano Enterprise: Salva no banco de inteligência e dispara para o CRM
    if plano == "ENTERPRISE":
        for index, row in df.iterrows():
            salvar_lead_historico(row.get('Nome', 'N/A'), row.get('Telefone', 'N/A'))
        enviar_para_crm(df.to_dict('records'))

    nome_arquivo = os.path.join(pasta_data, f"leads_{nicho}_{cidade}_{plano}.xlsx")
    
    # Utiliza xlsxwriter para criar uma planilha premium
    writer = pd.ExcelWriter(nome_arquivo, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Leads Extraídos')
    
    workbook = writer.book
    worksheet = writer.sheets['Leads Extraídos']
    
    # Definir Estilo Premium de Cabeçalho
    header_format = workbook.add_format({
        'bold': True,
        'font_color': 'white',
        'bg_color': '#003366',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    # Escrever Cabeçalhos com Formatação e Congelar Linha 1
    worksheet.freeze_panes(1, 0)
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    # Auto-Ajustar a Largura das Colunas
    for i, col in enumerate(df.columns):
        tamanho = 15
        if col == "Nome": tamanho = 35
        elif col in ["E-mail", "Instagram", "Facebook", "LinkedIn", "Site", "Link do Maps"]: tamanho = 30
        elif col == "Telefone": tamanho = 22
        worksheet.set_column(i, i, tamanho)

    writer.close()
    
    print(f"✅ Dados guardados com sucesso em: {nome_arquivo}")

def configurar_logging():
    base = get_base_path()
    pasta_logs = os.path.join(base, 'logs')
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)
        
    log_file = os.path.join(pasta_logs, "execucao.log")
    
    # Impede que o logging adicione múltiplos handlers se a função rodar 2x
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s - %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S",
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

# Roda configuração de logs logo na importação
configurar_logging()

def registrar_log(mensagem):
    """
    Mantido para compatibilidade. Usa a vova engine de logging nativa.
    """
    # Envia a mensagem a nível informativo
    logging.info(mensagem)