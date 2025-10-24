// Patient Types
export interface Patient {
  patient_id: string;
  name: string;
  date_of_birth: string;
  sex: 'M' | 'F';
  age: number;
  weight_kg?: number;
  height_cm?: number;
}

export interface Allergy {
  allergy_id: string;
  allergen: string;
  reaction?: string;
  severity: 'mild' | 'moderate' | 'severe';
  verified: boolean;
}

export interface ActiveMedication {
  medication_id: string;
  medication: string;
  dose?: string;
  frequency?: string;
  start_date?: string;
}

export interface VitalSigns {
  temperature?: number;
  blood_pressure?: string;
  heart_rate?: number;
  respiratory_rate?: number;
  oxygen_saturation?: number;
}

export interface PatientSnapshot {
  patient_id: string;
  name: string;
  age: number;
  sex: 'M' | 'F';
  weight_kg?: number;
  height_cm?: number;
  pregnant?: boolean;
  egfr?: number; // Estimated glomerular filtration rate
  allergies: string[];
  active_medications: string[];
  chief_complaint?: string;
  recent_labs?: Array<{
    test: string;
    value: string;
    date: string;
    flag?: 'high' | 'low' | 'normal';
  }>;
  previous_diagnoses?: string[];
}

// LLM-Generated Patient Summary
export interface PatientSummary {
  // Critical Safety Information
  critical_alerts: {
    allergies: Array<{
      allergen: string;
      severity: 'high' | 'medium' | 'low';
      avoid: string[]; // What to avoid (e.g., "β-lactámicos" for penicillin allergy)
    }>;
    active_conditions: string[]; // Chronic conditions that affect treatment
    risk_factors: string[]; // Clinical risk factors to consider
  };

  // Clinical Context for Today's Visit
  visit_context: {
    chief_complaint: string;
    relevant_history: string[]; // Previous similar episodes
    last_visit: {
      date: string;
      diagnosis: string;
      outcome: string;
    } | null;
  };

  // Medication Considerations
  medication_context: {
    current_medications: Array<{
      name: string;
      indication: string;
      interactions_to_watch: string[];
    }>;
    contraindications: string[]; // What NOT to prescribe
  };

  // Lab & Diagnostic Context
  lab_summary: {
    recent_abnormal: Array<{
      test: string;
      value: string;
      clinical_significance: string;
    }>;
    pending_results: string[];
  };

  // Social & Contextual Factors
  contextual_factors: {
    pregnancy_status: 'pregnant' | 'not_pregnant' | 'lactating' | 'unknown';
    renal_function: 'normal' | 'mild_impairment' | 'moderate_impairment' | 'severe_impairment';
    special_considerations: string[]; // E.g., "Patient prefers generic medications"
  };

  // Quick Reference
  one_liner: string; // E.g., "28F con alergia a penicilina, dx previo rinitis alérgica"
}

// API Request for Patient Summary
export interface PatientSummaryRequest {
  patient_id: string;
  chief_complaint?: string; // Current visit reason (optional, enhances summary)
}

// Suggestions Types (POST /assist/hpi) - DEPRECATED, keeping for backwards compatibility
export interface ClinicalScore {
  name: string;
  criteria: string[];
  why_it_matters: string;
}

export interface SuggestionsRequest {
  hpi_tail: string;
  snapshot: PatientSnapshot;
}

export interface SuggestionsResponse {
  suggested_questions: string[];
  red_flags: string[];
  scores: ClinicalScore[];
}

// Clinical Assessment Types (POST /assist/clinical-assessment)
export interface ClinicalAssessmentRequest {
  historia_clinica: string; // Complete subjective history
  snapshot: PatientSnapshot;
}

export interface PhysicalExamManeuver {
  maneuver: string;
  rationale: string;
  what_to_look_for: string;
}

export interface DifferentialDiagnosis {
  diagnosis: string;
  probability: 'high' | 'medium' | 'low';
  key_findings_supporting: string[];
  key_findings_against: string[];
}

export interface ClinicalAssessmentResponse {
  differential_diagnoses: DifferentialDiagnosis[];
  physical_exam_maneuvers: PhysicalExamManeuver[];
  red_flags: string[];
}

// Clinical Plan Types (POST /plan/generate)
export interface SOAPSummary {
  subjective: string;
  objective: string;
  assessment?: string;
  plan?: string;
}

export interface Differential {
  diagnosis: string;
  probability: 'high' | 'medium' | 'low';
  rationale: string;
}

export interface LabTest {
  test: string;
  indication: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Medication {
  generic: string;
  dose: string;
  route: string;
  frequency: string;
  duration: string;
  rationale: string;
  brands?: MedicationBrand[];
}

export interface MedicationBrand {
  brand_name: string;
  presentation: string;
  manufacturer?: string;
}

export interface SafetyAlert {
  type: 'allergy' | 'interaction' | 'pregnancy' | 'renal' | 'hepatic';
  severity: 'high' | 'medium' | 'low';
  message: string;
  action_taken?: string;
}

export interface Citation {
  source: string;
  namespace: 'gpc' | 'nom' | 'plm' | 'cofepris';
  chunk_index: number;
  upload_date: string;
  text?: string;
}

export interface PlanRequest {
  soap_summary: SOAPSummary;
  snapshot: PatientSnapshot;
}

export interface PlanResponse {
  differentials: Differential[];
  labs: LabTest[];
  medications: Medication[];
  alerts: SafetyAlert[];
  patient_instructions: string[];
  citations: Citation[];
}

// Q&A Types (POST /qa)
export interface QARequest {
  question: string;
  patient_context: Partial<PatientSnapshot>;
}

export interface QAResponse {
  answer: string;
  citations: Citation[];
  confidence: 'high' | 'medium' | 'low';
}

// Drug Mapping Types (GET /drugmap)
export interface DrugMapResponse {
  ingredient: string;
  brands: MedicationBrand[];
  source: string;
  note?: string;
}

// UI State Types
export interface EditorState {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
}

export interface AssistantState {
  suggestions: SuggestionsResponse | null;
  clinicalPlan: PlanResponse | null;
  loading: boolean;
  error: string | null;
}

export type AssistantTab = 'snapshot' | 'clinical-assessment' | 'plan' | 'sources';
export type EditorTab = 'subjective' | 'objective' | 'assessment' | 'plan';
