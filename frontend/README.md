# MediCopilot Nexus - Frontend

AI-powered medical assistant frontend built with Next.js, TypeScript, and TailwindCSS.

## Features

### Two-Column Interface
- **Left Column (55%)**: SOAP Editor with 4 tabs (Subjetivo, Objetivo, Evaluación, Plan)
- **Right Column (45%)**: AI Assistant Panel with 4 tabs (Paciente, Sugerencias, Plan, Fuentes)

### Real-time Intelligence
- **Debounced HPI Suggestions**: Suggestions appear automatically as you type (800ms delay)
- **Clinical Plan Generation**: Comprehensive plan with differentials, labs, and medications
- **Safety Alerts**: Allergy checking, drug interactions, and contraindications
- **Mexican Drug Brands**: Integration with PLM for commercial medication names

### Key Components
1. **Patient Snapshot**: Demographics, allergies, active medications, labs
2. **Suggestions Panel**: Suggested questions, red flags, clinical scores (e.g., Centor)
3. **Clinical Plan Panel**: Differentials, lab tests, medications with brands, patient instructions
4. **Citations Panel**: Sources from GPC, NOM, PLM, and COFEPRIS

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Axios** - API client
- **Lucide React** - Icons
- **React Markdown** - Markdown rendering

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The application will be available at **http://localhost:3000** (or port 3001 if 3000 is in use).

## Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_USE_MOCK_DATA=true  # Set to false to use real backend
```

## Development Modes

### Mock Data Mode (Default)
Set `NEXT_PUBLIC_USE_MOCK_DATA=true` to use built-in mock responses. This allows frontend development without a running backend.

### Real API Mode
Set `NEXT_PUBLIC_USE_MOCK_DATA=false` to connect to the actual FastAPI backend at `http://localhost:8000`.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Main page (home)
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── common/            # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Tabs.tsx
│   │   ├── editor/            # SOAP Editor components
│   │   │   └── SOAPEditor.tsx
│   │   └── assistant/         # Assistant Panel components
│   │       ├── AssistantPanel.tsx
│   │       ├── PatientSnapshot.tsx
│   │       ├── SuggestionsPanel.tsx
│   │       ├── ClinicalPlanPanel.tsx
│   │       └── CitationsPanel.tsx
│   ├── hooks/                 # Custom React hooks
│   │   └── useDebounce.ts
│   ├── services/              # API client
│   │   └── api.ts
│   ├── types/                 # TypeScript type definitions
│   │   └── index.ts
│   └── lib/                   # Utility functions
├── public/                    # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

## Key Features Implementation

### Real-time HPI Suggestions
The application uses a debounced hook to trigger suggestions as the user types in the Subjective field:

```typescript
// Triggers after 800ms of no typing
const debouncedSubjective = useDebounce(editorState.subjective, 800);

// Fetches suggestions with last 600 characters
const hpiTail = debouncedSubjective.slice(-600);
```

### Clinical Plan Generation
Click the "Generar Plan Clínico" button to:
1. Send SOAP summary to backend
2. Receive differential diagnoses
3. Get laboratory recommendations
4. Receive medication suggestions with Mexican brands
5. Display safety alerts (allergies, interactions)
6. Show patient instructions

### Export Functionality
- **Copy SOAP Note**: Copies formatted SOAP note to clipboard
- **Copy Prescription**: Copies medications with brands and dosing
- **Copy Instructions**: Copies patient instructions

## API Integration

The application communicates with the FastAPI backend through these endpoints:

### POST `/assist/hpi`
Real-time HPI suggestions
- **Latency target**: <2 seconds
- **Input**: HPI tail (last 600 chars) + patient snapshot
- **Output**: Suggested questions, red flags, clinical scores

### POST `/plan/generate`
Clinical plan generation
- **Latency target**: <5 seconds
- **Input**: SOAP summary + patient snapshot
- **Output**: Differentials, labs, medications, alerts, instructions, citations

### GET `/patients/{id}`
Patient data retrieval
- **Output**: Complete patient snapshot with demographics, allergies, medications

## Mock Data

The application includes comprehensive mock data for:
- **Patient**: María G., 28F with penicillin allergy
- **Pharyngitis scenario**: Centor criteria, suggested questions, treatment plan
- **Medications**: Azitromicina and Paracetamol with Mexican brands
- **Safety alerts**: Penicillin allergy detection

## Styling

The UI uses TailwindCSS with a medical-professional color scheme:
- **Blue**: Primary actions, suggestions
- **Red**: Allergies, high-priority alerts
- **Green**: Medications, treatments
- **Purple**: Laboratory tests, clinical scores
- **Orange**: Patient instructions, warnings

## Performance Optimizations

1. **Debouncing**: 800ms delay on HPI suggestions to reduce API calls
2. **AbortController**: Cancels previous requests when new ones are triggered
3. **Lazy Loading**: Components load only when needed
4. **Memoization**: React hooks prevent unnecessary re-renders

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

This is a hackathon project built for the Saptiva AI Healthcare Challenge (October 24, 2025).

## License

TBD (pending hackathon completion)

## Credits

Built with:
- [Saptiva AI](https://saptiva.com) - LLM orchestration and embeddings
- [Ragster](https://github.com/ragster/ragster) - RAG pipeline
- [Next.js](https://nextjs.org) - React framework
- [TailwindCSS](https://tailwindcss.com) - Styling
- [Lucide](https://lucide.dev) - Icons

---

**Version**: 0.1.0
**Author**: Juan Pablo
**Date**: October 24, 2025
