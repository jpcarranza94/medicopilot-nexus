# PLM Scraper - Quick Start

## 🚀 For Your Hackathon (Fastest Path)

**Use the pre-populated medication data** - it's ready to go!

```bash
# File location:
backend/data/plm_medications_manual.json

# Contains 8 medications with Mexican brand names
# ✅ Ready for your demo
# ✅ No scraping needed
# ✅ Clinically accurate
```

### Load in Python

```python
import json

# Load medication data
with open('backend/data/plm_medications_manual.json', 'r', encoding='utf-8') as f:
    plm_data = json.load(f)

# Get brands for amoxicilina
for med in plm_data['medications']:
    if med['generic_name'] == 'amoxicilina':
        print(f"Found {len(med['brands'])} brands:")
        for brand in med['brands']:
            print(f"  - {brand['brand_name']} ({brand['laboratory']})")
```

---

## 🔧 Web Scraping (Post-Hackathon)

If you want to scrape PLM later:

```bash
# 1. Install dependencies
pip install playwright beautifulsoup4 lxml pydantic
python -m playwright install chromium

# 2. Configure medications to scrape
# Edit: backend/data/medications_to_scrape.json

# 3. Run scraper
python backend/scripts/plm_scraper_playwright.py

# 4. Results saved to:
# backend/data/plm_medications.json
```

**Note**: PLM uses JavaScript rendering, so scraping is complex. The Playwright scraper is implemented but may need debugging based on PLM's current structure.

---

## 📁 Files Created

```
backend/
├── data/
│   ├── medications_to_scrape.json      # Scraper configuration
│   ├── plm_medications_manual.json     # ✅ USE THIS for hackathon
│   ├── plm_medications.json            # Scraper output (when run)
│   └── medications_test.json           # Test config
├── scripts/
│   ├── plm_scraper.py                  # BeautifulSoup version (basic)
│   ├── plm_scraper_playwright.py       # ✅ Main scraper (JavaScript support)
│   ├── debug_plm.py                    # Debug helper (httpx)
│   ├── debug_plm_playwright.py         # Debug helper (Playwright)
│   ├── run_plm_scraper.sh              # Convenience runner
│   ├── README_PLM_SCRAPER.md           # Detailed scraper docs
│   └── QUICK_START.md                  # This file
├── requirements.txt                     # Python dependencies
└── PLM_SETUP_GUIDE.md                  # Complete integration guide
```

---

## 🎯 What's in the Manual Data?

### Pharyngitis Medications (3)
- **Amoxicilina**: Amoxil (GSK), Amoxicilina Pisa
- **Azitromicina**: Azitromicina Sandoz, Azitromicina MK
- **Penicilina benzatínica**: Benzetacil (Pfizer)

### UTI Medications (3)
- **Ciprofloxacino**: Cipro (Bayer), Ciprofloxacina MK
- **Nitrofurantoína**: Macrodantina, Nitrofurantoína Liomont
- **Trimetoprima sulfametoxazol**: Bactrim F (Roche), Septrin (GSK)

### General Use (2)
- **Paracetamol**: Tempra (BMS), Paracetamol GI
- **Ceftriaxona**: Rocephin (Roche), Ceftriaxona Sandoz

Each medication includes:
- ✅ Mexican brand names
- ✅ Laboratory/manufacturer
- ✅ Pharmaceutical form (tablets, capsules, injection)
- ✅ Presentation (dosage, quantity)
- ✅ Clinical notes (dosing, indications)

---

## ⚡ Next Steps

1. **Integrate with your API** - See `PLM_SETUP_GUIDE.md` for code examples
2. **Add to Saptiva agents** - Include medication data in context
3. **Implement safety checks** - Cross-reference with patient allergies
4. **Build your demo** - You have everything you need!

---

## 📚 Full Documentation

- **Integration Guide**: `backend/PLM_SETUP_GUIDE.md`
- **Scraper Details**: `backend/scripts/README_PLM_SCRAPER.md`
- **Project Docs**: `CLAUDE.md`, `docs/ARCHITECTURE.md`

---

## ⏰ Time Estimate

| Task | Using Manual Data | Using Scraper |
|------|-------------------|---------------|
| Setup | 5 minutes | 3-4 hours |
| Reliability | ★★★★★ | ★★☆☆☆ |
| Data Quality | Curated | Variable |

**For hackathon**: Use manual data ✅
**For production**: Enhance with COFEPRIS or official PLM partnership

Good luck with your demo! 🚀
