import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  SuggestionsRequest,
  SuggestionsResponse,
  PlanRequest,
  PlanResponse,
  QARequest,
  QAResponse,
  DrugMapResponse,
  PatientSnapshot,
  PatientSummary,
  PatientSummaryRequest,
  ClinicalAssessmentRequest,
  ClinicalAssessmentResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * POST /assist/hpi - Real-time HPI Suggestions
   * Latency target: <2 seconds
   */
  async getHPISuggestions(
    hpiTail: string,
    snapshot: PatientSnapshot,
    signal?: AbortSignal
  ): Promise<SuggestionsResponse> {
    if (USE_MOCK_DATA) {
      return this.getMockSuggestions(hpiTail);
    }

    const request: SuggestionsRequest = {
      hpi_tail: hpiTail,
      snapshot,
    };

    const response = await this.client.post<SuggestionsResponse>(
      '/api/assist/hpi',
      request,
      { signal }
    );

    return response.data;
  }

  /**
   * POST /assist/clinical-assessment - Clinical Assessment (Differential Diagnosis + Physical Exam)
   * Generates differential diagnoses and suggests physical examination maneuvers
   * Latency target: <3 seconds
   */
  async generateClinicalAssessment(
    request: ClinicalAssessmentRequest
  ): Promise<ClinicalAssessmentResponse> {
    if (USE_MOCK_DATA) {
      return this.getMockClinicalAssessment(request);
    }

    const response = await this.client.post<ClinicalAssessmentResponse>(
      '/api/assist/clinical-assessment',
      request
    );

    return response.data;
  }

  /**
   * POST /plan/generate - Clinical Plan Generation
   * Latency target: <5 seconds
   */
  async generateClinicalPlan(request: PlanRequest): Promise<PlanResponse> {
    if (USE_MOCK_DATA) {
      return this.getMockPlan();
    }

    const response = await this.client.post<PlanResponse>(
      '/api/plan/generate',
      request
    );

    return response.data;
  }

  /**
   * POST /qa - Clinical Q&A
   */
  async askQuestion(request: QARequest): Promise<QAResponse> {
    const response = await this.client.post<QAResponse>('/api/qa', request);
    return response.data;
  }

  /**
   * GET /drugmap?ingredient={name} - Drug Brand Mapping
   */
  async getDrugMapping(ingredient: string): Promise<DrugMapResponse> {
    const response = await this.client.get<DrugMapResponse>('/api/drugmap', {
      params: { ingredient },
    });
    return response.data;
  }

  /**
   * GET /patients/{id} - Patient Data
   */
  async getPatient(patientId: string): Promise<PatientSnapshot> {
    if (USE_MOCK_DATA) {
      return this.getMockPatient();
    }

    const response = await this.client.get<PatientSnapshot>(
      `/api/patients/${patientId}`
    );
    return response.data;
  }

  /**
   * POST /patients/summary - Generate LLM-powered patient summary
   * Creates intelligent clinical summary focused on visit context
   */
  async generatePatientSummary(request: PatientSummaryRequest): Promise<PatientSummary> {
    if (USE_MOCK_DATA) {
      return this.getMockPatientSummary(request);
    }

    const response = await this.client.post<PatientSummary>(
      '/api/patients/summary',
      request
    );
    return response.data;
  }

  // Mock data methods (for parallel development)
  private async getMockSuggestions(hpiTail: string): Promise<SuggestionsResponse> {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Simple keyword detection for demo
    const hasSoreThroat = hpiTail.toLowerCase().includes('garganta') ||
                          hpiTail.toLowerCase().includes('odinofagia');

    if (hasSoreThroat) {
      return {
        suggested_questions: [
          '¿Presencia de exudado faríngeo?',
          '¿Adenopatías cervicales anteriores?',
          '¿Fiebre >38°C?',
          '¿Ausencia de tos?',
        ],
        red_flags: [
          'Dificultad respiratoria',
          'Trismus (dificultad para abrir la boca)',
        ],
        scores: [
          {
            name: 'Centor',
            criteria: [
              'Exudado faríngeo',
              'Adenopatía cervical anterior dolorosa',
              'Fiebre >38°C',
              'Ausencia de tos',
            ],
            why_it_matters: 'Score ≥3 sugiere faringitis estreptocócica y justifica test rápido o tratamiento antibiótico',
          },
        ],
      };
    }

    return {
      suggested_questions: [
        '¿Desde cuándo presenta los síntomas?',
        '¿Ha tenido fiebre?',
        '¿Tratamientos previos?',
      ],
      red_flags: [],
      scores: [],
    };
  }

  private async getMockPlan(): Promise<PlanResponse> {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    return {
      differentials: [
        {
          diagnosis: 'Faringoamigdalitis estreptocócica',
          probability: 'high',
          rationale: 'Centor score 4/4: exudado + adenopatía + fiebre + sin tos',
        },
        {
          diagnosis: 'Faringitis viral',
          probability: 'medium',
          rationale: 'Posible etiología viral, pero menos probable dado el cuadro clínico',
        },
      ],
      labs: [
        {
          test: 'Test rápido Streptococcus A',
          indication: 'Confirmar etiología estreptocócica',
          priority: 'high',
        },
      ],
      medications: [
        {
          generic: 'Azitromicina',
          dose: '500 mg',
          route: 'PO',
          frequency: 'cada 24h',
          duration: '3 días',
          rationale: 'Primera línea en alergia a penicilina',
          brands: [
            {
              brand_name: 'Azitro-500',
              presentation: '500 mg tableta',
              manufacturer: 'Laboratorios Liomont',
            },
            {
              brand_name: 'Azitromicina MK',
              presentation: '500 mg tableta',
              manufacturer: 'MK Labs',
            },
          ],
        },
        {
          generic: 'Paracetamol',
          dose: '500 mg',
          route: 'PO',
          frequency: 'cada 6-8h PRN',
          duration: '5 días',
          rationale: 'Control de dolor y fiebre',
          brands: [
            {
              brand_name: 'Tempra',
              presentation: '500 mg tableta',
            },
          ],
        },
      ],
      alerts: [
        {
          type: 'allergy',
          severity: 'high',
          message: 'ALERGIA A PENICILINA - Evitar β-lactámicos',
          action_taken: 'Azitromicina seleccionada como alternativa',
        },
      ],
      patient_instructions: [
        'Tomar azitromicina 1 hora antes de alimentos',
        'Completar curso antibiótico (3 días)',
        'Gárgaras con agua tibia con sal 3-4 veces al día',
        'Reposo relativo',
        'Hidratación abundante',
        'Regresar a consulta si: dificultad respiratoria, trismus, fiebre persistente >3 días',
      ],
      citations: [
        {
          source: 'GPC_Faringitis_2019.pdf',
          namespace: 'gpc',
          chunk_index: 12,
          upload_date: '2025-10-24T14:00:00Z',
        },
        {
          source: 'PLM_Azitromicina.html',
          namespace: 'plm',
          chunk_index: 3,
          upload_date: '2025-10-24T14:00:00Z',
        },
      ],
    };
  }

  private async getMockPatient(): Promise<PatientSnapshot> {
    await new Promise((resolve) => setTimeout(resolve, 300));

    return {
      patient_id: 'patient-001',
      name: 'María G.',
      age: 28,
      sex: 'F',
      weight_kg: 60,
      height_cm: 165,
      pregnant: false,
      egfr: 95,
      allergies: ['penicilina'],
      active_medications: ['anticonceptivo oral'],
      chief_complaint: 'dolor de garganta',
      recent_labs: [
        {
          test: 'Hemoglobina',
          value: '13.5 g/dL',
          date: '2025-09-15',
          flag: 'normal',
        },
      ],
      previous_diagnoses: ['Rinitis alérgica (2024)'],
    };
  }

  private async getMockPatientSummary(request: PatientSummaryRequest): Promise<PatientSummary> {
    // Simulate LLM processing delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    return {
      critical_alerts: {
        allergies: [
          {
            allergen: 'Penicilina',
            severity: 'high',
            avoid: ['β-lactámicos', 'Penicilinas', 'Ampicilina', 'Amoxicilina'],
          },
        ],
        active_conditions: ['Rinitis alérgica controlada'],
        risk_factors: [
          'Mujer en edad reproductiva (uso de anticonceptivos)',
          'Sin contraindicaciones renales (TFG 95 mL/min)',
        ],
      },

      visit_context: {
        chief_complaint: request.chief_complaint || 'Dolor de garganta',
        relevant_history: [
          'Episodio previo de faringitis viral (enero 2025) - resuelto con manejo sintomático',
          'No antecedentes de faringitis estreptocócica confirmada',
        ],
        last_visit: {
          date: '2024-11-15',
          diagnosis: 'Rinitis alérgica - control',
          outcome: 'Estable con antihistamínicos PRN',
        },
      },

      medication_context: {
        current_medications: [
          {
            name: 'Anticonceptivo oral combinado',
            indication: 'Anticoncepción',
            interactions_to_watch: [
              'Rifampicina (reduce efectividad)',
              'Algunos antibióticos de amplio espectro',
            ],
          },
        ],
        contraindications: [
          'EVITAR: Todos los β-lactámicos por alergia confirmada',
          'Precaución: Antibióticos que afectan flora intestinal (puede reducir eficacia anticonceptiva)',
        ],
      },

      lab_summary: {
        recent_abnormal: [],
        pending_results: [],
      },

      contextual_factors: {
        pregnancy_status: 'not_pregnant',
        renal_function: 'normal',
        special_considerations: [
          'Paciente prefiere tratamientos de curso corto por trabajo',
          'Buena adherencia a tratamientos previos',
        ],
      },

      one_liner:
        '28F, alergia penicilina (ALTA), anticonceptivo oral activo, TFG normal, rinitis alérgica estable',
    };
  }

  private async getMockClinicalAssessment(
    request: ClinicalAssessmentRequest
  ): Promise<ClinicalAssessmentResponse> {
    // Simulate LLM processing delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const historiaClinica = request.historia_clinica.toLowerCase();

    // Detect sore throat/pharyngitis scenario
    if (historiaClinica.includes('garganta') || historiaClinica.includes('odinofagia')) {
      return {
        differential_diagnoses: [
          {
            diagnosis: 'Faringoamigdalitis estreptocócica',
            probability: 'high',
            key_findings_supporting: [
              'Odinofagia aguda',
              'Fiebre reportada',
              'Inicio súbito de síntomas',
            ],
            key_findings_against: [
              'Ausencia de tos (favorece etiología bacteriana)',
            ],
          },
          {
            diagnosis: 'Faringitis viral',
            probability: 'medium',
            key_findings_supporting: [
              'Síntomas de vía aérea superior',
              'Temporada invernal',
            ],
            key_findings_against: [
              'Fiebre alta sugiere etiología bacteriana',
              'Ausencia de coriza/rinorrea',
            ],
          },
          {
            diagnosis: 'Mononucleosis infecciosa',
            probability: 'low',
            key_findings_supporting: [
              'Edad del paciente (20-30 años)',
              'Faringitis',
            ],
            key_findings_against: [
              'Historia clínica no menciona fatiga extrema',
              'No menciona adenopatías generalizadas',
            ],
          },
        ],
        physical_exam_maneuvers: [
          {
            maneuver: 'Inspección de orofaringe',
            rationale: 'Evaluar presencia de exudado faríngeo (Criterio Centor)',
            what_to_look_for: 'Exudado purulento en amígdalas, hipertrofia amigdalina, petequias en paladar',
          },
          {
            maneuver: 'Palpación de cadenas ganglionares cervicales',
            rationale: 'Detectar adenopatía cervical anterior dolorosa (Criterio Centor)',
            what_to_look_for: 'Ganglios cervicales anteriores aumentados de tamaño (>1cm) y dolorosos a la palpación',
          },
          {
            maneuver: 'Medición de temperatura',
            rationale: 'Confirmar fiebre >38°C (Criterio Centor)',
            what_to_look_for: 'Temperatura axilar >38°C o timpánica >38.5°C',
          },
          {
            maneuver: 'Auscultación pulmonar',
            rationale: 'Descartar compromiso de vía aérea inferior',
            what_to_look_for: 'Presencia o ausencia de tos, sibilancias, estertores',
          },
        ],
        red_flags: [
          'Dificultad respiratoria (estridor, taquipnea)',
          'Trismus (dificultad para abrir la boca) - sugiere absceso periamigdalino',
          'Disfagia severa con sialorrea',
          'Edema de cuello o asimetría amigdalina',
        ],
      };
    }

    // Default response for general symptoms
    return {
      differential_diagnoses: [
        {
          diagnosis: 'Pendiente - Requiere más información',
          probability: 'medium',
          key_findings_supporting: ['Historia clínica capturada'],
          key_findings_against: [],
        },
      ],
      physical_exam_maneuvers: [
        {
          maneuver: 'Examen físico general',
          rationale: 'Evaluación inicial del paciente',
          what_to_look_for: 'Signos vitales, apariencia general, signos de enfermedad aguda',
        },
      ],
      red_flags: [],
    };
  }
}

// Export singleton instance
export const apiClient = new APIClient();
