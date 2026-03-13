import asyncio
import os
import csv
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
        await page.goto(sitio['url'], wait_until="networkidle", timeout=90000)
        
        if sitio['nombre'] == "CLARO":
            try:
                # Resolvemos el problema de la pestaña detectado anteriormente
                await page.get_by_role("tab", name="Líneas Adicionales").click()
                await asyncio.sleep(5) 
            except: pass

        await asyncio.sleep(5)
        path_foto = f"{sitio['nombre'].lower()}.png"
        await page.screenshot(path=path_foto)
        
        with open(path_foto, "rb") as f:
            img_data = f.read()

        prompt = f"Extrae los planes de {sitio['nombre']} en formato CSV usando '|'. Solo datos: Operador|Plan|Precio Oferta|Precio Normal|Línea Adicional"

        # Implementamos un reintento simple si falla por cuota
        for intento in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash", # Modelo detectado en tus logs
                    contents=[types.Part.from_bytes(data=img_data, mime_type="image/png"), prompt]
                )
                return response.text if response.text else ""
            except Exception as e:
                if "429" in str(e):
                    espera = (intento + 1) * 20
                    print(f"⚠️ Cuota excedida para {sitio['nombre']}. Reintentando en {espera}s...")
                    await asyncio.sleep(espera)
                else:
                    raise e
        return ""

    except Exception as e:
        print(f"❌ Error final en {sitio['nombre']}: {e}")
        return ""
    finally:
        await page.close()

async def ejecutar_benchmark():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'api_version': 'v1'})

        todas_las_filas = []
        for sitio in SITIOS:
            resultado_raw = await analizar_operador(browser, sitio, client)
            
            # Validación para evitar el AttributeError: 'NoneType' detectado
            if resultado_raw:
                filas = [f.strip().split('|') for f in resultado_raw.split('\n') if '|' in f and 'Operador' not in f]
                todas_las_filas.extend(filas)
            
            # Pausa obligatoria de 30 segundos entre sitios para resetear la cuota TPM
            print("Pausando 30s para respetar límites de API...")
            await asyncio.sleep(30)

        await browser.close()

        # Generación del archivo CSV consolidado
        with open('benchmark_planes.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["Operador", "Plan", "Precio Oferta", "Precio Normal", "Línea Adicional"])
            writer.writerows(todas_las_filas)

        print(f"\n✅ Proceso completado. Archivo 'benchmark_planes.csv' generado.")

if __name__ == "__main__":
    asyncio.run(ejecutar_benchmark())
