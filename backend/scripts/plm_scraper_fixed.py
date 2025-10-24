#!/usr/bin/env python3
"""
PLM (Medicamentos PLM) Scraper - FIXED VERSION
Extracts REAL medication data from medicamentosplm.com
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote, unquote
import html

from playwright.async_api import async_playwright, Page
from pydantic import BaseModel


class MedicationBrand(BaseModel):
    """Individual brand/presentation of a medication"""
    brand_name: str
    laboratory: str
    pharmaceutical_form: str
    presentation: str
    plm_url: Optional[str] = None
    product_id: Optional[str] = None


class MedicationData(BaseModel):
    """Complete medication data including all brands"""
    generic_name: str
    indication: str
    priority: str
    brands: List[MedicationBrand] = []
    scraped_at: str
    scrape_status: str = "pending"
    error_message: Optional[str] = None


class PLMScraperFixed:
    """Scraper for medicamentosplm.com - extracts real data"""

    BASE_URL = "https://www.medicamentosplm.com"
    SEARCH_URL = f"{BASE_URL}/Home/Busqueda"

    def __init__(self, config_path: str = None, delay: float = 3.0, headless: bool = True):
        self.config_path = config_path or "backend/data/medications_to_scrape.json"
        self.delay = delay
        self.headless = headless
        self.config = self._load_config()
        self.results: List[MedicationData] = []

    def _load_config(self) -> dict:
        """Load medication configuration file"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def scrape_all(self) -> List[MedicationData]:
        """Scrape all medications from configuration file"""
        medications = self.config.get("medications", [])

        print(f"🔍 Starting PLM scraper for {len(medications)} medications...")
        print(f"⏱️  Delay between requests: {self.delay}s")
        print(f"🌐 Headless mode: {self.headless}\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                locale="es-MX"
            )
            page = await context.new_page()

            for idx, med_config in enumerate(medications, 1):
                generic_name = med_config["generic_name"]
                print(f"[{idx}/{len(medications)}] Scraping: {generic_name}...")

                med_data = await self._scrape_medication(page, med_config)
                self.results.append(med_data)

                # Rate limiting
                if idx < len(medications):
                    await asyncio.sleep(self.delay)

            await browser.close()

        return self.results

    async def _scrape_medication(
        self,
        page: Page,
        med_config: dict
    ) -> MedicationData:
        """Scrape a single medication"""
        generic_name = med_config["generic_name"]

        med_data = MedicationData(
            generic_name=generic_name,
            indication=med_config.get("indication", ""),
            priority=med_config.get("priority", "medium"),
            scraped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        try:
            # Navigate to search page
            search_url = f"{self.SEARCH_URL}?texto={quote(generic_name)}"
            await page.goto(search_url, wait_until="networkidle", timeout=60000)

            # Wait for JavaScript to populate the table
            print(f"  ⏳ Waiting for results to load...")
            await asyncio.sleep(8)  # Give JavaScript time to load

            # Extract medication data from table rows
            brands = await self._extract_medication_data(page)

            med_data.brands = brands
            med_data.scrape_status = "success" if brands else "failed"

            if not brands:
                med_data.error_message = "No brands found in search results"
                print(f"  ⚠️  No brands found for {generic_name}")
            else:
                print(f"  ✅ Found {len(brands)} brand(s)")
                # Show first few examples
                for brand in brands[:3]:
                    print(f"     • {brand.brand_name} - {brand.presentation} ({brand.laboratory})")
                if len(brands) > 3:
                    print(f"     ... and {len(brands) - 3} more")

        except Exception as e:
            med_data.scrape_status = "failed"
            med_data.error_message = f"Error: {str(e)}"
            print(f"  ❌ Error: {e}")

        return med_data

    async def _extract_medication_data(self, page: Page) -> List[MedicationBrand]:
        """Extract medication data from PLM page"""
        brands = []

        # PLM stores data in input checkboxes within table rows
        rows = await page.query_selector_all("table.table tbody tr")

        print(f"  📊 Found {len(rows)} table rows")

        for row in rows:
            try:
                # Find the input checkbox that contains the JSON data
                checkbox = await row.query_selector("input.check-prescription")
                if not checkbox:
                    continue

                # Get the value attribute which contains JSON data
                value_attr = await checkbox.get_attribute("value")
                if not value_attr:
                    continue

                # Parse the JSON data
                # The value is HTML-encoded JSON
                decoded_value = html.unescape(value_attr)
                data = json.loads(decoded_value)

                # Extract medication information
                brand_name = data.get("Brand", "")
                laboratory = data.get("DivisionShortName", "Unknown")
                pharm_form = data.get("PharmaForm", "Unknown")
                presentation = data.get("Presentation", "Unknown")
                product_url = data.get("BrandClean", "")

                if not brand_name:
                    continue

                # Build full URL
                plm_url = None
                if product_url:
                    plm_url = self.BASE_URL + product_url if product_url.startswith("/") else product_url

                # Create brand entry
                brand = MedicationBrand(
                    brand_name=brand_name,
                    laboratory=laboratory,
                    pharmaceutical_form=pharm_form,
                    presentation=presentation,
                    plm_url=plm_url,
                    product_id=str(data.get("ProductId", ""))
                )

                brands.append(brand)

            except json.JSONDecodeError as e:
                print(f"    ⚠️  Failed to parse JSON: {e}")
                continue
            except Exception as e:
                print(f"    ⚠️  Error processing row: {e}")
                continue

        return brands

    def save_results(self, output_path: str = "backend/data/plm_medications.json"):
        """Save scraped results to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict format
        output_data = {
            "version": "1.0",
            "source": "PLM (medicamentosplm.com) - Real scraped data",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_medications": len(self.results),
            "successful_scrapes": sum(1 for m in self.results if m.scrape_status == "success"),
            "medications": [m.model_dump() for m in self.results]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {output_path}")
        print(f"   Total medications: {output_data['total_medications']}")
        print(f"   Successful: {output_data['successful_scrapes']}")
        print(f"   Failed: {output_data['total_medications'] - output_data['successful_scrapes']}")

        # Calculate total brands
        if output_data['successful_scrapes'] > 0:
            total_brands = sum(len(m['brands']) for m in output_data['medications'] if m['scrape_status'] == 'success')
            print(f"   Total brands/presentations: {total_brands}")


async def main():
    """Main entry point for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="PLM Medication Scraper - Fixed Version")
    parser.add_argument(
        "--config",
        default="backend/data/medications_to_scrape.json",
        help="Path to medications configuration file"
    )
    parser.add_argument(
        "--output",
        default="backend/data/plm_medications.json",
        help="Output path for scraped data"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay between requests in seconds (default: 3.0)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in visible mode (for debugging)"
    )

    args = parser.parse_args()

    scraper = PLMScraperFixed(
        config_path=args.config,
        delay=args.delay,
        headless=not args.no_headless
    )
    await scraper.scrape_all()
    scraper.save_results(output_path=args.output)


if __name__ == "__main__":
    asyncio.run(main())
