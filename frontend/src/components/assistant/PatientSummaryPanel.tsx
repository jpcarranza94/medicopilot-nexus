import React from 'react';
import { PatientSummary } from '@/types';
import { AlertCircle, Activity, Pill, FlaskConical, Info, Star } from 'lucide-react';

interface PatientSummaryPanelProps {
  summary: PatientSummary | null;
  isLoading: boolean;
  patientName: string;
  patientAge: number;
  patientSex: 'M' | 'F';
}

export function PatientSummaryPanel({
  summary,
  isLoading,
  patientName,
  patientAge,
  patientSex,
}: PatientSummaryPanelProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <svg className="animate-spin h-8 w-8 text-blue-600 mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-sm text-gray-600">Generando resumen clínico...</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Activity size={48} className="mx-auto mb-3 text-gray-300" />
        <p className="text-sm">Resumen del paciente no disponible</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Quick One-Liner */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
        <div className="flex items-start gap-2">
          <Star size={18} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-xs font-semibold text-blue-900 mb-1">RESUMEN RÁPIDO</p>
            <p className="text-sm text-blue-800 font-medium">{summary.one_liner}</p>
          </div>
        </div>
      </div>

      {/* Critical Alerts - Most Important */}
      {summary.critical_alerts.allergies.length > 0 && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle size={18} className="text-red-600" />
            <h3 className="font-bold text-red-900 text-sm uppercase">⚠️ Alertas Críticas</h3>
          </div>
          {summary.critical_alerts.allergies.map((allergy, index) => (
            <div key={index} className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-red-900">{allergy.allergen}</span>
                <span className="text-xs px-2 py-0.5 bg-red-200 text-red-900 rounded-full">
                  Severidad: {allergy.severity === 'high' ? 'ALTA' : allergy.severity === 'medium' ? 'MEDIA' : 'BAJA'}
                </span>
              </div>
              <div className="bg-red-100 rounded p-2">
                <p className="text-xs font-semibold text-red-800 mb-1">Evitar:</p>
                <div className="flex flex-wrap gap-1">
                  {allergy.avoid.map((avoid, idx) => (
                    <span key={idx} className="text-xs bg-red-200 text-red-900 px-2 py-0.5 rounded">
                      {avoid}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Visit Context */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Info size={18} className="text-blue-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Contexto de la Consulta</h3>
        </div>
        <div className="space-y-2">
          <div>
            <p className="text-xs text-gray-600 font-medium">Motivo de consulta:</p>
            <p className="text-sm text-gray-900">{summary.visit_context.chief_complaint}</p>
          </div>
          {summary.visit_context.relevant_history.length > 0 && (
            <div>
              <p className="text-xs text-gray-600 font-medium">Historial relevante:</p>
              <ul className="text-sm space-y-1">
                {summary.visit_context.relevant_history.map((item, idx) => (
                  <li key={idx} className="text-gray-700 flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {summary.visit_context.last_visit && (
            <div className="bg-gray-50 rounded p-2 text-xs">
              <p className="font-medium text-gray-700">Última visita: {summary.visit_context.last_visit.date}</p>
              <p className="text-gray-600">Dx: {summary.visit_context.last_visit.diagnosis}</p>
              <p className="text-gray-600">Resultado: {summary.visit_context.last_visit.outcome}</p>
            </div>
          )}
        </div>
      </div>

      {/* Medication Considerations */}
      {summary.medication_context.current_medications.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Pill size={18} className="text-green-600" />
            <h3 className="font-semibold text-gray-900 text-sm">Medicamentos Actuales</h3>
          </div>
          {summary.medication_context.current_medications.map((med, index) => (
            <div key={index} className="mb-3 last:mb-0">
              <div className="flex items-start justify-between mb-1">
                <span className="font-medium text-gray-900 text-sm">{med.name}</span>
                <span className="text-xs text-gray-600 italic">{med.indication}</span>
              </div>
              {med.interactions_to_watch.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
                  <p className="text-xs font-semibold text-yellow-900 mb-1">⚠️ Interacciones a vigilar:</p>
                  <ul className="text-xs space-y-0.5">
                    {med.interactions_to_watch.map((interaction, idx) => (
                      <li key={idx} className="text-yellow-800">• {interaction}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Contraindications */}
      {summary.medication_context.contraindications.length > 0 && (
        <div className="bg-orange-50 border border-orange-300 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle size={18} className="text-orange-600" />
            <h3 className="font-semibold text-orange-900 text-sm">Contraindicaciones</h3>
          </div>
          <ul className="space-y-1">
            {summary.medication_context.contraindications.map((contraindication, idx) => (
              <li key={idx} className="text-sm text-orange-900 flex items-start gap-2">
                <span className="text-orange-600 font-bold mt-0.5">🚫</span>
                <span>{contraindication}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Active Conditions & Risk Factors */}
      {(summary.critical_alerts.active_conditions.length > 0 || summary.critical_alerts.risk_factors.length > 0) && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Activity size={18} className="text-purple-600" />
            <h3 className="font-semibold text-gray-900 text-sm">Condiciones y Factores de Riesgo</h3>
          </div>
          {summary.critical_alerts.active_conditions.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-gray-700 mb-1">Condiciones activas:</p>
              <div className="flex flex-wrap gap-2">
                {summary.critical_alerts.active_conditions.map((condition, idx) => (
                  <span key={idx} className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                    {condition}
                  </span>
                ))}
              </div>
            </div>
          )}
          {summary.critical_alerts.risk_factors.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-700 mb-1">Factores de riesgo:</p>
              <ul className="text-xs space-y-1">
                {summary.critical_alerts.risk_factors.map((factor, idx) => (
                  <li key={idx} className="text-gray-600 flex items-start gap-2">
                    <span className="text-purple-600 mt-0.5">▪</span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Contextual Factors */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <FlaskConical size={18} className="text-amber-600" />
          <h3 className="font-semibold text-amber-900 text-sm">Consideraciones Especiales</h3>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-amber-800 font-medium">Embarazo:</span>
            <span className="text-amber-900">
              {summary.contextual_factors.pregnancy_status === 'pregnant' ? '✓ Sí' :
               summary.contextual_factors.pregnancy_status === 'lactating' ? 'Lactancia' :
               summary.contextual_factors.pregnancy_status === 'not_pregnant' ? '✗ No' : 'Desconocido'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-amber-800 font-medium">Función renal:</span>
            <span className="text-amber-900">
              {summary.contextual_factors.renal_function === 'normal' ? 'Normal' :
               summary.contextual_factors.renal_function === 'mild_impairment' ? 'Leve deterioro' :
               summary.contextual_factors.renal_function === 'moderate_impairment' ? 'Moderado deterioro' :
               'Severo deterioro'}
            </span>
          </div>
          {summary.contextual_factors.special_considerations.length > 0 && (
            <div className="pt-2 border-t border-amber-200">
              <p className="text-xs font-medium text-amber-800 mb-1">Otras consideraciones:</p>
              <ul className="text-xs space-y-1">
                {summary.contextual_factors.special_considerations.map((consideration, idx) => (
                  <li key={idx} className="text-amber-700">• {consideration}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
