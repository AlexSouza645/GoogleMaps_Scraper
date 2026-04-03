from fpdf import FPDF

class PropostaPDF(FPDF):
    def header(self):
        # Cabeçalho com cor sólida (Azul Corporativo)
        self.set_fill_color(31, 78, 120)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, 'PROPOSTA DE INTELIGÊNCIA COMERCIAL', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def criar_proposta():
    pdf = PropostaPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- SEÇÃO 1: APRESENTAÇÃO ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '1. O Problema: O Gargalo da Prospecção Manual', ln=True)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 7, 'Empresas perdem até 15h semanais pesquisando contatos manualmente no Google Maps. Isso gera um alto custo de oportunidade e cansaço da equipe de vendas.')
    pdf.ln(5)

    # --- SEÇÃO 2: A SOLUÇÃO TÉCNICA ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '2. Nossa Solução: Automação via Python', ln=True)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 7, 'Utilizamos scripts de Web Scraping e Processamento de Dados para mapear nichos específicos em tempo real, entregando dados higienizados e prontos para ação.')
    pdf.ln(5)

    # --- SEÇÃO 3: NÍVEIS DE SERVIÇO (PLANOS) ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '3. Planos e Investimento', ln=True)
    
    # Tabela Simples
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(60, 10, 'Recurso', 1, 0, 'C', True)
    pdf.cell(40, 10, 'Plano START', 1, 0, 'C', True)
    pdf.cell(40, 10, 'Plano PRO', 1, 0, 'C', True)
    pdf.cell(50, 10, 'Plano ENTERPRISE', 1, 1, 'C', True)

    pdf.set_font('helvetica', '', 9)
    dados = [
        ['Leads Geocalizados', 'Sim', 'Sim', 'Sim'],
        ['Link Direto WhatsApp', 'Não', 'Sim', 'Sim'],
        ['Dashboard Visual', 'Não', 'Sim', 'Sim'],
        ['E-mail Institucional', 'Não', 'Não', 'Sim'],
        ['Integração CRM (API)', 'Não', 'Não', 'Sim'],
    ]

    for linha in dados:
        pdf.cell(60, 8, linha[0], 1)
        pdf.cell(40, 8, linha[1], 1, 0, 'C')
        pdf.cell(40, 8, linha[2], 1, 0, 'C')
        pdf.cell(50, 8, linha[3], 1, 1, 'C')
    pdf.ln(10)

    # --- SEÇÃO 4: GARANTIA E SEGURANÇA ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '4. Garantia e Confidencialidade (LGPD)', ln=True)
    pdf.set_font('helvetica', 'I', 10)
    pdf.multi_cell(0, 6, 'Garantimos a reposição imediata de leads com dados inconsistentes. Atuamos em conformidade com a LGPD, garantindo sigilo absoluto sobre os nichos e estratégias do cliente.')
    
    # Finalização
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 10, 'Interessado em escalar suas vendas? Fale conosco agora.', ln=True, align='C')
    
    # Link (Ajuste para o seu número quando tiver o Business)
    pdf.set_font('helvetica', 'U', 11)
    pdf.cell(0, 10, 'CLIQUE AQUI PARA FALAR NO WHATSAPP', ln=True, align='C', link='https://wa.me/5500000000000')

    pdf.output('Proposta_Automacao_Leads.pdf')
    print("✅ PDF 'Proposta_Automacao_Leads.pdf' gerado com sucesso!")

criar_proposta()