import React from 'react';
import { Citation } from '@/types';
import { BookOpen, Calendar, Tag } from 'lucide-react';

interface CitationsPanelProps {
  citations: Citation[];
}

export function CitationsPanel({ citations }: CitationsPanelProps) {
  if (citations.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <BookOpen size={48} className="mx-auto mb-3 text-gray-300" />
        <p className="text-sm">No hay citas disponibles aún</p>
        <p className="text-xs mt-1">Las fuentes aparecerán aquí después de generar sugerencias o plan</p>
      </div>
    );
  }

  const namespaceLabels: Record<string, string> = {
    gpc: 'Guía de Práctica Clínica',
    nom: 'Norma Oficial Mexicana',
    plm: 'PLM - Diccionario Farmacéutico',
    cofepris: 'COFEPRIS - Registro Sanitario',
  };

  const namespaceColors: Record<string, string> = {
    gpc: 'bg-blue-100 text-blue-800 border-blue-300',
    nom: 'bg-purple-100 text-purple-800 border-purple-300',
    plm: 'bg-green-100 text-green-800 border-green-300',
    cofepris: 'bg-orange-100 text-orange-800 border-orange-300',
  };

  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        <p>Todas las recomendaciones están respaldadas por las siguientes fuentes:</p>
      </div>

      {citations.map((citation, index) => (
        <div
          key={index}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start gap-3">
            <BookOpen size={18} className="text-gray-400 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <h4 className="font-medium text-gray-900 text-sm">
                  {citation.source}
                </h4>
                <span className={`text-xs px-2 py-0.5 rounded border ${namespaceColors[citation.namespace]}`}>
                  {namespaceLabels[citation.namespace]}
                </span>
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                <div className="flex items-center gap-1">
                  <Tag size={12} />
                  <span>Fragmento #{citation.chunk_index + 1}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar size={12} />
                  <span>{new Date(citation.upload_date).toLocaleDateString('es-MX')}</span>
                </div>
              </div>

              {citation.text && (
                <div className="bg-gray-50 rounded p-3 mt-2">
                  <p className="text-xs text-gray-700 italic leading-relaxed">
                    "{citation.text}"
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-xs text-blue-900">
          <span className="font-semibold">Nota:</span> MediCopilot Nexus genera recomendaciones basadas en
          guías de práctica clínica mexicanas y regulaciones oficiales. Siempre revise y valide las
          recomendaciones según su juicio clínico.
        </p>
      </div>
    </div>
  );
}
