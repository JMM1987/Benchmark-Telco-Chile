import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os

# 1. Configuración ultra-simple
# No añadimos parámetros extra para que Google use sus valores por defecto
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = await context.new_page()

        print("Accediendo a WOM...")
        try:
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="domcontentloaded")
            await asyncio.sleep(10)
            
            path_foto = "captura.png"
            await page.screenshot(path=path_foto, full_page=True)
            print("Captura de pantalla OK.")
            await browser.close()

            # 2. SELECCIÓN DE MODELO SEGURA
            # Usamos solo el nombre del modelo, sin prefijos de 'models/'
            model = genai.GenerativeModel('gemini-1.5-flash')

            # 3. SUBIDA Y ANÁLISIS
            print("Enviando a Gemini...")
            # Subimos el archivo
            img_file = genai.upload_file(path=path_foto)
            
            # Pedimos el contenido
            response = model.generate_content([
                "Genera una tabla con los planes de portabilidad de la imagen, incluyendo precio de oferta y meses de descuento.",
                img_file
            ])
            
            print("\n=== RESULTADOS DEL AGENTE ===")
            print(response.text)

        except Exception as e:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
