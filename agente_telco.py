import asyncio
from playwright.async_api import async_playwright
from google import genai
from google.genai import types
import os

async def ejecutar():
    async with async_playwright() as p:
        # 1. Navegación y captura (Esto ya es sólido)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 2500})
        
        print("1. Capturando WOM...")
        try:
            await page.goto("https://store.wom.cl/planes/planes-portabilidad", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(15) 
            await page.screenshot(path="wom.png", full_page=True)
            await browser.close()

            print("2. Conectando a Gemini v1 (Estable)...")
            # FORZAMOS LA VERSIÓN V1 PARA EVITAR EL 404 DE LA BETA
            client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"],
                http_options={'api_version': 'v1'}
            )
            
            with open("wom.png", "rb") as f:
                img_data = f.read()

            # Estructura de mensaje blindada
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text="Analiza la imagen y extrae los planes de portabilidad en una tabla."),
                            types.Part.from_bytes(data=img_data, mime_type="image/png")
                        ]
                    )
                ]
            )

            print("\n=== RESULTADO ===\n")
            print(response.text)

        except Exception as e:
            print(f"ERROR FINAL: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar())
