import asyncio
import os
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

async def ejecutar():
    async with async_playwright() as p:
        print("1. Iniciando navegador (Full HD) y capturando WOM...")
        # Aumentamos el ancho para que los 4 planes respiren y se vean claros
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(15) 
            
            path_foto = "wom_full.png"
            await page.screenshot(path=path_foto, full_page=False) # Captura lo que se ve en pantalla
            await browser.close()
            print("Captura panorámica guardada.")

            client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"],
                http_options={'api_version': 'v1'}
            )

            with open(path_foto, "rb") as f:
                img_data = f.read()

            modelo_confirmado = "gemini-2.5-flash"
            print(f"2. Analizando con {modelo_confirmado} (Prompt Estricto)...")

            # PROMPT REFORZADO: Obligamos a contar y a no omitir nada
            prompt_estricto = """
            Analiza la imagen minuciosamente de izquierda a derecha. 
            Debes extraer los CUATRO (4) planes de portabilidad que aparecen en la parrilla principal. 
            No omitas ninguno, especialmente los de los extremos.
            
            Para cada plan, entrega:
            - Nombre exacto del Plan.
            - Precio Oferta (el más grande).
            - Precio Normal (el que aparece después de 'luego').
            - Meses de Descuento.
            - Beneficios extra (Apps, Roaming, etc.).
            
            Presenta todo en una tabla Markdown limpia.
            """

            response = client.models.generate_content(
                model=modelo_confirmado,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt_estricto),
                            types.Part.from_bytes(data=img_data, mime_type="image/png")
                        ]
                    )
                ]
            )

            print("\n" + "="*40)
            print("   BENCHMARK COMPLETO (4 PLANES)")
            print("="*40 + "\n")
            print(response.text)

        except Exception as e:
            print(f"\n[!] ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar())
