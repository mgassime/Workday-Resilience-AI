import os
import json
import math
from typing import Dict, List, Any, Optional


# ============================================================
# Helpers
# ============================================================

def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def safe_int(x, default=0):
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        return default


def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def load_json_history(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def get_last_n(history: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    if not history:
        return []
    return history[-n:]


def weighted_average(scores: List[float], weights: List[float]) -> float:
    if not scores:
        return 0.0
    if len(scores) != len(weights):
        raise ValueError("Scores and weights length mismatch.")
    total_w = sum(weights)
    if total_w <= 0:
        return 0.0
    return sum(s * w for s, w in zip(scores, weights)) / total_w


def compute_weighted_recent_score(scores: List[float]) -> float:
    """
    Weighted average with recency preference.
    Designed for last 5 entries.
    """
    if not scores:
        return 0.0

    # If fewer entries exist, slice weights accordingly
    base_weights = [0.40, 0.25, 0.15, 0.12, 0.08]
    base_weights = base_weights[:len(scores)]

    # Scores list expected from oldest->newest; weights apply newest heavier
    # Convert to newest-first
    scores_newest_first = list(reversed(scores))

    # Weighted average (newest first)
    wavg = weighted_average(scores_newest_first, base_weights)

    # Spike protection: max in window
    max_score = max(scores)

    # Final combination
    final = 0.75 * wavg + 0.25 * max_score
    return clamp(final, 0, 100)


def normalize_score(raw_points: float, raw_max: float) -> float:
    if raw_max <= 0:
        return 0.0
    score = 100.0 * (raw_points / raw_max)
    return clamp(score, 0, 100)


# ============================================================
# TAB SCORING TABLES (Local Score per entry)
# ============================================================

def score_workspace_entry(ui: Dict[str, Any]) -> float:
    raw = 0

    # good_posture
    if ui.get("good_posture") is False:
        raw += 18

    # breaks
    breaks = (ui.get("breaks") or "").strip()
    if breaks == "Some breaks":
        raw += 8
    elif breaks == "Few breaks":
        raw += 16
    elif breaks == "No breaks":
        raw += 24

    # monitor height
    mh = (ui.get("monitor_height") or "").strip()
    if mh == "Slightly Below Eye Level":
        raw += 6
    elif mh == "Below Eye Level (Looking Down)":
        raw += 14
    elif mh == "Above Eye Level":
        raw += 10

    # lumbar support
    if ui.get("lumbar_support") is False:
        raw += 10

    # feet position
    fp = (ui.get("feet_position") or "").strip()
    if fp == "Not Supported / Dangling":
        raw += 8
    elif fp == "Crossed / Tucked":
        raw += 6

    # input device
    dev = (ui.get("input_device") or "").strip()
    if dev == "Standard Mouse":
        raw += 4
    elif dev == "Trackpad":
        raw += 10

    # keyboard type
    kb = (ui.get("keyboard_type") or "").strip()
    if kb == "Laptop Keyboard":
        raw += 8

    # wrist support
    ws = (ui.get("wrist_support") or "").strip()
    if ws == "No":
        raw += 6

    # armrests
    ar = (ui.get("armrests") or "").strip()
    if ar == "Level with desk":
        raw += 2
    elif ar in ["Too low", "Too high", "None", "No"]:
        raw += 6

    # eat at desk
    if ui.get("eat_at_desk") is True:
        raw += 6

    # noise
    noise = (ui.get("noise_level") or "").strip()
    if noise == "Hum/White Noise":
        raw += 3
    elif noise == "Distracting/Loud":
        raw += 10

    # temperature
    temp = (ui.get("temperature") or "").strip()
    if temp in ["Cold", "Hot"]:
        raw += 6

    # clutter
    cl = (ui.get("clutter") or "").strip()
    if cl == "Average":
        raw += 3
    elif cl == "Cluttered":
        raw += 8

    RAW_MAX = 100.0
    return normalize_score(raw, RAW_MAX)


def score_eye_entry(ui: Dict[str, Any]) -> float:
    raw = 0

    strain = safe_int(ui.get("strain_level"), 0)
    raw += strain * 4  # max 40

    session = (ui.get("session_length") or note_or_empty(ui.get("session_length"))).strip()
    if session == "1-2 hours":
        raw += 8
    elif session == "2-4 hours":
        raw += 16
    elif session == "4+ hours":
        raw += 24

    symptoms = ui.get("symptoms") or []
    symptom_points = 0
    symptom_map = {
        "Dryness / Gritty feeling": 8,
        "Blurred Vision (end of day)": 10,
        "Headache (behind eyes)": 12,
        "Eye Twitching": 8,
        "Watery Eyes": 6,
        "Burning / Irritation": 8,
        "Difficulty focusing": 10
    }
    for s in symptoms:
        symptom_points += symptom_map.get(s, 0)

    raw += min(symptom_points, 30)

    lighting = (ui.get("lighting") or "").strip()
    if lighting == "Mixed":
        raw += 6
    elif lighting == "Dim":
        raw += 10
    elif lighting == "Harsh/Overhead":
        raw += 10

    bright = (ui.get("screen_brightness") or "").strip()
    if bright == "Brighter than room":
        raw += 8
    elif bright == "Too dim":
        raw += 6

    if ui.get("glare") is True:
        raw += 10

    if ui.get("distance_check") is False:
        raw += 6

    rule = (ui.get("rule_20_20_20") or "").strip()
    if rule == "Often":
        raw += 4
    elif rule == "Occasionally":
        raw += 10
    elif rule == "Never":
        raw += 16

    if ui.get("used_drops") is True:
        raw -= 2

    RAW_MAX = 110.0
    return normalize_score(raw, RAW_MAX)


def score_hydration_entry(ui: Dict[str, Any]) -> float:
    raw = 0

    water = safe_int(ui.get("water_intake"), 0)

    if water <= 2:
        raw += 35
    elif 3 <= water <= 4:
        raw += 25
    elif 5 <= water <= 6:
        raw += 15
    elif 7 <= water <= 9:
        raw += 6
    elif 10 <= water <= 13:
        raw += 2
    else:
        raw += 0

    caffeine = safe_float(ui.get("caffeine_intake"), 0)
    if caffeine <= 1:
        raw += 0
    elif caffeine == 2:
        raw += 5
    elif caffeine == 3:
        raw += 10
    elif caffeine == 4:
        raw += 15
    elif caffeine >= 5:
        raw += 20

    sugary = safe_float(ui.get("sugary_drinks"), 0)
    if sugary == 0:
        raw += 0
    elif sugary == 1:
        raw += 5
    elif sugary == 2:
        raw += 10
    elif sugary == 3:
        raw += 15
    elif sugary >= 4:
        raw += 20

    if ui.get("bottle_on_desk") is False:
        raw += 6

    urine = (ui.get("urine_color") or "").strip()
    if urine == "Yellow (Okay)":
        raw += 6
    elif urine == "Dark Yellow":
        raw += 16
    elif urine == "Amber/Brown":
        raw += 28

    thirst = (ui.get("thirst_level") or "").strip()
    if thirst == "Mildly Thirsty":
        raw += 10
    elif thirst == "Very Thirsty / Parched":
        raw += 22

    symptoms = ui.get("symptoms") or []
    symptom_points = 0
    symptom_map = {
        "Dry Mouth/Lips": 8,
        "Headache": 10,
        "Dizziness": 12,
        "Fatigue": 8
    }
    for s in symptoms:
        symptom_points += symptom_map.get(s, 0)

    raw += min(symptom_points, 20)

    RAW_MAX = 100.0
    return normalize_score(raw, RAW_MAX)


def score_msk_entry(ui: Dict[str, Any]) -> float:
    raw = 0

    pain = safe_int(ui.get("pain_level"), 0)
    raw += pain * 4.5  # max 45

    onset = (ui.get("onset_timing") or "").strip()
    if onset == "During Work":
        raw += 10
    elif onset == "End of Workday":
        raw += 14
    elif onset == "Morning / On waking":
        raw += 18

    focus_area = ui.get("focus_area") or []
    raw += min(len(focus_area) * 5, 20)

    nature = (ui.get("pain_nature") or "").strip()
    if nature == "Mild Ache":
        raw += 4
    elif nature == "Stiffness/Tightness":
        raw += 10
    elif nature == "Sharp Pain":
        raw += 16
    elif nature == "Numbness/Tingling":
        raw += 22

    rom = (ui.get("neck_rom") or "").strip()
    if rom == "Limited (Stiff)":
        raw += 10
    elif rom == "Painful Movement":
        raw += 16

    seated = (ui.get("seated_duration") or "").strip()
    if seated == "1 hour":
        raw += 8
    elif seated == "2 hours":
        raw += 14
    elif seated == "3+ hours":
        raw += 22

    if ui.get("morning_stiffness") is True:
        raw += 10

    if ui.get("good_posture") is False:
        raw += 10

    triggers = ui.get("triggers") or []
    raw += min(len(triggers) * 4, 16)

    if ui.get("impact_work") is True:
        raw += 10

    if ui.get("impact_sleep") is True:
        raw += 12

    relief = ui.get("relief_methods") or []
    raw -= min(len(relief) * 3, 9)

    RAW_MAX = 120.0
    return normalize_score(raw, RAW_MAX)


def score_baseline_entry(ui: Dict[str, Any]) -> float:
    raw = 0

    height_cm = safe_float(ui.get("height"), 0)
    weight_kg = safe_float(ui.get("weight"), 0)

    bmi = 0
    if height_cm > 0 and weight_kg > 0:
        h_m = height_cm / 100.0
        bmi = weight_kg / (h_m * h_m)

    # BMI
    if bmi >= 35:
        raw += 32
    elif bmi >= 30:
        raw += 22
    elif bmi >= 25:
        raw += 10

    sys = safe_float(ui.get("bp_systolic"), 0)
    dia = safe_float(ui.get("bp_diastolic"), 0)

    if sys >= 140 or dia >= 90:
        raw += 24
    elif sys >= 130 or dia >= 80:
        raw += 14
    elif sys >= 120 and dia < 80:
        raw += 6

    rhr = safe_float(ui.get("rhr"), 0)
    if rhr >= 100:
        raw += 18
    elif rhr >= 90:
        raw += 12
    elif rhr >= 80:
        raw += 6
    elif rhr < 60 and rhr > 0:
        raw += 2

    activity = (ui.get("activity_level") or "").strip()
    if activity == "Sedentary":
        raw += 14
    elif activity == "Moderately active":
        raw += 4

    waist = safe_float(ui.get("waist_cm"), 0)
    if waist > 0:
        # crude threshold; you can refine later by sex
        if waist >= 102:
            raw += 14
        elif waist >= 94:
            raw += 10

    RAW_MAX = 110.0
    return normalize_score(raw, RAW_MAX)


def score_longitudinal_entry(ui: Dict[str, Any]) -> float:
    raw = 0

    glucose = safe_float(ui.get("glucose"), 0)
    if glucose >= 126:
        raw += 24
    elif glucose >= 100:
        raw += 12

    hba1c = safe_float(ui.get("hba1c"), 0)
    if hba1c >= 6.5:
        raw += 28
    elif hba1c >= 5.7:
        raw += 14

    chol = safe_float(ui.get("cholesterol"), 0)
    if chol >= 240:
        raw += 20
    elif chol >= 200:
        raw += 10

    tg = safe_float(ui.get("triglycerides"), 0)
    if tg >= 500:
        raw += 30
    elif tg >= 200:
        raw += 20
    elif tg >= 150:
        raw += 10

    vit_d = safe_float(ui.get("vit_d"), 0)
    if vit_d > 0 and vit_d < 20:
        raw += 10

    vit_b12 = safe_float(ui.get("vit_b12"), 0)
    if vit_b12 > 0 and vit_b12 < 200:
        raw += 10

    RAW_MAX = 140.0
    return normalize_score(raw, RAW_MAX)


# ============================================================
# Trend Penalty for Longitudinal (optional improvement)
# ============================================================

def trend_penalty(values: List[float]) -> float:
    """
    values oldest->newest
    Returns a penalty between -10 and +15
    """
    if len(values) < 2:
        return 0.0

    prev = values[-2]
    last = values[-1]
    if prev <= 0:
        return 0.0

    change = (last - prev) / prev

    if change >= 0.20:
        return 15.0
    if change >= 0.10:
        return 8.0
    if change <= -0.10:
        return -6.0

    return 0.0


def longitudinal_with_trend(history: List[Dict[str, Any]]) -> float:
    """
    70% latest + 30% trend penalty based on glucose/hba1c/chol/tg.
    """
    if not history:
        return 0.0

    last = history[-1].get("user_input", {})
    latest_score = score_longitudinal_entry(last)

    # Trend signals
    glucose_vals = []
    hba1c_vals = []
    chol_vals = []
    tg_vals = []

    for row in history[-3:]:
        ui = row.get("user_input", {})
        glucose_vals.append(safe_float(ui.get("glucose"), 0))
        hba1c_vals.append(safe_float(ui.get("hba1c"), 0))
        chol_vals.append(safe_float(ui.get("cholesterol"), 0))
        tg_vals.append(safe_float(ui.get("triglycerides"), 0))

    penalty = 0
    penalty += trend_penalty(glucose_vals)
    penalty += trend_penalty(hba1c_vals)
    penalty += trend_penalty(chol_vals)
    penalty += trend_penalty(tg_vals)

    penalty = clamp(penalty, -10, 15)

    final = 0.70 * latest_score + 0.30 * clamp(latest_score + penalty, 0, 100)
    return clamp(final, 0, 100)


# ============================================================
# Compute Tab Scores from History
# ============================================================

def tab_score_from_history(history: List[Dict[str, Any]], score_fn, window=5) -> float:
    if not history:
        return 0.0

    last_n = get_last_n(history, window)
    entry_scores = []

    for row in last_n:
        ui = row.get("user_input", {})
        entry_scores.append(score_fn(ui))

    return compute_weighted_recent_score(entry_scores)


def workspace_score_from_history(history: List[Dict[str, Any]]) -> float:
    """
    Workspace changes slowly: last 3 weighted.
    """
    if not history:
        return 0.0

    last_n = get_last_n(history, 3)
    scores = [score_workspace_entry(r.get("user_input", {})) for r in last_n]

    # newest weight highest
    scores_newest_first = list(reversed(scores))
    weights = [0.60, 0.30, 0.10][:len(scores_newest_first)]
    avg = weighted_average(scores_newest_first, weights)
    return clamp(avg, 0, 100)


def baseline_score_from_history(history: List[Dict[str, Any]]) -> float:
    """
    Baseline: use latest only (profile).
    """
    if not history:
        return 0.0
    ui = history[-1].get("user_input", {})
    return score_baseline_entry(ui)


# ============================================================
# Overall Workday Health Index (WHI)
# ============================================================

def compute_whi(scores: Dict[str, float]) -> float:
    """
    Weighted WHI.
    You can adjust weights later.
    """
    # default weights
    weights = {
        "mental": 0.22,
        "sleep": 0.20,
        "msk": 0.18,
        "eye": 0.15,
        "hydration": 0.10,
        "workspace": 0.08,
        "baseline": 0.04,
        "longitudinal": 0.03,
    }

    total = 0.0
    total_w = 0.0

    for k, w in weights.items():
        total += scores.get(k, 0.0) * w
        total_w += w

    if total_w <= 0:
        return 0.0

    return clamp(total / total_w, 0, 100)


def apply_global_pressure(local_score: float, whi: float, pressure_factor=0.35) -> float:
    """
    FinalTabScore = 0.70 * Local + 0.30 * (WHI * pressure_factor)
    """
    return clamp(0.70 * local_score + 0.30 * (whi * pressure_factor), 0, 100)


# ============================================================
# Main Entry Point
# ============================================================

def compute_all_scores(data_dir: str) -> Dict[str, Any]:
    """
    Reads all known tab files from data_dir.
    Returns full scoring output dictionary.
    """

    # --- Define filenames (adjust names to match your project) ---
    FILES = {
        "eye": "eye_user_input.json",
        "workspace": "workspace_user_input.json",
        "hydration": "hydration_user_input.json",
        "msk": "msk_user_input.json",
        "baseline": "baseline_user_input.json",
        "longitudinal": "longitudinal_user_input.json",
        # Add these when you have them:
        "mental": "mental_user_input.json",
        "sleep": "sleep_user_input.json",
        "productivity": "productivity_user_input.json",
    }

    histories = {}
    for tab, fname in FILES.items():
        path = os.path.join(data_dir, fname)
        histories[tab] = load_json_history(path)

    # --- Compute Local Scores ---
    local_scores = {}

    local_scores["eye"] = tab_score_from_history(histories["eye"], score_eye_entry, window=5)
    local_scores["hydration"] = tab_score_from_history(histories["hydration"], score_hydration_entry, window=5)
    local_scores["msk"] = tab_score_from_history(histories["msk"], score_msk_entry, window=5)

    local_scores["workspace"] = workspace_score_from_history(histories["workspace"])
    local_scores["baseline"] = baseline_score_from_history(histories["baseline"])

    # longitudinal special
    if histories["longitudinal"]:
        local_scores["longitudinal"] = longitudinal_with_trend(histories["longitudinal"])
    else:
        local_scores["longitudinal"] = 0.0

    # Placeholder: if mental/sleep/productivity don't exist yet
    local_scores["mental"] = tab_score_from_history(histories.get("mental", []), lambda ui: 0.0, window=5)
    local_scores["sleep"] = tab_score_from_history(histories.get("sleep", []), lambda ui: 0.0, window=5)
    local_scores["productivity"] = tab_score_from_history(histories.get("productivity", []), lambda ui: 0.0, window=5)

    # --- Compute Overall WHI ---
    whi = compute_whi(local_scores)

    # --- Apply Global Pressure ---
    final_scores = {}
    for tab, score in local_scores.items():
        final_scores[tab] = apply_global_pressure(score, whi, pressure_factor=0.35)

    return {
        "workday_health_index": round(whi, 1),
        "local_scores": {k: round(v, 1) for k, v in local_scores.items()},
        "final_scores": {k: round(v, 1) for k, v in final_scores.items()},
    }
import os
import json
from datetime import datetime, timedelta

# ============================================================
# Helpers
# ============================================================

def load_json_history(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def parse_ts(ts):
    # handles "2026-02-10T01:30:54.842839"
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def filter_last_days(history, days=7):
    cutoff = datetime.now() - timedelta(days=days)
    out = []
    for row in history:
        ts = parse_ts(row.get("timestamp", ""))
        if ts and ts >= cutoff:
            out.append(row)
    return out


def filter_prev_week(history):
    """
    Previous week = 7-14 days ago.
    """
    now = datetime.now()
    start = now - timedelta(days=14)
    end = now - timedelta(days=7)

    out = []
    for row in history:
        ts = parse_ts(row.get("timestamp", ""))
        if ts and start <= ts < end:
            out.append(row)
    return out


def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def pct_change(curr, prev):
    if prev is None or prev == 0:
        return None
    return ((curr - prev) / prev) * 100.0


def avg(values):
    if not values:
        return None
    return sum(values) / len(values)


# ============================================================
# Metric 1: Sedentary Hours Reduced
# ============================================================

def seated_duration_to_hours(label):
    label = (label or "").strip()
    mapping = {
        "30 min": 0.5,
        "1 hour": 1.0,
        "2 hours": 2.0,
        "3+ hours": 3.5
    }
    return mapping.get(label, None)


def compute_sedentary_metric(msk_history):
    this_week = filter_last_days(msk_history, 7)
    last_week = filter_prev_week(msk_history)

    def extract(h):
        vals = []
        for row in h:
            ui = row.get("user_input", {})
            hours = seated_duration_to_hours(ui.get("seated_duration"))
            if hours is not None:
                vals.append(hours)
        return vals

    curr_avg = avg(extract(this_week))
    prev_avg = avg(extract(last_week))

    return {
        "this_week_avg_seated_block_hours": None if curr_avg is None else round(curr_avg, 2),
        "last_week_avg_seated_block_hours": None if prev_avg is None else round(prev_avg, 2),
        "change_hours": None if (curr_avg is None or prev_avg is None) else round(curr_avg - prev_avg, 2),
        "change_percent": None if (curr_avg is None or prev_avg is None) else round(pct_change(curr_avg, prev_avg), 1)
    }


# ============================================================
# Metric 2: Hydration Compliance %
# ============================================================

def hydration_compliant(ui):
    water = safe_float(ui.get("water_intake"), 0)
    urine = (ui.get("urine_color") or "").strip()
    thirst = (ui.get("thirst_level") or "").strip()

    if water < 8:
        return False
    if urine in ["Dark Yellow", "Amber/Brown"]:
        return False
    if thirst == "Very Thirsty / Parched":
        return False
    return True


def compute_hydration_metric(hydration_history):
    this_week = filter_last_days(hydration_history, 7)
    last_week = filter_prev_week(hydration_history)

    def compliance_rate(h):
        if not h:
            return None
        ok = 0
        for row in h:
            ui = row.get("user_input", {})
            if hydration_compliant(ui):
                ok += 1
        return (ok / len(h)) * 100.0

    curr = compliance_rate(this_week)
    prev = compliance_rate(last_week)

    return {
        "this_week_compliance_percent": None if curr is None else round(curr, 1),
        "last_week_compliance_percent": None if prev is None else round(prev, 1),
        "change_percent_points": None if (curr is None or prev is None) else round(curr - prev, 1)
    }


# ============================================================
# Metric 3: Sleep Improvement Trend
# ============================================================

def compute_sleep_metric(sleep_history):
    this_week = filter_last_days(sleep_history, 7)
    last_week = filter_prev_week(sleep_history)

    def extract_sleep_hours(h):
        vals = []
        for row in h:
            ui = row.get("user_input", {})
            hrs = safe_float(ui.get("sleep_hours"), None)
            if hrs is not None and hrs > 0:
                vals.append(hrs)
        return vals

    curr_avg = avg(extract_sleep_hours(this_week))
    prev_avg = avg(extract_sleep_hours(last_week))

    trend = None
    if curr_avg is not None and prev_avg is not None:
        delta = curr_avg - prev_avg
        if delta >= 0.5:
            trend = "improving"
        elif delta <= -0.5:
            trend = "worsening"
        else:
            trend = "stable"

    return {
        "this_week_avg_sleep_hours": None if curr_avg is None else round(curr_avg, 2),
        "last_week_avg_sleep_hours": None if prev_avg is None else round(prev_avg, 2),
        "change_hours": None if (curr_avg is None or prev_avg is None) else round(curr_avg - prev_avg, 2),
        "trend": trend
    }


# ============================================================
# Metric 4: Reminders Completed
# ============================================================

def compute_reminders_metric(reminders_history):
    this_week = filter_last_days(reminders_history, 7)
    last_week = filter_prev_week(reminders_history)

    def count_completed(h):
        if not h:
            return None
        completed = 0
        for row in h:
            ui = row.get("user_input", row)
            if ui.get("completed") is True:
                completed += 1
        return completed

    curr = count_completed(this_week)
    prev = count_completed(last_week)

    return {
        "this_week_completed": curr,
        "last_week_completed": prev,
        "change": None if (curr is None or prev is None) else curr - prev
    }


# ============================================================
# Extra Metric: High Risk Days Avoided (WHI)
# ============================================================

def compute_high_risk_days(whi_history, threshold=60):
    this_week = filter_last_days(whi_history, 7)
    last_week = filter_prev_week(whi_history)

    def count_high(h):
        if not h:
            return None
        c = 0
        for row in h:
            ui = row.get("user_input", row)
            score = safe_float(ui.get("workday_health_index"), None)
            if score is not None and score >= threshold:
                c += 1
        return c

    curr = count_high(this_week)
    prev = count_high(last_week)

    return {
        "threshold": threshold,
        "this_week_high_risk_days": curr,
        "last_week_high_risk_days": prev,
        "change": None if (curr is None or prev is None) else curr - prev
    }


# ============================================================
# Main Weekly Metrics Function
# ============================================================

def compute_weekly_metrics(data_dir="data"):
    paths = {
        "msk": os.path.join(data_dir, "msk_user_input.json"),
        "hydration": os.path.join(data_dir, "hydration_user_input.json"),
        "sleep": os.path.join(data_dir, "sleep_user_input.json"),  # if exists
        "reminders": os.path.join(data_dir, "reminders_log.json"),  # you may create this
        "whi": os.path.join(data_dir, "risk_scores_history.json"),  # optional
    }

    msk_hist = load_json_history(paths["msk"])
    hydration_hist = load_json_history(paths["hydration"])
    sleep_hist = load_json_history(paths["sleep"])
    reminders_hist = load_json_history(paths["reminders"])
    whi_hist = load_json_history(paths["whi"])

    return {
        "sedentary": compute_sedentary_metric(msk_hist),
        "hydration": compute_hydration_metric(hydration_hist),
        "sleep": compute_sleep_metric(sleep_hist),
        "reminders": compute_reminders_metric(reminders_hist),
        "high_risk_days": compute_high_risk_days(whi_hist, threshold=60)
    }


# ============================================================
# Run in Notebook
# ============================================================

metrics = compute_weekly_metrics("data")
print(json.dumps(metrics, indent=2))



import gradio as gr
import matplotlib.pyplot as plt




def risk_label(score):
    if score >= 80:
        return "🔴 Critical"
    elif score >= 60:
        return "🟠 High"
    elif score >= 40:
        return "🟡 Moderate"
    else:
        return "🟢 Low"


def build_risk_impact_tab(store=None, gemini=None, lang_state=None, locales_dir=None):

    with gr.Column():
        gr.Markdown("## 📊 Dashboard")
        gr.Markdown("A quick overview of your current health risks and weekly progress.")

        btn_refresh = gr.Button("🔄 Refresh Dashboard")

        # --- Cards (Top Summary) ---
        with gr.Row():
            whi_box = gr.Markdown()
            top_risks_box = gr.Markdown()

        # --- Risk Chart ---
        gr.Markdown("### Risk Scores (0–100)")
        risk_plot = gr.Plot()

        # --- Impact Metrics Summary ---
        gr.Markdown("### Weekly Impact Metrics")
        impact_box = gr.Markdown()

        # --- Impact Chart ---
        impact_plot = gr.Plot()

        def render():
            data_dir = "data"  # or store.base_dir if you have it

            # --- Get Risk Output ---
            risk = compute_all_scores(data_dir)
            whi = risk["workday_health_index"]
            scores = risk["final_scores"]

            # sort highest risks
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top4 = sorted_scores[:4]

            whi_text = f"""
### Overall Workday Health Index
**{whi:.1f} / 100**  
**Status:** {risk_label(whi)}
"""

            top_risks_text = "### Top Risk Areas\n"
            for k, v in top4:
                top_risks_text += f"- **{k.upper()}**: {v:.1f}/100 ({risk_label(v)})\n"

            # --- Risk Plot ---
            labels = [k.upper() for k, v in sorted_scores]
            values = [v for k, v in sorted_scores]

            fig1 = plt.figure(figsize=(9, 4))
            plt.bar(labels, values)
            plt.ylim(0, 100)
            plt.title(f"Risk Dashboard (WHI: {whi:.1f})")
            plt.ylabel("Risk Score")
            plt.xticks(rotation=35)
            plt.axhline(60, linestyle="--", linewidth=1)
            plt.axhline(80, linestyle="--", linewidth=1)
            plt.tight_layout()

            # --- Impact Metrics ---
            impact = compute_weekly_metrics(data_dir)

            hydration = impact["hydration"]["this_week_compliance_percent"]
            sedentary = impact["sedentary"]["this_week_avg_seated_block_hours"]
            reminders = impact["reminders"]["this_week_completed"]
            high_risk_days = impact["high_risk_days"]["this_week_high_risk_days"]

            # handle None values
            hydration = hydration if hydration is not None else 0
            sedentary = sedentary if sedentary is not None else 0
            reminders = reminders if reminders is not None else 0
            high_risk_days = high_risk_days if high_risk_days is not None else 0

            impact_text = f"""
- 💧 **Hydration compliance:** **{hydration:.1f}%**
- 🪑 **Avg seated block (hours):** **{sedentary:.2f}**
- ✅ **Reminders completed:** **{reminders}**
- ⚠️ **High-risk days (WHI ≥ 60):** **{high_risk_days}**
"""

            # --- Impact Plot ---
            metric_labels = ["Hydration %", "Seated Hours", "Reminders", "High Risk Days"]
            metric_values = [hydration, sedentary, reminders, high_risk_days]

            fig2 = plt.figure(figsize=(9, 4))
            plt.bar(metric_labels, metric_values)
            plt.title("Weekly Progress Metrics (This Week)")
            plt.ylabel("Value")
            plt.xticks(rotation=25)
            plt.tight_layout()

            return whi_text, top_risks_text, fig1, impact_text, fig2

        btn_refresh.click(
            fn=render,
            inputs=[],
            outputs=[whi_box, top_risks_box, risk_plot, impact_box, impact_plot]
        )
