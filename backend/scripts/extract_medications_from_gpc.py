#!/usr/bin/env python3
"""
Extract medications from GPC PDFs
Creates a list of medications to scrape from PLM based on clinical practice guidelines
"""

import re
from pathlib import Path
import PyPDF2
import json


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text


def extract_medications_from_text(text):
    """Extract medication names from text using patterns"""
    # Common medication patterns in Spanish medical texts
    medications = set()

    # Common medication endings and patterns
    patterns = [
        r'\b([A-Z][a-zá-ú]+(?:cilina|micina|floxacino|xacina|tiazida|prazol|statina|dipina|sartan|olol|pril))\b',
        r'\b(metformina|insulina|glibenclamida|atorvastatina|simvastatina|losartan|enalapril)\b',
        r'\b(amoxicilina|azitromicina|claritromicina|levofloxacino|ciprofloxacino)\b',
        r'\b(ceftriaxona|cefotaxima|ceftazidima|cefepime)\b',
        r'\b(paracetamol|ibuprofeno|naproxeno|diclofenaco|ketorolaco)\b',
        r'\b(omeprazol|lansoprazol|pantoprazol|ranitidina)\b',
        r'\b(captopril|enalapril|losartan|valsartan|telmisartan)\b',
        r'\b(metoprolol|atenolol|propranolol|carvedilol|bisoprolol)\b',
        r'\b(furosemida|hidroclorotiazida|espironolactona)\b',
        r'\b(amlodipino|nifedipino|diltiazem|verapamilo)\b',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        medications.update([m.lower() for m in matches])

    return sorted(list(medications))


def main():
    gpc_dir = Path("data/GPC")
    results = {}

    print("📚 Extracting medications from GPC documents...\n")

    for pdf_file in gpc_dir.glob("*.pdf"):
        print(f"📄 Processing: {pdf_file.name}")

        text = extract_text_from_pdf(pdf_file)
        medications = extract_medications_from_text(text)

        # Map filename to condition
        condition_map = {
            "neumonia": "Neumonía adquirida en la comunidad",
            "diabetes": "Diabetes Mellitus",
            "hipertension": "Hipertensión arterial",
            "dislipidemias": "Dislipidemias",
            "cardiopatia": "Cardiopatía isquémica",
            "cefalea": "Cefalea",
            "hipotiroidismo": "Hipotiroidismo",
            "obesidad": "Obesidad",
            "enfermedad-renal": "Enfermedad renal crónica"
        }

        condition = "Unknown"
        for key, value in condition_map.items():
            if key in pdf_file.stem.lower():
                condition = value
                break

        results[pdf_file.stem] = {
            "condition": condition,
            "medications_found": len(medications),
            "medications": medications
        }

        print(f"  ✅ Found {len(medications)} medications")
        if medications:
            print(f"     Examples: {', '.join(medications[:5])}")
        print()

    # Save results
    output_file = Path("backend/data/gpc_medications_extracted.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_file}")

    # Create summary
    all_meds = set()
    for data in results.values():
        all_meds.update(data["medications"])

    print(f"\n📊 Summary:")
    print(f"   Total GPC documents: {len(results)}")
    print(f"   Unique medications found: {len(all_meds)}")
    print(f"\n   All unique medications:")
    for med in sorted(all_meds):
        print(f"   - {med}")


if __name__ == "__main__":
    main()
