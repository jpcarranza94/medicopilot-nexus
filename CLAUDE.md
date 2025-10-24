# MediCopilot Nexus

## Project Overview

MediCopilot Nexus is an AI-powered medical assistant designed to support doctors during their daily patient consultations. Unlike traditional Electronic Health Record (EHR) systems that force doctors to change their workflow, MediCopilot works alongside physicians in the way they're already accustomed to working—like a trusted colleague or supervising physician.

## The Problem

Many doctors, especially in private practice or smaller clinics, still rely on paper notes or Word documents to track patient information. They avoid complex EHR systems because:
- They disrupt the natural flow of consultation
- They require extensive data entry
- They focus on billing/compliance rather than clinical support
- They don't provide real-time decision support

## Our Solution

MediCopilot Nexus provides intelligent, contextual assistance throughout the three main phases of a medical consultation:

### 1. Anamnesis (Medical History)
- Doctor writes freely in natural language
- System suggests relevant follow-up questions in real-time
- Recommends clinical scoring tools (e.g., Centor criteria for pharyngitis)
- Highlights red flags based on patient history

### 2. Physical Examination
- Suggests specific physical maneuvers based on symptoms
- Guides what to look for during examination
- Helps document findings systematically

### 3. Clinical Assessment & Plan
- Proposes differential diagnoses with rationale
- Recommends laboratory tests following institutional guidelines
- Suggests appropriate medications with:
  - Automatic allergy checking
  - Drug interaction warnings
  - Commercial names and presentations (Mexico-specific via PLM/COFEPRIS)
  - Dosing guidance considering patient factors (pregnancy, renal function, etc.)

## Key Features

- **Patient Context Awareness**: Full access to patient history, generating pre-visit summaries
- **RAG-Powered Intelligence**: Trained on clinical practice guidelines (GPC), Mexican regulations (NOM), and pharmaceutical databases
- **Real-time Suggestions**: Low-latency responses during note-taking (<2 seconds)
- **Safety First**: Built-in guardrails for allergies, drug interactions, pregnancy, and renal function
- **Compliance Ready**: Follows NOM-004-SSA3-2012 (clinical records) and NOM-024-SSA3-2012 (electronic health systems)
- **Mexican Healthcare Context**: Integrated with COFEPRIS registries and PLM (Diccionario de Especialidades Farmacéuticas)

## Technology Stack

### AI & LLM
- **Saptiva Agents**: Multi-agent orchestration framework
  - Fast model (SAPTIVA_LEGACY) for real-time suggestions
  - Capable model (SAPTIVA_OPS) for clinical planning
- **Saptiva Embeddings API**: 1024-dimensional vectors for semantic search

### RAG & Knowledge Base
- **Ragster Pipeline**: Document processing (adapted from TypeScript to Python)
- **Weaviate Cloud**: Vector database for semantic search
- **Knowledge Sources**:
  - GPC (Guías de Práctica Clínica - Mexico)
  - NOM (Normas Oficiales Mexicanas)
  - PLM (pharmaceutical database)
  - COFEPRIS (drug registries)

### Standards & Interoperability
- **RxNorm**: Drug normalization
- **ATC/WHO**: Drug classification

### Backend & Infrastructure
- **FastAPI**: Python async API framework
- **PostgreSQL**: Structured data (patients, encounters, drug mappings)
- **Redis**: Caching layer (optional for MVP)

### Frontend
- **React/Next.js**: Dual-column interface
- **TypeScript**: Type safety
- **TailwindCSS**: Styling

## Target Users

Primary: General practitioners and specialists in private practice or small clinics who want clinical decision support without the overhead of traditional EHR systems.

## Development Approach

This project is being built for a hackathon with a modular architecture that enables parallel work:
- **Backend Engineer**: RAG pipeline, Saptiva Agents integration, API endpoints
- **Frontend Engineer**: Dual-column interface, real-time UI updates, export functionality
- **Main Orchestrator**: Architecture design, task coordination, documentation

## Demo Scope (Hackathon - Oct 24, 2025)

For the initial demo, we're focusing on:
- **2 clinical scenarios**: Pharyngitis and Urinary Tract Infection (UTI)
- **6-10 documents**: GPC excerpts, NOM sections, PLM drug info
- **6-8 medications**: Full Mexican commercial mappings
- **Real-time assistance**: Suggestions appear while typing clinical notes
- **Safety alerts**: Allergy checking, drug interactions
- **Export capability**: SOAP note, prescription, patient instructions

## Vision

Transform the doctor-patient consultation by providing the equivalent of a highly knowledgeable medical colleague who:
- Never gets tired
- Has instant access to all guidelines and drug information
- Catches potential safety issues
- Handles documentation burden
- Respects the doctor's workflow and autonomy

## Project Structure

```
medicopilot/
├── backend/              # Python/FastAPI backend
│   ├── rag/             # RAG pipeline (Ragster-based)
│   ├── services/        # Saptiva Agents
│   ├── api/             # FastAPI endpoints
│   ├── db/              # Database connections
│   └── data/            # Documents, drug mappings
├── frontend/            # Next.js/React frontend
│   ├── src/
│   │   ├── app/        # Pages
│   │   ├── components/ # UI components
│   │   ├── services/   # API client
│   │   └── types/      # TypeScript definitions
│   └── public/
├── docs/
│   ├── ARCHITECTURE.md          # System architecture
│   ├── SAPTIVA_INTEGRATION.md   # Saptiva integration details
│   └── WORK_BREAKDOWN.md        # Parallel task breakdown
├── ragster/             # Saptiva Ragster (submodule/reference)
└── CLAUDE.md            # This file
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Saptiva API key (from [lab.saptiva.com](https://lab.saptiva.com))
- Weaviate Cloud account

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Create .env file with API keys
cp .env.example .env
# Edit .env with your credentials

# Run FastAPI server
uvicorn api.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local

# Run Next.js dev server
npm run dev  # Runs on http://localhost:3000
```

### Document Ingestion
```bash
cd backend
python -m rag.pipeline ingest data/docs/GPC_Faringitis.pdf --namespace gpc
python -m rag.pipeline ingest data/docs/GPC_ITU.pdf --namespace gpc
```

## Documentation

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)**: Complete system architecture with Saptiva integration
- **[SAPTIVA_INTEGRATION.md](./docs/SAPTIVA_INTEGRATION.md)**: Detailed Saptiva Agents and Ragster integration guide
- **[WORK_BREAKDOWN.md](./docs/WORK_BREAKDOWN.md)**: Parallel task breakdown for backend and frontend engineers

## Timeline (Hackathon Day)

| Time | Backend | Frontend |
|------|---------|----------|
| 09:00-10:00 | Setup + RAG pipeline skeleton | Setup + UI layout |
| 10:00-11:30 | RAG implementation | API client + types |
| 11:30-12:30 | Document ingestion + drug map | Patient snapshot |
| 12:30-13:00 | **Lunch Break** | **Lunch Break** |
| 13:00-14:30 | Saptiva Agents implementation | Real-time HPI suggestions |
| 14:30-16:00 | API endpoints | Plan generation UI |
| 16:00-17:00 | Integration testing | Export + polish |
| 17:00-17:30 | Support frontend | Demo prep |
| 17:30-18:00 | **Video Recording** | **Video Recording** |

## Demo Video Outline (60 seconds)

1. **0-10s**: Intro - "MediCopilot Nexus: tu asistente clínico inteligente"
2. **10-30s**: Show real-time HPI suggestions as doctor types
3. **30-50s**: Generate clinical plan with safety alerts (allergy to penicillin)
4. **50-60s**: Export SOAP note and prescription; closing with Saptiva/Ragster credits

## API Endpoints (Contract)

### `POST /assist/hpi` - Real-time Suggestions
- **Input**: HPI text tail (300-600 chars) + patient snapshot
- **Output**: Suggested questions, red flags, clinical scores (JSON)
- **Latency**: <2 seconds

### `POST /plan/generate` - Clinical Plan
- **Input**: SOAP summary + patient snapshot
- **Output**: Differentials, labs, medications with brands, safety alerts, patient instructions (JSON)
- **Latency**: <5 seconds

### `GET /patients/{id}` - Patient Data
- **Output**: Demographics, allergies, active meds, vital signs

## License

TBD (pending hackathon completion)

---

**Status**: Active Development for October 24, 2025 Hackathon
**Team**: Solo developer (Juan Pablo) with AI coding assistance (Claude Code)
**Hackathon**: Saptiva AI Healthcare Challenge
**Deliverable**: 60-second demo video by 5:59 PM
