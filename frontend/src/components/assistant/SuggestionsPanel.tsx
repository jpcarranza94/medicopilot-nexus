import React from 'react';
import { SuggestionsResponse } from '@/types';
import { Lightbulb, AlertTriangle, Target } from 'lucide-react';

interface SuggestionsPanelProps {
  suggestions: SuggestionsResponse | null;
  isLoading: boolean;
  onInsertQuestion: (question: string) => void;
}

export function SuggestionsPanel({
  suggestions,
  isLoading,
  onInsertQuestion,
}: SuggestionsPanelProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <svg className="animate-spin h-8 w-8 text-blue-600 mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-sm text-gray-600">Generando sugerencias...</p>
        </div>
      </div>
    );
  }

  if (!suggestions) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Lightbulb size={48} className="mx-auto mb-3 text-gray-300" />
        <p className="text-sm">Comience a escribir la Historia Clínica</p>
        <p className="text-xs mt-1">Las sugerencias aparecerán automáticamente</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Suggested Questions */}
      {suggestions.suggested_questions.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb size={18} className="text-blue-600" />
            <h3 className="font-semibold text-gray-900 text-sm">Preguntas Sugeridas</h3>
          </div>
          <div className="space-y-2">
            {suggestions.suggested_questions.map((question, index) => (
              <div
                key={index}
                className="bg-blue-50 border border-blue-200 rounded-lg p-3 hover:bg-blue-100 transition-colors group"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm text-gray-800 flex-1">{question}</p>
                  <button
                    onClick={() => onInsertQuestion(question)}
                    className="text-xs bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700 transition-all opacity-70 hover:opacity-100 hover:scale-105 flex-shrink-0"
                  >
                    Insertar
                  </button>
                </div>              </div>
            ))}
          </div>
        </div>
      )}

      {/* Red Flags */}
      {suggestions.red_flags.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={18} className="text-red-600" />
            <h3 className="font-semibold text-red-900 text-sm">Signos de Alarma</h3>
          </div>
          <div className="space-y-2">
            {suggestions.red_flags.map((flag, index) => (
              <div
                key={index}
                className="bg-red-50 border border-red-200 rounded-lg p-3"
              >
                <p className="text-sm text-red-800 font-medium flex items-center gap-2">
                  <span>⚠️</span>
                  {flag}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clinical Scores */}
      {suggestions.scores.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Target size={18} className="text-purple-600" />
            <h3 className="font-semibold text-gray-900 text-sm">Escalas Clínicas Relevantes</h3>
          </div>
          <div className="space-y-3">
            {suggestions.scores.map((score, index) => (
              <div
                key={index}
                className="bg-purple-50 border border-purple-200 rounded-lg p-4"
              >
                <h4 className="font-semibold text-purple-900 mb-2">
                  {score.name}
                </h4>
                <div className="mb-3">
                  <p className="text-xs text-purple-700 font-medium mb-1">Criterios:</p>
                  <ul className="space-y-1">
                    {score.criteria.map((criterion, idx) => (
                      <li key={idx} className="text-sm text-purple-800 flex items-start gap-2">
                        <span className="text-purple-600 mt-0.5">•</span>
                        <span>{criterion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-purple-100 rounded p-2">
                  <p className="text-xs text-purple-900">
                    <span className="font-semibold">Por qué importa:</span>{' '}
                    {score.why_it_matters}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
