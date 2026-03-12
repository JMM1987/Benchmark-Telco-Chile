import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os
import datetime

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Aumentamos el alto de la captura para asegurar que capturemos las líneas adicionales abajo
        context = await browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Accediendo a Portabilidad WOM...")
        await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="networkidle")
        
        # Esperamos a que carguen las "cards" de planes y adicionales
        await asyncio.sleep(8) 
        
        path_foto = "captura_wom_detallada.png"
        await page.screenshot(path=path_foto, full_page=True)
        await browser.close()

        # --- PROCESAMIENTO CON IA ---
        print("Enviando captura a Gemini para análisis financiero detallado...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        foto = genai.upload_file(path_foto)
        
        # Este prompt es mucho más técnico y específico
        prompt = """
        Analiza esta imagen de WOM Chile y extrae los datos para un benchmark de precios profesional.
        Necesito una tabla con las siguientes columnas para cada plan visible:
        
        1. Plan (Nombre/Gigas)
        2. Valor Entrada (Precio con descuento inicial)
        3. Meses de Descuento (Duración de la oferta)
        4. Valor Aterrizaje (Precio final post-descuento)
        5. Precio Línea Adicional (Entrada)
        6. Meses Descuento Adicional
        7. Aterrizaje Línea Adicional
        8. Atributos (Roaming, Apps, etc.)

        Si la información de líneas adicionales no está explícita para un plan, busca los banners inferiores donde WOM suele poner los precios de líneas extra.
        """
        
        response = model.generate_content([prompt, foto])
        
        print("\n=== BENCHMARK DETALLADO WOM PORTABILIDAD ===")
        print(response.text)

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
