'use client';

import { useState, useEffect, useRef } from 'react';
import { SOAPEditor } from '@/components/editor/SOAPEditor';
import { AssistantPanel } from '@/components/assistant/AssistantPanel';
import { useDebounce } from '@/hooks/useDebounce';
import { apiClient } from '@/services/api';
import {
  EditorState,
  PatientSnapshot,
  PatientSummary,
  SuggestionsResponse,
  PlanResponse,
  ClinicalAssessmentResponse,
  AssistantTab,
} from '@/types';
import { Save, Download, Copy, Check } from 'lucide-react';

export default function Home() {
  // Patient data
  const [patient, setPatient] = useState<PatientSnapshot | null>(null);
  const [patientSummary, setPatientSummary] = useState<PatientSummary | null>(null);
  const [isLoadingPatientSummary, setIsLoadingPatientSummary] = useState(false);

  // Editor state
  const [editorState, setEditorState] = useState<EditorState>({
    subjective: '',
    objective: '',
    assessment: '',
    plan: '',
  });

  // Assistant state
  const [clinicalAssessment, setClinicalAssessment] = useState<ClinicalAssessmentResponse | null>(null);
  const [isLoadingClinicalAssessment, setIsLoadingClinicalAssessment] = useState(false);
  const [suggestions, setSuggestions] = useState<SuggestionsResponse | null>(null);
  const [clinicalPlan, setClinicalPlan] = useState<PlanResponse | null>(null);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedSOAP, setCopiedSOAP] = useState(false);
  const [assistantActiveTab, setAssistantActiveTab] = useState<AssistantTab>('snapshot');


  // Load patient data and generate smart summary on mount
  useEffect(() => {
    const loadPatient = async () => {
      try {
        const patientData = await apiClient.getPatient('patient-001');
        setPatient(patientData);

        // Generate LLM-powered patient summary
        setIsLoadingPatientSummary(true);
        try {
          const summary = await apiClient.generatePatientSummary({
            patient_id: patientData.patient_id,
            chief_complaint: patientData.chief_complaint,
            snapshot: patientData, // Include full patient snapshot as required by backend
          });
          setPatientSummary(summary);
        } catch (summaryErr) {
          console.error('Failed to generate patient summary:', summaryErr);
          // Don't block the whole app if summary fails
        } finally {
          setIsLoadingPatientSummary(false);
        }
      } catch (err) {
        console.error('Failed to load patient:', err);
        setError('No se pudo cargar los datos del paciente');
      }
    };

    loadPatient();
  }, []);

  const handleGenerateClinicalAssessment = async () => {
    if (!patient || editorState.subjective.length < 100) return;

    setIsLoadingClinicalAssessment(true);
    setError(null);

    // Automatically switch to clinical-assessment tab
    setAssistantActiveTab('clinical-assessment');

    try {
      const assessment = await apiClient.generateClinicalAssessment({
        historia_clinica: editorState.subjective,
        snapshot: patient,
      });

      setClinicalAssessment(assessment);
    } catch (err) {
      console.error('Failed to generate clinical assessment:', err);
      setError('Error al generar la evaluación clínica');
    } finally {
      setIsLoadingClinicalAssessment(false);
    }
  };

  const handleEditorChange = (field: keyof EditorState, value: string) => {
    setEditorState((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleGeneratePlan = async () => {
    if (!patient) return;

    setIsLoadingPlan(true);
    setError(null);

    // Automatically switch to plan tab
    setAssistantActiveTab('plan');

    try {
      const planData = await apiClient.generateClinicalPlan({
        soap_summary: {
          subjective: editorState.subjective,
          objective: editorState.objective,
          assessment: editorState.assessment,
          plan: editorState.plan,
        },
        snapshot: patient,
      });

      setClinicalPlan(planData);

      // Auto-fill assessment and plan if empty
      if (!editorState.assessment && planData.differentials.length > 0) {
        const assessmentText = planData.differentials
          .map((d) => `${d.diagnosis} (${d.probability})`)
          .join('\n');
        setEditorState((prev) => ({ ...prev, assessment: assessmentText }));
      }

      if (!editorState.plan && planData.medications.length > 0) {
        const planText = planData.medications
          .map((m) => `${m.generic} ${m.dose} ${m.route} - ${m.frequency} x ${m.duration}`)
          .join('\n');
        setEditorState((prev) => ({ ...prev, plan: planText }));
      }
    } catch (err) {
      console.error('Failed to generate plan:', err);
      setError('Error al generar el plan clínico');
    } finally {
      setIsLoadingPlan(false);
    }
  };

  const handleInsertQuestion = (question: string) => {
    setEditorState((prev) => ({
      ...prev,
      subjective: prev.subjective + (prev.subjective ? '\n\n' : '') + question,
    }));
  };

  const copySOAPNote = async () => {
    const soapText = `SOAP NOTE
==========

SUBJETIVO:
${editorState.subjective || '(vacío)'}

OBJETIVO:
${editorState.objective || '(vacío)'}

EVALUACIÓN:
${editorState.assessment || '(vacío)'}

PLAN:
${editorState.plan || '(vacío)'}
`;

    await navigator.clipboard.writeText(soapText);
    setCopiedSOAP(true);
    setTimeout(() => setCopiedSOAP(false), 2000);
  };

  if (!patient) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Cargando datos del paciente...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              MediCopilot Nexus
            </h1>
            <p className="text-sm text-gray-500">Asistente Clínico Inteligente</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {patient.name}
              </p>
              <p className="text-xs text-gray-500">
                {patient.age} años, {patient.sex === 'F' ? 'Femenino' : 'Masculino'}
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={copySOAPNote}
                className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
              >
                {copiedSOAP ? (
                  <><Check size={16} /> Copiado</>
                ) : (
                  <><Copy size={16} /> Copiar SOAP</>
                )}
              </button>

              <button className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
                <Save size={16} />
                Guardar
              </button>

              <button className="px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2">
                <Download size={16} />
                Exportar
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-3 bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
      </header>

      {/* Main Content - Two Column Layout */}
      <main className="flex-1 p-6 overflow-hidden">
        <div className="h-full flex gap-6">
          {/* Left Column - SOAP Editor (55%) */}
          <div className="w-[55%] h-full">
            <SOAPEditor
              editorState={editorState}
              onChange={handleEditorChange}
              onGeneratePlan={handleGeneratePlan}
              isGeneratingPlan={isLoadingPlan}
              onGenerateClinicalAssessment={handleGenerateClinicalAssessment}
              isGeneratingAssessment={isLoadingClinicalAssessment}
            />
          </div>

          {/* Right Column - Assistant Panel (45%) */}
          <div className="w-[45%] h-full">
            <AssistantPanel
              patient={patient}
              patientSummary={patientSummary}
              isLoadingPatientSummary={isLoadingPatientSummary}
              clinicalAssessment={clinicalAssessment}
              isLoadingClinicalAssessment={isLoadingClinicalAssessment}
              suggestions={suggestions}
              clinicalPlan={clinicalPlan}
              isLoadingSuggestions={isLoadingSuggestions}
              isLoadingPlan={isLoadingPlan}
              onInsertQuestion={handleInsertQuestion}
              activeTab={assistantActiveTab}
              onTabChange={setAssistantActiveTab}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-3 text-center text-xs text-gray-500 flex-shrink-0">
        <p>
          Powered by{' '}
          <a href="https://saptiva.com" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
            Saptiva AI
          </a>
          {' '}&{' '}
          <a href="https://github.com/ragster/ragster" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
            Ragster
          </a>
          {' '}• MediCopilot Nexus v0.1.0 • Demo Hackathon Oct 2025
        </p>
      </footer>
    </div>
  );
}
