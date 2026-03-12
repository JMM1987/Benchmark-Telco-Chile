import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os
import datetime

# Configuración de la IA con tu llave de GitHub
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

async def ejecutar_agente_visual():
    async with async_playwright() as p:
        # Iniciamos el navegador
        browser = await p.chromium.launch(headless=True)
        
        # DISFRAZ HUMANO: Esto evita que la página se quede cargando eternamente
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 2000}
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Accediendo a WOM Portabilidad...")
        
        try:
            # 'commit' hace que no espere a la publicidad o rastreadores lentos
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="commit", timeout=60000)
            
            # Esperamos 15 segundos fijos para que los precios aparezcan en pantalla
            print("Esperando 15 segundos para que carguen los precios...")
            await asyncio.sleep(15) 
            
            path_foto = "captura_wom.png"
            await page.screenshot(path=path_foto, full_page=True)
            print("Captura de pantalla realizada con éxito.")
            await browser.close()

            # --- PROCESAMIENTO CON IA ---
            print("Enviando captura a Gemini para análisis detallado...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Subimos la imagen a la nube de Google para que la IA la vea
            foto_ia = genai.upload_file(path_foto)
            
            prompt = """
            Analiza esta imagen de la tienda WOM Chile y extrae los datos de los planes de PORTABILIDAD.
            Necesito una tabla con:
            1. Plan (Nombre/Gigas)
            2. Valor Entrada (Precio con descuento)
            3. Meses de Descuento (Duración de la oferta inicial)
            4. Valor Aterrizaje (Precio final después del descuento)
            5. Línea Adicional (Precio entrada, meses y precio final)
            6. Atributos (Roaming, redes sociales libres, etc.)
            
            Si no encuentras el valor de aterrizaje, indica 'No visible'.
            """
            
            response = model.generate_content([prompt, foto_ia])
            
            print("\n" + "="*50)
            print(" RESULTADOS DEL BENCHMARK PROFESIONAL ")
            print("="*50)
            print(response.text)
            print("="*50)

        except Exception as e:
            print(f"Error detectado durante la ejecución: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_agente_visual())
