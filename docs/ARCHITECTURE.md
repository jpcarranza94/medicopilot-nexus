# MediCopilot Nexus - System Architecture

## Architecture Overview

MediCopilot Nexus follows a modular, microservices-inspired architecture optimized for real-time clinical decision support. The system integrates **Saptiva's infrastructure** (Ragster for RAG and Saptiva Agents for LLM orchestration) to provide intelligent medical assistance during patient consultations.

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React/Next.js)                      │
│  ┌──────────────────┐  ┌────────────────────────────────────┐  │
│  │  SOAP Editor     │  │   Assistant Panel (Tabs)           │  │
│  │  (Left Column)   │  │   - Patient Snapshot               │  │
│  │                  │  │   - Suggestions                    │  │
│  │  - Free text     │  │   - Plan Generator                 │  │
│  │  - SOAP sections │  │   - Citations/Sources              │  │
│  └──────────────────┘  └────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────────┘
                        │ REST API / SSE (Streaming)
┌───────────────────────┴─────────────────────────────────────────┐
│                    API Gateway (FastAPI)                         │
│                 - Routing                                        │
│                 - Request validation                             │
└──┬────────────┬────────────┬─────────────┬──────────────┬───────┘
   │            │            │             │              │
   │    ┌───────▼────────┐   │             │              │
   │    │  RAG Module    │   │             │              │
   │    │  (Ragster)     │◄──┘             │              │
   │    │                │                 │              │
   │    │ - Ingest       │                 │              │
   │    │ - Chunk        │                 │              │
   │    │ - Embed        │                 │              │
   │    │ - Retrieve     │                 │              │
   │    └────┬───────────┘                 │              │
   │         │                             │              │
   ▼         ▼                             ▼              ▼
┌──────────────────┐              ┌─────────────────────────────┐
│ Saptiva Agents   │              │    Data Layer               │
│ (Multi-Agent)    │              │                             │
│                  │              │  ┌──────────────────────┐   │
│ ┌──────────────┐ │              │  │   Weaviate Cloud     │   │
│ │  QA Agent    │ │              │  │   (Vector DB)        │   │
│ │  (RAG-based) │ │              │  │                      │   │
│ └──────────────┘ │              │  │  - DocumentChunk     │   │
│                  │              │  │  - Embeddings        │   │
│ ┌──────────────┐ │              │  └──────────────────────┘   │
│ │ Assist Agent │ │              │                             │
│ │ (Real-time)  │ │              │  ┌──────────────────────┐   │
│ └──────────────┘ │              │  │   PostgreSQL         │   │
│                  │              │  │                      │   │
│ ┌──────────────┐ │              │  │  - Patients          │   │
│ │  Plan Agent  │ │              │  │  - Encounters        │   │
│ │ (Clinical)   │ │              │  │  - Drug mappings     │   │
│ └──────────────┘ │              │  │  - Allergies         │   │
│                  │              │  └──────────────────────┘   │
│ ┌──────────────┐ │              │                             │
│ │ DrugMap Agent│ │              │  ┌──────────────────────┐   │
│ │              │ │              │  │      Redis           │   │
│ └──────────────┘ │              │  │                      │   │
└──────────┬───────┘              │  │  - RAG cache         │   │
           │                      │  │  - Session cache     │   │
           ▼                      │  └──────────────────────┘   │
  ┌─────────────────┐             └─────────────────────────────┘
  │  Saptiva API    │
  │                 │
  │ - SAPTIVA_OPS   │             ┌─────────────────────────────┐
  │ - SAPTIVA_LEGACY│             │   Document Sources          │
  │ - SAPTIVA_CORTEX│             │                             │
  │ - Embeddings    │             │  - GPC (Guías Clínicas)     │
  └─────────────────┘             │  - NOM (Regulaciones)       │
                                  │  - PLM (Fármacos)           │
                                  │  - COFEPRIS (Registros)     │
                                  └─────────────────────────────┘
```

## Core Technology Stack

### AI & LLM Layer
- **Saptiva API (Direct HTTP calls)**: No SDK needed, simple REST API integration
  - Chat Completions: `POST https://api.saptiva.com/v1/chat/completions`
  - Embeddings: `POST https://api.saptiva.com/api/embed`
- **Models Available**:
  - `saptiva-legacy` (llama3.3:70b): Fast model for real-time suggestions
  - `saptiva-ops`: General clinical reasoning and planning
  - `saptiva-cortex` (qwen3-tk:30b): Complex reasoning tasks (optional)
- **Authentication**: Simple Bearer token via `Authorization: Bearer {SAPTIVA_API_KEY}`

### RAG & Knowledge Base
- **Ragster**: Document processing and RAG pipeline (adapted from TypeScript to Python)
- **Weaviate Cloud**: Vector database for semantic search
- **Document Processing**: PyPDF2, python-docx for PDF/DOCX extraction
- **Knowledge Sources**:
  - GPC (Guías de Práctica Clínica - Mexico)
  - NOM-004-SSA3-2012 (Clinical records standard)
  - NOM-024-SSA3-2012 (Electronic health systems)
  - PLM (Diccionario de Especialidades Farmacéuticas)
  - COFEPRIS (Drug registries)

### Standards & Interoperability
- **RxNorm**: Drug normalization (ingredient mapping)
- **ATC/WHO**: Drug classification
- **SNOMED CT**: Clinical terminology (future)

### Security & Compliance
- **Presidio**: PHI/PII masking in logs
- **LlamaGuard**: Content safety validation
- **NOM Compliance**: Follows Mexican healthcare standards

### Observability & Quality
- **Langfuse**: LLM call tracing, token usage, latency monitoring
- **Structured Logging**: JSON logs with request_id correlation

### Backend & Infrastructure
- **FastAPI**: Python async API framework
- **PostgreSQL**: Structured data (patients, encounters, drug mappings)
- **Redis**: Caching layer (RAG results, session data)
- **Docker**: Containerization (future deployment)

### Frontend
- **React/Next.js**: Dual-column interface
- **TailwindCSS**: Styling
- **TypeScript**: Type safety

---

## Module Specifications

### 1. RAG Module (Ragster-based)

**Purpose**: Document ingestion, chunking, embedding generation, and semantic retrieval.

**Technology**: Python port of Ragster's proven TypeScript pipeline.

#### Sub-modules:

**A. Document Processor (`rag/ingest.py`)**

**Responsibilities**:
- Extract text from PDF, DOCX, TXT files
- Split into chunks (800 chars, 80 char overlap)
- Respect sentence/paragraph boundaries
- Generate rich metadata

**Chunking Strategy**:
```python
{
  "chunk_size": 800,  # characters
  "overlap": 80,
  "strategy": "sentence-aware",  # Respects paragraph boundaries
  "metadata": {
    "sourceName": "GPC_Faringitis_2019.pdf",
    "sourceType": ".pdf",
    "sourceNamespace": "gpc",  # gpc|nom|plm|cofepris
    "chunkIndex": 0,
    "totalChunks": 45,
    "uploadDate": "2025-10-24T14:00:00Z",
    "prevChunkIndex": null,
    "nextChunkIndex": 1
  }
}
```

**B. Embedding Service (`rag/embeddings.py`)**

**Provider**: Saptiva Embeddings API

**Features**:
- 1024-dimensional vectors
- Retry logic (max 2 retries, 1s backoff)
- Rate limiting (500ms delay between requests)
- Batch processing support

**API Endpoint**: `https://api.saptiva.com/api/embed`

**C. Vector Store (`rag/vectorstore.py`)**

**Database**: Weaviate Cloud

**Schema**: `DocumentChunk` collection
```python
{
  "class": "DocumentChunk",
  "properties": [
    {"name": "text", "dataType": ["text"]},
    {"name": "sourceName", "dataType": ["text"]},
    {"name": "sourceType", "dataType": ["text"]},
    {"name": "sourceNamespace", "dataType": ["text"]},
    {"name": "uploadDate", "dataType": ["text"]},
    {"name": "chunkIndex", "dataType": ["int"]},
    {"name": "totalChunks", "dataType": ["int"]},
    {"name": "prevChunkIndex", "dataType": ["int"]},
    {"name": "nextChunkIndex", "dataType": ["int"]}
  ],
  "vectorizer": "none"  # Manual embeddings via Saptiva
}
```

**Operations**:
- `insert_chunks()`: Batch insert with embeddings
- `search()`: Semantic search with metadata filters
- `delete_collection()`: Reset database

**D. RAG Pipeline (`rag/pipeline.py`)**

**Complete Flow**:
```
Document File → Extract Text → Chunk → Generate Embeddings → Insert to Weaviate
     ↓              ↓            ↓              ↓                    ↓
  PDF/DOCX      PyPDF2     800 chars    Saptiva API         Vector Storage
```

**Search Flow**:
```
User Query → Generate Embedding → Vector Search → Top-K Results → Citations
     ↓              ↓                    ↓              ↓              ↓
  "Centor"    Saptiva API           Weaviate      3 passages    Source refs
```

**Interface**:
```python
class RAGPipeline:
    async def ingest_document(file_path: str, namespace: str) -> Dict
    async def ingest_multiple(file_paths: List[str], namespace: str) -> List[Dict]
    async def search(query: str, top_k: int, namespace_filter: str) -> List[Dict]
```

---

### 2. Saptiva LLM Services Module

**Purpose**: Direct API integration with Saptiva for clinical decision support.

**Implementation**: Simple HTTP clients using `httpx` (async HTTP library)

**Base Saptiva Client** (`services/saptiva_client.py`):

```python
import httpx
import os
from typing import List, Dict, Optional, AsyncGenerator
import json

class SaptivaClient:
    """Direct Saptiva API client - no SDK needed"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SAPTIVA_API_KEY")
        self.base_url = "https://api.saptiva.com"
        self.chat_url = f"{self.base_url}/v1/chat/completions"
        self.embed_url = f"{self.base_url}/api/embed"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "saptiva-ops",
        temperature: float = 0.3,
        max_tokens: int = 1500,
        stream: bool = False
    ) -> Dict | AsyncGenerator:
        """
        Call Saptiva chat completion API

        Args:
            messages: List of {"role": "system|user|assistant", "content": "..."}
            model: "saptiva-ops" | "saptiva-legacy" | "saptiva-cortex"
            temperature: 0.0-1.0
            max_tokens: Max response length
            stream: Enable streaming responses

        Returns:
            Dict with response or AsyncGenerator for streaming
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            if stream:
                return self._stream_response(client, payload, headers)
            else:
                response = await client.post(
                    self.chat_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()

    async def _stream_response(
        self,
        client: httpx.AsyncClient,
        payload: Dict,
        headers: Dict
    ) -> AsyncGenerator[str, None]:
        """Stream SSE responses from Saptiva"""
        async with client.stream(
            "POST",
            self.chat_url,
            json=payload,
            headers=headers
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        content = chunk["choices"][0]["delta"].get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector via Saptiva API

        Args:
            text: Input text

        Returns:
            1024-dimensional embedding vector
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.embed_url,
                json={"text": text},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", data.get("vector", []))
```

#### Service Specifications:

**A. QA Service (`services/qa_service.py`)**

**Purpose**: General clinical Q&A with RAG backing

**Model**: `saptiva-ops`

**Input**:
```python
{
  "question": "¿Cuándo solicitar test rápido para Streptococcus?",
  "patient_context": {
    "age": 28,
    "sex": "F",
    "allergies": ["penicilina"],
    "chief_complaint": "dolor de garganta"
  }
}
```

**Output**:
```python
{
  "answer": "El test rápido se recomienda cuando...",
  "citations": [
    {
      "source": "GPC_Faringitis_2019.pdf",
      "namespace": "gpc",
      "chunk_index": 12,
      "upload_date": "2025-10-24T..."
    }
  ],
  "confidence": "high"
}
```

**Workflow**:
1. Retrieve top-3 relevant passages from RAG
2. Build prompt with patient context + evidence
3. Call Saptiva agent with streaming
4. Extract and format citations
5. Log to Langfuse

**System Prompt**:
```
Eres un asistente clínico experto para médicos en México.

Responde basándote en las guías clínicas proporcionadas.
- Siempre cita la fuente
- Sé conciso y profesional
- Nunca inventes datos
- Si no tienes información, indícalo claramente
```

**B. Assist Agent (`services/agents/assist_agent.py`)**

**Purpose**: Real-time suggestions during anamnesis (HPI entry)

**Model**: `SAPTIVA_LEGACY` (faster for real-time)

**Latency Target**: <2 seconds

**Input**:
```python
{
  "hpi_tail": "últimos 300-600 caracteres del HPI",
  "snapshot": {
    "age": 28,
    "sex": "F",
    "allergies": ["penicilina"],
    "chief_complaint": "dolor de garganta"
  }
}
```

**Output** (JSON strict):
```python
{
  "suggested_questions": [
    "¿Presencia de exudado faríngeo?",
    "¿Adenopatías cervicales anteriores?",
    "¿Fiebre >38°C?",
    "¿Ausencia de tos?"
  ],
  "red_flags": [
    "Dificultad respiratoria",
    "Trismus"
  ],
  "scores": [
    {
      "name": "Centor",
      "criteria": ["Exudado", "Adenopatía", "Fiebre", "Sin tos"],
      "why_it_matters": "Score ≥3 sugiere faringitis estreptocócica"
    }
  ]
}
```

**Optimization**:
- Debounce: 800ms on frontend before triggering
- AbortController: Cancel previous requests
- Optional RAG: Quick cache lookup for common patterns
- Temperature: 0.2 (more deterministic)
- Max tokens: 300

**Frontend Integration**:
```javascript
// Debounced onChange
useEffect(() => {
  const timer = setTimeout(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    fetchSuggestions(hpiText.slice(-600), patientSnapshot);
  }, 800);

  return () => clearTimeout(timer);
}, [hpiText]);
```

**C. Plan Agent (`services/agents/plan_agent.py`)**

**Purpose**: Comprehensive clinical plan generation

**Model**: `SAPTIVA_OPS` (more capable)

**Latency Target**: <5 seconds (acceptable for button-triggered action)

**Input**:
```python
{
  "soap_summary": {
    "subjective": "mujer 28 años, dolor faríngeo 3 días...",
    "objective": "exudado amigdalino bilateral, adenopatías..."
  },
  "snapshot": {
    "age": 28,
    "sex": "F",
    "weight_kg": 60,
    "pregnant": false,
    "egfr": 95,
    "allergies": ["penicilina"],
    "active_medications": ["anticonceptivo oral"]
  }
}
```

**Output** (JSON strict):
```python
{
  "differentials": [
    {
      "diagnosis": "Faringoamigdalitis estreptocócica",
      "probability": "high",
      "rationale": "Centor score 4/4: exudado + adenopatía + fiebre + sin tos"
    }
  ],
  "labs": [
    {
      "test": "Test rápido Streptococcus A",
      "indication": "Confirmar etiología estreptocócica",
      "priority": "high"
    }
  ],
  "medications": [
    {
      "generic": "Azitromicina",
      "dose": "500 mg",
      "route": "PO",
      "frequency": "cada 24h",
      "duration": "3 días",
      "rationale": "Primera línea en alergia a penicilina"
    }
  ],
  "alerts": [
    {
      "type": "allergy",
      "severity": "high",
      "message": "ALERGIA A PENICILINA - Evitar β-lactámicos",
      "action_taken": "Azitromicina seleccionada"
    }
  ],
  "patient_instructions": [
    "Tomar azitromicina 1 hora antes de alimentos",
    "Completar curso antibiótico",
    "Gárgaras con agua tibia con sal",
    "Regresar si: dificultad respiratoria, trismus, fiebre >3 días"
  ],
  "citations": [...]
}
```

**Workflow**:
1. Retrieve top-3 clinical guidelines (RAG) for treatment recommendations
2. Build comprehensive prompt with evidence + safety constraints
3. Call Saptiva agent with access to RAG tool for drug lookup (streaming)
4. Agent generates plan and automatically queries PLM documents via RAG tool when needed
5. Apply safety rules to validate output:
   - Check allergies
   - Check drug interactions (active meds)
   - Adjust for renal function (eGFR)
   - Check pregnancy/lactation contraindications
6. Parse and validate JSON response
7. Return with citations

**Note**: Drug brand information comes from PLM documents in vector DB. Agent queries RAG during plan generation when it needs specific drug presentations. No separate DrugMap service call needed.

**Safety Rules Engine**:
```python
class SafetyChecker:
    def check_allergies(med: str, allergies: List[str]) -> Optional[Alert]
    def check_interactions(med: str, active_meds: List[str]) -> Optional[Alert]
    def check_pregnancy(med: str, pregnant: bool) -> Optional[Alert]
    def check_renal(med: str, egfr: float) -> Optional[Alert]
```

**Temperature**: 0.3 (balanced creativity/consistency)

**Max Tokens**: 1500

**D. DrugMap Agent (`services/agents/drugmap_agent.py`)**

**Purpose**: Look up Mexican commercial drug brands and presentations using RAG or web search

**Model**: `SAPTIVA_OPS` with tool calling

**Approach**: Use Saptiva Agents' tool calling capability to either:
1. **RAG Tool**: Query PLM/COFEPRIS documents ingested into Weaviate
2. **Web Search Tool**: Real-time lookup on PLM or COFEPRIS websites (if available)

**Tools Available**:
```python
from saptiva_agents.tools import AgentTool

# Option 1: RAG Tool
class PLMLookupTool:
    async def search(self, ingredient: str, indication: str = None) -> str:
        """Search PLM documents in vector database"""
        query = f"presentaciones comerciales de {ingredient} en México"
        if indication:
            query += f" para {indication}"

        passages = await rag_pipeline.search(
            query=query,
            top_k=3,
            namespace_filter="plm"
        )
        return self._format_results(passages)

# Option 2: Web Search Tool (if Saptiva provides web search)
# Or simple HTTP fetch to structured API
```

**Input**:
```python
{
  "ingredient": "azitromicina",
  "indication": "faringitis"  # Optional context
}
```

**Output** (from agent reasoning + tool results):
```python
{
  "ingredient": "Azitromicina",
  "brands": [
    {
      "brand_name": "Azitro-500",
      "presentation": "500 mg tableta",
      "manufacturer": "Laboratorios X"  # If found
    },
    {
      "brand_name": "Azitromicina MK",
      "presentation": "500 mg tableta",
      "manufacturer": "MK Labs"
    }
  ],
  "source": "plm",  # or "cofepris" or "web_search"
  "note": "Múltiples presentaciones disponibles; verificar disponibilidad local"
}
```

**Implementation Strategy**:

1. **Simplest (MVP)**: Agent uses RAG to search PLM documents already ingested
   - No CSV needed
   - Just query vector DB with "presentaciones de [drug]"
   - Agent parses natural language results

2. **Alternative**: Agent returns generic format, UI shows simplified output
   - Instead of trying to perfectly structure brands, just return:
   ```python
   {
     "ingredient": "Azitromicina",
     "available_info": "Presentaciones comunes: Azitro-500, Azitromicina MK, en tabletas de 500mg",
     "source": "PLM database"
   }
   ```

**Advantage**: No manual CSV maintenance, leverages existing RAG infrastructure, more flexible

**E. Agent Orchestrator (`services/agents/orchestrator.py`)**

**Purpose**: Central coordinator for all agents

**Interface**:
```python
class AgentOrchestrator:
    def __init__(self):
        self.qa_agent = QAAgent()
        self.assist_agent = AssistAgent()
        self.plan_agent = PlanAgent()
        self.drugmap_agent = DrugMapAgent()

    async def handle_qa(question: str, patient_context: Dict) -> Dict
    async def handle_assist(hpi_tail: str, snapshot: Dict) -> Dict
    async def handle_plan(soap_summary: Dict, snapshot: Dict) -> Dict
    async def handle_drugmap(ingredient: str) -> Dict

    async def close_all(self):
        # Cleanup all agent connections
```

**Singleton Pattern**: One orchestrator per API server instance

---

### 3. Data Layer

**A. PostgreSQL (`db/postgres.py`)**

**Schema**:

```sql
-- Patients
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    sex CHAR(1) CHECK (sex IN ('M', 'F')),
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Allergies
CREATE TABLE allergies (
    allergy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(patient_id),
    allergen VARCHAR(255) NOT NULL,
    reaction VARCHAR(255),
    severity VARCHAR(50) CHECK (severity IN ('mild', 'moderate', 'severe')),
    verified BOOLEAN DEFAULT false
);

-- Active Medications
CREATE TABLE active_medications (
    medication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(patient_id),
    medication VARCHAR(255) NOT NULL,
    dose VARCHAR(100),
    frequency VARCHAR(100),
    start_date DATE,
    end_date DATE
);

-- Encounters
CREATE TABLE encounters (
    encounter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(patient_id),
    encounter_date TIMESTAMP NOT NULL,
    chief_complaint TEXT,
    hpi TEXT,
    physical_exam TEXT,
    assessment TEXT,
    plan TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drug Mappings
CREATE TABLE drug_mappings (
    drug_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rxnorm_ingredient VARCHAR(100),
    atc_code VARCHAR(20),
    generic_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    presentation VARCHAR(255),
    route VARCHAR(20),
    strength VARCHAR(100),
    cofepris_reg VARCHAR(100),
    plm_id VARCHAR(100),
    manufacturer VARCHAR(255),
    pregnancy_category CHAR(1),
    renal_adjustment BOOLEAN DEFAULT false,
    hepatic_adjustment BOOLEAN DEFAULT false
);
```

**B. Weaviate Cloud (`vectorstore`)**

**Connection**:
```python
import weaviate

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_HOST"),
    auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY"))
)
```

**Collection**: `DocumentChunk` (schema defined in RAG Module)

**C. Redis (`cache/redis.py`)**

**Usage**:
1. **RAG Query Cache**: TTL 15 minutes
   - Key: `rag:query:{hash(query)}`
   - Value: JSON list of passages

2. **Patient Snapshot Cache**: TTL 30 minutes
   - Key: `patient:snapshot:{patient_id}`
   - Value: JSON patient object

3. **Rate Limiting**: Token bucket
   - Key: `ratelimit:{user_id}`
   - Commands: INCR, EXPIRE

---

### 4. API Gateway (FastAPI)

**Purpose**: Route requests, apply middleware, handle streaming responses

**Endpoints**:

```python
# Clinical Q&A
POST /qa
Body: {"question": str, "patient_context": Dict}
Response: {"answer": str, "citations": List[Dict], "confidence": str}

# Real-time HPI Suggestions
POST /assist/hpi
Body: {"hpi_tail": str, "snapshot": Dict}
Response: {"suggested_questions": List[str], "red_flags": List[str], "scores": List[Dict]}

# Clinical Plan Generation
POST /plan/generate
Body: {"soap_summary": Dict, "snapshot": Dict}
Response: {
  "differentials": List[Dict],
  "labs": List[Dict],
  "medications": List[Dict],
  "alerts": List[Dict],
  "patient_instructions": List[str],
  "citations": List[Dict]
}

# Drug Mapping
GET /drugmap?ingredient={name}
Response: {"ingredient": str, "brands": List[Dict]}

# Patient Management
GET /patients/{id}
POST /patients
GET /patients/{id}/encounters
POST /patients/{id}/encounters
```

**Middleware Stack**:
```python
@app.middleware("http")
async def middleware_pipeline(request: Request, call_next):
    # 1. Request ID generation
    request_id = str(uuid.uuid4())

    # 2. Presidio PHI masking (on logging)
    # 3. LlamaGuard content safety check
    # 4. Rate limiting (Redis)
    # 5. Execute request
    response = await call_next(request)

    # 6. Langfuse logging
    # 7. Response time headers

    return response
```

**Streaming Support**:
```python
from fastapi.responses import StreamingResponse

@app.post("/plan/generate")
async def generate_plan_stream(request: PlanRequest):
    async def event_generator():
        async for chunk in orchestrator.handle_plan_stream(request):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

### 5. Frontend Application

**Purpose**: Dual-column interface for clinical note-taking with AI assistance

**Technology**: React + Next.js + TypeScript + TailwindCSS

**Layout**:

```
┌────────────────────────────────────────────────────────────┐
│  Header: [Patient: María G., 28F] [Save] [Export]         │
├──────────────────────────┬─────────────────────────────────┤
│  SOAP Editor (Left 55%)  │  Assistant Panel (Right 45%)   │
│                          │                                 │
│  [Tab: Subjetivo      ] │  [Snapshot│Sugerencias│Plan│...]│
│  ┌────────────────────┐ │  ┌──────────────────────────┐   │
│  │ Free text editor   │ │  │ 💡 Sugerencias           │   │
│  │                    │ │  │                          │   │
│  │ "Dolor de garganta │ │  │ ¿Exudado faríngeo?      │   │
│  │  3 días, fiebre,   │ │  │ [Insertar]              │   │
│  │  odinofagia..."    │ │  │                          │   │
│  │                    │ │  │ ¿Adenopatías?           │   │
│  │                    │ │  │ [Insertar]              │   │
│  └────────────────────┘ │  │                          │   │
│                          │  │ 🎯 Score de Centor      │   │
│  [Tab: Objetivo      ]  │  │ [ver detalle]           │   │
│  [Tab: Evaluación    ]  │  │                          │   │
│  [Tab: Plan          ]  │  │ [⚡ Cargando...]         │   │
│                          │  └──────────────────────────┘   │
│  [🔵 Generar Plan]      │                                 │
└──────────────────────────┴─────────────────────────────────┘
```

**Key Components**:

1. **SOAP Editor**:
   - Tabs: Subjetivo, Objetivo, Evaluación, Plan
   - Rich text with markdown support
   - Auto-save every 30s
   - Character counter
   - `onChange` → debounce 800ms → `/assist/hpi`

2. **Patient Snapshot Tab**:
   - Demographics (age, sex)
   - Allergies (highlighted in red)
   - Active medications
   - Recent labs with flags
   - Previous diagnoses

3. **Sugerencias Tab**:
   - Suggested questions (clickable to insert)
   - Red flags (highlighted)
   - Clinical scores with explanations
   - Skeleton loader during fetch

4. **Plan Tab**:
   - Differentials (expandable cards)
   - Labs recommended (checklist)
   - Medications with brand selector
   - Safety alerts (prominent)
   - Patient instructions (copyable)

5. **Fuentes Tab**:
   - Citations with source, section, date
   - Click to see full passage

**State Management**:
```typescript
interface EditorState {
  hpiText: string;
  objectiveText: string;
  assessmentText: string;
  planText: string;
  suggestions: Suggestions | null;
  loading: boolean;
  error: string | null;
}
```

---

> **Note**: Compliance (PHI masking, NOM validation) and Observability (Langfuse, metrics) have been moved to separate enhancement documents for optional implementation if time permits during the hackathon.

---

## Data Flow Examples

### Flow 1: Real-time HPI Suggestions

```
┌─────────┐    800ms debounce     ┌──────────┐
│ User    │───────────────────────>│ Frontend │
│ types   │                        └─────┬────┘
└─────────┘                              │
                                         │ POST /assist/hpi
                                         │ {hpi_tail, snapshot}
                                         ▼
                                   ┌─────────────┐
                                   │ API Gateway │
                                   │ - Presidio  │
                                   │ - LlamaGuard│
                                   └──────┬──────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ Assist Agent │
                                   │ (SAPTIVA     │
                                   │  LEGACY)     │
                                   └──────┬───────┘
                                          │
                                          │ Optional: RAG lookup
                                          │ (cached, 2 passages)
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ Saptiva API  │
                                   │ (Streaming)  │
                                   └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ JSON Parser  │
                                   │ + Validator  │
                                   └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ Langfuse Log │
                                   └──────┬───────┘
                                          │
                                          │ Response
                                          ▼
                                   ┌──────────────┐
                                   │ Frontend     │
                                   │ Render       │
                                   │ Suggestions  │
                                   └──────────────┘

Latency Target: <2 seconds
```

### Flow 2: Clinical Plan Generation

```
┌─────────┐                              ┌──────────┐
│ Doctor  │─── Click "Generar Plan" ────>│ Frontend │
│         │                              └─────┬────┘
└─────────┘                                    │
                                               │ POST /plan/generate
                                               │ {soap_summary, snapshot}
                                               ▼
                                         ┌─────────────┐
                                         │ API Gateway │
                                         └──────┬──────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │ Plan Agent   │
                                         └──────┬───────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          │                     │                     │
                          ▼                     ▼                     ▼
                    ┌──────────┐         ┌──────────┐         ┌──────────┐
                    │ RAG      │         │ DrugMap  │         │ Safety   │
                    │ Retrieve │         │ Service  │         │ Checker  │
                    │ (top-3)  │         │          │         │          │
                    └────┬─────┘         └────┬─────┘         └────┬─────┘
                         │                    │                    │
                         └────────────────────┴────────────────────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ Build Prompt │
                                       │ - Evidence   │
                                       │ - Constraints│
                                       │ - Few-shot   │
                                       └──────┬───────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ Saptiva API  │
                                       │ SAPTIVA_OPS  │
                                       │ (Streaming)  │
                                       └──────┬───────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ JSON Parser  │
                                       │ + Enrichment │
                                       │   (brands)   │
                                       └──────┬───────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ Validate     │
                                       │ - Allergies  │
                                       │ - Interactions│
                                       └──────┬───────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ Frontend     │
                                       │ Render Plan  │
                                       └──────────────┘

Latency Target: <5 seconds
```

### Flow 3: Document Ingestion

```
┌─────────────┐
│ CLI Command │
│ python rag/ │
│  ingest.py  │
│  --src docs/│
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Document         │
│ Processor        │
│ - Extract text   │
│ - Chunk (800ch)  │
└─────┬────────────┘
      │
      │ List of chunks with metadata
      │
      ▼
┌──────────────────┐
│ Embedding        │
│ Service          │
│ - Batch process  │
│ - 500ms delay    │
│ - 2 retries      │
└─────┬────────────┘
      │
      │ Embedding vectors
      │
      ▼
┌──────────────────┐
│ Weaviate         │
│ Vector Store     │
│ - Insert chunks  │
│ - With vectors   │
└─────┬────────────┘
      │
      ▼
┌──────────────────┐
│ Summary Report   │
│ - Chunks created │
│ - UUIDs returned │
└──────────────────┘
```

---

## Configuration

### Environment Variables

```bash
# .env

# Saptiva
SAPTIVA_API_KEY=your_api_key_from_lab_saptiva_com
SAPTIVA_API_BASE_URL=https://api.saptiva.com
EMBEDDING_API_URL=https://api.saptiva.com/api/embed

# Weaviate
WEAVIATE_HOST=your-cluster.weaviate.cloud
WEAVIATE_API_KEY=your_weaviate_api_key

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=medicopilot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# RAG Configuration
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=80
RAG_TOP_K=3

# LLM Configuration
LLM_MODEL_FAST=SAPTIVA_LEGACY
LLM_MODEL_PRO=SAPTIVA_OPS
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1500

# Security
PRESIDIO_ENABLED=true
LLAMAGUARD_ENABLED=false

# Observability
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LOG_LEVEL=INFO

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

### Python Dependencies

```txt
# requirements.txt

# Saptiva
saptiva-agents>=0.1.3

# Document Processing
PyPDF2>=3.0.0
python-docx>=1.1.0

# Vector Database
weaviate-client>=4.0.0

# API Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
httpx>=0.26.0

# Database
psycopg2-binary>=2.9.9
redis>=5.0.1

# Security
presidio-analyzer>=2.2.0
presidio-anonymizer>=2.2.0

# Observability
langfuse>=2.0.0

# Utilities
python-dotenv>=1.0.0
python-multipart>=0.0.6
```

---

## Development Roadmap

### Phase 0: Hackathon MVP (Friday, Oct 24, 2025)

**Timeline**: 9:00 AM - 5:59 PM

**Deliverable**: 60-second demo video

**Scope**:
- [ ] 2 clinical scenarios: Pharyngitis, UTI
- [ ] 6-10 documents ingested (GPC, NOM excerpts)
- [ ] 10-30 drug mappings (CSV)
- [ ] 3 core endpoints working: `/assist/hpi`, `/plan/generate`, `/drugmap`
- [ ] Dual-column frontend (basic)
- [ ] RAG pipeline functional
- [ ] Saptiva agents integrated
- [ ] Real-time suggestions working
- [ ] Plan generation with safety alerts
- [ ] Export SOAP note + prescription

**Time Allocation**:
- 09:00-09:30: Setup (repo, env vars)
- 09:30-10:30: RAG ingestion (60 min)
- 10:30-11:30: `/qa` endpoint (60 min)
- 11:30-12:30: Drug mappings (60 min)
- 12:30-13:00: Lunch + testing
- 13:00-14:30: Frontend base (90 min)
- 14:30-15:30: `/assist/hpi` (60 min)
- 15:30-16:15: `/plan/generate` (45 min)
- 16:15-16:45: Security/observability (30 min)
- 16:45-17:15: UI polish (30 min)
- 17:15-17:45: Video recording (30 min)
- 17:45-17:59: Upload video

### Phase 1: Post-Hackathon Enhancements

- [ ] User authentication (OAuth)
- [ ] Persistent patient records
- [ ] Expanded drug database (100+ medications)
- [ ] 10+ clinical scenarios
- [ ] Mobile-responsive UI
- [ ] PDF export with NOM-004 formatting

### Phase 2: Clinical Validation

- [ ] Pilot with 3-5 doctors
- [ ] Feedback iterations
- [ ] Accuracy validation
- [ ] Performance optimization
- [ ] Multi-tenant architecture

### Phase 3: Production

- [ ] FHIR interoperability
- [ ] EHR integration (API)
- [ ] Subscription model
- [ ] Cloud deployment (AWS/GCP)

---

## Key Design Decisions

### 1. Why Saptiva Agents over Direct API Calls?

| Aspect | Direct API | Saptiva Agents |
|--------|-----------|----------------|
| Structure | Manual orchestration | Framework-provided |
| Tool Calling | Custom implementation | Built-in support |
| Multi-Agent | Complex coordination | RoundRobinGroupChat |
| Streaming | Manual SSE handling | Native support |
| Observability | Custom logging | Built-in tracing |
| Mexican Spanish | Standard models | Optimized models |

**Decision**: Use Saptiva Agents for structure, tool support, and Mexican context.

### 2. Why Ragster over LangChain Directly?

| Aspect | LangChain Direct | Ragster |
|--------|------------------|---------|
| Chunking | Basic splitter | Sentence-aware |
| Metadata | Manual | Rich, structured |
| Pipeline | Build from scratch | Proven pipeline |
| Rate Limiting | Custom | Built-in (500ms) |
| Retry Logic | Manual | 2 retries, backoff |

**Decision**: Port Ragster's proven pipeline to Python for reliability.

### 3. Why Dual LLM Approach?

| Use Case | Model | Rationale |
|----------|-------|-----------|
| Real-time suggestions | SAPTIVA_LEGACY | Faster (<2s latency) |
| Clinical planning | SAPTIVA_OPS | More capable reasoning |
| Drug mapping | SAPTIVA_LEGACY | Simpler task |
| General Q&A | SAPTIVA_OPS | Balance of speed/quality |

**Decision**: Optimize for latency on real-time paths, quality on planning.

### 4. Why Weaviate over Pinecone?

| Aspect | Pinecone | Weaviate |
|--------|----------|----------|
| Ragster Support | No | Yes (native) |
| Metadata Filtering | Good | Excellent |
| Self-Hosting | No | Yes (optional) |
| Cost | Per-vector pricing | Cluster pricing |
| Mexican Data | US/EU regions | Flexible hosting |

**Decision**: Weaviate for Ragster compatibility and metadata flexibility.

---

## Security & Compliance Summary

### Data Protection
1. **PHI Masking**: Presidio on all logs
2. **Encryption**: TLS in transit, at rest for PostgreSQL
3. **Access Control**: (Future) RBAC with OAuth
4. **Audit Trail**: Immutable logs

### Clinical Safety
1. **Guardrails**: LlamaGuard for harmful content
2. **Safety Rules**: Hard-coded allergy/interaction checks
3. **Citations**: Every suggestion cites source
4. **Disclaimers**: Visible on every screen

### Regulatory Compliance
1. **NOM-004**: SOAP structure validation
2. **NOM-024**: Designed for interoperability
3. **COFEPRIS**: Only registered drugs recommended

---

## Appendices

### A. Document Sources

| Source | Type | Description | Example Files |
|--------|------|-------------|---------------|
| GPC | Clinical Guidelines | CENETEC/IMSS/SSA practice guidelines | `GPC_Faringitis_2019.pdf` |
| NOM | Regulations | Official Mexican norms | `NOM-004-SSA3-2012.pdf` |
| PLM | Drug Info | Commercial drug database | `PLM_Azitromicina.html` |
| COFEPRIS | Drug Registry | Official drug registrations | `COFEPRIS_Antibioticos.csv` |

### B. Drug Mappings Schema

```csv
rxnorm_ingredient,atc_code,generic_name,brand_name,presentation,route,strength,cofepris_reg,plm_id,manufacturer,pregnancy_category,renal_adjustment
18631,J01FA10,Azitromicina,Azitro-500,500 mg tableta,PO,500 mg,123M2019SSA,PLM-12345,Laboratorios X,B,false
723,J01CA04,Amoxicilina,Amoxil,500 mg cápsula,PO,500 mg,456M2018SSA,PLM-23456,GSK,B,true
```

### C. Prompt Templates

See `docs/SAPTIVA_INTEGRATION.md` for detailed prompt examples.

---

**Document Version**: 2.0 (Saptiva Integration)
**Last Updated**: October 24, 2025
**Status**: Ready for Implementation
**Author**: Juan Pablo (with Claude Code assistance)
