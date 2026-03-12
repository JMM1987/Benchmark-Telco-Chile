import asyncio
from playwright.async_api import async_playwright
import datetime

async def scraping_wom():
    async with async_playwright() as p:
        # Iniciamos el navegador
        browser = await p.chromium.launch(headless=True)
        # Creamos un contexto que imita a un computador real en Chile
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print(f"[{datetime.datetime.now()}] Intentando entrar a WOM...")
        
        try:
            # Vamos directamente a la página de planes de fibra o móvil
            # Probemos con fibra esta vez que suele ser más estable para el robot
            await page.goto("https://www.wom.cl/hogar/internet-fibra-optica/", wait_until="networkidle", timeout=60000)
            
            # En lugar de buscar ".price", buscaremos cualquier texto que tenga un "$"
            # Esto es mucho más robusto
            await page.wait_for_selector("text=$", timeout=20000)
            
            # Capturamos los precios (WOM usa etiquetas h2 o span para esto)
            precios = await page.locator("text=$").all_inner_texts()
            
            print("--- ¡ÉXITO! DATOS ENCONTRADOS ---")
            for p in precios[:5]: # Solo mostramos los primeros 5 para probar
                print(f"Precio detectado: {p.strip()}")
                
        except Exception as e:
            print(f"Error: No pudimos ver los precios. El sitio dice: {e}")
            # Esto nos ayudará mucho: guarda una foto de lo que el robot ve
            await page.screenshot(path="lo_que_ve_el_robot.png")
            print("Captura de pantalla guardada como lo_que_ve_el_robot.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scraping_wom())
