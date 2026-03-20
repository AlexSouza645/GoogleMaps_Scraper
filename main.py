import asyncio
from scraper_logic import iniciar_busca, extrair_detalhes
from utils import salvar_excel, registrar_log

async def rodar_automacao(nicho, cidade):
    """
    Função principal que coordena o fluxo do robô.
    """
    try:
        registrar_log(f"--- NOVA EXECUÇÃO: {nicho} em {cidade} ---")
        print(f"🚀 Iniciando busca por '{nicho}' em '{cidade}'...")

        # 1. Abre o navegador e faz a pesquisa
        browser, page = await iniciar_busca(nicho, cidade)

        # 2. Extrai os dados dos leads
        print("🕵️  Extraindo dados dos estabelecimentos...")
        lista_leads = await extrair_detalhes(page)

        # 3. Fecha o navegador (Importante para liberar memória!)
        await browser.close()

        # 4. Processa e salva os dados se houver resultados
        if lista_leads:
            print(f"📊 Processando {len(lista_leads)} leads...")
            salvar_excel(lista_leads, nicho, cidade)
            registrar_log(f"SUCESSO: {len(lista_leads)} leads coletados.")
            print(f"✅ Concluído! Verifique a pasta 'data'.")
        else:
            print("❌ Nenhum lead foi encontrado nesta busca.")
            registrar_log("AVISO: Nenhum lead encontrado.")

    except Exception as e:
        erro_msg = f"ERRO CRÍTICO na main: {str(e)}"
        print(f"🔴 {erro_msg}")
        registrar_log(erro_msg)

if __name__ == "__main__":
    # Defina aqui o que você quer buscar
    PROFISSAO = "Contabilidade"
    LOCALIDADE = "São Paulo"
    
    asyncio.run(rodar_automacao(PROFISSAO, LOCALIDADE))