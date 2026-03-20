# 🤖 Google Maps Lead Scraper (RPA)

### **Descrição do Projeto**

Este é um sistema de Automação de Processos Robóticos (RPA) desenvolvido em **Python** para extração inteligente de leads diretamente do Google Maps. O projeto foi desenhado com foco em **escalabilidade** e  **qualidade de dados** , permitindo que empresas de marketing e vendas mapeiem mercados locais de forma automática.

---

### **🚀 Funcionalidades Principais**

* **Extração Assíncrona:** Utiliza **Playwright** para navegação ultra-rápida e eficiente, simulando o comportamento humano para evitar bloqueios.
* **Data Cleaning (Limpeza de Dados):** Pipeline integrado que padroniza números de telefone (formato E.164) e remove caracteres especiais via Regex.
* **Deduplicação Inteligente:** Sistema que impede a gravação de leads duplicados no banco de dados final (Excel).
* **Sistema de Logging:** Registro detalhado de cada execução para auditoria e monitoramento de erros em tempo real.
* **Arquitetura Modular:** Código dividido em módulos (`Scraper`, `Utils`, `Main`) facilitando a manutenção e testes unitários.

---

### **🛠️ Tecnologias Utilizadas**

* **Python 3.10+**
* **Playwright:** Automação de navegador (Chromium).
* **Pandas:** Manipulação e tratamento de grandes volumes de dados.
* **Openpyxl:** Exportação de relatórios profissionais em `.xlsx`.
* **Asyncio:** Gestão de concorrência e tarefas assíncronas.

---

### **📁 Estrutura do Repositório**

**Plaintext**

```
├── 📄 main.py              # Orquestrador do fluxo de automação
├── 📄 scraper_logic.py     # Motor de interação com a DOM do Google Maps
├── 📄 utils.py             # Funções auxiliares de limpeza e persistência
├── 📁 data/                # Output dos leads processados (Excel)
├── 📁 logs/                # Histórico de auditoria do sistema
└── 📄 requirements.txt     # Dependências do projeto
```

---

### **📥 Instalação e Uso**

1. **Clonar o repositório:**
   **Bash**

   ```
   git clone https://github.com/seu-usuario/google-maps-scraper.git
   ```
2. **Instalar dependências:**
   **Bash**

   ```
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Executar:**
   **Bash**

   ```
   python main.py
   ```

---

### **🎯 Diferenciais Técnicos (Para Recrutadores)**

Este projeto não é apenas um "script de raspagem". Ele demonstra domínio sobre:

1. **Gerenciamento de Contexto:** Uso de `with` e encerramento de processos para economia de memória.
2. **Robustez:** Tratamento de exceções em cada etapa do clique e extração.
3. **Visão de Negócio:** Foco em entregar um dado "limpo" (Lead Qualificado) pronto para o setor comercial
