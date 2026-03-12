import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os
import datetime

# Configuración técnica
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 2500}
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Accediendo a WOM...")
        
        try:
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(15) 
            
            path_foto = "captura_wom.png"
            await page.screenshot(path=path_foto, full_page=True)
            print("Captura de pantalla OK.")
            await browser.close()

            # --- LLAMADA A LA IA (Sintaxis blindada) ---
            print("Enviando a Gemini...")
            
            # Subir archivo
            file_uploaded = genai.upload_file(path=path_foto)
            
            # Usamos el identificador de modelo más básico y compatible
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = "Analiza los planes de portabilidad de la imagen y entrégalos en una tabla con Precios y Meses de Descuento."
            
            # Forzamos la generación
            response = model.generate_content([prompt, file_uploaded])
            
            print("\n=== RESULTADOS ===")
            print(response.text)

        except Exception as e:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
