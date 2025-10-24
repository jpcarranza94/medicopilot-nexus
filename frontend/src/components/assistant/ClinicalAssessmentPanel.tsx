import React from 'react';
import { ClinicalAssessmentResponse } from '@/types';
import { Stethoscope, AlertTriangle, ClipboardList } from 'lucide-react';

interface ClinicalAssessmentPanelProps {
  assessment: ClinicalAssessmentResponse | null;
  isLoading: boolean;
}

export function ClinicalAssessmentPanel({
  assessment,
  isLoading,
}: ClinicalAssessmentPanelProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <svg
            className="animate-spin h-8 w-8 text-blue-600 mx-auto mb-3"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="text-sm text-gray-600">Generando diagnósticos diferenciales y sugerencias de examen físico...</p>
        </div>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="text-center py-12 text-gray-500">
        <ClipboardList size={48} className="mx-auto mb-3 text-gray-300" />
        <p className="text-sm font-medium mb-2">No hay evaluación clínica disponible</p>
        <p className="text-xs text-gray-400">
          Escribe la historia clínica y haz clic en "Generar Sugerencias" para obtener diagnósticos diferenciales y maniobras de examen físico.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Red Flags - Most Important */}
      {assessment.red_flags.length > 0 && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={18} className="text-red-600" />
            <h3 className="font-bold text-red-900 text-sm uppercase">⚠️ Banderas Rojas</h3>
          </div>
          <ul className="space-y-1">
            {assessment.red_flags.map((flag, idx) => (
              <li key={idx} className="text-sm text-red-900 flex items-start gap-2">
                <span className="text-red-600 font-bold mt-0.5">•</span>
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Differential Diagnoses */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <ClipboardList size={18} className="text-purple-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Diagnósticos Diferenciales</h3>
        </div>
        <div className="space-y-3">
          {assessment.differential_diagnoses.map((diff, index) => (
            <div key={index} className="border-l-4 border-purple-500 bg-purple-50 p-3 rounded-r">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-900 text-sm">{diff.diagnosis}</h4>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    diff.probability === 'high'
                      ? 'bg-red-200 text-red-900'
                      : diff.probability === 'medium'
                      ? 'bg-yellow-200 text-yellow-900'
                      : 'bg-green-200 text-green-900'
                  }`}
                >
                  {diff.probability === 'high' ? 'Alta' : diff.probability === 'medium' ? 'Media' : 'Baja'}
                </span>
              </div>

              {diff.key_findings_supporting.length > 0 && (
                <div className="mb-2">
                  <p className="text-xs font-semibold text-green-800 mb-1">✓ A favor:</p>
                  <ul className="text-xs space-y-0.5">
                    {diff.key_findings_supporting.map((finding, idx) => (
                      <li key={idx} className="text-green-700">
                        • {finding}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {diff.key_findings_against.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-700 mb-1">✗ En contra:</p>
                  <ul className="text-xs space-y-0.5">
                    {diff.key_findings_against.map((finding, idx) => (
                      <li key={idx} className="text-gray-600">
                        • {finding}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Physical Exam Maneuvers */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Stethoscope size={18} className="text-blue-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Maniobras de Examen Físico Sugeridas</h3>
        </div>
        <div className="space-y-3">
          {assessment.physical_exam_maneuvers.map((maneuver, index) => (
            <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <h4 className="font-semibold text-blue-900 text-sm mb-1">{maneuver.maneuver}</h4>
              <div className="space-y-1">
                <div>
                  <p className="text-xs font-medium text-blue-800">¿Por qué?</p>
                  <p className="text-xs text-blue-700">{maneuver.rationale}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-blue-800">¿Qué buscar?</p>
                  <p className="text-xs text-blue-700">{maneuver.what_to_look_for}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
