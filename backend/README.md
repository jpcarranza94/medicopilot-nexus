# MediCopilot Nexus - Backend API

Minimal backend focused on LLM calls for clinical assistance using Saptiva AI.

## Architecture

This backend is designed to be minimal and focused:
- **Patient data is mocked in the frontend** and passed to the backend
- **Backend only handles LLM processing** using Saptiva API
- No database required for MVP
- FastAPI for high performance async API

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your SAPTIVA_API_KEY
```

### 3. Run the Server

```bash
# From the backend directory
uvicorn app.main:app --reload --port 8000
```

Or using Python directly:

```bash
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### 1. Patient Summary
`POST /api/patients/summary`

Generates an intelligent clinical summary from patient snapshot data.

### 2. Clinical Assessment
`POST /api/assist/clinical-assessment`

Generates differential diagnoses and physical exam suggestions based on clinical history.

### 3. Clinical Plan
`POST /api/plan/generate`

Generates complete clinical plan with medications, labs, and patient instructions.

## Testing

Run the backend and visit http://localhost:8000/docs for interactive API testing via Swagger UI.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py          # FastAPI routes
│   ├── services/
│   │   ├── llm_service.py     # Saptiva LLM integration
│   │   └── clinical_service.py # Clinical AI services
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── config/
│   │   └── settings.py        # Configuration
│   └── main.py                # FastAPI app
├── requirements.txt
├── .env.example
└── README.md
```

## Development Notes

- The backend is stateless - all patient data comes from the frontend
- LLM calls use Saptiva OPS model for clinical decision-making
- Temperature is set to 0.3 for medical accuracy
- All responses are in Spanish (Mexican medical terminology)
