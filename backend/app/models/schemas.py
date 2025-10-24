"""
Pydantic models for API request/response schemas
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Patient Models
# ============================================================================

class RecentLab(BaseModel):
    test: str
    value: str
    date: str
    flag: Optional[Literal["high", "low", "normal"]] = None


class PatientSnapshot(BaseModel):
    """Patient snapshot data sent from frontend"""
    patient_id: str
    name: str
    age: int
    sex: Literal["M", "F"]
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    pregnant: Optional[bool] = None
    egfr: Optional[int] = None  # Estimated glomerular filtration rate
    allergies: List[str] = Field(default_factory=list)
    active_medications: List[str] = Field(default_factory=list)
    chief_complaint: Optional[str] = None
    recent_labs: List[RecentLab] = Field(default_factory=list)
    previous_diagnoses: List[str] = Field(default_factory=list)


# ============================================================================
# Patient Summary (LLM-Generated)
# ============================================================================

class AllergyInfo(BaseModel):
    allergen: str
    severity: Literal["high", "medium", "low"]
    avoid: List[str]


class LastVisit(BaseModel):
    date: str
    diagnosis: str
    outcome: str


class CurrentMedication(BaseModel):
    name: str
    indication: str
    interactions_to_watch: List[str]


class AbnormalLab(BaseModel):
    test: str
    value: str
    clinical_significance: str


class PatientSummaryRequest(BaseModel):
    patient_id: str
    chief_complaint: Optional[str] = None
    snapshot: PatientSnapshot


class PatientSummaryResponse(BaseModel):
    critical_alerts: dict = Field(
        description="Critical safety information",
        example={
            "allergies": [{"allergen": "Penicilina", "severity": "high", "avoid": ["β-lactámicos"]}],
            "active_conditions": ["Rinitis alérgica controlada"],
            "risk_factors": ["Mujer en edad reproductiva"]
        }
    )
    visit_context: dict
    medication_context: dict
    lab_summary: dict
    contextual_factors: dict
    one_liner: str


# ============================================================================
# Clinical Assessment (Differential Diagnosis + Physical Exam)
# ============================================================================

class ClinicalAssessmentRequest(BaseModel):
    historia_clinica: str = Field(description="Complete subjective clinical history")
    snapshot: PatientSnapshot


class DifferentialDiagnosis(BaseModel):
    diagnosis: str
    probability: Literal["high", "medium", "low"]
    key_findings_supporting: List[str]
    key_findings_against: List[str]


class PhysicalExamManeuver(BaseModel):
    maneuver: str
    rationale: str
    what_to_look_for: str


class ClinicalAssessmentResponse(BaseModel):
    differential_diagnoses: List[DifferentialDiagnosis]
    physical_exam_maneuvers: List[PhysicalExamManeuver]
    red_flags: List[str]


# ============================================================================
# Clinical Plan Generation
# ============================================================================

class SOAPSummary(BaseModel):
    subjective: str
    objective: str
    assessment: Optional[str] = ""
    plan: Optional[str] = ""


class Differential(BaseModel):
    diagnosis: str
    probability: Literal["high", "medium", "low"]
    rationale: str


class LabTest(BaseModel):
    test: str
    indication: str
    priority: Literal["high", "medium", "low"]


class MedicationBrand(BaseModel):
    brand_name: str
    presentation: str
    manufacturer: Optional[str] = None


class Medication(BaseModel):
    generic: str
    dose: str
    route: str
    frequency: str
    duration: str
    rationale: str
    brands: List[MedicationBrand] = Field(default_factory=list)


class SafetyAlert(BaseModel):
    type: Literal["allergy", "interaction", "pregnancy", "renal", "hepatic"]
    severity: Literal["high", "medium", "low"]
    message: str
    action_taken: Optional[str] = None


class Citation(BaseModel):
    source: str
    namespace: Literal["gpc", "nom", "plm", "cofepris"]
    chunk_index: int
    upload_date: str
    text: Optional[str] = None


class PlanRequest(BaseModel):
    soap_summary: SOAPSummary
    snapshot: PatientSnapshot


class PlanResponse(BaseModel):
    differentials: List[Differential]
    labs: List[LabTest]
    medications: List[Medication]
    alerts: List[SafetyAlert]
    patient_instructions: List[str]
    citations: List[Citation]
