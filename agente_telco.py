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
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Accediendo a WOM...")
        await page.goto("https://www.wom.cl/planes/", wait_until="networkidle")
        await asyncio.sleep(5) # Esperamos que carguen los elementos visuales
        
        path_foto = "captura_wom.png"
        await page.screenshot(path=path_foto)
        await browser.close()

        # --- PROCESAMIENTO CON IA ---
        print("Enviando captura a Gemini para análisis visual...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Subimos la imagen
        foto = genai.upload_file(path_foto)
        
        prompt = """
        Analiza esta imagen de planes de telefonía de WOM Chile.
        Extrae la información y entrégamela EXCLUSIVAMENTE en una tabla con estas columnas:
        Empresa | Producto | Atributo Clave (Gigas) | Precio Oferta | Precio Normal | Condición
        """
        
        response = model.generate_content([prompt, foto])
        
        print("\n=== BENCHMARK GENERADO POR IA ===")
        print(response.text)

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
