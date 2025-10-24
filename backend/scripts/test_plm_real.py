#!/usr/bin/env python3
"""Test script to see actual PLM data structure"""

import asyncio
from playwright.async_api import async_playwright


async def test_plm():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="es-MX")
        page = await context.new_page()

        url = "https://www.medicamentosplm.com/Home/Busqueda?texto=amoxicilina"
        print(f"🌐 Loading: {url}")

        await page.goto(url, wait_until="networkidle", timeout=60000)

        # Wait longer for JavaScript to load
        print("⏳ Waiting for JavaScript to load content...")
        await asyncio.sleep(10)

        # Try to find the table/results
        print("\n🔍 Looking for results container...")

        # Check if prescriptionGrid has content
        grid = await page.query_selector("#prescriptionGrid")
        if grid:
            inner_html = await grid.inner_html()
            print(f"✅ Found #prescriptionGrid - Content length: {len(inner_html)} chars")
            if len(inner_html) > 100:
                print("\nFirst 500 chars:")
                print(inner_html[:500])

                # Save full HTML
                with open("plm_grid_content.html", "w", encoding="utf-8") as f:
                    f.write(inner_html)
                print("\n💾 Full content saved to: plm_grid_content.html")
        else:
            print("❌ #prescriptionGrid not found")

        # Try alternative selectors
        print("\n🔍 Trying alternative selectors...")

        selectors = [
            "table.table tbody tr",
            ".container-result table tr",
            "[data-searchtext] ~ * table tr",
            "table tr",
        ]

        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements and len(elements) > 0:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")

                # Get first element content
                if len(elements) > 0:
                    first_elem = elements[0]
                    html = await first_elem.inner_html()
                    print(f"   First element preview: {html[:200]}")

                break

        # Save full page HTML
        full_html = await page.content()
        with open("plm_full_page.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        print("\n💾 Full page saved to: plm_full_page.html")

        # Take screenshot
        await page.screenshot(path="plm_screenshot.png", full_page=True)
        print("📸 Screenshot saved to: plm_screenshot.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_plm())
