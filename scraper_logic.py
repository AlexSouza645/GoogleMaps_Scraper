import asyncio
import re
import requests
import urllib3
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

urllib3.disable_warnings()

def extrair_email_site(url):
    """ Tenta buscar o email usando BeautifulSoup de forma mais veloz """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=5, verify=False)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Limpa scripts e styles
            for script in soup(['script', 'style']):
                script.extract()
                
            texto = soup.get_text()
            
            # Procura por Regex no texto visível
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texto)
            
            # Procura em links (href="mailto:")
            for a in soup.find_all('a', href=True):
                if 'mailto:' in a['href']:
                    emails.append(a['href'].replace('mailto:', '').split('?')[0])
                    
            # Limpa e filtra
            validos = [e.strip().lower() for e in set(emails) if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            if validos:
                return validos[0]
    except Exception:
        pass
    return "N/A"

def encurtar_url(url):
    """ Encurta o link gigante do Maps usando a API gratuita do TinyURL """
    try:
        if not url or url == "N/A": return "N/A"
        resp = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=5)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return url # Retorna original se falhar
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
    for local in locais[:5]:                  
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
            
            # 5. Extrai o E-mail (visitando o site via requests+BS4)
            email = "N/A"
            if site and site != "N/A" and site.startswith("http"):
                print(f"   🔍 Buscando e-mail no site: {site}")
                # Roda a função requests de forma assíncrona para não travar o robô do mapa
                email = await asyncio.to_thread(extrair_email_site, site)
                if email != "N/A":
                    print(f"   📧 E-mail encontrado: {email}")
                else:
                    print(f"   ⚠️ Nenhum e-mail visível ou site bloqueado.")
            
            # 6. Pega a URL diretamente do link HTML original
            url_maps = await local.get_attribute("href")
            if url_maps:
                print("   🔗 Encurtando link do Google Maps...")
                link_maps = await asyncio.to_thread(encurtar_url, url_maps)
            else:
                link_maps = "N/A"
            
            # 7. Define a Presença Digital
            presenca = "Sem site" if site == "N/A" else "Com site"
            
            leads.append({
                "Nome": nome,
                "Telefone": telefone,
                "E-mail": email,
                "Site": site,
                "Presença Digital": presenca,
                "Link do Maps": link_maps,
                "Status do Lead": "Novo"
            })
            
            print(f"📍 Coletado: {nome}")
            
        except Exception as e:
            print(f"⚠️ Erro ao processar um item: {e}")
            continue
            
    return leads
