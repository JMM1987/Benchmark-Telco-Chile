import asyncio
import os
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
    print(f"\n--- Procesando {sitio['nombre']} ---")
    page = await browser.new_page(viewport={'width': 1920, 'height': 1200})
    
    try:
        # User-Agent para evitar ser bloqueados
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        
        await page.goto(sitio['url'], wait_until="networkidle", timeout=90000)
        
        # Lógica especial para las pestañas de CLARO
        if sitio['nombre'] == "CLARO":
            try:
                print("Cambiando a pestaña 'Líneas Adicionales' en Claro...")
                await page.get_by_role("tab", name="Líneas Adicionales").click()
                await asyncio.sleep(8) 
            except:
                print("No se pudo hacer clic en la pestaña, intentando captura directa.")

        await asyncio.sleep(10) # Espera para que carguen los precios dinámicos
        
        path_foto = f"{sitio['nombre'].lower()}.png"
        await page.screenshot(path=path_foto, full_page=False)
        
        with open(path_foto, "rb") as f:
            img_data = f.read()

        prompt = f"""
        Analiza la imagen de {sitio['nombre']}.
        Extrae los planes de portabilidad y sus líneas adicionales en una tabla Markdown.
        COLUMNAS: Operador (siempre '{sitio['nombre']}'), Plan, Precio Oferta, Precio Normal, Línea Adicional (Precio/Dcto).
        Si un dato no es visible, pon 'N/A'.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", # Confirmado en tus logs anteriores
            contents=[
                types.Content(role="user", parts=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(data=img_data, mime_type="image/png")
                ])
            ]
        )
        return response.text

    except Exception as e:
        return f"Error en {sitio['nombre']}: {str(e)}"
    finally:
        await page.close()

async def ejecutar_benchmark():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'api_version': 'v1'})

        resultados = []
        for sitio in SITIOS:
            res = await analizar_operador(browser, sitio, client)
            resultados.append(res)
        
        await browser.close()
        print("\n" + "="*60 + "\n   REPORTE CONSOLIDADO FINAL\n" + "="*60)
        for r in resultados:
            print(r)

if __name__ == "__main__":
    # CORRECCIÓN CLAVE: El nombre de la función debe coincidir
    asyncio.run(ejecutar_benchmark())
