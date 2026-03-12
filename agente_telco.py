import asyncio
from playwright.async_api import async_playwright
from google import genai # Importación de la nueva librería
import os
import datetime

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        # Configuración del navegador (Ya dominada)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 2500}
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Accediendo a la tienda WOM...")
        
        try:
            # Captura de pantalla
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(15) 
            
            path_foto = "captura_wom.png"
            await page.screenshot(path=path_foto, full_page=True)
            print("Captura de pantalla OK.")
            await browser.close()

            # --- NUEVA CONEXIÓN DIRECTA ---
            print("Conectando con la API mediante el nuevo SDK...")
            # Usamos el nuevo cliente
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            
            # Leemos la imagen directamente como bytes
            with open(path_foto, "rb") as f:
                bytes_imagen = f.read()

            print("Analizando datos con Gemini 1.5 Flash...")
            # Llamada directa: evitamos carpetas temporales y errores 404 de ruta
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "Analiza esta imagen de WOM Chile. Extrae los planes de portabilidad en una tabla: Plan, Precio Oferta, Meses de Descuento y Precio Final.",
                    {"mime_type": "image/png", "data": bytes_imagen}
                ]
            )
            
            print("\n" + "="*50)
            print(" RESULTADO DEL BENCHMARK ")
            print("="*50)
            print(response.text)
            print("="*50)

        except Exception as e:
            print(f"ERROR TÉCNICO: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
