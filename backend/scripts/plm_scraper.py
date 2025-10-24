#!/usr/bin/env python3
"""
PLM (Medicamentos PLM) Scraper
Extracts medication data from medicamentosplm.com based on configuration file
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup
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


class PLMScraper:
    """Scraper for medicamentosplm.com"""

    BASE_URL = "https://www.medicamentosplm.com"
    SEARCH_URL = f"{BASE_URL}/Home/Busqueda"

    def __init__(self, config_path: str = None, delay: float = 3.0):
        self.config_path = config_path or "backend/data/medications_to_scrape.json"
        self.delay = delay
        self.config = self._load_config()
        self.results: List[MedicationData] = []

        # Configure HTTP client
        self.headers = {
            "User-Agent": self.config.get("scraper_settings", {}).get(
                "user_agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        }

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
        print(f"⏱️  Delay between requests: {self.delay}s\n")

        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            follow_redirects=True
        ) as client:
            for idx, med_config in enumerate(medications, 1):
                generic_name = med_config["generic_name"]
                print(f"[{idx}/{len(medications)}] Scraping: {generic_name}...")

                med_data = await self._scrape_medication(client, med_config)
                self.results.append(med_data)

                # Rate limiting
                if idx < len(medications):
                    await asyncio.sleep(self.delay)

        return self.results

    async def _scrape_medication(
        self,
        client: httpx.AsyncClient,
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
            # Search for medication
            search_url = f"{self.SEARCH_URL}?texto={quote(generic_name)}"
            response = await client.get(search_url)
            response.raise_for_status()

            # Parse search results
            soup = BeautifulSoup(response.text, 'html.parser')
            brands = self._parse_search_results(soup, generic_name)

            med_data.brands = brands
            med_data.scrape_status = "success" if brands else "failed"

            if not brands:
                med_data.error_message = "No brands found in search results"
                print(f"  ⚠️  No brands found for {generic_name}")
            else:
                print(f"  ✅ Found {len(brands)} brand(s)")

        except httpx.HTTPError as e:
            med_data.scrape_status = "failed"
            med_data.error_message = f"HTTP error: {str(e)}"
            print(f"  ❌ HTTP error: {e}")
        except Exception as e:
            med_data.scrape_status = "failed"
            med_data.error_message = f"Unexpected error: {str(e)}"
            print(f"  ❌ Error: {e}")

        return med_data

    def _parse_search_results(self, soup: BeautifulSoup, generic_name: str) -> List[MedicationBrand]:
        """Parse medication brands from search results page"""
        brands = []

        # Look for medication results table
        # PLM typically uses tables or divs with specific classes
        # We need to adapt based on actual HTML structure

        # Try multiple possible selectors
        possible_selectors = [
            "table.resultados tbody tr",  # Table-based results
            "div.medicamento-item",        # Div-based results
            "div.resultado-medicamento",   # Alternative div structure
        ]

        medication_rows = []
        for selector in possible_selectors:
            medication_rows = soup.select(selector)
            if medication_rows:
                break

        if not medication_rows:
            # Fallback: try to find any table with medication data
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                if rows and len(rows) > 0:
                    medication_rows = rows
                    break

        for row in medication_rows:
            try:
                brand = self._parse_medication_row(row, generic_name)
                if brand:
                    brands.append(brand)
            except Exception as e:
                print(f"    ⚠️  Failed to parse row: {e}")
                continue

        return brands

    def _parse_medication_row(self, row, generic_name: str) -> Optional[MedicationBrand]:
        """Parse a single medication row/element"""
        try:
            # Extract text from all cells/elements
            if row.name == 'tr':
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    return None

                # Typical structure: [Brand, Substance, Form, Lab, Presentation]
                brand_name = cells[0].get_text(strip=True)
                substances = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                pharm_form = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                laboratory = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                presentation = cells[4].get_text(strip=True) if len(cells) > 4 else ""

                # Extract detail URL
                plm_url = None
                link = cells[0].find('a')
                if link and link.get('href'):
                    plm_url = self.BASE_URL + link['href'] if link['href'].startswith('/') else link['href']

            else:  # div-based structure
                brand_name = row.select_one('.brand-name, .nombre-medicamento')
                brand_name = brand_name.get_text(strip=True) if brand_name else ""

                substances = row.select_one('.sustancia, .active-substance')
                substances = substances.get_text(strip=True) if substances else ""

                pharm_form = row.select_one('.forma, .pharmaceutical-form')
                pharm_form = pharm_form.get_text(strip=True) if pharm_form else ""

                laboratory = row.select_one('.laboratorio, .lab')
                laboratory = laboratory.get_text(strip=True) if laboratory else ""

                presentation = row.select_one('.presentacion, .presentation')
                presentation = presentation.get_text(strip=True) if presentation else ""

                plm_url = None
                link = row.find('a')
                if link and link.get('href'):
                    plm_url = self.BASE_URL + link['href'] if link['href'].startswith('/') else link['href']

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


async def main():
    """Main entry point for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="PLM Medication Scraper")
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

    args = parser.parse_args()

    scraper = PLMScraper(config_path=args.config, delay=args.delay)
    await scraper.scrape_all()
    scraper.save_results(output_path=args.output)


if __name__ == "__main__":
    asyncio.run(main())
