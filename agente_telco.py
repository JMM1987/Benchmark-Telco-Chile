import asyncio
from playwright.async_api import async_playwright
import datetime

async def scraping_wom():
    async with async_playwright() as p:
        # Lanzamos el navegador
        browser = await p.chromium.launch(headless=True)
        # Nos hacemos pasar por un usuario real para evitar bloqueos
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"[{datetime.datetime.now()}] Iniciando visita a WOM...")
        
        try:
            # Vamos a la sección de planes
            await page.goto("https://www.wom.cl/planes/", timeout=60000)
            
            # Esperamos a que carguen los precios (usamos un selector común en WOM)
            await page.wait_for_selector(".price", timeout=10000)
            
            # Extraemos todos los precios que encuentre en la página
            precios = await page.locator(".price").all_inner_texts()
            # Extraemos los nombres de los planes
            planes = await page.locator("h3").all_inner_texts()
            
            print("--- RESULTADOS ENCONTRADOS ---")
            for plan, precio in zip(planes, precios):
                print(f"Plan: {plan.strip()} | Precio: {precio.strip()}")
                
        except Exception as e:
            print(f"Ups! Algo falló: {e}")
            # Guardamos una captura de pantalla si falla (puedes verla en GitHub Actions)
            await page.screenshot(path="error_wom.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scraping_wom())
