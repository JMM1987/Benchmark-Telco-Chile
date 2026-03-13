import asyncio
import os
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

async def ejecutar():
    async with async_playwright() as p:
        # 1. Captura de pantalla
        print("1. Iniciando navegador y capturando WOM...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 2500})
        
        try:
            # Navegamos a la URL
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="domcontentloaded", timeout=60000)
            # Espera estratégica para que carguen los precios dinámicos
            await asyncio.sleep(15) 
            
            path_foto = "wom.png"
            await page.screenshot(path=path_foto, full_page=True)
            await browser.close()
            print("Captura guardada exitosamente.")

            # 2. Configuración del Cliente Gemini
            # Forzamos la versión v1 que es compatible con los modelos 2.x detectados
            client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"],
                http_options={'api_version': 'v1'}
            )

            # 3. Preparación de la imagen
            with open(path_foto, "rb") as f:
                img_data = f.read()

            # 4. Análisis con el modelo detectado en tu log (Gemini 2.5 Flash)
            modelo_confirmado = "gemini-2.5-flash"
            print(f"2. Enviando imagen a {modelo_confirmado}...")

            response = client.models.generate_content(
                model=modelo_confirmado,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text="Analiza la imagen y extrae los planes de portabilidad en una tabla con: Plan, Precio Oferta, Precio Normal y Meses de Descuento."),
                            types.Part.from_bytes(data=img_data, mime_type="image/png")
                        ]
                    )
                ]
            )

            print("\n" + "="*30)
            print("   RESULTADO DEL ANÁLISIS")
            print("="*30 + "\n")
            print(response.text)

        except Exception as e:
            print(f"\n[!] ERROR: {str(e)}")
            # En caso de error, intentamos listar de nuevo para ver qué pasó
            try:
                print("Re-verificando modelos disponibles...")
                for m in client.models.list():
                    print(f"Disponible: {m.name}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(ejecutar())
