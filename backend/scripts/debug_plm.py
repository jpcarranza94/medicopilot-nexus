#!/usr/bin/env python3
"""
Debug script to inspect PLM HTML structure
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote


async def debug_search(medication: str):
    """Debug PLM search for a specific medication"""
    base_url = "https://www.medicamentosplm.com"
    search_url = f"{base_url}/Home/Busqueda?texto={quote(medication)}"

    print(f"🔍 Debugging search for: {medication}")
    print(f"📍 URL: {search_url}\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    }

    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(search_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Save raw HTML for inspection
            with open(f'debug_plm_{medication}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ Raw HTML saved to: debug_plm_{medication}.html")

            # Look for different possible structures
            print("\n📊 HTML Structure Analysis:")
            print("=" * 60)

            # Check for tables
            tables = soup.find_all('table')
            print(f"\n🔹 Tables found: {len(tables)}")
            for idx, table in enumerate(tables[:3], 1):
                print(f"   Table {idx} - classes: {table.get('class', 'no class')}")
                rows = table.find_all('tr')
                print(f"   Rows: {len(rows)}")
                if rows:
                    first_row_cells = rows[0].find_all(['td', 'th'])
                    print(f"   First row cells: {len(first_row_cells)}")

            # Check for divs with specific classes
            print(f"\n🔹 Divs with medication-related classes:")
            for class_name in ['medicamento', 'resultado', 'product', 'item', 'list']:
                divs = soup.find_all('div', class_=lambda x: x and class_name in str(x).lower())
                if divs:
                    print(f"   .{class_name}*: {len(divs)} found")

            # Look for links
            links = soup.find_all('a', href=lambda x: x and 'producto' in str(x).lower())
            print(f"\n🔹 Product links found: {len(links)}")
            if links:
                print("   Sample links:")
                for link in links[:3]:
                    print(f"   - {link.get_text(strip=True)[:50]} -> {link.get('href')}")

            # Check for result counts
            result_text = soup.get_text()
            if 'Medicamentos' in result_text:
                # Try to find result count
                import re
                match = re.search(r'Medicamentos\s+(\d+)', result_text)
                if match:
                    print(f"\n🔹 Medications count in page: {match.group(1)}")

            # Look for any structured data
            print(f"\n🔹 Searching for common PLM elements:")
            for selector in ['.brand', '.lab', '.substance', '.presentation', '#resultados', '.resultados']:
                elements = soup.select(selector)
                if elements:
                    print(f"   {selector}: {len(elements)} found")

        except httpx.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    medication = sys.argv[1] if len(sys.argv) > 1 else "amoxicilina"
    asyncio.run(debug_search(medication))
