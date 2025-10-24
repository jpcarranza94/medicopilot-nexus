"""
API routes for MediCopilot Nexus
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PatientSummaryRequest,
    PatientSummaryResponse,
    ClinicalAssessmentRequest,
    ClinicalAssessmentResponse,
    PlanRequest,
    PlanResponse,
)
from app.services.clinical_service import clinical_service

router = APIRouter()


@router.post("/patients/summary", response_model=PatientSummaryResponse)
async def generate_patient_summary(request: PatientSummaryRequest):
    """
    Generate LLM-powered patient summary

    This endpoint analyzes patient snapshot data and generates an intelligent
    clinical summary with critical alerts, medication context, and safety information.
    """
    try:
        summary = await clinical_service.generate_patient_summary(request)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate patient summary: {str(e)}")


@router.post("/assist/clinical-assessment", response_model=ClinicalAssessmentResponse)
async def generate_clinical_assessment(request: ClinicalAssessmentRequest):
    """
    Generate clinical assessment (differential diagnoses + physical exam maneuvers)

    This endpoint analyzes the patient's clinical history (historia clínica) and
    generates differential diagnoses with suggested physical examination maneuvers.
    """
    try:
        assessment = await clinical_service.generate_clinical_assessment(request)
        return assessment
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate clinical assessment: {str(e)}"
        )


@router.post("/plan/generate", response_model=PlanResponse)
async def generate_clinical_plan(request: PlanRequest):
    """
    Generate complete clinical plan

    This endpoint generates a comprehensive clinical plan including:
    - Differential diagnoses
    - Recommended laboratory tests
    - Medication prescriptions with Mexican brand names
    - Safety alerts (allergies, interactions)
    - Patient instructions in Spanish
    """
    try:
        plan = await clinical_service.generate_clinical_plan(request)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate clinical plan: {str(e)}")


@router.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    """
    Get patient data by ID

    For demo purposes, returns hardcoded patient data.
    In production, this would query a patient database.
    """
    # Demo patient data - diabetes case
    if patient_id == "patient-001":
        return {
            "patient_id": "patient-001",
            "name": "María González Pérez",
            "age": 52,
            "sex": "F",
            "weight_kg": 82,
            "height_cm": 160,
            "pregnant": False,
            "egfr": 78,
            "allergies": [],
            "active_medications": ["Losartán 50 mg 1 vez al día"],
            "chief_complaint": "polidipsia, poliuria, pérdida de peso",
            "recent_labs": [
                {
                    "test": "Glucosa en ayuno",
                    "value": "185 mg/dL",
                    "date": "2025-10-24",
                    "flag": "high"
                },
                {
                    "test": "HbA1c",
                    "value": "8.5%",
                    "date": "2025-10-24",
                    "flag": "high"
                },
                {
                    "test": "Creatinina",
                    "value": "0.9 mg/dL",
                    "date": "2025-10-24",
                    "flag": "normal"
                }
            ],
            "previous_diagnoses": ["Hipertensión arterial (2 años)"]
        }

    raise HTTPException(status_code=404, detail="Patient not found")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MediCopilot Nexus API",
        "version": "0.1.0"
    }
