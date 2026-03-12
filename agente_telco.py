import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os
import datetime

# Conectamos con la clave que guardaste en GitHub
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        # Lanzamos el navegador
        browser = await p.chromium.launch(headless=True)
        # Ajustamos el tamaño de la ventana para ver todos los planes
        context = await browser.new_context(viewport={'width': 1280, 'height': 1600})
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Accediendo a Portabilidad WOM...")
        
        # URL PARAMETRIZADA AQUÍ:
        await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="networkidle")
        
        # Esperamos un poco extra para que los precios carguen (a veces WOM es lenta)
        await asyncio.sleep(7) 
        
        path_foto = "captura_wom_portabilidad.png"
        await page.screenshot(path=path_foto, full_page=True)
        await browser.close()

        # --- PROCESAMIENTO CON IA ---
        print("Enviando captura a Gemini para análisis visual...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Subimos la imagen a la IA
        foto = genai.upload_file(path_foto)
        
        prompt = """
        Analiza esta imagen de la tienda WOM Chile.
        Busca los cuadros de planes de PORTABILIDAD.
        Extrae la información y entrégamela en una tabla con:
        Empresa | Plan (Gigas) | Precio Oferta | Precio Normal | Atributo Diferenciador (ej: Roaming, Apps Libres)
        """
        
        response = model.generate_content([prompt, foto])
        
        print("\n=== BENCHMARK PORTABILIDAD WOM ===")
        print(response.text)

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
