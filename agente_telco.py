import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os
import datetime

# CONFIGURACIÓN ROBUSTA
api_key = os.getenv("GEMINI_API_KEY")
# Forzamos la configuración para evitar el error 404
genai.configure(api_key=api_key)

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 2500}
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Accediendo a WOM Portabilidad...")
        
        try:
            # Ir a la página
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="domcontentloaded", timeout=60000)
            print("Esperando 15 segundos para renderizado...")
            await asyncio.sleep(15) 
            
            path_foto = "captura_wom.png"
            await page.screenshot(path=path_foto, full_page=True)
            print("Captura de pantalla realizada con éxito.")
            await browser.close()

            # --- PROCESAMIENTO CON IA ---
            print("Enviando captura a Gemini...")
            
            # Subir la imagen
            sample_file = genai.upload_file(path=path_foto, display_name="Captura WOM")
            
            # Elegir el modelo (esta sintaxis es la más compatible)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = """
            Analiza esta imagen de WOM Chile y genera una tabla con:
            Plan | Precio Inicial | Meses Descuento | Precio Final | Adicionales | Atributos
            """
            
            # Generar contenido
            response = model.generate_content([prompt, sample_file])
            
            print("\n" + "="*50)
            print(" RESULTADOS DEL BENCHMARK ")
            print("="*50)
            print(response.text)
            print("="*50)

        except Exception as e:
            # Si hay un error, lo imprimimos detalladamente para saber qué falló
            print(f"ERROR DETALLADO: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
