# PLM Medication Scraper

Extracts medication data from [medicamentosplm.com](https://www.medicamentosplm.com/) based on a configurable list of medications.

## Features

- ✅ **Configurable**: Specify which medications to scrape via JSON config
- ✅ **Respectful**: Built-in rate limiting (default 3s between requests)
- ✅ **Structured Data**: Extracts brand names, laboratories, forms, presentations
- ✅ **Error Handling**: Graceful failure with detailed error messages
- ✅ **Async**: Fast parallel-ready architecture using httpx
- ✅ **Output**: Clean JSON format for easy integration

## Quick Start

### 1. Configure Medications

Edit `backend/data/medications_to_scrape.json` to specify which medications to scrape:

```json
{
  "medications": [
    {
      "generic_name": "amoxicilina",
      "indication": "pharyngitis",
      "priority": "high"
    },
    {
      "generic_name": "ciprofloxacino",
      "indication": "uti",
      "priority": "high"
    }
  ]
}
```

### 2. Run the Scraper

**Option A - Using the helper script (recommended):**
```bash
./backend/scripts/run_plm_scraper.sh
```

**Option B - Direct Python:**
```bash
cd /path/to/medicopilot
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install httpx beautifulsoup4 lxml pydantic
python backend/scripts/plm_scraper.py
```

**Option C - With custom arguments:**
```bash
python backend/scripts/plm_scraper.py \
  --config backend/data/medications_to_scrape.json \
  --output backend/data/plm_medications.json \
  --delay 5.0
```

### 3. Check Results

Results are saved to `backend/data/plm_medications.json`:

```json
{
  "version": "1.0",
  "scraped_at": "2025-10-24 15:30:00",
  "total_medications": 8,
  "successful_scrapes": 7,
  "medications": [
    {
      "generic_name": "amoxicilina",
      "indication": "pharyngitis",
      "priority": "high",
      "brands": [
        {
          "brand_name": "Amoxil",
          "laboratory": "GSK",
          "pharmaceutical_form": "Cápsulas",
          "presentation": "500 mg, caja con 12 cápsulas",
          "plm_url": "https://www.medicamentosplm.com/...",
          "active_substances": ["Amoxicilina"]
        }
      ],
      "scraped_at": "2025-10-24 15:30:15",
      "scrape_status": "success"
    }
  ]
}
```

## Configuration Options

### medications_to_scrape.json

| Field | Type | Description |
|-------|------|-------------|
| `generic_name` | string | Generic medication name (e.g., "amoxicilina") |
| `indication` | string | Clinical indication (e.g., "pharyngitis", "uti") |
| `priority` | string | Priority level: "high", "medium", "low" |
| `notes` | string | Optional notes about the medication |

### Scraper Settings

```json
{
  "scraper_settings": {
    "delay_between_requests": 3,
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 ..."
  }
}
```

## CLI Arguments

```bash
python backend/scripts/plm_scraper.py [OPTIONS]

Options:
  --config PATH    Path to medications config file
                   (default: backend/data/medications_to_scrape.json)

  --output PATH    Output path for scraped data
                   (default: backend/data/plm_medications.json)

  --delay FLOAT    Delay between requests in seconds
                   (default: 3.0)
```

## Output Schema

### MedicationData
- `generic_name` (str): Generic medication name
- `indication` (str): Clinical indication
- `priority` (str): Priority level
- `brands` (List[MedicationBrand]): List of brand medications found
- `scraped_at` (str): Timestamp of scraping
- `scrape_status` (str): "success", "failed", or "partial"
- `error_message` (str, optional): Error details if scraping failed

### MedicationBrand
- `brand_name` (str): Commercial brand name
- `laboratory` (str): Manufacturer/laboratory
- `pharmaceutical_form` (str): Form (e.g., "Cápsulas", "Tabletas")
- `presentation` (str): Presentation details (dosage, quantity)
- `plm_url` (str, optional): URL to detailed PLM page
- `active_substances` (List[str]): List of active ingredients

## Adding New Medications

To scrape additional medications, simply add them to `medications_to_scrape.json`:

```json
{
  "medications": [
    {
      "generic_name": "ibuprofeno",
      "indication": "pain",
      "priority": "high",
      "notes": "NSAID for pain and inflammation"
    }
  ]
}
```

Then re-run the scraper. It will fetch data for all medications in the config file.

## Troubleshooting

### No brands found
- PLM search may not have exact matches for the generic name you provided
- Try alternative spellings (e.g., "trimetoprim sulfametoxazol" vs "trimetoprima sulfametoxazol")
- Check the PLM website directly to verify the medication exists

### HTTP errors (403, 429)
- You may be rate-limited. Increase the `--delay` parameter
- PLM may have anti-scraping measures. Consider manual extraction for critical medications
- Check your internet connection

### Parsing errors
- PLM may have changed their HTML structure
- The scraper tries multiple CSS selectors, but may need updates
- Check `plm_scraper.py:_parse_search_results()` and adjust selectors

## Legal & Ethical Considerations

⚠️ **Important Notes:**
- This scraper is intended for **educational and research purposes** (hackathon demo)
- PLM's terms of service may prohibit automated scraping
- Always respect rate limits (default 3s delay between requests)
- For production use, consider:
  - Contacting PLM for official API access or data partnership
  - Manual curation of critical medications
  - Purchasing commercial medication databases

## Integration with MediCopilot

Once scraped, medication data can be used in:

1. **RAG Pipeline**: Ingest into Weaviate for semantic search
2. **Drug Mapping**: Map to RxNorm/ATC codes for standardization
3. **Clinical Agents**: Provide to Saptiva agents for medication recommendations
4. **Safety Checks**: Cross-reference with patient allergies and interactions

Example integration:
```python
# In backend/services/medication_service.py
import json

def load_plm_medications():
    with open('backend/data/plm_medications.json') as f:
        data = json.load(f)
    return data['medications']

def find_brands(generic_name: str):
    medications = load_plm_medications()
    for med in medications:
        if med['generic_name'].lower() == generic_name.lower():
            return med['brands']
    return []
```

## Future Enhancements

- [ ] **Detail Page Scraping**: Extract full prescribing information from individual medication pages
- [ ] **Drug Interactions**: Scrape PLM's interaction checker
- [ ] **Incremental Updates**: Only scrape medications added since last run
- [ ] **Database Integration**: Store directly in PostgreSQL instead of JSON
- [ ] **Parallel Scraping**: Use asyncio.gather() for faster bulk scraping
- [ ] **Retry Logic**: Automatic retries with exponential backoff
- [ ] **Validation**: Cross-check with COFEPRIS registry

## License

Part of MediCopilot Nexus - See main project LICENSE
