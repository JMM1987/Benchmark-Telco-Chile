import asyncio
import os
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

async def ejecutar():
    async with async_playwright() as p:
        print("1. Capturando WOM con foco en detalles inferiores...")
        browser = await p.chromium.launch(headless=True)
        # Usamos una altura mayor (1200) para asegurar que el pie de página de los planes sea visible
        page = await browser.new_page(viewport={'width': 1920, 'height': 1200})
        
        try:
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(15) 
            
            path_foto = "wom_completo.png"
            await page.screenshot(path=path_foto)
            await browser.close()

            client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"],
                http_options={'api_version': 'v1'}
            )

            with open(path_foto, "rb") as f:
                img_data = f.read()

            modelo_confirmado = "gemini-2.5-flash"
            print(f"2. Analizando Planes + Líneas Adicionales con {modelo_confirmado}...")

            # PROMPT ULTRA-DETALLADO
            prompt_final = """
            Analiza la imagen y extrae la información de los 4 planes de portabilidad.
            Para cada plan, debes capturar DOS niveles de información:
            
            1. NIVEL PLAN PRINCIPAL: Nombre, Precio Oferta, Precio Normal y Beneficios.
            2. NIVEL LÍNEAS ADICIONALES: Justo debajo de cada plan hay un recuadro blanco que dice 'Suma líneas adicionales'. Extrae el precio por línea, el porcentaje de descuento y el precio normal que aparece ahí.
            
            Formato de salida requerido (Tabla):
            | Plan | Precio Portabilidad | Línea Adicional (Precio/Dcto) | Precio Normal Adicional |
            | :--- | :--- | :--- | :--- |
            """

            response = client.models.generate_content(
                model=modelo_confirmado,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt_final),
                            types.Part.from_bytes(data=img_data, mime_type="image/png")
                        ]
                    )
                ]
            )

            print("\n" + "="*50)
            print("   BENCHMARK WOM: PLANES + ADICIONALES")
            print("="*50 + "\n")
            print(response.text)

        except Exception as e:
            print(f"\n[!] ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar())
