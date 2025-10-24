# MediCopilot Nexus

**AI-Powered Medical Assistant for Clinical Consultations**

MediCopilot Nexus is an intelligent clinical decision support system that assists doctors during patient consultations by providing real-time, evidence-based recommendations from Mexican clinical practice guidelines (GPC).

---

## 🌟 Features

- **RAG-Powered Intelligence**: Retrieves evidence from 347+ clinical guideline chunks using semantic search
- **LLM Clinical Assistant**: Generates patient summaries, differential diagnoses, and treatment plans
- **Safety First**: Automatic allergy checking, drug interaction warnings, contraindication alerts
- **Mexican Healthcare Context**: Integrated with COFEPRIS and uses Mexican clinical guidelines (GPC)
- **Real-time Suggestions**: Low-latency responses during clinical note-taking
- **Evidence-Based Recommendations**: Citations from authoritative medical sources

---

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async/await
- **LLM Provider**: Saptiva AI API
- **Vector Database**: Weaviate Cloud
- **Embeddings**: Saptiva Embed API (1024-dimensional vectors)
- **Knowledge Base**: Mexican GPC (Guías de Práctica Clínica)

### Frontend (Next.js/React)
- **Framework**: Next.js 15.5.6 with React
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **API Client**: Axios

### RAG Pipeline
- **Document Processing**: 347 chunks from clinical guidelines
- **Similarity Search**: Weaviate vector similarity with 0.7 certainty threshold
- **Evidence Retrieval**: Top-K results with citations and metadata

---

## 📋 Prerequisites

### Required Software
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher

### Required API Keys
1. **Saptiva API Key**: Get from [lab.saptiva.com](https://lab.saptiva.com)
   - Used for: LLM inference and embeddings generation

2. **Weaviate Cloud**: Free account at [console.weaviate.cloud](https://console.weaviate.cloud)
   - Used for: Vector database (RAG knowledge base)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd medicopilot
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cat > .env << 'EOF'
# Saptiva API Configuration
SAPTIVA_API_KEY=your_saptiva_api_key_here
SAPTIVA_OPS_MODEL=saptiva-1
SAPTIVA_LEGACY_MODEL=saptiva-1

# Weaviate Configuration
WEAVIATE_URL=your_weaviate_cluster_url_here
WEAVIATE_API_KEY=your_weaviate_api_key_here

# API Configuration (optional)
API_V1_PREFIX=/api
TEMPERATURE=0.3
MAX_TOKENS=6000
EOF
```

**How to get your API keys:**

1. **Saptiva API Key**:
   - Visit [lab.saptiva.com](https://lab.saptiva.com)
   - Sign up or log in
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key to `SAPTIVA_API_KEY`

2. **Weaviate Cloud**:
   - Visit [console.weaviate.cloud](https://console.weaviate.cloud)
   - Create a free cluster
   - Copy the cluster URL (e.g., `https://xyz.c0.us-west3.gcp.weaviate.cloud`)
   - Copy the API key from cluster details
   - **Note**: The demo database already has 347 chunks loaded. Contact the maintainer for access.

#### Start the Backend Server

```bash
# Make sure you're in the backend directory with venv activated
source venv/bin/activate  # If not already activated
uvicorn app.main:app --reload --port 8000
```

The backend will start on **http://localhost:8000**

You can verify it's running by visiting:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### 3. Frontend Setup

Open a **new terminal** (keep the backend running):

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
cd frontend
cat > .env.local << 'EOF'
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_USE_MOCK_DATA=false
EOF
```

#### Start the Frontend Server

```bash
npm run dev
```

The frontend will start on **http://localhost:3001** (or 3003 if 3001 is busy)

**Note**: Next.js will automatically find an available port if 3000-3002 are occupied.

---

## 🖥️ Using the Application

### Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3001 (or check terminal output for actual port)
- **Backend API Docs**: http://localhost:8000/docs

### Demo Patient

The application comes with a pre-loaded demo patient:
- **Name**: María González Pérez
- **Age**: 52 years, Female
- **Condition**: Suspected diabetes mellitus type 2
- **Chief Complaint**: Polidipsia, poliuria, pérdida de peso
- **Comorbidities**: Hypertension (controlled with Losartán)
- **Labs**: Glucose 185 mg/dL, HbA1c 8.5%

### Clinical Workflow

1. **Patient Summary** (Right Panel)
   - Automatically loads when you open the app
   - Shows: One-liner summary, medications, contraindications, risk factors

2. **Historia Clínica** (Left Panel - Historia Clínica Tab)
   - Enter the patient's clinical history
   - Example from `DEMO_PATIENT_DIABETES.md`:
     ```
     Paciente femenina de 52 años de edad que acude a consulta por cuadro
     de aproximadamente 3 meses de evolución caracterizado por polidipsia,
     poliuria y pérdida de peso no intencionada de 5 kg.
     ```

3. **Examen Físico** (Left Panel - Examen Físico Tab)
   - Document physical examination findings
   - Example:
     ```
     TA: 130/85 mmHg, FC: 78 lpm, Peso: 82 kg, Talla: 160 cm, IMC: 32.0 kg/m²
     ```

4. **Generate Clinical Assessment** (Evaluación Tab)
   - Click "Generar Evaluación" button
   - Receives AI-generated differential diagnoses
   - Gets physical exam maneuver suggestions
   - Identifies red flags

5. **Generate Clinical Plan** (Plan Tab)
   - Click "Generar Plan" button
   - **RAG retrieves evidence** from clinical guidelines
   - LLM generates complete treatment plan with:
     - Differential diagnoses with rationale
     - Laboratory test recommendations
     - Medication prescriptions with Mexican brand names
     - Safety alerts (allergies, interactions)
     - Patient instructions in Spanish

---

## 🧪 Testing

### Test RAG Integration

```bash
cd /home/jpcar/personal-projects/medicopilot
source backend/venv/bin/activate
python tests/test_rag.py
```

Expected output:
```
✅ Weaviate connection successful
Total chunks in database: 347
✅ RAG search successful
Found 3 results (diabetes-related)
```

### Test Diabetes Demo Patient RAG Queries

```bash
python tests/test_diabetes_rag.py
```

This tests:
- Clinical plan queries for diabetes
- Metformin treatment recommendations
- Complications and monitoring guidelines

Expected: High certainty scores (0.7-0.8+) for diabetes-related queries

### Test All Endpoints

```bash
python tests/test_endpoints.py
```

Tests all backend API endpoints including patient summary, clinical assessment, and plan generation.

### Test API Endpoints Directly

```bash
# Health check
curl http://localhost:8000/api/health

# Get patient data
curl http://localhost:8000/api/patients/patient-001

# Generate patient summary (requires JSON payload)
curl -X POST http://localhost:8000/api/patients/summary \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-001",
    "chief_complaint": "polidipsia, poliuria, pérdida de peso",
    "snapshot": {
      "patient_id": "patient-001",
      "name": "María González Pérez",
      "age": 52,
      "sex": "F",
      "weight_kg": 82,
      "allergies": [],
      "active_medications": ["Losartán 50 mg"]
    }
  }'
```

### End-to-End Testing (Playwright)

```bash
# Install Playwright (one-time setup)
cd /home/jpcar/personal-projects/medicopilot
npm install -D playwright
npx playwright install chromium

# Run E2E test
node tests/e2e-test-diabetes.js
```

---

## 📁 Project Structure

```
medicopilot/
├── backend/                      # Python/FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   ├── config/
│   │   │   └── settings.py      # Configuration & environment variables
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   ├── rag/                 # RAG pipeline
│   │   │   ├── embeddings.py   # Saptiva embeddings service
│   │   │   ├── vectorstore.py  # Weaviate vector database client
│   │   │   └── pipeline.py     # RAG orchestration
│   │   ├── services/
│   │   │   ├── llm_service.py  # Saptiva LLM client
│   │   │   └── clinical_service.py  # Clinical AI operations
│   │   └── main.py             # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables (create this)
│
├── frontend/                    # Next.js/React frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Main application page
│   │   │   └── layout.tsx      # Root layout
│   │   ├── components/         # React components
│   │   ├── services/
│   │   │   └── api.ts          # Backend API client
│   │   └── types/              # TypeScript definitions
│   ├── package.json
│   └── .env.local              # Environment variables (create this)
│
├── tests/                       # Test files
│   ├── test_rag.py             # RAG integration tests
│   ├── test_diabetes_rag.py    # Diabetes-specific RAG tests
│   ├── test_endpoints.py       # API endpoint tests
│   ├── test_weaviate_connection.py  # Weaviate connection tests
│   └── e2e-test-diabetes.js    # Playwright E2E test
│
├── scripts/                     # Utility scripts
│   ├── ingest_documents.py     # Document ingestion to Weaviate
│   ├── upload_plm_to_weaviate.py  # PLM data upload
│   ├── extract_medications_from_gpc.py  # Extract medication data
│   ├── generate_plm_fake_data.py  # Generate test data
│   └── clear_cofepris.py       # Database cleanup
│
├── docs/
│   ├── ARCHITECTURE.md         # System architecture
│   ├── SAPTIVA_INTEGRATION.md  # Saptiva integration guide
│   └── WEAVIATE_INTEGRATION_GUIDE.md  # Weaviate setup
│
├── DEMO_PATIENT_DIABETES.md    # Demo patient data
├── INTEGRATION_STATUS.md       # Integration status report
├── CLAUDE.md                   # Project context (for AI assistant)
└── README.md                   # This file
```

---

## 🔧 Configuration Reference

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SAPTIVA_API_KEY` | ✅ Yes | Saptiva AI API key | `sk_live_...` |
| `SAPTIVA_OPS_MODEL` | ✅ Yes | LLM model for clinical operations | `saptiva-1` |
| `WEAVIATE_URL` | ✅ Yes | Weaviate cluster URL | `https://xyz.weaviate.cloud` |
| `WEAVIATE_API_KEY` | ✅ Yes | Weaviate API key | `abc123...` |
| `API_V1_PREFIX` | ⬜ No | API route prefix | `/api` (default) |
| `TEMPERATURE` | ⬜ No | LLM temperature | `0.3` (default) |
| `MAX_TOKENS` | ⬜ No | LLM max tokens | `6000` (default) |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | ✅ Yes | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_USE_MOCK_DATA` | ⬜ No | Use mock data (dev only) | `false` (default) |

---

## 🐛 Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'weaviate'"

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install weaviate-client==4.17.0
```

#### "Connection refused" when calling backend

**Check**:
1. Is the backend running? Look for `Uvicorn running on http://127.0.0.1:8000`
2. Is it on the correct port? Default is 8000
3. Check logs for errors: Look at terminal where backend is running

**Solution**:
```bash
# Restart backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

#### "422 Unprocessable Entity" errors

**Common causes**:
- Missing required fields in request payload
- Type mismatch (e.g., sending string instead of number)
- Check API docs at http://localhost:8000/docs for correct schema

### Frontend Issues

#### "Failed to load resource: net::ERR_CONNECTION_REFUSED"

**Solution**:
1. Ensure backend is running on http://localhost:8000
2. Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
3. Verify CORS settings in `backend/app/config/settings.py`

#### "CORS policy: No 'Access-Control-Allow-Origin'"

**Solution**:
Check that your frontend port is listed in `backend/app/config/settings.py`:
```python
CORS_ORIGINS: list = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3003",  # Add your port here
]
```

Restart backend after changing CORS settings.

#### Frontend stuck on "Cargando datos del paciente..."

**Check**:
1. Open browser console (F12) and look for errors
2. Verify `NEXT_PUBLIC_USE_MOCK_DATA=false` in `.env.local`
3. Check Network tab in browser dev tools for failed requests

**Solution**:
```bash
# Restart frontend
cd frontend
npm run dev
```

### RAG/Weaviate Issues

#### "Weaviate is not ready"

**Check**:
1. Verify `WEAVIATE_URL` and `WEAVIATE_API_KEY` in `.env`
2. Check internet connection (Weaviate Cloud requires internet)
3. Verify Weaviate cluster is running in Weaviate Console

**Test connection**:
```bash
cd /home/jpcar/personal-projects/medicopilot
source backend/venv/bin/activate
python tests/test_rag.py
```

#### "No results found" in RAG queries

**Possible causes**:
- Database is empty (no documents ingested)
- Query embeddings not matching document content
- Certainty threshold too high (try lowering from 0.7 to 0.6)

**Check database stats**:
```python
from app.rag.pipeline import rag_pipeline
stats = rag_pipeline.get_stats()
print(stats)  # Should show total_chunks > 0
```

---

## 🔌 API Endpoints

### Patient Endpoints

#### `GET /api/patients/{patient_id}`
Get patient demographic and clinical data.

**Response**: `PatientSnapshot`
```json
{
  "patient_id": "patient-001",
  "name": "María González Pérez",
  "age": 52,
  "sex": "F",
  "weight_kg": 82,
  "allergies": [],
  "active_medications": ["Losartán 50 mg"],
  "chief_complaint": "polidipsia, poliuria, pérdida de peso",
  "recent_labs": [...]
}
```

#### `POST /api/patients/summary`
Generate LLM-powered patient summary.

**Request**: `PatientSummaryRequest`
```json
{
  "patient_id": "patient-001",
  "chief_complaint": "polidipsia, poliuria",
  "snapshot": { ... }
}
```

**Response**: `PatientSummaryResponse`
```json
{
  "critical_alerts": {
    "allergies": [],
    "active_conditions": ["Hipertensión arterial"],
    "risk_factors": ["Edad > 50 años", "Obesidad"]
  },
  "one_liner": "52F, hipertensión arterial, TFG normal, sin alergias, polidipsia, poliuria",
  ...
}
```

### Clinical Assistance Endpoints

#### `POST /api/assist/clinical-assessment`
Generate differential diagnoses and physical exam suggestions.

**Request**: `ClinicalAssessmentRequest`
```json
{
  "historia_clinica": "Paciente con polidipsia...",
  "snapshot": { ... }
}
```

**Response**: Differential diagnoses, physical exam maneuvers, red flags

#### `POST /api/plan/generate`
Generate complete clinical plan with RAG-retrieved evidence.

**Request**: `PlanRequest`
```json
{
  "soap_summary": {
    "subjective": "Polidipsia, poliuria, pérdida de peso",
    "objective": "Glucosa 185 mg/dL, HbA1c 8.5%"
  },
  "snapshot": { ... }
}
```

**Response**: Complete plan with medications, labs, alerts, citations from GPC

### Utility Endpoints

#### `GET /api/health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "MediCopilot Nexus API",
  "version": "0.1.0"
}
```

---

## 📊 RAG System Details

### Document Collection

- **Total Chunks**: 347
- **Source**: Mexican GPC (Guías de Práctica Clínica)
- **Topics**: Diabetes, Pharyngitis, Hypertension, Dyslipidemia, Pneumonia
- **Vector Dimensions**: 1024 (Saptiva Embed)
- **Similarity Metric**: Cosine similarity
- **Default Threshold**: 0.7 certainty

### Query Examples

**Diabetes Treatment**:
```python
results = await rag_pipeline.search(
    query="diabetes tipo 2 tratamiento primera línea",
    top_k=3,
    namespace_filter="gpc",
    min_certainty=0.7
)
# Returns: Metformin recommendations with 0.82 certainty
```

**Clinical Criteria**:
```python
results = await rag_pipeline.search(
    query="criterios diagnóstico diabetes HbA1c glucosa",
    top_k=5,
    namespace_filter="gpc"
)
# Returns: ADA 2018 diagnostic criteria
```

---

## 🤝 Contributing

This is a hackathon project (October 2025). For questions or contributions:

1. Check existing documentation in `/docs`
2. Review `INTEGRATION_STATUS.md` for current status
3. Run tests before submitting changes
4. Ensure CORS and API paths are correctly configured

---

## 📄 License

TBD (pending hackathon completion)

---

## 👥 Credits

- **Framework**: Built with Saptiva AI and Ragster
- **Vector Database**: Weaviate Cloud
- **Clinical Guidelines**: Mexican GPC (Guías de Práctica Clínica)
- **Developed by**: Juan Pablo (with AI coding assistance from Claude Code)
- **Hackathon**: Saptiva AI Healthcare Challenge - October 2025

---

## 🆘 Support

For issues or questions:

1. **Check Documentation**:
   - `INTEGRATION_STATUS.md` - Current integration status
   - `ARCHITECTURE.md` - System architecture
   - `WEAVIATE_INTEGRATION_GUIDE.md` - RAG setup

2. **Common Issues**: See Troubleshooting section above

3. **Test Files**:
   - `tests/test_rag.py` - Test RAG connectivity
   - `tests/test_diabetes_rag.py` - Test diabetes queries
   - `tests/test_endpoints.py` - Test all API endpoints
   - `tests/e2e-test-diabetes.js` - Full integration test

---

**Status**: ✅ **READY FOR DEMO** (100% Integration Complete)

**Last Updated**: 2025-10-24
**Version**: 0.1.0 (Hackathon Demo)
