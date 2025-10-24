"""
Clinical services for generating medical insights using LLM with RAG support
"""
import json
from typing import Dict, Any
from app.services.llm_service import llm_service
from app.config.settings import settings
from app.rag.pipeline import rag_pipeline
from app.models.schemas import (
    PatientSnapshot,
    PatientSummaryRequest,
    ClinicalAssessmentRequest,
    PlanRequest,
)


class ClinicalService:
    """Service for clinical AI operations"""

    async def generate_patient_summary(self, request: PatientSummaryRequest) -> Dict[str, Any]:
        """
        Generate intelligent patient summary using LLM

        Args:
            request: Patient summary request with snapshot data

        Returns:
            Structured patient summary
        """
        snapshot = request.snapshot

        system_prompt = """Eres un asistente médico experto que analiza datos de pacientes y genera resúmenes clínicos concisos y seguros.

Tu tarea es analizar el snapshot del paciente y generar un resumen clínico estructurado que resalte:
1. Alertas críticas de seguridad (alergias, condiciones activas, factores de riesgo)
2. Contexto de la visita actual
3. Medicamentos actuales y posibles interacciones
4. Factores contextuales (embarazo, función renal, etc.)
5. Un resumen de una línea (one-liner) estilo médico

IMPORTANTE:
- Enfócate en seguridad del paciente
- Identifica contraindicaciones absolutas
- Sé conciso pero completo
- Usa terminología médica en español (México)
- Responde SOLO con JSON válido"""

        user_prompt = f"""Genera un resumen clínico del siguiente paciente:

**Datos del Paciente:**
- Nombre: {snapshot.name}
- Edad: {snapshot.age} años
- Sexo: {snapshot.sex}
- Peso: {snapshot.weight_kg} kg
- Alergias: {', '.join(snapshot.allergies) if snapshot.allergies else 'Ninguna'}
- Medicamentos activos: {', '.join(snapshot.active_medications) if snapshot.active_medications else 'Ninguno'}
- Motivo de consulta: {request.chief_complaint or snapshot.chief_complaint or 'No especificado'}
- Diagnósticos previos: {', '.join(snapshot.previous_diagnoses) if snapshot.previous_diagnoses else 'Ninguno'}
- TFG: {snapshot.egfr or 'No disponible'}
- Embarazada: {'Sí' if snapshot.pregnant else 'No'}

Genera el resumen en el siguiente formato JSON:
{{
  "critical_alerts": {{
    "allergies": [
      {{
        "allergen": "nombre del alérgeno",
        "severity": "high|medium|low",
        "avoid": ["lista de medicamentos/familias a evitar"]
      }}
    ],
    "active_conditions": ["lista de condiciones activas relevantes"],
    "risk_factors": ["lista de factores de riesgo clínico"]
  }},
  "visit_context": {{
    "chief_complaint": "motivo de consulta",
    "relevant_history": ["episodios previos relevantes"],
    "last_visit": {{
      "date": "fecha",
      "diagnosis": "diagnóstico",
      "outcome": "resultado"
    }}
  }},
  "medication_context": {{
    "current_medications": [
      {{
        "name": "nombre del medicamento",
        "indication": "indicación",
        "interactions_to_watch": ["interacciones a vigilar"]
      }}
    ],
    "contraindications": ["lista de contraindicaciones absolutas"]
  }},
  "lab_summary": {{
    "recent_abnormal": [],
    "pending_results": []
  }},
  "contextual_factors": {{
    "pregnancy_status": "not_pregnant|pregnant|lactating|unknown",
    "renal_function": "normal|mild_impairment|moderate_impairment|severe_impairment",
    "special_considerations": ["consideraciones especiales"]
  }},
  "one_liner": "resumen de una línea estilo médico (ej: 28F, alergia penicilina (ALTA), TFG normal)"
}}"""

        response = await llm_service.call_with_json_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=settings.SAPTIVA_OPS_MODEL,
            temperature=0.3
        )

        return response

    async def generate_clinical_assessment(self, request: ClinicalAssessmentRequest) -> Dict[str, Any]:
        """
        Generate differential diagnoses and physical exam suggestions

        Args:
            request: Clinical assessment request with historia clínica

        Returns:
            Differential diagnoses, physical exam maneuvers, and red flags
        """
        snapshot = request.snapshot

        system_prompt = """Eres un médico experto en diagnóstico clínico.

Tu tarea:
- Generar máximo 3 diagnósticos diferenciales
- Sugerir máximo 3 maniobras de examen físico
- Identificar máximo 3 banderas rojas

IMPORTANTE: Responde SOLO con JSON válido. Sé conciso."""

        user_prompt = f"""Historia clínica: {request.historia_clinica}

Paciente: {snapshot.age}años, {snapshot.sex}, alergias: {', '.join(snapshot.allergies) if snapshot.allergies else 'ninguna'}

JSON (máximo 3 items por sección):
{{
  "differential_diagnoses": [
    {{
      "diagnosis": "nombre",
      "probability": "high|medium|low",
      "key_findings_supporting": ["hallazgo 1", "hallazgo 2"],
      "key_findings_against": ["hallazgo 1"]
    }}
  ],
  "physical_exam_maneuvers": [
    {{
      "maneuver": "nombre",
      "rationale": "por qué",
      "what_to_look_for": "qué buscar"
    }}
  ],
  "red_flags": ["señal de alarma 1", "señal 2"]
}}"""

        response = await llm_service.call_with_json_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=settings.SAPTIVA_OPS_MODEL,
            temperature=0.3,
            max_tokens=8000  # Doubled to ensure complete responses
        )

        return response

    async def generate_clinical_plan(self, request: PlanRequest) -> Dict[str, Any]:
        """
        Generate complete clinical plan with medications, labs, and instructions

        Args:
            request: Plan request with SOAP summary and patient snapshot

        Returns:
            Complete clinical plan
        """
        soap = request.soap_summary
        snapshot = request.snapshot

        # Retrieve relevant clinical guidelines using RAG
        query = f"{soap.subjective} {soap.objective}"
        rag_results = []
        evidence_context = ""

        try:
            rag_results = await rag_pipeline.search(
                query=query,
                top_k=3,
                namespace_filter="gpc",  # Only search clinical practice guidelines
                min_certainty=0.7
            )
            evidence_context = rag_pipeline.format_context_for_prompt(rag_results)
        except Exception as e:
            print(f"RAG search failed, proceeding without evidence: {e}")
            evidence_context = "No se pudo recuperar evidencia de guías clínicas."

        system_prompt = """Eres un médico experto que genera planes clínicos completos, seguros y basados en evidencia.

Tu tarea:
1. Generar diagnósticos diferenciales BASADOS EN LA EVIDENCIA proporcionada
2. Recomendar laboratorios necesarios
3. Prescribir medicamentos apropiados
4. Identificar alertas de seguridad
5. Proveer instrucciones al paciente

IMPORTANTE: USA LA EVIDENCIA de las guías clínicas. Responde SOLO con JSON válido."""

        user_prompt = f"""**EVIDENCIA CLÍNICA (Guías de Práctica Clínica):**
{evidence_context}

---

Genera un plan clínico completo basado en la siguiente información:

**SOAP:**
- Subjetivo: {soap.subjective}
- Objetivo: {soap.objective}
- Evaluación: {soap.assessment or 'No capturada aún'}
- Plan: {soap.plan or 'No capturado aún'}

**Datos del Paciente:**
- Edad: {snapshot.age} años, Sexo: {snapshot.sex}
- Peso: {snapshot.weight_kg} kg
- Alergias: {', '.join(snapshot.allergies) if snapshot.allergies else 'Ninguna'}
- Medicamentos actuales: {', '.join(snapshot.active_medications) if snapshot.active_medications else 'Ninguno'}
- TFG: {snapshot.egfr or 'No disponible'}
- Embarazada: {'Sí' if snapshot.pregnant else 'No'}

Genera el plan en el siguiente formato JSON:
{{
  "differentials": [
    {{
      "diagnosis": "diagnóstico",
      "probability": "high|medium|low",
      "rationale": "justificación médica"
    }}
  ],
  "labs": [
    {{
      "test": "nombre del estudio",
      "indication": "indicación médica",
      "priority": "high|medium|low"
    }}
  ],
  "medications": [
    {{
      "generic": "nombre genérico",
      "dose": "dosis",
      "route": "vía (PO, IV, etc.)",
      "frequency": "frecuencia",
      "duration": "duración",
      "rationale": "justificación",
      "brands": [
        {{
          "brand_name": "nombre comercial mexicano",
          "presentation": "presentación",
          "manufacturer": "fabricante"
        }}
      ]
    }}
  ],
  "alerts": [
    {{
      "type": "allergy|interaction|pregnancy|renal|hepatic",
      "severity": "high|medium|low",
      "message": "mensaje de alerta",
      "action_taken": "acción tomada en respuesta"
    }}
  ],
  "patient_instructions": [
    "lista de instrucciones claras al paciente en español"
  ],
  "citations": [
    {{
      "source": "fuente de evidencia",
      "namespace": "gpc",
      "chunk_index": 0,
      "upload_date": "2025-10-24T00:00:00Z"
    }}
  ]
}}"""

        response = await llm_service.call_with_json_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=settings.SAPTIVA_OPS_MODEL,
            temperature=0.3
        )

        return response


# Singleton instance
clinical_service = ClinicalService()
