import asyncio
import os
import csv
import re
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

SITIOS = [
    {"nombre": "WOM", "url": "https://store.wom.cl/planes/planes-portabilidad"},
    {"nombre": "CLARO", "url": "https://www.clarochile.cl/personas/servicios/servicios-moviles/planes-moviles/"},
    {"nombre": "ENTEL", "url": "https://www.entel.cl/ofertas/planes-moviles"},
    {"nombre": "MOVISTAR", "url": "https://ww2.movistar.cl/movil/planes-portabilidad/"}
]

async def analizar_operador(browser, sitio, client):
    print(f"--- Procesando {sitio['nombre']} ---")
    page = await browser.new_page(viewport={'width': 1920, 'height': 1200})
    
    try:
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"})
        await page.goto(sitio['url'], wait_until="networkidle", timeout=90000)
        
        if sitio['nombre'] == "CLARO":
            try:
                await page.get_by_role("tab", name="Líneas Adicionales").click()
                await asyncio.sleep(8) 
            except: pass

        await asyncio.sleep(10)
        path_foto = f"{sitio['nombre'].lower()}.png"
        await page.screenshot(path=path_foto)
        
        with open(path_foto, "rb") as f:
            img_data = f.read()

        # Prompt optimizado para que la IA devuelva solo las filas de datos
        prompt = f"""
        Analiza la imagen de {sitio['nombre']}.
        Extrae los datos de portabilidad y genera UNICAMENTE las filas de una tabla CSV usando el separador '|'.
        Formato: {sitio['nombre']}|Nombre del Plan|Precio Oferta|Precio Normal|Detalle Adicional
        No incluyas encabezados ni texto explicativo. Solo las filas de datos.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Content(role="user", parts=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=img_data, mime_type="image/png")
            ])]
        )
        return response.text

    except Exception as e:
        print(f"Error en {sitio['nombre']}: {e}")
        return ""
    finally:
        await page.close()

async def ejecutar_benchmark():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'api_version': 'v1'})

        todas_las_filas = []
        for sitio in SITIOS:
            resultado_raw = await analizar_operador(browser, sitio, client)
            # Limpiamos el output de la IA para obtener solo las líneas con datos
            filas = [f.strip().split('|') for f in resultado_raw.split('\n') if '|' in f and 'Operador' not in f]
            todas_las_filas.extend(filas)
        
        await browser.close()

        # Guardar en archivo CSV
        archivo_csv = "benchmark_telco.csv"
        encabezados = ["Operador", "Plan", "Precio Oferta", "Precio Normal", "Línea Adicional"]
        
        with open(archivo_csv, mode='w', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerow(encabezados)
            escritor.writerows(todas_las_filas)

        print(f"\n✅ Proceso terminado. Archivo '{archivo_csv}' generado con {len(todas_las_filas)} planes.")

if __name__ == "__main__":
    asyncio.run(ejecutar_benchmark())
