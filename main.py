import asyncio
from scraper_logic import iniciar_busca, extrair_detalhes
from utils import salvar_excel, registrar_log
import threading
import tkinter as tk
from tkinter import ttk, messagebox

async def rodar_automacao(nicho, cidade, plano="ENTERPRISE", limite=20):
    """
    Função principal que coordena o fluxo do robô.
    """
    try:
        registrar_log(f"--- NOVA EXECUÇÃO: {nicho} em {cidade} | PLANO: {plano} | LIMITE: {limite} ---")
        print(f"🚀 Iniciando busca por '{nicho}' em '{cidade}' (Plano {plano}, {limite} leads)...")

        # 1. Abre o navegador e faz a pesquisa
        pw, browser, page = await iniciar_busca(nicho, cidade)

        # 2. Extrai os dados dos leads
        print("🕵️  Extraindo dados dos estabelecimentos...")
        lista_leads = await extrair_detalhes(page, plano=plano, limite=limite)

        # 3. Fecha o navegador (Importante para liberar memória!)
        await browser.close()
        await pw.stop()

        # 4. Processa e salva os dados se houver resultados
        if lista_leads:
            print(f"📊 Processando {len(lista_leads)} leads...")
            salvar_excel(lista_leads, nicho, cidade, plano=plano)
            registrar_log(f"SUCESSO: {len(lista_leads)} leads coletados.")
            print(f"✅ Concluído! Verifique a pasta 'data'.")
        else:
            print("❌ Nenhum lead foi encontrado nesta busca.")
            registrar_log("AVISO: Nenhum lead encontrado.")

    except Exception as e:
        erro_msg = f"ERRO CRÍTICO na main: {str(e)}"
        print(f"🔴 {erro_msg}")
        registrar_log(erro_msg)

def disparar_robo():
    nicho = entry_nicho.get().strip()
    cidade = entry_cidade.get().strip()
    limite = entry_limite.get().strip()
    plano_nome = combo_plano.get().split(" - ")[0]
    
    if not nicho or not cidade:
        messagebox.showerror("Erro", "Você precisa informar o nicho e a cidade!")
        return
        
    try:
        limite = int(limite)
    except ValueError:
        limite = 20
        
    btn_iniciar.config(state="disabled", text="Rodando...")
    
    # Roda em thread separada para não travar a UI
    def iniciar_async():
        try:
            asyncio.run(rodar_automacao(nicho, cidade, plano=plano_nome, limite=limite))
            messagebox.showinfo("Sucesso", "Extração concluída com sucesso!\nVerifique a pasta 'data'.")
        except Exception as e:
            messagebox.showerror("Erro Crítico", str(e))
        finally:
            btn_iniciar.config(state="normal", text="Iniciar Robô")
            
    threading.Thread(target=iniciar_async, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Google Maps Scraper Pro")
    root.geometry("450x350")
    
    ttk.Label(root, text="Robô de Vendas Google Maps", font=("Helvetica", 14, "bold")).pack(pady=10)
    
    # Formulário
    frame = ttk.Frame(root)
    frame.pack(pady=10, padx=20, fill="x")
    
    ttk.Label(frame, text="Nicho/Profissão:").grid(row=0, column=0, sticky="w", pady=5)
    entry_nicho = ttk.Entry(frame, width=30)
    entry_nicho.grid(row=0, column=1, pady=5)
    
    ttk.Label(frame, text="Cidade/Estado:").grid(row=1, column=0, sticky="w", pady=5)
    entry_cidade = ttk.Entry(frame, width=30)
    entry_cidade.grid(row=1, column=1, pady=5)
    
    ttk.Label(frame, text="Limite de Leads:").grid(row=2, column=0, sticky="w", pady=5)
    entry_limite = ttk.Entry(frame, width=30)
    entry_limite.insert(0, "20")
    entry_limite.grid(row=2, column=1, pady=5)
    
    ttk.Label(frame, text="Plano de Extração:").grid(row=3, column=0, sticky="w", pady=5)
    combo_plano = ttk.Combobox(frame, values=["START - Básico", "PRO - Intermediário", "ENTERPRISE - Completo"], state="readonly", width=27)
    combo_plano.current(2)
    combo_plano.grid(row=3, column=1, pady=5)
    
    btn_iniciar = ttk.Button(root, text="Iniciar Robô", command=disparar_robo)
    btn_iniciar.pack(pady=20)
    
    root.mainloop()