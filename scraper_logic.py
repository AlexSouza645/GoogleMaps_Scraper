from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from utils import lead_existe
from tenacity import retry, wait_fixed, stop_after_attempt

import asyncio
import re
import requests
import warnings

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def extrair_contatos_site(url):
    """ Tenta buscar o email e redes sociais usando BeautifulSoup de forma mais veloz """
    contatos = {"Email": "N/A", "Instagram": "N/A", "Facebook": "N/A", "LinkedIn": "N/A"}
    try:
        # Suprime temporariamente o warning de SSL Inseguro apenas nesta requisição
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', requests.packages.urllib3.exceptions.InsecureRequestWarning)
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
            
            # Procura em links(href e redes)
            for a in soup.find_all('a', href=True):
                href = a['href'].lower()
                if 'mailto:' in href:
                    emails.append(a['href'].replace('mailto:', '').split('?')[0])
                elif 'instagram.com' in href:
                    contatos['Instagram'] = a['href']
                elif 'facebook.com' in href:
                    contatos['Facebook'] = a['href']
                elif 'linkedin.com' in href:
                    contatos['LinkedIn'] = a['href']
                    
            # Limpa e filtra Email
            validos = [e.strip().lower() for e in set(emails) if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            if validos:
                contatos['Email'] = validos[0]
                
    except Exception:
        pass
    return contatos

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
async def iniciar_busca(nicho, cidade):
    """
    Inicia o navegador e faz a pesquisa inicial.
    """
    pw = await async_playwright().start()
    # Para executáveis (PyInstaller), é melhor usar o Chrome ou Edge já instalados
    # no computador do usuário, em vez de embutir um navegador gigante.
    try:
        browser = await pw.chromium.launch(channel="chrome", headless=False)
    except Exception:
        browser = await pw.chromium.launch(channel="msedge", headless=False)
        
    page = await browser.new_page()
    
    # Formata a URL de busca do Google Maps
    query = f"{nicho} em {cidade}"
    await page.goto(f"https://www.google.com/maps/search/{query}")
    
    # Espera o carregamento inicial
    await page.wait_for_timeout(3000)
    return pw, browser, page

async def extrair_detalhes(page, plano="ENTERPRISE", limite=20):
    """
    Percorre a lista de resultados e extrai os dados.
    """
    leads = []
    
    # Seleciona os containers dos resultados (os cards na lateral esquerda)
    await page.wait_for_selector('//a[contains(@href, "maps/place")]')
    
    # Vamos pegar os links de todos os lugares visíveis
    locais = await page.locator('//a[contains(@href, "maps/place")]').all()
    
    # Limitamos pela variável customizada pelo usuário
    for local in locais[:limite]:                  
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
            
            # Verifica Deduplicação APENAS NO PLANO ENTERPRISE
            if plano == "ENTERPRISE":
                if lead_existe(nome, telefone):
                    continue
                
            site = "N/A"
            email = "N/A"
            instagram = "N/A"
            facebook = "N/A"
            linkedin = "N/A"
            status_site = "Sem Site"
            presenca = "Sem site"
            prioridade = "N/A"
            
            # No Plano START, pula extração lógicas complexas e site.
            if plano in ["PRO", "ENTERPRISE"]:
                # 4. Extrai o Site
                site_seletor = page.locator('//a[@data-item-id="authority"]')
                site = await site_seletor.get_attribute("href") if await site_seletor.count() > 0 else "N/A"
                presenca = "Sem site" if site == "N/A" else "Com site"
            
                if plano == "ENTERPRISE":
                    # 5. Extrai Múltiplos Contatos e Valida o Site
                    if site and site != "N/A" and site.startswith("http"):
                        print(f"   🔍 Analisando site: {site}")
                        try:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            resp = requests.get(site, headers=headers, timeout=5, verify=False)
                            if resp.status_code == 200:
                                status_site = "Ativo (200 OK)"
                                dados_site = await asyncio.to_thread(extrair_contatos_site, site)
                                email = dados_site["Email"]
                                instagram = dados_site["Instagram"]
                                facebook = dados_site["Facebook"]
                                linkedin = dados_site["LinkedIn"]
                            else:
                                status_site = f"Erro {resp.status_code}"
                        except Exception:
                            status_site = "Fora do Ar / Timeout"
                        
                        if email != "N/A" or instagram != "N/A":
                            print(f"   📧 Contatos ou Redes Sociais encontradas!")
                        else:
                            if status_site == "Ativo (200 OK)":
                                print(f"   ⚠️ Site ativo, mas sem contato direto visualizado.")
                            else:
                                print(f"   🚨 Site indisponível ({status_site}).")
                    
                    # Cálculo de Prioridade (Enterprise)
                    prioridade = "Baixa"
                    if telefone != "N/A" and status_site == "Ativo (200 OK)" and email != "N/A":
                        prioridade = "Alta (Quente)"
                    elif telefone != "N/A" and (site == "N/A" or status_site != "Ativo (200 OK)"):
                        prioridade = "Média (Morno)"
                    elif telefone != "N/A" and status_site == "Ativo (200 OK)" and email == "N/A":
                        prioridade = "Média (Morno)"
            
            # 6. Pega a URL diretamente do link HTML original (Em todos os planos)
            url_maps = await local.get_attribute("href")
            link_maps = "N/A"
            if url_maps:
                # Opcional: Só encurtar link no PRO ou ENTERPRISE para poupar chamadas de API grátis? Vamos deixar pra todos.
                print("   🔗 Encurtando link do Google Maps...")
                link_maps = await asyncio.to_thread(encurtar_url, url_maps)
            
            leads.append({
                "Nome": nome,
                "Prioridade": prioridade,
                "Telefone": telefone,
                "E-mail": email,
                "Instagram": instagram,
                "Facebook": facebook,
                "LinkedIn": linkedin,
                "Site": site,
                "Status do Site": status_site,
                "Presença Digital": presenca,
                "Link do Maps": link_maps,
                "Status do Lead": "Novo"
            })
            
            print(f"📍 Coletado: {nome}")
            
        except Exception as e:
            print(f"⚠️ Erro ao processar um item: {e}")
            continue
            
    return leads
