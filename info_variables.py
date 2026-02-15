ABOUT_APP_MD = """# 🏢 Workday Resilience AI

## Overview

**Sedentary work is one of the most underestimated modern health risks.**  
The World Health Organization reports that **31% of adults worldwide (≈1.8 billion people)** are insufficiently physically active — a pattern strongly linked to chronic disease risk and premature mortality. WHO also warns that insufficient physical activity is associated with a **20–30% higher risk of death**, and recommends actively reducing sedentary time throughout the day.  

At the same time, long screen exposure has become the default. Digital Eye Strain (Computer Vision Syndrome) is widely reported among screen users, causing symptoms such as **dry eyes, blurred vision, headaches, and difficulty focusing**, especially when workdays are built around uninterrupted monitor time.

The result is a predictable cycle for desk workers:  
**back and neck pain → fatigue → low productivity → stress → worse sleep → repeat.**

The **Workday Resilience AI** is a **privacy-first, local-only, context-aware preventive health assistant** designed specifically for office and remote desk workers.  
It helps users reflect on their daily workplace behaviors (posture, hydration, stress, eye strain, productivity, musculoskeletal symptoms, sleep recovery, and longitudinal lab trends) and then produces **clear, non-diagnostic, evidence-aligned recommendations**.

This platform is not a symptom checker and does not attempt to replace clinicians.  
Instead, it acts as a **structured reasoning layer** between everyday work habits and actionable prevention — translating scattered inputs into practical steps, reminders, and habit nudges.

---

## 🎯 Problem & Target Users

### The problem
Desk work concentrates multiple risk factors into a single routine:
- prolonged sitting and low movement,
- poor posture and repetitive strain,
- screen-based eye fatigue and headaches,
- mental overload, stress, and burnout patterns,
- inconsistent hydration, recovery, and sleep.

Many existing tools either:
- collect health data without generating meaningful guidance, or
- rely on cloud-based processing that compromises privacy and user control.

### Target users
- Office and remote desk workers  
- Knowledge workers with long screen hours  
- Professionals with chronic fatigue, posture pain, or eye strain  
- Health-conscious users who value **privacy, autonomy, and clarity**

---

## ✨ Key Features

- **Modular Health Tabs**  
  Baseline, Workspace, MSK, Eye, Mental, Hydration, Productivity, Recovery/Sleep, Checklist, Reminders.

- **Local-Only Storage (Privacy by Design)**  
  All user data is stored locally as JSON — no automatic uploads, no hidden telemetry.

- **Context-Aware Reasoning**  
  The system builds a cross-domain context from real user inputs, allowing the assistant to detect patterns (e.g., hydration + headaches + screen time + poor sleep).

- **Safety Guardrails**  
  Explicit checks for high-risk signals (e.g., severe symptoms, mental distress keywords, extreme values) to trigger urgent warnings.

- **Optional AI Integration (Graceful Fallback)**  
  Uses a language model only when configured; otherwise runs locally with safe placeholder logic.

- **Actionable Output, Not Just Tracking**  
  Generates clear recommendations plus structured **tasks and reminders** that convert insight into daily behavior change.

- **Internationalization (i18n)**  
  Built-in multilingual support (English & Arabic included), designed for global deployment.

---

## 🧠 Architecture & Data

The platform is built around a simple but powerful principle:

**Collect structured user inputs → build contextual memory → apply reasoning → output practical prevention guidance.**

Each module stores user entries and AI outputs in domain-specific JSON files.  
A lightweight shared context layer allows cross-domain summaries without exposing raw histories, enabling explainable reasoning while maintaining performance and privacy.

This notebook is a **self-contained, executable skeleton** demonstrating:
- how user health inputs are collected,
- how context is constructed across domains,
- how safe reasoning is applied,
- and how the full system runs locally with optional AI support.

---

## 🌍 Why This Matters

Workplace health is not only a medical issue — it is a productivity and sustainability issue.  
Preventable desk-work habits contribute to pain, fatigue, reduced concentration, and long-term chronic risk.  
By turning routine behaviors into actionable guidance, this platform helps individuals regain control over their health **without giving up their data**.

The goal is simple:

**help desk workers build healthier workdays — one small decision at a time.**
"""

MENTAL_WELLBEING_INFO_MD = """
# 🧠 Mental Wellbeing Module  
*Cognitive Load & Burnout Awareness*

Desk-based work places sustained demands on attention, emotional regulation, and
mental energy. Over time, high cognitive load, constant interruptions, and limited
recovery can contribute to stress accumulation, reduced focus, and early burnout
signals—often before individuals consciously recognize them.

This module is designed to support **mental wellbeing awareness**, not diagnosis.
It helps identify daily patterns related to stress, cognitive fatigue, and emotional
load in the context of work routines.

### What this module captures
- Perceived stress level
- Mood state
- Mental energy and brain fog
- Focus quality and workload perception
- Distractions (internal vs external)
- Burnout warning signs (detachment, overwhelm)
- Sleep quality and coping mechanisms

### Why this matters
Mental fatigue and burnout rarely appear suddenly. They typically develop through
small, repeated stressors combined with insufficient recovery. Desk work can
intensify this process due to prolonged screen exposure, cognitive overload, and
blurred boundaries between work and rest.

By reflecting on daily mental signals, this module helps highlight trends that may
affect productivity, wellbeing, and long-term resilience—before more severe
consequences occur.

### How AI is used in this section
The AI provides **supportive, non-diagnostic guidance** focused on:
- Simple grounding and reset techniques
- Burnout prevention through small, realistic actions
- Improving coping strategies during demanding workdays
- Practical sleep hygiene recommendations

The aim is to promote awareness, balance, and early prevention—not to replace
professional care.
"""
HYDRATION_INFO_MD = """
# 💧 Hydration & Kidney Health Module

Hydration plays a critical role in concentration, energy levels, kidney function,
and overall physical wellbeing—especially for people who spend long hours at a desk.
Mild dehydration is common in office settings and often goes unnoticed until symptoms
such as headache, fatigue, or brain fog appear.

This module is designed to move beyond simple “water tracking” by combining
**daily hydration behaviors** with **physiological bio-feedback signals**. Together,
these provide a more realistic picture of hydration status than intake alone.

### What this module captures
- Daily water intake (number of glasses)
- Caffeine consumption (coffee, tea, energy drinks)
- Sugary drink intake
- Hydration habits (e.g., keeping a water bottle visible on the desk)
- Urine color indicator
- Thirst sensation
- Common dehydration symptoms (headache, brain fog, dizziness)

### Why this matters
Relying on thirst alone can be misleading, as thirst is often a **late signal**
of dehydration. Caffeine use, long screen time, and busy work routines can further
mask early warning signs.

By combining habits and body signals, this module helps identify patterns that may
affect productivity, comfort, and kidney health—without requiring perfect tracking
or medical interpretation.

### How AI is used in this section
The AI generates **non-diagnostic, preventive guidance** focused on:
- Practical hydration targets for desk-based work
- Habit nudges that fit real workdays
- Early warning signals of possible dehydration
- Short, actionable checklists for same-day improvement

The goal is awareness and prevention—not diagnosis.
"""
WORKSPACE_INFO_MD = """
# 🪑 Workspace & Ergonomics Module  
*Physical Environment & Posture Awareness*

The physical workspace plays a central role in musculoskeletal health, comfort,
and sustained productivity. Desk-based work often involves prolonged sitting,
repetitive movements, and fixed postures that can gradually place strain on the
neck, shoulders, back, wrists, and eyes—often without immediate pain.

This module is designed to support **workspace and posture awareness**, not
diagnosis. It helps identify everyday environmental and ergonomic factors that may
contribute to discomfort, fatigue, or long-term strain during desk work.

### What this module captures
- Type of workspace (office, home, shared)
- Chair and desk setup
- Screen height and viewing distance
- Keyboard and mouse positioning
- Sitting duration and movement breaks
- Posture-related discomfort or pain signals
- Use of ergonomic supports (chair, stand, external devices)

### Why this matters
Poor ergonomics rarely cause sudden injury. Instead, strain typically accumulates
through small mismatches between the body and the work environment—such as low
screens, unsupported seating, or long periods without movement.

Over time, these factors can contribute to musculoskeletal discomfort, reduced
concentration, and decreased work endurance. Early awareness allows for simple,
low-cost adjustments that may significantly reduce long-term risk.

### How AI is used in this section
The AI provides **non-diagnostic, preventive guidance** focused on:
- Practical ergonomic adjustments for desk-based work
- Posture and movement reminders that fit real workdays
- Reducing strain through small environmental changes
- Simple habits to support long-term musculoskeletal health

The goal is to promote comfort, sustainability, and prevention—not to replace
professional ergonomic or medical assessment.
"""
MSK_INFO_MD = """
# 🦴 Musculoskeletal (MSK) Health Module  
*Movement, Load & Pain Awareness*

Musculoskeletal discomfort is one of the most common consequences of prolonged
desk-based work. Limited movement, static postures, repetitive tasks, and poor
load distribution can gradually affect the neck, shoulders, back, hips, and
upper limbs—often starting as mild discomfort before progressing further.

This module is designed to support **musculoskeletal health awareness**, not
diagnosis. It focuses on identifying movement patterns, pain signals, and daily
habits that may influence physical comfort and long-term joint and muscle health.

### What this module captures
- Presence and location of musculoskeletal pain
- Pain intensity and frequency
- Stiffness or reduced mobility
- Duration of sitting and physical inactivity
- Break frequency and movement habits
- Physical strain related to work tasks
- Use of stretching or physical activity for relief

### Why this matters
Musculoskeletal strain typically develops gradually rather than through sudden
injury. Ignoring early warning signs such as stiffness or recurring pain can allow
problems to accumulate over time.

By increasing awareness of pain patterns and movement behavior, this module helps
highlight opportunities for simple preventive actions that may reduce discomfort
and support long-term physical function.

### How AI is used in this section
The AI provides **non-diagnostic, preventive guidance** focused on:
- Gentle movement and stretching suggestions
- Reducing prolonged static load during work
- Encouraging regular movement breaks
- Supporting sustainable physical habits at work

The aim is prevention and early awareness—not medical assessment or treatment.
"""
EYE_HEALTH_INFO_MD = """
# 👁️ Eye Health Module  
*Visual Load & Screen Strain Awareness*

Extended screen exposure is a defining feature of modern desk work. Prolonged
visual focus, reduced blinking, glare, and improper screen positioning can place
significant strain on the eyes—often leading to symptoms such as dryness, blurred
vision, headaches, or eye fatigue.

This module is designed to support **eye health awareness**, not diagnosis. It
helps identify daily screen-related behaviors and visual symptoms that may affect
comfort, focus, and visual endurance during work.

### What this module captures
- Daily screen time duration
- Frequency of visual breaks
- Eye strain or discomfort symptoms
- Headaches related to screen use
- Screen distance and height
- Lighting conditions and glare
- Use of corrective lenses or filters

### Why this matters
Eye strain often develops silently and may be mistaken for general fatigue or
headache. Without regular visual breaks and proper screen setup, symptoms can
accumulate and affect both comfort and work performance.

Early awareness allows for small, practical adjustments that can significantly
reduce visual load and support long-term eye comfort.

### How AI is used in this section
The AI provides **non-diagnostic, preventive guidance** focused on:
- Visual break strategies suitable for workdays
- Screen positioning and lighting adjustments
- Habits that support eye comfort during screen use
- Reducing cumulative visual strain over time

The goal is to promote visual comfort and sustainability—not to replace eye care
assessment.
"""
PRODUCTIVITY_INFO_MD = """
# 📈 Productivity & Focus Module  
*Attention, Workflow & Efficiency Awareness*

Productivity during desk work is influenced not only by workload, but also by
attention management, task structure, and environmental distractions. Cognitive
overload, frequent interruptions, and unclear task boundaries can gradually
reduce focus and perceived efficiency.

This module is designed to support **productivity and focus awareness**, not
performance evaluation. It helps identify patterns related to attention,
distraction, and workflow that may affect daily output and mental effort.

### What this module captures
- Perceived focus quality
- Workload intensity and pacing
- Task switching frequency
- Internal and external distractions
- Energy consistency throughout the day
- Break patterns and recovery pauses
- Perceived productivity barriers

### Why this matters
Reduced productivity is often a signal of system strain rather than individual
failure. Persistent distraction and overload can increase mental fatigue and
reduce work satisfaction over time.

By identifying attention patterns and workflow challenges, this module supports
small, realistic adjustments that may improve focus and sustainability at work.

### How AI is used in this section
The AI provides **non-diagnostic, supportive guidance** focused on:
- Attention management strategies
- Structuring work to reduce cognitive overload
- Improving task flow and break timing
- Supporting sustainable productivity habits

The aim is to enhance clarity and efficiency—not to measure or judge performance.
"""
RECOVERY_SLEEP_INFO_MD = """
# 😴 Recovery & Sleep Module  
*Rest, Recovery & Sleep Awareness*

Adequate recovery is essential for both physical and mental performance. Desk
work, irregular schedules, stress, and extended screen exposure—especially late
in the day—can interfere with sleep quality and overnight recovery.

This module is designed to support **recovery and sleep awareness**, not diagnosis.
It focuses on identifying rest patterns, sleep-related behaviors, and recovery
signals that influence daily energy and resilience.

### What this module captures
- Sleep duration and perceived quality
- Sleep consistency and timing
- Daytime fatigue or sleepiness
- Evening screen exposure
- Recovery practices and wind-down routines
- Use of caffeine or stimulants
- Perceived restfulness upon waking

### Why this matters
Poor sleep and inadequate recovery often accumulate gradually, affecting mood,
focus, physical comfort, and stress tolerance. These effects may be subtle at
first but can compound over time.

Early awareness of sleep and recovery patterns allows for simple behavioral
adjustments that may support long-term wellbeing and daily performance.

### How AI is used in this section
The AI provides **non-diagnostic, preventive guidance** focused on:
- Sleep hygiene and consistency
- Evening routines that support recovery
- Managing stimulants and screen exposure
- Practical steps to improve daily restoration

The goal is to promote sustainable recovery—not to replace sleep or medical care.
"""
