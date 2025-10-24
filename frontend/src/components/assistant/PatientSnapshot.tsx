import React from 'react';
import { PatientSnapshot as PatientSnapshotType } from '@/types';
import { User, AlertCircle, Pill, FileText } from 'lucide-react';

interface PatientSnapshotProps {
  patient: PatientSnapshotType;
}

export function PatientSnapshot({ patient }: PatientSnapshotProps) {
  return (
    <div className="space-y-4">
      {/* Demographics */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <User size={18} className="text-blue-600" />
          <h3 className="font-semibold text-blue-900">Datos del Paciente</h3>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-600">Nombre:</span>
            <p className="font-medium">{patient.name}</p>
          </div>
          <div>
            <span className="text-gray-600">Edad:</span>
            <p className="font-medium">{patient.age} años</p>
          </div>
          <div>
            <span className="text-gray-600">Sexo:</span>
            <p className="font-medium">{patient.sex === 'F' ? 'Femenino' : 'Masculino'}</p>
          </div>
          {patient.weight_kg && (
            <div>
              <span className="text-gray-600">Peso:</span>
              <p className="font-medium">{patient.weight_kg} kg</p>
            </div>
          )}
        </div>
      </div>

      {/* Allergies */}
      {patient.allergies.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle size={18} className="text-red-600" />
            <h3 className="font-semibold text-red-900">Alergias</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {patient.allergies.map((allergy, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 border border-red-300"
              >
                ⚠️ {allergy}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Active Medications */}
      {patient.active_medications.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Pill size={18} className="text-gray-600" />
            <h3 className="font-semibold text-gray-900">Medicamentos Activos</h3>
          </div>
          <ul className="space-y-1">
            {patient.active_medications.map((med, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                {med}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Chief Complaint */}
      {patient.chief_complaint && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <FileText size={18} className="text-gray-600" />
            <h3 className="font-semibold text-gray-900">Motivo de Consulta</h3>
          </div>
          <p className="text-sm text-gray-700">{patient.chief_complaint}</p>
        </div>
      )}

      {/* Recent Labs */}
      {patient.recent_labs && patient.recent_labs.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3 text-sm">Laboratorios Recientes</h3>
          <div className="space-y-2">
            {patient.recent_labs.map((lab, index) => (
              <div key={index} className="flex justify-between items-center text-sm">
                <span className="text-gray-600">{lab.test}</span>
                <span className={`font-medium ${
                  lab.flag === 'high' ? 'text-red-600' :
                  lab.flag === 'low' ? 'text-orange-600' :
                  'text-green-600'
                }`}>
                  {lab.value}
                  {lab.flag !== 'normal' && (
                    <span className="ml-1">
                      {lab.flag === 'high' ? '↑' : '↓'}
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Previous Diagnoses */}
      {patient.previous_diagnoses && patient.previous_diagnoses.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2 text-sm">Diagnósticos Previos</h3>
          <ul className="space-y-1">
            {patient.previous_diagnoses.map((diagnosis, index) => (
              <li key={index} className="text-sm text-gray-600 flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-gray-300 rounded-full"></span>
                {diagnosis}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Clinical Context */}
      {(patient.pregnant || patient.egfr) && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <h3 className="font-semibold text-amber-900 mb-2 text-sm">Contexto Clínico</h3>
          <div className="space-y-1 text-sm">
            {patient.pregnant !== undefined && (
              <p className="text-amber-800">
                Embarazo: {patient.pregnant ? '✓ Sí' : '✗ No'}
              </p>
            )}
            {patient.egfr && (
              <p className="text-amber-800">
                TFG estimada: {patient.egfr} mL/min/1.73m²
                {patient.egfr < 60 && <span className="ml-2 text-red-600 font-medium">⚠️ Insuficiencia renal</span>}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
