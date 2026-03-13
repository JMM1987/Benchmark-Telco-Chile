import asyncio
import os
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

# Configuración de los objetivos
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
        await page.goto(sitio['url'], wait_until="networkidle", timeout=60000)
        await asyncio.sleep(10) # Espera para carga de precios dinámicos
        
        path_foto = f"{sitio['nombre'].lower()}.png"
        await page.screenshot(path=path_foto)
        
        with open(path_foto, "rb") as f:
            img_data = f.read()

        prompt = f"""
        Analiza la imagen de la web de {sitio['nombre']}.
        Extrae los planes de portabilidad principales y sus líneas adicionales.
        
        Debes incluir esta columna obligatoria:
        - Operador: Siempre debe decir '{sitio['nombre']}'
        
        Para cada plan:
        1. Plan: Nombre del plan.
        2. Precio Oferta: Precio portabilidad (meses iniciales).
        3. Precio Normal: Precio después de la oferta.
        4. Línea Adicional: Precio y descuento de líneas extra si aparecen.
        
        Formato requerido: Tabla Markdown. No agregues texto extra fuera de la tabla.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_bytes(data=img_data, mime_type="image/png")
                    ]
                )
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
        
        client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options={'api_version': 'v1'}
        )

        resultados = []
        for sitio in SITIOS:
            resultado = await analizar_operador(browser, sitio, client)
            resultados.append(resultado)
        
        await browser.close()

        print("\n" + "="*60)
        print("   BENCHMARK TELCO CHILE - REPORTE CONSOLIDADO")
        print("="*60 + "\n")
        
        for res in resultados:
            print(res)
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(ejecutar_benchmark())

if __name__ == "__main__":
    asyncio.run(ejecutar())
