'use client';

import React, { useState } from 'react';
import { Tabs } from '@/components/common/Tabs';
import { PatientSummaryPanel } from './PatientSummaryPanel';
import { SuggestionsPanel } from './SuggestionsPanel';
import { ClinicalPlanPanel } from './ClinicalPlanPanel';
import { ClinicalAssessmentPanel } from './ClinicalAssessmentPanel';
import { CitationsPanel } from './CitationsPanel';
import { AssistantTab, PatientSnapshot as PatientSnapshotType, PatientSummary, SuggestionsResponse, PlanResponse, ClinicalAssessmentResponse, Citation } from '@/types';
import { User, Stethoscope, FileText, BookOpen } from 'lucide-react';

interface AssistantPanelProps {
  patient: PatientSnapshotType;
  patientSummary: PatientSummary | null;
  isLoadingPatientSummary: boolean;
  clinicalAssessment: ClinicalAssessmentResponse | null;
  isLoadingClinicalAssessment: boolean;
  suggestions: SuggestionsResponse | null;
  clinicalPlan: PlanResponse | null;
  isLoadingSuggestions: boolean;
  isLoadingPlan: boolean;
  onInsertQuestion: (question: string) => void;
  activeTab?: AssistantTab;
  onTabChange?: (tab: AssistantTab) => void;
}

export function AssistantPanel({
  patient,
  patientSummary,
  isLoadingPatientSummary,
  clinicalAssessment,
  isLoadingClinicalAssessment,
  suggestions,
  clinicalPlan,
  isLoadingSuggestions,
  isLoadingPlan,
  onInsertQuestion,
  activeTab: controlledActiveTab,
  onTabChange,
}: AssistantPanelProps) {
  const [internalActiveTab, setInternalActiveTab] = useState<AssistantTab>('snapshot');

  // Use controlled tab if provided, otherwise use internal state
  const activeTab = controlledActiveTab !== undefined ? controlledActiveTab : internalActiveTab;
  const setActiveTab = onTabChange || setInternalActiveTab;

  const tabs = [
    { id: 'snapshot' as AssistantTab, label: 'Paciente', icon: <User size={16} /> },
    { id: 'clinical-assessment' as AssistantTab, label: 'Diagnóstico & Examen', icon: <Stethoscope size={16} /> },
    { id: 'plan' as AssistantTab, label: 'Plan', icon: <FileText size={16} /> },
    { id: 'sources' as AssistantTab, label: 'Fuentes', icon: <BookOpen size={16} /> },
  ];

  // Gather all citations from suggestions and plan
  const allCitations: Citation[] = [
    ...(suggestions?.scores.flatMap(() => []) || []),
    ...(clinicalPlan?.citations || []),
  ];

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="border-b border-gray-200">
        <Tabs
          tabs={tabs}
          activeTab={activeTab}
          onChange={(tabId) => setActiveTab(tabId as AssistantTab)}
          className="px-4"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'snapshot' && (
          <PatientSummaryPanel
            summary={patientSummary}
            isLoading={isLoadingPatientSummary}
            patientName={patient.name}
            patientAge={patient.age}
            patientSex={patient.sex}
          />
        )}

        {activeTab === 'clinical-assessment' && (
          <ClinicalAssessmentPanel
            assessment={clinicalAssessment}
            isLoading={isLoadingClinicalAssessment}
          />
        )}

        {activeTab === 'plan' && (
          <ClinicalPlanPanel
            plan={clinicalPlan}
            isLoading={isLoadingPlan}
          />
        )}

        {activeTab === 'sources' && <CitationsPanel citations={allCitations} />}
      </div>
    </div>
  );
}
