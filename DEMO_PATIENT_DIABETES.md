# Demo Patient - Diabetes Tipo 2

## Patient Information (Snapshot)

```
Nombre: María González Pérez
Edad: 52 años
Sexo: Femenino
Peso: 82 kg
Talla: 160 cm
IMC: 32.0 (Obesidad grado I)

Alergias: Ninguna conocida
Medicamentos actuales: Losartán 50 mg 1 vez al día

Antecedentes:
- Hipertensión arterial (diagnosticada hace 2 años, controlada)
- Madre con diabetes tipo 2
- Padre con cardiopatía isquémica
```

---

## HISTORIA CLÍNICA (Anamnesis/HPI)

**Copy this into the "Historia Clínica" field:**

```
Paciente femenina de 52 años de edad que acude a consulta por cuadro de aproximadamente 3 meses de evolución caracterizado por polidipsia, poliuria y pérdida de peso no intencionada de 5 kg.

Refiere que ha notado aumento en la frecuencia urinaria, levantándose 3-4 veces por la noche para orinar. Menciona sed excesiva, llegando a tomar hasta 3 litros de agua al día. Niega visión borrosa, parestesias o heridas de difícil cicatrización.

Reporta astenia y adinamia en las últimas semanas. Comenta que su madre fue diagnosticada con diabetes a los 55 años.

Antecedentes personales patológicos: Hipertensión arterial diagnosticada hace 2 años, actualmente en tratamiento con losartán 50 mg/día con buen control. Niega tabaquismo. Consumo de alcohol ocasional (social).

Antecedentes heredofamiliares: Madre con diabetes mellitus tipo 2. Padre finado por infarto agudo al miocardio a los 68 años.
```

**What the RAG should suggest:**
- ¿Ha presentado visión borrosa?
- ¿Antecedentes de infecciones recurrentes?
- ¿Ha notado pérdida de peso? ¿Cuántos kg?
- Valorar HbA1c y glucosa en ayuno
- Considerar perfil de lípidos
- Evaluar score de riesgo cardiovascular

---

## EXAMEN FÍSICO (Physical Examination)

**Copy this into the "Examen Físico" field:**

```
Paciente consciente, orientada en tiempo, lugar y persona. Adecuada coloración de piel y mucosas. Hidratada.

Signos vitales:
- TA: 130/85 mmHg
- FC: 78 lpm
- FR: 16 rpm
- Temperatura: 36.7°C
- Peso: 82 kg
- Talla: 160 cm
- IMC: 32.0 kg/m²

Cabeza y cuello: Normocéfalo. Pupilas isocóricas y normorreflécticas. Mucosa oral hidratada. Cuello sin adenomegalias, tiroides no palpable.

Tórax: Ruidos cardíacos rítmicos, sin soplos. Campos pulmonares bien ventilados, sin estertores.

Abdomen: Blando, depresible, no doloroso a la palpación. Ruidos peristálticos presentes. Sin visceromegalias.

Extremidades: Pulsos periféricos presentes y simétricos. Llenado capilar <2 segundos. Sensibilidad conservada. Reflejos osteotendinosos normales. Sin edema.

Pie diabético: Inspección de pies sin lesiones, úlceras o deformidades. Sensibilidad al monofilamento conservada bilateral.
```

**What the RAG should suggest:**
- Revisar sensibilidad en pies con monofilamento
- Evaluar pulsos pedios
- Medir perímetro abdominal
- Realizar fondo de ojo (o referir a oftalmología)

---

## LABORATORIOS (To mention/order)

**Resultados disponibles hoy:**
```
Glucosa en ayuno: 185 mg/dL (VN: 70-100)
HbA1c: 8.5% (VN: <5.7%)
Creatinina: 0.9 mg/dL
TFG estimada: 78 mL/min/1.73m²
```

**Laboratorios a solicitar:**
```
- Perfil de lípidos (colesterol total, HDL, LDL, triglicéridos)
- Pruebas de función hepática
- Examen general de orina
- Microalbuminuria
- TSH
```

---

## PLAN (Assessment & Plan)

**Copy this into the "Plan" field (or let RAG generate it):**

```
IMPRESIÓN DIAGNÓSTICA:
1. Diabetes Mellitus tipo 2 de reciente diagnóstico (HbA1c 8.5%)
2. Obesidad grado I (IMC 32)
3. Hipertensión arterial controlada

PLAN TERAPÉUTICO:

1. TRATAMIENTO FARMACOLÓGICO - Diabetes:
   - Metformina 850 mg vía oral cada 12 horas con alimentos
   - Marca sugerida: Glucophage o Dabex
   - Iniciar con 850 mg cada 24 horas por 1 semana, luego aumentar a cada 12 horas si tolera
   - Advertir sobre efectos gastrointestinales (diarrea, náuseas) - tomar con alimentos

2. TRATAMIENTO NO FARMACOLÓGICO:
   - Modificación del estilo de vida:
     * Dieta: Plan de alimentación con restricción de carbohidratos simples, 1500-1800 kcal/día
     * Referencia a nutrición para plan personalizado
     * Ejercicio: 150 minutos de actividad aeróbica moderada por semana (30 min/día, 5 días)
     * Reducción de peso: Meta de pérdida del 5-10% del peso actual (4-8 kg)

3. MONITOREO:
   - Automonitoreo de glucosa capilar: En ayuno y 2 horas postprandial, 3 veces por semana
   - Llevar bitácora de glucosas
   - Control médico en 4 semanas para ajuste de dosis
   - Meta glucémica: Glucosa en ayuno 80-130 mg/dL, HbA1c <7%

4. ESTUDIOS COMPLEMENTARIOS:
   - Perfil de lípidos
   - Microalbuminuria
   - Referencia a oftalmología para fondo de ojo (descartar retinopatía)
   - EKG

5. EDUCACIÓN AL PACIENTE:
   - Explicar qué es la diabetes y sus complicaciones
   - Reconocer signos de hipoglucemia y cómo tratarla
   - Importancia de adherencia al tratamiento
   - Cuidado de los pies
   - Signos de alarma: visión borrosa, dolor torácico, úlceras en pies

6. SEGUIMIENTO:
   - Próxima cita: 4 semanas
   - HbA1c de control en 3 meses
   - Evaluación anual de complicaciones crónicas

PRONÓSTICO: Favorable con adherencia al tratamiento y modificaciones del estilo de vida.
```

---

## PRESCRIPTION (Receta)

**What the system should generate:**

```
PRESCRIPCIÓN MÉDICA

Paciente: María González Pérez
Fecha: [Fecha actual]

Rx:
1. METFORMINA 850 mg
   - Presentación: Tabletas
   - Marca comercial: Dabex (Laboratorios Silanes) o Glucophage (Merck)
   - Dosis: 1 tableta cada 12 horas
   - Vía: Oral
   - Indicaciones: Tomar con alimentos para reducir efectos gastrointestinales
   - Iniciar con 1 tableta cada 24 horas por 7 días, luego aumentar a cada 12 horas
   - Cantidad a surtir: 60 tabletas (2 cajas de 30)
   - Duración: 1 mes

2. LOSARTÁN 50 mg
   - Continuar tratamiento actual
   - Dosis: 1 tableta cada 24 horas
   - Vía: Oral

RECOMENDACIONES:
- Tomar metformina con alimentos
- Suspender 48 horas antes si requiere estudios con medio de contraste
- Monitoreo de glucosa capilar según indicado
- Dieta baja en carbohidratos simples
- Ejercicio 30 minutos diarios
- Acudir a urgencias si presenta: visión borrosa súbita, dolor torácico, dificultad respiratoria

Próxima cita: 4 semanas

____________________
Dr. [Nombre]
Cédula profesional: [Número]
```

---

## PATIENT INSTRUCTIONS (Instrucciones al Paciente)

**What the system should generate in patient-friendly language:**

```
INSTRUCCIONES PARA LA PACIENTE - DIABETES

Señora María:

Le diagnosticamos DIABETES TIPO 2. Esto significa que su cuerpo no está procesando bien el azúcar. Con tratamiento y cambios en su estilo de vida, puede controlarla bien.

MEDICAMENTO:
📋 METFORMINA (Dabex o Glucophage)
   - Tomar 1 pastilla cada 12 horas CON ALIMENTOS (desayuno y cena)
   - La primera semana: solo 1 pastilla al día
   - Segunda semana en adelante: 1 pastilla cada 12 horas
   - Es normal tener un poco de diarrea o náuseas los primeros días - mejorará

⚠️ IMPORTANTE: Si le van a hacer estudios con contraste (rayos X especiales), avise que toma metformina - debe suspenderla 48 horas antes.

ALIMENTACIÓN:
🥗 Lo que SÍ puede comer:
   - Verduras (todas las que quiera)
   - Carnes magras (pollo, pescado, res sin grasa)
   - Huevo
   - Aguacate, nueces (con moderación)
   - Frijoles, lentejas (media taza)

❌ Lo que debe EVITAR:
   - Refrescos, jugos (aunque sean naturales)
   - Pan dulce, pasteles, galletas
   - Tortillas en exceso (máximo 2-3 al día)
   - Frutas muy dulces (plátano, mango, uvas)
   - Arroz, pasta en grandes cantidades

EJERCICIO:
🚶‍♀️ Caminar 30 minutos al día, 5 días a la semana
   - Puede ser en 2 sesiones de 15 minutos
   - No tiene que ser muy rápido, solo mantener el paso

MONITOREO:
📊 Medir su azúcar 3 veces por semana:
   - En ayunas (antes de desayunar)
   - 2 horas después del desayuno
   - Anotar los resultados en una libreta

METAS:
🎯 Azúcar en ayunas: 80-130 mg/dL
🎯 Bajar 4-8 kilos en 3-6 meses
🎯 HbA1c menor a 7% en 3 meses

SIGNOS DE ALARMA - Acudir a urgencias si presenta:
🚨 Visión borrosa de repente
🚨 Dolor en el pecho
🚨 Mareo intenso o desmayo
🚨 Heridas en los pies que no sanan
🚨 Azúcar menor a 70 mg/dL (hipoglucemia)

CUIDADO DE LOS PIES:
👣 Revisar sus pies todos los días
   - Buscar cortadas, ampollas, enrojecimiento
   - Usar zapatos cómodos
   - Nunca andar descalza
   - Secar bien entre los dedos después de bañarse

CITAS:
📅 Próxima consulta: 4 semanas
📅 Nutrición: [Fecha por agendar]
📅 Oftalmología: [Fecha por agendar]

¿Dudas? Llame al consultorio: [Teléfono]
```

---

## RAG INTERACTION POINTS

### When typing Historia Clínica:
**Trigger**: "polidipsia, poliuria, pérdida de peso"
**RAG suggests**:
- ¿Triada clásica completa? (polifagia)
- ¿Visión borrosa?
- ¿Parestesias en extremidades?
- Aplicar Escala de Riesgo Findrisc
- Solicitar HbA1c

### When typing Examen Físico:
**Trigger**: "diabetes", "IMC 32"
**RAG suggests**:
- Evaluar sensibilidad con monofilamento de Semmes-Weinstein
- Medir perímetro abdominal
- Buscar acantosis nigricans
- Explorar reflejos osteotendinosos

### When generating Plan:
**Query**: "tratamiento diabetes tipo 2 primera línea"
**RAG returns** (from GPC):
- Metformina como primera línea
- Metas de HbA1c <7%
- Modificaciones de estilo de vida
- Referencia a educación diabetológica

### When selecting medication:
**Query**: "metformina marcas comerciales México"
**RAG returns** (from PLM):
```
1. Glucophage 850mg - $185.50
   Dosing: 500-850mg con alimentos, 1-2 veces/día
   Contraindicaciones: TFG <30, acidosis metabólica

2. Dabex 500mg - $95.00
   Dosing: 500mg 2-3 veces/día
   Interacciones: Contrastes yodados, alcohol
```

### Safety Check:
**Automatic checks**:
- ✅ No alergias a metformina
- ✅ TFG: 78 mL/min (OK para metformina)
- ✅ Sin contraindicaciones con losartán
- ⚠️ Recordatorio: Suspender antes de contrastes

---

## EXPECTED DEMO FLOW

1. **Open patient file** → See snapshot (52F, obese, hypertensive)
2. **Start typing HPI** → RAG suggests questions in real-time
3. **Type Physical Exam** → RAG suggests what to examine
4. **Click "Generate Plan"** → RAG searches GPC, suggests metformin
5. **Search "metformina"** → RAG shows 2 brands from PLM with prices
6. **Select Dabex** → System shows dosing, contraindications
7. **Run safety check** → ✅ All clear (show the checks)
8. **Generate prescription** → PDF with all details
9. **Generate patient instructions** → Patient-friendly Spanish
10. **Show sources** → Links to GPC diabetes, PLM Dabex entry

---

## WHY THIS DEMO WORKS

✅ **Complete data pipeline:**
- GPC guideline (185 chunks) → Treatment recommendation
- PLM database (2 brands) → Medication selection
- Safety checks → Drug interactions, contraindications

✅ **Real clinical scenario:**
- Common condition
- Clear treatment path
- Multiple decision points

✅ **Impressive AI features:**
- Real-time suggestions while typing
- Evidence-based recommendations (GPC)
- Commercial medication information (PLM)
- Safety checking
- Patient education generation

✅ **Mexican context:**
- Medications available in Mexico
- Prices in pesos
- COFEPRIS registry
- Spanish language throughout

---

**Ready to paste and test!**
