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
        # Ventana para capturar todo el scroll
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 2000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Iniciando captura en WOM Portabilidad...")
        
        try:
            # Usamos una URL que suele ser más estable para bots
            await page.goto("https://www.wom.cl/portabilidad/", wait_until="networkidle", timeout=90000)
            await asyncio.sleep(10) # Tiempo extra para carga de precios
            
            path_foto = "captura_wom.png"
            await page.screenshot(path=path_foto, full_page=True)
            await browser.close()

            # Análisis con Gemini (Nombre de modelo corregido)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Subir archivo
            print("Subiendo captura a Gemini...")
            foto_upload = genai.upload_file(path=path_foto)
            
            prompt = """
            Analiza esta imagen de WOM Chile. Extrae los planes de portabilidad en una tabla:
            Plan | Precio Inicial | Meses Descuento | Precio Final | Adicionales (Precio/Aterrizaje) | Atributos
            """
            
            response = model.generate_content([prompt, foto_upload])
            
            print("\n" + "="*40)
            print(" RESULTADOS DEL BENCHMARK ")
            print("="*40)
            print(response.text)
            
        except Exception as e:
            print(f"Error detectado: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
