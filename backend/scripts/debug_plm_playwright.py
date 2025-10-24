#!/usr/bin/env python3
"""Debug PLM with Playwright - save screenshot and HTML"""

import asyncio
from playwright.async_api import async_playwright


async def debug_plm(medication: str = "amoxicilina"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible browser
        context = await browser.new_context(locale="es-MX")
        page = await context.new_page()

        url = f"https://www.medicamentosplm.com/Home/Busqueda?texto={medication}"
        print(f"🌐 Navigating to: {url}")

        await page.goto(url, wait_until="networkidle")

        # Wait a bit for JavaScript to load
        print("⏳ Waiting 5 seconds for page to load...")
        await asyncio.sleep(5)

        # Save screenshot
        await page.screenshot(path=f"debug_plm_{medication}_playwright.png")
        print(f"📸 Screenshot saved: debug_plm_{medication}_playwright.png")

        # Save HTML
        html = await page.content()
        with open(f"debug_plm_{medication}_playwright.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"💾 HTML saved: debug_plm_{medication}_playwright.html")

        # Check for prescription grid
        grid = await page.query_selector("#prescriptionGrid")
        if grid:
            grid_html = await grid.inner_html()
            print(f"\n✅ Found #prescriptionGrid")
            print(f"   Length: {len(grid_html)} chars")
            if len(grid_html) > 100:
                print(f"   Preview: {grid_html[:200]}...")
        else:
            print("\n❌ #prescriptionGrid not found")

        # Check for table rows
        rows = await page.query_selector_all("#prescriptionGrid tr")
        print(f"\n📊 Table rows found: {len(rows)}")

        # Keep browser open for inspection
        print("\n🔍 Browser will stay open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_plm())
