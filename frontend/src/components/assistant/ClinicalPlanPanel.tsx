import React, { useState } from 'react';
import { PlanResponse, SafetyAlert } from '@/types';
import { Activity, TestTube, Pill, AlertCircle, FileText, Copy, Check } from 'lucide-react';

interface ClinicalPlanPanelProps {
  plan: PlanResponse | null;
  isLoading: boolean;
}

export function ClinicalPlanPanel({ plan, isLoading }: ClinicalPlanPanelProps) {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const copyToClipboard = async (text: string, section: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <svg className="animate-spin h-8 w-8 text-blue-600 mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-sm text-gray-600">Generando plan clínico...</p>
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="text-center py-12 text-gray-500">
        <FileText size={48} className="mx-auto mb-3 text-gray-300" />
        <p className="text-sm">Haga clic en "Generar Plan Clínico"</p>
        <p className="text-xs mt-1">Complete al menos el Subjetivo u Objetivo primero</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Safety Alerts */}
      {plan.alerts.length > 0 && (
        <div className="space-y-2">
          {plan.alerts.map((alert, index) => (
            <AlertBanner key={index} alert={alert} />
          ))}
        </div>
      )}

      {/* Differentials */}
      {plan.differentials.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Activity size={18} className="text-blue-600" />
            <h3 className="font-semibold text-gray-900 text-sm">Diagnósticos Diferenciales</h3>
          </div>
          <div className="space-y-3">
            {plan.differentials.map((diff, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900 flex-1">{diff.diagnosis}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    diff.probability === 'high' ? 'bg-red-100 text-red-700' :
                    diff.probability === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {diff.probability === 'high' ? 'Alta' :
                     diff.probability === 'medium' ? 'Media' : 'Baja'}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{diff.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Laboratory Tests */}
      {plan.labs.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <TestTube size={18} className="text-purple-600" />
            <h3 className="font-semibold text-gray-900 text-sm">Laboratorios Recomendados</h3>
          </div>
          <div className="space-y-2">
            {plan.labs.map((lab, index) => (
              <div key={index} className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <div className="flex items-start justify-between mb-1">
                  <p className="font-medium text-purple-900 text-sm">{lab.test}</p>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    lab.priority === 'high' ? 'bg-red-200 text-red-800' :
                    lab.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-gray-200 text-gray-800'
                  }`}>
                    {lab.priority === 'high' ? 'Alta' :
                     lab.priority === 'medium' ? 'Media' : 'Baja'} prioridad
                  </span>
                </div>
                <p className="text-xs text-purple-700">{lab.indication}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medications */}
      {plan.medications.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Pill size={18} className="text-green-600" />
              <h3 className="font-semibold text-gray-900 text-sm">Medicamentos</h3>
            </div>
            <button
              onClick={() => {
                const prescriptionText = plan.medications.map((med) =>
                  `${med.generic} ${med.dose} ${med.route}\n${med.frequency} por ${med.duration}\n${med.brands?.[0]?.brand_name || ''}`
                ).join('\n\n');
                copyToClipboard(prescriptionText, 'prescription');
              }}
              className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              {copiedSection === 'prescription' ? (
                <><Check size={14} /> Copiado</>
              ) : (
                <><Copy size={14} /> Copiar receta</>
              )}
            </button>
          </div>
          <div className="space-y-4">
            {plan.medications.map((med, index) => (
              <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="mb-2">
                  <h4 className="font-semibold text-green-900">{med.generic}</h4>
                  <p className="text-sm text-green-800">
                    {med.dose} {med.route} - {med.frequency} por {med.duration}
                  </p>
                </div>
                {med.brands && med.brands.length > 0 && (
                  <div className="mb-2">
                    <p className="text-xs text-green-700 font-medium mb-1">Marcas comerciales:</p>
                    <div className="flex flex-wrap gap-2">
                      {med.brands.map((brand, idx) => (
                        <span key={idx} className="text-xs bg-white border border-green-300 rounded px-2 py-1">
                          {brand.brand_name} ({brand.presentation})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div className="bg-green-100 rounded p-2">
                  <p className="text-xs text-green-900">
                    <span className="font-semibold">Justificación:</span> {med.rationale}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Patient Instructions */}
      {plan.patient_instructions.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <FileText size={18} className="text-orange-600" />
              <h3 className="font-semibold text-gray-900 text-sm">Instrucciones al Paciente</h3>
            </div>
            <button
              onClick={() => {
                const instructionsText = plan.patient_instructions.join('\n');
                copyToClipboard(instructionsText, 'instructions');
              }}
              className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              {copiedSection === 'instructions' ? (
                <><Check size={14} /> Copiado</>
              ) : (
                <><Copy size={14} /> Copiar</>
              )}
            </button>
          </div>
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <ul className="space-y-2">
              {plan.patient_instructions.map((instruction, index) => (
                <li key={index} className="text-sm text-orange-900 flex items-start gap-2">
                  <span className="text-orange-600 mt-0.5 font-bold">{index + 1}.</span>
                  <span>{instruction}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

function AlertBanner({ alert }: { alert: SafetyAlert }) {
  const colors = {
    high: 'bg-red-50 border-red-300 text-red-900',
    medium: 'bg-yellow-50 border-yellow-300 text-yellow-900',
    low: 'bg-blue-50 border-blue-300 text-blue-900',
  };

  return (
    <div className={`border rounded-lg p-4 ${colors[alert.severity]}`}>
      <div className="flex items-start gap-3">
        <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="font-semibold text-sm mb-1">{alert.message}</p>
          {alert.action_taken && (
            <p className="text-xs opacity-90">✓ {alert.action_taken}</p>
          )}
        </div>
      </div>
    </div>
  );
}
