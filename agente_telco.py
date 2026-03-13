import asyncio
from playwright.async_api import async_playwright
from google import genai
from google.genai import types
import os

async def ejecutar():
    async with async_playwright() as p:
        # 1. Captura (Sin cambios, ya que funciona)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 2500})
        
        print("1. Capturando WOM...")
        try:
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="domcontentloaded")
            await asyncio.sleep(12) 
            await page.screenshot(path="wom.png", full_page=True)
            await browser.close()

            print("2. Configurando Cliente (v1 estable)...")
            client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"],
                http_options={'api_version': 'v1'}
            )

            # --- BLOQUE DE DIAGNÓSTICO ---
            print("Verificando modelos disponibles para tu cuenta...")
            modelos_validos = []
            for m in client.models.list():
                modelos_validos.append(m.name)
            print(f"Modelos detectados: {modelos_validos}")
            # -----------------------------

            with open("wom.png", "rb") as f:
                img_data = f.read()

            # PROBAMOS CON EL MODELO PRO (Más robusto)
            modelo_a_usar = "gemini-1.5-pro" 
            print(f"3. Intentando análisis con: {modelo_a_usar}")
            
            response = client.models.generate_content(
                model=modelo_a_usar,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text="Extrae los planes de portabilidad en una tabla: Plan, Precio, y Meses de Descuento."),
                            types.Part.from_bytes(data=img_data, mime_type="image/png")
                        ]
                    )
                ]
            )

            print("\n=== RESULTADO DEL MODELO PRO ===\n")
            print(response.text)

        except Exception as e:
            print(f"\n¡ALERTA! El error persiste: {str(e)}")
            print("Si el error es 404, revisa la lista de 'Modelos detectados' más arriba para ver cuál podemos usar.")

if __name__ == "__main__":
    asyncio.run(ejecutar())
if __name__ == "__main__":
    asyncio.run(ejecutar())
