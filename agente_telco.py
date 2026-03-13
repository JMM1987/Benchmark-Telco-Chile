import asyncio
import os
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

async def ejecutar():
    async with async_playwright() as p:
        # 1. Configuración de Navegador y Captura
        print("1. Iniciando navegador y capturando WOM...")
        browser = await p.chromium.launch(headless=True)
        # Seteamos un user-agent real para evitar bloqueos
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.set_viewport_size({'width': 1280, 'height': 2000})
        
        try:
            # Vamos a la URL
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="networkidle", timeout=90000)
            
            # Espera extra para asegurar que carguen los elementos dinámicos
            await asyncio.sleep(10) 
            
            # Guardamos la captura
            await page.screenshot(path="wom.png", full_page=True)
            print("Captura guardada como wom.png")
            await browser.close()

            # 2. Conexión a Gemini 1.5 Flash
            print("2. Conectando a Gemini 1.5 Flash...")
            
            # Inicializamos el cliente sin forzar api_version (deja que la librería decida)
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            
            # Leemos la imagen
            with open("wom.png", "rb") as f:
                img_data = f.read()

            # Llamada al modelo con el nombre completo para evitar 404
            response = client.models.generate_content(
                model="models/gemini-1.5-flash",
                contents=[
                    types.Part.from_text(text="Analiza esta imagen de planes de telefonía de WOM Chile. Extrae todos los planes disponibles y estructúralos en una tabla de Markdown que incluya: Nombre del plan, Gigas, Precio y si incluye redes sociales libres."),
                    types.Part.from_bytes(data=img_data, mime_type="image/png")
                ]
            )

            print("\n=== DATOS EXTRAÍDOS ===\n")
            if response.text:
                print(response.text)
            else:
                print("No se pudo generar texto de la imagen.")

        except Exception as e:
            print(f"ERROR DURANTE LA EJECUCIÓN: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar())
