#!/usr/bin/env python3
"""
PLM (Medicamentos PLM) Scraper with Playwright
Extracts medication data from medicamentosplm.com using headless browser
Handles JavaScript-rendered content
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page
from pydantic import BaseModel


class MedicationBrand(BaseModel):
    """Individual brand/presentation of a medication"""
    brand_name: str
    laboratory: str
    pharmaceutical_form: str
    presentation: str
    plm_url: Optional[str] = None
    active_substances: List[str] = []


class MedicationData(BaseModel):
    """Complete medication data including all brands"""
    generic_name: str
    indication: str
    priority: str
    brands: List[MedicationBrand] = []
    scraped_at: str
    scrape_status: str = "pending"  # pending, success, failed, partial
    error_message: Optional[str] = None


class PLMScraperPlaywright:
    """Scraper for medicamentosplm.com using Playwright"""

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

        print(f"🔍 Starting PLM scraper (Playwright) for {len(medications)} medications...")
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
            await page.goto(search_url, wait_until="networkidle", timeout=30000)

            # Wait for results to load (the JavaScript populates prescriptionGrid)
            try:
                # Wait for either the results container or the "no results" message
                await page.wait_for_selector(
                    "#prescriptionGrid, .no-results",
                    timeout=10000
                )
                # Give it extra time to fully populate
                await asyncio.sleep(2)
            except Exception:
                print(f"  ⚠️  Timeout waiting for results to load")

            # Get the rendered HTML
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Parse search results
            brands = self._parse_search_results(soup, generic_name)

            med_data.brands = brands
            med_data.scrape_status = "success" if brands else "failed"

            if not brands:
                med_data.error_message = "No brands found in search results"
                print(f"  ⚠️  No brands found for {generic_name}")
            else:
                print(f"  ✅ Found {len(brands)} brand(s)")
                for brand in brands[:3]:  # Show first 3
                    print(f"     - {brand.brand_name} ({brand.laboratory})")

        except Exception as e:
            med_data.scrape_status = "failed"
            med_data.error_message = f"Error: {str(e)}"
            print(f"  ❌ Error: {e}")

        return med_data

    def _parse_search_results(self, soup: BeautifulSoup, generic_name: str) -> List[MedicationBrand]:
        """Parse medication brands from search results page"""
        brands = []

        # Look for the results container
        results_container = soup.select_one("#prescriptionGrid")
        if not results_container:
            return brands

        # PLM uses table rows for medication results
        medication_rows = results_container.select("tr")

        # Skip header row if present
        for row in medication_rows:
            # Check if it's a header row
            if row.find('th'):
                continue

            brand = self._parse_medication_row(row, generic_name)
            if brand:
                brands.append(brand)

        return brands

    def _parse_medication_row(self, row, generic_name: str) -> Optional[MedicationBrand]:
        """Parse a single medication row"""
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                return None

            # PLM typical structure:
            # Column 0: Brand name (with link)
            # Column 1: Active substance(s)
            # Column 2: Pharmaceutical form
            # Column 3: Laboratory
            # Column 4: Presentation

            brand_name_cell = cells[0]
            brand_name = brand_name_cell.get_text(strip=True)

            # Extract detail URL
            plm_url = None
            link = brand_name_cell.find('a')
            if link and link.get('href'):
                href = link['href']
                plm_url = self.BASE_URL + href if href.startswith('/') else href

            # Extract other fields
            substances = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            pharm_form = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            laboratory = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            presentation = cells[4].get_text(strip=True) if len(cells) > 4 else ""

            # Basic validation
            if not brand_name or len(brand_name) < 2:
                return None

            # Parse substances into list
            substance_list = [s.strip() for s in substances.split(',') if s.strip()]

            return MedicationBrand(
                brand_name=brand_name,
                laboratory=laboratory or "Unknown",
                pharmaceutical_form=pharm_form or "Unknown",
                presentation=presentation or "Unknown",
                plm_url=plm_url,
                active_substances=substance_list
            )

        except Exception as e:
            print(f"    ⚠️  Error parsing medication row: {e}")
            return None

    def save_results(self, output_path: str = "backend/data/plm_medications.json"):
        """Save scraped results to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict format
        output_data = {
            "version": "1.0",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_medications": len(self.results),
            "successful_scrapes": sum(1 for m in self.results if m.scrape_status == "success"),
            "medications": [m.model_dump() for m in self.results]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {output_path}")
        print(f"   Total: {output_data['total_medications']}")
        print(f"   Successful: {output_data['successful_scrapes']}")
        print(f"   Failed: {output_data['total_medications'] - output_data['successful_scrapes']}")

        # Also print summary statistics
        if output_data['successful_scrapes'] > 0:
            total_brands = sum(len(m['brands']) for m in output_data['medications'] if m['scrape_status'] == 'success')
            print(f"   Total brands found: {total_brands}")


async def main():
    """Main entry point for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="PLM Medication Scraper (Playwright)")
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

    scraper = PLMScraperPlaywright(
        config_path=args.config,
        delay=args.delay,
        headless=not args.no_headless
    )
    await scraper.scrape_all()
    scraper.save_results(output_path=args.output)


if __name__ == "__main__":
    asyncio.run(main())
