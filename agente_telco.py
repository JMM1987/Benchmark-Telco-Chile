import asyncio
from playwright.async_api import async_playwright
import datetime

async def scraping_wom():
    async with async_playwright() as p:
        # Abrimos un navegador invisible
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"[{datetime.datetime.now()}] Entrando a WOM Chile...")
        
        # Vamos a la página de planes
        await page.goto("https://www.wom.cl/plan-movil/", wait_until="networkidle")
        
        # Buscamos el precio del primer plan que aparezca
        # Nota: Los 'selectores' (h2, span) pueden cambiar si la web se actualiza
        try:
            nombre_plan = await page.inner_text("h2") # Título del plan
            precio = await page.inner_text(".price")  # Clase donde suele estar el precio
            
            print(f"RESULTADO: {nombre_plan.strip()} a un precio de {precio.strip()}")
        except Exception as e:
            print(f"Error al encontrar el dato: {e}")
            # Si falla, tomamos una foto para ver qué pasó
            await page.screenshot(path="error_wom.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scraping_wom())
