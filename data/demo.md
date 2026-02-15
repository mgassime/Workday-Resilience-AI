Absolutely — and since your notebook already **saves real inputs/outputs into `data/`**, the cleanest demo engine is:

* **Replay saved demo data** (fast, works offline, shows real outputs in the notebook)
* **Only call the same “Generate AI” callbacks** *if* a module has no saved AI output yet

Below is a complete, drop-in implementation (engine + notebook button + UI button), and the **tiny hook you add once per module** so the demo can reuse the same functions your buttons already use.

---

## 0) What this gives you

✅ One **shared demo engine** used by both:

* a **Notebook button** (output appears in notebook cells)
* a **Gradio button** (output appears in UI)

✅ Uses **existing saved files in `data/`**:

* `{domain}_user_input.json` (latest user input)
* `{domain}_ai_output.json` (latest AI output)
* plus global:

  * `general_recommendations_ai_output.json`
  * `tasks_reminders_user_input.json`
  * optional schedule: `reminder_schedule.json`

✅ Uses **the same logic as your app buttons** because:

* if saved AI output is missing, it calls your module’s existing `generate_ai(...)` callback (the same function wired to “Generate AI …”)

---

# 1) Add this cell near the top of the notebook (Notebook button + shared engine)

> Put this in an early cell (near top).
> It’s safe: it won’t run until you click the demo button.

```python
# ==========================================
# DEMO ENGINE (shared) + NOTEBOOK BUTTON
# ==========================================

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Callable, Dict, List, Optional, Any, Tuple

import pandas as pd

# Global registry filled by module hooks (see section 2)
_DEMO_HOOKS: Dict[str, "DemoHook"] = {}

@dataclass
class DemoHook:
    domain: str
    label: str
    user_file: str
    ai_file: str
    record_keys: List[str]                 # order = same order your generate_ai expects
    generate_fn: Optional[Callable] = None # your existing generate_ai callback

def register_demo_hook(
    domain: str,
    label: str,
    user_file: str,
    ai_file: str,
    record_keys: List[str],
    generate_fn: Optional[Callable] = None,
):
    """Call this from inside each connect_*_logic to expose existing callbacks to the demo engine."""
    _DEMO_HOOKS[domain] = DemoHook(
        domain=domain,
        label=label,
        user_file=user_file,
        ai_file=ai_file,
        record_keys=record_keys,
        generate_fn=generate_fn,
    )

def _latest_record(store, filename: str, field: str) -> Any:
    """Loads latest record[field] from a JSON list file. Returns None if missing."""
    raw = store.load_json(filename, [])
    if not isinstance(raw, list) or not raw:
        return None
    last = raw[-1]
    if not isinstance(last, dict):
        return None
    return last.get(field, None)

def _compact_input_md(d: dict, max_items: int = 12) -> str:
    """Small, judge-friendly snapshot (not huge JSON dumps)."""
    if not isinstance(d, dict) or not d:
        return "_(no input found)_"
    items = list(d.items())[:max_items]
    lines = []
    for k, v in items:
        if isinstance(v, list):
            v = ", ".join(map(str, v[:8])) + (" ..." if len(v) > 8 else "")
        lines.append(f"- **{k}**: {v}")
    if len(d) > max_items:
        lines.append(f"- … _(and {len(d)-max_items} more fields)_")
    return "\n".join(lines)

def run_full_demo_core(
    store=None,
    gemini=None,
    lang_state=None,
    *,
    replay_saved_outputs: bool = True,
    generate_if_missing: bool = True,
    domains_order: Optional[List[str]] = None,
) -> Tuple[str, str, Optional[pd.DataFrame]]:
    """
    Shared engine:
    - Prefer showing saved AI output from data folder (fast)
    - If missing and generate_fn exists, call the same generate_ai callbacks your buttons use
    Returns: (report_md, status_md, schedule_df_or_None)
    """

    # Resolve store/client/lang_state from globals if not passed
    g = globals()
    store = store or g.get("store")
    gemini = gemini or g.get("client") or g.get("gemini")
    lang_state = lang_state or g.get("lang_state") or SimpleNamespace(value="en")

    if store is None:
        return "", "❌ Demo engine: `store` not found. Run setup cells first.", None

    # If hooks are empty, try building the app once (so connect_*_logic runs and registers hooks)
    if not _DEMO_HOOKS:
        build_app_fn = g.get("build_app")
        if callable(build_app_fn):
            try:
                _ = build_app_fn()  # builds tabs, triggers connect_*_logic, fills hooks
            except Exception as e:
                return "", f"❌ Demo engine: hooks not ready and build_app() failed: {e}", None

    if not _DEMO_HOOKS:
        return "", "❌ Demo engine: no module hooks registered yet. (See section 2 below.)", None

    # default order (matches your platform structure)
    if domains_order is None:
        domains_order = [
            "baseline",
            "workspace",
            "longitudinal",
            "msk",
            "eye",
            "mental",
            "hydration",
            "productivity",
            "recovery_sleep",
        ]

    status_lines = []
    parts = []

    # --- HEADER ---
    parts.append("# 🚀 Full Demo Report (from saved data)")
    parts.append(
        "This demo replays the latest saved inputs/outputs from the `data/` folder. "
        "If a module has no saved AI output, it will generate it using the same callback your tab button uses."
    )

    # --- PER-MODULE ---
    for dom in domains_order:
        hook = _DEMO_HOOKS.get(dom)
        if not hook:
            status_lines.append(f"⚠️ {dom}: no hook registered")
            continue

        user_in = _latest_record(store, hook.user_file, "user_input")
        ai_out = _latest_record(store, hook.ai_file, "ai_output")

        if user_in is None:
            status_lines.append(f"⚠️ {hook.label}: no saved user input ({hook.user_file})")
            parts.append(f"\n---\n## {hook.label}\n⚠️ No saved user input found.\n")
            continue

        # Try to replay saved output
        if replay_saved_outputs and isinstance(ai_out, str) and ai_out.strip():
            status_lines.append(f"✅ {hook.label}: replayed saved AI output")
            parts.append(f"\n---\n## {hook.label}\n### Demo Input Snapshot\n{_compact_input_md(user_in)}\n\n### AI Output (saved)\n{ai_out}\n")
            continue

        # Otherwise, generate using the same generate_ai callback wired to the button
        if generate_if_missing and hook.generate_fn:
            try:
                args = [user_in.get(k, None) for k in hook.record_keys]
                result = hook.generate_fn(*args)
                # your generate_ai returns (text, status)
                if isinstance(result, tuple) and len(result) >= 1:
                    gen_text = result[0] or ""
                else:
                    gen_text = str(result or "")
                status_lines.append(f"✅ {hook.label}: generated via tab callback")
                parts.append(f"\n---\n## {hook.label}\n### Demo Input Snapshot\n{_compact_input_md(user_in)}\n\n### AI Output (generated)\n{gen_text}\n")
                continue
            except Exception as e:
                status_lines.append(f"❌ {hook.label}: generate failed ({e})")
                parts.append(f"\n---\n## {hook.label}\n❌ Generate failed: `{e}`\n")
                continue

        status_lines.append(f"⚠️ {hook.label}: no saved AI output and no generate_fn")
        parts.append(f"\n---\n## {hook.label}\n### Demo Input Snapshot\n{_compact_input_md(user_in)}\n\n⚠️ No saved AI output and no generator hook registered.\n")

    # --- GLOBAL ACTION CENTER (replay if exists; otherwise generate) ---
    parts.append("\n---\n# 🌍 General Recommendations (Action Center)\n")
    try:
        # You already have this helper in the notebook:
        load_state = g.get("load_global_recommendations_state")
        if callable(load_state):
            last_recs, last_tasks, last_reminders = load_state(store)
        else:
            last_recs = last_tasks = last_reminders = ""

        if (last_recs or "").strip():
            parts.append("### Health Analysis (saved)\n" + last_recs)
        elif gemini and callable(g.get("generate_global_recommendations")):
            rec_text, rec_status = g["generate_global_recommendations"](store, gemini, lang_state)
            parts.append("### Health Analysis (generated)\n" + (rec_text or ""))
            status_lines.append(rec_status or "Generated recommendations")
        else:
            parts.append("⚠️ No saved recommendations and generator not available.")

        if (last_tasks or "").strip() or (last_reminders or "").strip():
            parts.append("\n### Tasks (saved)\n" + (last_tasks or ""))
            parts.append("\n### Reminders (saved)\n" + (last_reminders or ""))
        elif gemini and callable(g.get("generate_tasks_and_reminders_from_analysis")):
            # Only if we have analysis text to feed
            analysis_text = (last_recs or "").strip()
            if not analysis_text and "rec_text" in locals():
                analysis_text = (rec_text or "").strip()
            t_text, r_text, t_status = g["generate_tasks_and_reminders_from_analysis"](gemini, lang_state, analysis_text)
            parts.append("\n### Tasks (generated)\n" + (t_text or ""))
            parts.append("\n### Reminders (generated)\n" + (r_text or ""))
            status_lines.append(t_status or "Generated tasks/reminders")
        else:
            parts.append("\n⚠️ No saved tasks/reminders and generator not available.")
    except Exception as e:
        parts.append(f"\n❌ Global Action Center demo failed: `{e}`")

    # --- OPTIONAL: Reminder schedule preview (if it exists) ---
    schedule_df = None
    try:
        sched = store.load_json("reminder_schedule.json", {})
        if isinstance(sched, dict) and isinstance(sched.get("schedule"), list) and sched["schedule"]:
            schedule_df = pd.DataFrame(sched["schedule"])
    except Exception:
        schedule_df = None

    report_md = "\n".join(parts)
    status_md = "## Demo Status\n" + ("\n".join(f"- {s}" for s in status_lines) if status_lines else "- ✅ Ready")

    return report_md, status_md, schedule_df


# --------------------------
# NOTEBOOK BUTTON (ipywidgets)
# --------------------------
try:
    import ipywidgets as widgets
    from IPython.display import display, Markdown, clear_output

    demo_btn = widgets.Button(description="🚀 Run Full Demo", button_style="success")
    clear_btn = widgets.Button(description="🧹 Clear Output", button_style="")
    out = widgets.Output()

    def _on_demo_click(_):
        with out:
            clear_output(wait=True)
            report, status, df = run_full_demo_core()
            display(Markdown(status))
            display(Markdown(report))
            if df is not None and not df.empty:
                display(df)

    def _on_clear_click(_):
        with out:
            clear_output(wait=True)

    demo_btn.on_click(_on_demo_click)
    clear_btn.on_click(_on_clear_click)

    display(widgets.HBox([demo_btn, clear_btn]))
    display(out)

except Exception as e:
    print("⚠️ ipywidgets not available/enabled in this environment:", e)
    print("You can still run: report, status, df = run_full_demo_core()")
```

---

# 2) Add ONE “hook line” inside each module’s `connect_*_logic` (so demo can reuse the same button callback)

This is the only “wiring” you need per module.

### Example: Baseline (`connect_baseline_logic`)

Insert this **right before** the “Buttons UI” section in your `connect_baseline_logic` cell:

```python
    # -------------------------
    # Demo hook registration
    # -------------------------
    try:
        register_demo_hook(
            domain=domain,
            label="Baseline",
            user_file=user_file,
            ai_file=ai_file,
            record_keys=[
                "height",
                "weight",
                "bp_systolic",
                "bp_diastolic",
                "rhr",
                "body_fat",
                "waist_cm",
                "activity_level",
                "notes",
            ],
            generate_fn=generate_ai,  # SAME function used by the tab button
        )
    except Exception as e:
        print(f"[baseline] ⚠️ demo hook registration failed: {e}")
```

### Do the same for each domain (copy/paste these blocks)

**Workspace**

```python
    try:
        register_demo_hook(
            domain=domain,
            label="Workspace",
            user_file=user_file,
            ai_file=ai_file,
            record_keys=[
                "good_posture",
                "breaks",
                "eat_at_desk",
                "input_device",
                "keyboard_type",
                "wrist_support",
                "armrests",
                "lumbar_support",
                "monitor_height",
                "feet_position",
                "noise_level",
                "temperature",
                "clutter",
                "notes",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[workspace] ⚠️ demo hook registration failed: {e}")
```

**Longitudinal**

```python
    try:
        register_demo_hook(
            domain=domain,
            label="Longitudinal",
            user_file=user_file,
            ai_file=ai_file,
            record_keys=[
                "notes",
                "hb",
                "wbc",
                "platelets",
                "glucose",
                "hba1c",
                "cholesterol",
                "triglycerides",
                "vit_d",
                "vit_b12",
                "tsh",
                "custom_name",
                "custom_value",
                "custom_unit",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[longitudinal] ⚠️ demo hook registration failed: {e}")
```

**MSK** (your code uses `local_domain/local_user_file/local_ai_file`)

```python
    try:
        register_demo_hook(
            domain=local_domain,
            label="MSK",
            user_file=local_user_file,
            ai_file=local_ai_file,
            record_keys=[
                "pain_level",
                "onset_timing",
                "focus_area",
                "pain_nature",
                "neck_rom",
                "seated_duration",
                "morning_stiffness",
                "good_posture",
                "triggers",
                "relief_methods",
                "impact_work",
                "impact_sleep",
                "notes",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[msk] ⚠️ demo hook registration failed: {e}")
```

**Eye**

```python
    try:
        register_demo_hook(
            domain=local_domain,
            label="Eye",
            user_file=local_user_file,
            ai_file=local_ai_file,
            record_keys=[
                "strain_level",
                "session_length",
                "symptoms",
                "lighting",
                "screen_brightness",
                "glare",
                "distance_check",
                "correction",
                "rule_20_20_20",
                "used_drops",
                "notes",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[eye] ⚠️ demo hook registration failed: {e}")
```

**Mental**

```python
    try:
        register_demo_hook(
            domain=local_domain,
            label="Mental",
            user_file=local_user_file,
            ai_file=local_ai_file,
            record_keys=[
                "stress",
                "mood",
                "energy",
                "focus_quality",
                "workload",
                "distractions",
                "detachment",
                "overwhelm",
                "social",
                "sleep_quality",
                "coping",
                "notes",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[mental] ⚠️ demo hook registration failed: {e}")
```

**Hydration**

```python
    try:
        register_demo_hook(
            domain=local_domain,
            label="Hydration",
            user_file=local_user_file,
            ai_file=local_ai_file,
            record_keys=[
                "water_intake",
                "caffeine_intake",
                "bottle_on_desk",
                "sugary_drinks",
                "urine_color",
                "thirst_level",
                "symptoms",
                "notes",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[hydration] ⚠️ demo hook registration failed: {e}")
```

**Productivity**

```python
    try:
        register_demo_hook(
            domain=local_domain,
            label="Productivity",
            user_file=local_user_file,
            ai_file=local_ai_file,
            record_keys=[
                "focus_quality",
                "deep_work",
                "flow_state",
                "satisfaction",
                "health_tax",
                "blocker",
                "peak_energy",
                "slump_severity",
                "top_distraction",
                "context_switching",
                "methods",
                "notes",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[productivity] ⚠️ demo hook registration failed: {e}")
```

**Recovery / Sleep**

```python
    try:
        register_demo_hook(
            domain=local_domain,
            label="Recovery / Sleep",
            user_file=local_user_file,
            ai_file=local_ai_file,
            record_keys=[
                "well_rested",
                "sleep_hours",
                "screen_cutoff",
                "blue_light_filter",
                "evening_movement",
                "stress_level",
                "room_comfort",
            ],
            generate_fn=generate_ai,
        )
    except Exception as e:
        print(f"[recovery_sleep] ⚠️ demo hook registration failed: {e}")
```

---

# 3) Add a Demo button in the Gradio UI (using the SAME engine)

Add this **new tab builder** anywhere near your other `build_*_tab` functions:

```python
import gradio as gr

def build_demo_tab(store, gemini, lang_state, locales_dir=None):
    gr.Markdown("## 🚀 Full Demo (Notebook + UI shared engine)")
    gr.Markdown("Replays the latest saved demo data from `data/` and generates missing outputs if needed.")

    btn = gr.Button("🚀 Run Full Demo", variant="primary")
    status = gr.Markdown()
    report = gr.Markdown()
    sched = gr.Dataframe(label="Reminder Schedule Preview (if available)", interactive=False)

    def _run():
        rep, st, df = run_full_demo_core(store=store, gemini=gemini, lang_state=lang_state)
        # gr.Dataframe handles None, but we normalize
        if df is None:
            df = pd.DataFrame([])
        return st, rep, df

    btn.click(fn=_run, outputs=[status, report, sched])
```

Then add it to your tab registry list (`TAB_BUILDERS = [...]`) near the top:

```python
("Demo", build_demo_tab),
```

Put it above “General Recommendations” so judges see it first.

---

## Notes about your “data folder demo” requirement

* This engine **prefers** saved outputs first (fast + stable)
* It will call AI **only when a saved AI output file is missing/empty**
* It does **not overwrite** anything by default (it just reads), unless your generate callbacks save internally (your global rec generator does save; module generators usually only save when “Save AI Output” is clicked)

---

## If you want, I can also deliver a patched notebook file

I didn’t auto-edit your `.ipynb` in this message (to avoid breaking cells you may be actively modifying), but if you want I can generate an updated notebook that:

* inserts the demo engine cell at the top
* injects the hook blocks into each `connect_*_logic`
* adds the Demo tab to `TAB_BUILDERS`

Just tell me “yes patch it” and I’ll output the updated notebook as a downloadable file.
