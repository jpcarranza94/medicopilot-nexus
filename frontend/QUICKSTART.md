# Quick Start Guide

## Open the Application

🌐 **http://localhost:3001**

The server is already running!

## 5-Minute Demo Flow

### 1. View Patient Info (10 seconds)
- Click **"Paciente"** tab on the right
- See María G., 28F with penicillin allergy
- Note the red allergy badge ⚠️

### 2. Type HPI and See Suggestions (60 seconds)
- Click **"Subjetivo"** tab on the left
- Type this text:
  ```
  Paciente refiere dolor de garganta de 3 días de evolución,
  acompañado de fiebre hasta 38.5°C y odinofagia intensa.
  Niega presencia de tos.
  ```
- Switch to **"Sugerencias"** tab on the right
- Wait ~1 second for suggestions to appear
- See:
  - ✅ Suggested questions (clickable)
  - ⚠️ Red flags
  - 🎯 Centor score criteria
- Click **"Insertar"** on a suggested question

### 3. Add Physical Exam (20 seconds)
- Click **"Objetivo"** tab on the left
- Type:
  ```
  Temperatura: 38.2°C
  FC: 88 lpm, FR: 16 rpm
  Orofaringe: Exudado amigdalino bilateral, eritema faríngeo
  Cuello: Adenopatías cervicales anteriores palpables y dolorosas
  ```

### 4. Generate Clinical Plan (90 seconds)
- Click **"🔵 Generar Plan Clínico"** button
- Wait ~2 seconds
- Switch to **"Plan"** tab on the right
- See:
  - 🔴 **Safety Alert**: "ALERGIA A PENICILINA"
  - 📊 **Differentials**: Faringoamigdalitis estreptocócica (alta)
  - 🧪 **Labs**: Test rápido Streptococcus A
  - 💊 **Medications**:
    - Azitromicina 500mg (brands: Azitro-500, Azitromicina MK)
    - Paracetamol 500mg
  - 📋 **Patient Instructions**: 6 clear steps

### 5. Export (20 seconds)
- Click **"Copiar SOAP"** in header
- Paste into notepad (see formatted SOAP note)
- Click **"Copiar receta"** in Plan panel
- Paste to see prescription format
- Click **"Copiar"** on Patient Instructions

### 6. View Sources (10 seconds)
- Click **"Fuentes"** tab
- See citations from:
  - GPC_Faringitis_2019.pdf
  - PLM_Azitromicina.html

**Total Demo Time**: ~3 minutes

## Key Features to Highlight

### Real-time Intelligence
- Suggestions appear automatically as you type
- 800ms debounce = smooth UX
- No button clicks needed

### Safety First
- **Red allergy alerts** prevent dangerous prescriptions
- Penicillin allergy → Azitromicina selected automatically
- Clear warning messages

### Mexican Healthcare Context
- Drug brands from PLM
- Commercial names (Azitro-500, Tempra)
- Presentations in mg/tablet format

### Professional UX
- Clean, medical-grade interface
- Color-coded sections
- Copy-to-clipboard for everything

## Troubleshooting

### Can't access localhost:3001?
Check if server is running:
```bash
cd /home/jpcar/personal-projects/medicopilot/frontend
npm run dev
```

### Want to use a different port?
```bash
npm run dev -- -p 3000
```

### Need to restart?
```bash
pkill -f "next dev"
npm run dev
```

## Demo Script for Video

```
[0-10s] "MediCopilot Nexus: tu asistente clínico inteligente"
        - Show patient snapshot with allergy

[10-35s] Real-time suggestions
         - Type HPI about sore throat
         - Show Centor criteria appearing
         - Click to insert a question

[35-55s] Generate comprehensive plan
         - Click "Generar Plan"
         - Highlight allergy alert
         - Show Azitromicina as safe alternative

[55-60s] Export and close
         - Copy prescription
         - Show Mexican brands
         - Credits: "Powered by Saptiva & Ragster"
```

---

**Ready to demo! 🎬**
