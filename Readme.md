# 🧠 Workday Resilience AI  
**Privacy-first, offline-capable, context-aware health assistant for desk workers.**

Workday Resilience AI is a multi-tab Gradio application designed to help office and remote workers detect hidden workplace health risks (burnout, musculoskeletal strain, dehydration, eye strain, poor recovery) and translate daily inputs into **actionable prevention guidance**.

Unlike typical tracking tools, this platform focuses on **structured reasoning**, **risk scoring**, and **measurable progress metrics**, while keeping user data local by default.

---

## 🚀 Why This Project Matters

Sedentary work is a major modern health risk. It contributes to:

- chronic musculoskeletal pain
- burnout and stress-related fatigue
- digital eye strain
- poor hydration habits
- sleep disruption
- long-term cardiometabolic risk

Workday Resilience AI provides a practical solution by helping users detect risk patterns early and take small preventive actions daily.

---

## ✨ Key Features

### 🧩 Multi-Tab Structured Health Inputs
The platform collects structured user inputs through specialized tabs:

- Baseline (biometrics and vitals)
- Workspace (ergonomics & environment)
- Longitudinal (labs tracking)
- MSK (musculoskeletal symptoms)
- Eye (screen strain & headaches)
- Mental (stress and burnout signals)
- Hydration (water/caffeine symptoms)
- Productivity (workload & focus patterns)
- Recovery/Sleep (rest and recovery indicators)
- Checklist (habit tracking)
- Reminders (task nudges)
- Context (cross-domain extracted context)
- Reports (exportable summaries)
- Settings / Help
- **Dashboard (Risk + Impact Metrics)**

---

## 📊 Risk Scoring & Dashboard

Workday Resilience AI includes a built-in scoring system:

- Tab-level risk scores (0–100)
- Overall **Workday Health Index (WHI)**
- Cross-domain influence weighting (70% tab + 30% global context)
- Risk levels: Low / Moderate / High / Critical

The Dashboard provides:
- WHI score
- top risk areas
- risk visualization chart
- weekly progress metrics

---

## 📈 Impact Metrics (Measurable Change)

To demonstrate measurable health improvement, the platform computes weekly progress metrics such as:

- hydration compliance %
- sedentary sitting block reduction
- reminders completed
- high-risk days avoided (WHI ≥ threshold)
- sleep trend (if sleep history is available)

This allows users and evaluators to track improvement over time, not just raw risk detection.

---

# 🏗️ Architecture Overview

Workday Resilience AI follows a simple, scalable architecture:

### Core pipeline
**Structured inputs → Local storage → Context memory → Reasoning engine → Recommendations + Scores + Reminders**

---

## 🧠 Architecture Diagram (High-Level)

```text
┌──────────────────────────────┐
│        User Inputs Tabs       │
│ Baseline / Workspace / MSK    │
│ Eye / Hydration / Mental      │
│ Productivity / Sleep / Labs   │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│     Local JSON Storage Layer  │
│   (privacy-first, offline)    │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ Context Builder & Memory Layer│
│ (cross-tab pattern extraction)│
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│   Reasoning & Safety Engine   │
│ - risk scoring (WHI)          │
│ - flags & urgent warnings     │
│ - logic-based fallbacks       │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│     AI Agent (Optional)       │
│ Hybrid Mode: Offline/Online   │
│ (LLM-based recommendations)   │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│  Output Layer (Gradio UI)     │
│ Recommendations + Reports     │
│ Reminders + Dashboard Charts  │
└──────────────────────────────┘
