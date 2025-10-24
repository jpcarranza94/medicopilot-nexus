'use client';

import React, { useState } from 'react';
import { Tabs } from '@/components/common/Tabs';
import { EditorTab, EditorState } from '@/types';
import { FileText, Eye, ClipboardList, FileCheck } from 'lucide-react';

interface SOAPEditorProps {
  editorState: EditorState;
  onChange: (field: keyof EditorState, value: string) => void;
  onGeneratePlan: () => void;
  isGeneratingPlan: boolean;
  onGenerateClinicalAssessment?: () => void;
  isGeneratingAssessment?: boolean;
}

export function SOAPEditor({
  editorState,
  onChange,
  onGeneratePlan,
  isGeneratingPlan,
  onGenerateClinicalAssessment,
  isGeneratingAssessment = false,
}: SOAPEditorProps) {
  const [activeTab, setActiveTab] = useState<EditorTab>('subjective');

  const tabs = [
    { id: 'subjective' as EditorTab, label: 'Historia Clínica', icon: <FileText size={16} /> },
    { id: 'objective' as EditorTab, label: 'Examen Físico', icon: <Eye size={16} /> },
    { id: 'assessment' as EditorTab, label: 'Evaluación', icon: <ClipboardList size={16} /> },
    { id: 'plan' as EditorTab, label: 'Plan', icon: <FileCheck size={16} /> },
  ];

  const placeholders = {
    subjective: 'Escriba la historia clínica del paciente...\n\nEjemplo: Paciente refiere dolor de garganta de 3 días de evolución, acompañado de fiebre hasta 38.5°C y odinofagia...',
    objective: 'Escriba los hallazgos del examen físico...\n\nEjemplo: Temperatura: 38.2°C\nFrecuencia cardíaca: 88 lpm\nOrofaringe: Exudado amigdalino bilateral\nCuello: Adenopatías cervicales anteriores palpables y dolorosas',
    assessment: 'La evaluación se generará automáticamente o puede escribirla manualmente...',
    plan: 'El plan se generará automáticamente o puede escribirla manualmente...',
  };

  const currentValue = editorState[activeTab];
  const charCount = currentValue.length;

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="border-b border-gray-200">
        <Tabs
          tabs={tabs}
          activeTab={activeTab}
          onChange={(tabId) => setActiveTab(tabId as EditorTab)}
          className="px-4"
        />
      </div>

      <div className="flex-1 flex flex-col p-4 min-h-0">
        <textarea
          value={currentValue}
          onChange={(e) => onChange(activeTab, e.target.value)}
          placeholder={placeholders[activeTab]}
          className="flex-1 w-full p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base leading-relaxed min-h-[500px]"
          style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
        />

        <div className="flex items-center justify-between mt-3 flex-shrink-0">
          <span className={`text-xs font-medium ${
            charCount < 50 ? 'text-gray-500' :
            charCount <= 1000 ? 'text-green-600' :
            'text-yellow-600'
          }`}>
            {charCount} caracteres
            {charCount < 50 && activeTab === 'subjective' && (
              <span className="ml-2 text-gray-400">(escribe al menos 50 caracteres para activar sugerencias)</span>
            )}
          </span>

          {activeTab === 'subjective' && charCount >= 50 && (
            <span className="text-xs text-green-600 font-medium">
              ✓ Sugerencias activas
            </span>
          )}
        </div>
      </div>

      <div className="border-t border-gray-200 p-4">
        {/* Show Clinical Assessment button when on Historia Clínica tab */}
        {activeTab === 'subjective' && onGenerateClinicalAssessment && (
          <button
            onClick={onGenerateClinicalAssessment}
            disabled={isGeneratingAssessment || editorState.subjective.length < 100}
            className={`
              w-full px-4 py-3 rounded-lg font-medium text-white transition-colors
              ${
                isGeneratingAssessment || editorState.subjective.length < 100
                  ? 'bg-purple-300 cursor-not-allowed'
                  : 'bg-purple-600 hover:bg-purple-700'
              }
            `}
          >
            {isGeneratingAssessment ? (
              <div className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Generando sugerencias...</span>
              </div>
            ) : (
              '🔍 Generar Sugerencias de Diagnóstico y Examen Físico'
            )}
          </button>
        )}

        {/* Show Generate Plan button on other tabs or when no assessment callback */}
        {(activeTab !== 'subjective' || !onGenerateClinicalAssessment) && (
          <button
            onClick={onGeneratePlan}
            disabled={isGeneratingPlan || (!editorState.subjective && !editorState.objective)}
            className={`
              w-full px-4 py-3 rounded-lg font-medium text-white transition-colors
              ${
                isGeneratingPlan || (!editorState.subjective && !editorState.objective)
                  ? 'bg-blue-300 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }
            `}
          >
            {isGeneratingPlan ? (
              <div className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Generando plan...</span>
              </div>
            ) : (
              '🔵 Generar Plan Clínico'
            )}
          </button>
        )}
      </div>
    </div>
  );
}
