import asyncio
from playwright.async_api import async_playwright

async def iniciar_busca(nicho, cidade):
    """
    Inicia o navegador e faz a pesquisa inicial.
    """
    pw = await async_playwright().start()
    # Lançamos o Chromium. headless=False permite que você veja o robô trabalhando.
    browser = await pw.chromium.launch(headless=False) 
    page = await browser.new_page()
    
    # Formata a URL de busca do Google Maps
    query = f"{nicho} em {cidade}"
    await page.goto(f"https://www.google.com/maps/search/{query}")
    
    # Espera o carregamento inicial
    await page.wait_for_timeout(3000)
    return browser, page

async def extrair_detalhes(page):
    """
    Percorre a lista de resultados e extrai os dados.
    """
    leads = []
    
    # Seleciona os containers dos resultados (os cards na lateral esquerda)
    # O seletor '.nv261' ou similares podem mudar, por isso usamos o locator robusto
    await page.wait_for_selector('//a[contains(@href, "maps/place")]')
    
    # Vamos pegar os links de todos os lugares visíveis
    locais = await page.locator('//a[contains(@href, "maps/place")]').all()
    
    # Limitamos aos 10 primeiros para o teste inicial
    for local in locais[:10]:
        try:
            # 1. Clica no local para abrir os detalhes na direita
            await local.click()
            await page.wait_for_timeout(2000) # Espera o painel lateral carregar
            
            # 2. Extrai o Nome (geralmente dentro de um h1)
            nome_seletor = page.locator('//h1[contains(@class, "DUwDvf")]')
            nome = await nome_seletor.inner_text() if await nome_seletor.count() > 0 else "N/A"
            
            # 3. Extrai o Telefone (procura pelo ícone de telefone ou link tel:)
            fone_seletor = page.locator('//button[contains(@data-item-id, "phone:tel:")]')
            telefone = await fone_seletor.get_attribute("data-item-id") if await fone_seletor.count() > 0 else "N/A"
            
            # 4. Extrai o Site
            site_seletor = page.locator('//a[@data-item-id="authority"]')
            site = await site_seletor.get_attribute("href") if await site_seletor.count() > 0 else "N/A"
            
            leads.append({
                "Nome": nome,
                "Telefone": telefone,
                "Site": site
            })
            
            print(f"📍 Coletado: {nome}")
            
        except Exception as e:
            print(f"⚠️ Erro ao processar um item: {e}")
            continue
            
    return leads
    