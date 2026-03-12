import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os
import datetime

# Configuración de la IA
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Ventana alta para capturar planes y banners de adicionales abajo
        context = await browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Iniciando captura en WOM Portabilidad...")
        
        try:
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(8) # Tiempo para que carguen los precios dinámicos
            
            path_foto = "captura_wom.png"
            await page.screenshot(path=path_foto, full_page=True)
            await browser.close()

            # Análisis con Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            foto = genai.upload_file(path_foto)
            
            prompt = """
            Analiza esta imagen de WOM Chile. Necesito un benchmark detallado:
            Para cada plan de portabilidad identifica:
            1. Nombre del Plan y Gigas.
            2. Valor de Entrada (Precio inicial).
            3. Meses de Descuento (¿Cuánto dura el precio inicial?).
            4. Valor de Aterrizaje (Precio final cuando acaba el descuento).
            5. Línea Adicional: Precio entrada, meses de descuento y precio de aterrizaje.
            6. Atributos clave (Apps libres, Roaming, etc).
            
            Presenta la información en una tabla clara.
            """
            
            response = model.generate_content([prompt, foto])
            
            print("\n" + "="*40)
            print(" RESULTADOS DEL BENCHMARK (IA) ")
            print("="*40)
            print(response.text)
            
        except Exception as e:
            print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
