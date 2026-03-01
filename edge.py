# -*- coding: utf-8 -*-
"""
EDGE — Domain Evaluation Lens Generator
========================================
A three-order structural analysis engine for generating domain-specific
evaluation criteria, using the formula:

    E_total = E0 + E_upstream + E_inherited + P_structure

Where:
  E0           = Local metrics (1st order) — intrinsic, measurable attributes
  E_upstream   = Bottlenecks & synergies (2nd order) — metric interdependencies
  E_inherited  = Systemic stress (3rd order) — infrastructure, saturation, cycles
  P_structure  = Structural penalty from the above

Output: a structured JSON "lens" file saved to ./lenses/<domain>_lens.json

Usage:
  python edge.py

Environment variables:
  EDGE_LLM_URL    — Base URL for an OpenAI-compatible LLM server (default: http://127.0.0.1:1234)
  EDGE_LLM_MODEL  — Model name to use (default: meta-llama-3-8b-instruct)

Dependencies (all optional — graceful fallback if missing):
  pip install wikipedia-api googlesearch-python requests beautifulsoup4 ollama
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

# ── Optional dependencies (graceful degradation) ─────────────────────────────

try:
    import wikipedia
except ImportError:
    wikipedia = None

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

try:
    import ollama
except ImportError:
    ollama = None

# ── Configuration ─────────────────────────────────────────────────────────────

LLM_BASE_URL = os.environ.get("EDGE_LLM_URL", "http://127.0.0.1:1234")
LLM_MODEL    = os.environ.get("EDGE_LLM_MODEL", "meta-llama-3-8b-instruct")

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE GATHERING
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_wikipedia(domain: str, max_chars: int = 8000) -> str:
    """Search Wikipedia (EN + one additional language) and return concatenated text."""
    if not wikipedia:
        return ""
    texts = []
    for lang in ["en", "pt"]:
        try:
            wikipedia.set_lang(lang)
            results = wikipedia.search(f"{domain} evaluation criteria metrics", results=3)
            for title in results[:2]:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    texts.append(page.content[:4000])
                except Exception:
                    continue
        except Exception:
            continue
    combined = " ".join(texts)[:max_chars]
    return combined if combined.strip() else ""


def fetch_web(domain: str, num_results: int = 5, max_chars: int = 6000) -> str:
    """Search the web and scrape text from the top results."""
    if not google_search:
        return ""
    query = f"{domain} best metrics evaluation criteria specifications"
    urls = []
    try:
        for url in google_search(query, num_results=num_results, lang="en"):
            urls.append(url)
    except Exception:
        return ""
    snippets = []
    if requests and BeautifulSoup:
        for url in urls[:2]:
            try:
                r = requests.get(
                    url, timeout=8,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; EDGE/1.0)"}
                )
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                body = soup.get_text(separator=" ", strip=True)
                snippets.append(body[:3000])
            except Exception:
                continue
    return " ".join(snippets)[:max_chars]


def gather_knowledge(domain: str) -> str:
    """Aggregate knowledge from Wikipedia and the web for a given domain."""
    wiki  = fetch_wikipedia(domain)
    web   = fetch_web(domain)
    combined = f"[Wikipedia context]\n{wiki}\n\n[Web / criteria]\n{web}".strip()
    return combined or f"Domain: {domain}. Typical evaluation metrics and criteria."


# ═══════════════════════════════════════════════════════════════════════════════
# LLM INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def call_llm(prompt: str, model: str = None, max_attempts: int = 3) -> str:
    """
    Call a local LLM via:
      1. OpenAI-compatible HTTP endpoint (e.g. llama.cpp server, LM Studio)
      2. Ollama (fallback)

    Returns the model's text response, or an empty string on failure.
    """
    model = model or LLM_MODEL

    # 1) HTTP endpoint
    if requests and LLM_BASE_URL:
        url = LLM_BASE_URL.rstrip("/") + "/v1/chat/completions"
        for _ in range(max_attempts):
            try:
                print(f"  [LLM] Calling {LLM_BASE_URL} (model: {model})...")
                r = requests.post(
                    url,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=120,
                    headers={"Content-Type": "application/json"},
                )
                r.raise_for_status()
                data    = r.json()
                content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content
            except Exception as e:
                print(f"  [LLM] HTTP error: {e}")

    # 2) Ollama fallback
    if ollama:
        for _ in range(max_attempts):
            try:
                print(f"  [LLM] Calling Ollama (model: {model})...")
                r = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
                return (r.get("message") or {}).get("content", "")
            except Exception as e:
                print(f"  [LLM] Ollama error: {e}")

    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# JSON PARSING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def _strip_markdown_json(text: str) -> str:
    """Remove markdown fences from LLM responses, returning raw JSON content."""
    if not text:
        return ""
    m = re.search(r"```\s*json\s*([\s\S]*?)```", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    return text.strip()


def extract_json_array(text: str) -> list:
    """
    Robustly extract a JSON array from LLM output.
    Handles markdown fences, extra text, and partially-malformed JSON.
    """
    if not text or not text.strip():
        return []

    clean = _strip_markdown_json(text) or text.strip()

    # 1) Direct parse
    try:
        parsed = json.loads(clean)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
    except json.JSONDecodeError:
        pass

    # 2) Regex: find outermost [...]
    m = re.search(r"\[[\s\S]*\]", clean)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    # 3) Walk character-by-character to extract balanced {...} objects
    objects, i = [], 0
    while i < len(clean):
        if clean[i] == "{":
            depth, start = 0, i
            for j in range(i, len(clean)):
                if clean[j] == "{":
                    depth += 1
                elif clean[j] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            obj = json.loads(clean[start:j + 1])
                            if isinstance(obj, dict):
                                objects.append(obj)
                        except json.JSONDecodeError:
                            pass
                        i = j + 1
                        break
            else:
                i += 1
        else:
            i += 1

    return objects


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT FALLBACKS
# ═══════════════════════════════════════════════════════════════════════════════

def default_1st_order_metrics(domain: str) -> list:
    """Generic fallback metrics when the LLM returns nothing useful."""
    return [
        {"name": "overall_quality",    "order": 1, "direction": "maximize", "weight": 0.25, "threshold": 0.5, "justification": "Aggregate quality metric."},
        {"name": "price_value_ratio",  "order": 1, "direction": "maximize", "weight": 0.20, "threshold": 0.4, "justification": "Price-to-value relationship."},
        {"name": "durability",         "order": 1, "direction": "maximize", "weight": 0.20, "threshold": 0.4, "justification": "Lifespan and reliability."},
        {"name": "performance",        "order": 1, "direction": "maximize", "weight": 0.20, "threshold": 0.5, "justification": "Technical performance."},
        {"name": "user_satisfaction",  "order": 1, "direction": "maximize", "weight": 0.15, "threshold": 0.4, "justification": "User experience quality."},
    ]


def default_2nd_order_relations(domain: str) -> list:
    """Generic fallback bottlenecks/synergies."""
    return [
        {"type": "bottleneck", "metrics": ["performance", "overall_quality"], "intensity": 0.6, "penalty_or_bonus": 0.5, "explanation": "Weak performance limits perceived quality."},
        {"type": "synergy",    "metrics": ["price_value_ratio", "durability"],  "intensity": 0.5, "penalty_or_bonus": 0.3, "explanation": "Good value and durability reinforce each other."},
    ]


def default_3rd_order_stress(domain: str) -> list:
    """Generic fallback systemic stress factors."""
    return [
        {"type": "infrastructure", "name": "supply_chain",     "inherited_stress": 0.30, "penalty": 0.20, "explanation": "Dependency on global supply chains."},
        {"type": "saturation",     "name": "market",           "inherited_stress": 0.20, "penalty": 0.15, "explanation": "Possible market saturation."},
        {"type": "cycle",          "name": "marketing_cycles", "inherited_stress": 0.25, "penalty": 0.20, "explanation": "Marketing may distort objective evaluation."},
    ]


def default_profiles() -> list:
    """Generic fallback user profiles."""
    return [
        {"id": "casual",    "label": "Casual User",    "description": "General purpose user.",    "weight_adjustments": {}},
        {"id": "advanced",  "label": "Advanced User",  "description": "Demanding power user.",    "weight_adjustments": {}},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS PIPELINE — THREE ORDERS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_1st_order(domain: str, context_text: str) -> list:
    """
    E0 — Local metrics (5–8).
    Intrinsic, measurable, domain-specific attributes.
    """
    prompt = f'''Given the domain "{domain}" and this context: {context_text[:6000]}

Identify the 5–8 most important LOCAL metrics for evaluating a {domain}.
Local metrics = intrinsic to the object, measurable, independent of external factors.

Return a JSON array where each element is:
{{
  "name": str,
  "order": 1,
  "direction": "maximize" | "minimize",
  "weight": float (all weights must sum to 1.0),
  "threshold": float (minimum acceptable value, normalized 0–1),
  "justification": str
}}

IMPORTANT: Your response must start with [ and end with ]. No text before or after. No markdown. Pure JSON array only.'''

    raw  = call_llm(prompt)
    print(f"  [DEBUG] 1st order raw preview: {raw[:300]}")
    data = extract_json_array(raw)

    if not data or not isinstance(data, list):
        return default_1st_order_metrics(domain)

    # Retry if too few metrics
    if len(data) < 4:
        print("  [1st order] Too few metrics, retrying...")
        raw2  = call_llm(prompt)
        data2 = extract_json_array(raw2)
        if data2 and len(data2) >= 4:
            data = data2

    # Normalize weights to sum to 1.0
    total = sum(m.get("weight", 0) for m in data if isinstance(m, dict))
    if total > 0:
        for m in data:
            if isinstance(m, dict) and "weight" in m:
                m["weight"] = round(m["weight"] / total, 3)

    return data[:8]


def analyze_2nd_order(domain: str, metrics_1st: list) -> list:
    """
    E_upstream — Bottlenecks and synergies between 1st-order metrics.
    """
    m_str  = json.dumps(metrics_1st, ensure_ascii=False, indent=0)
    prompt = f'''Given the domain "{domain}" and these 1st-order metrics: {m_str}

Analyze the interdependencies. Identify:
1. BOTTLENECKS: combinations where one weak metric cancels another strong one.
   Example: great CPU + weak RAM = critical bottleneck in a smartphone.
2. SYNERGIES: combinations where both metrics amplify each other positively.

Return a JSON array where each element is:
{{
  "type": "bottleneck" | "synergy",
  "metrics": [str, str],
  "intensity": float (0–1),
  "penalty_or_bonus": float (0–1),
  "explanation": str
}}

IMPORTANT: Your response must start with [ and end with ]. No text before or after. No markdown. Pure JSON array only.'''

    raw  = call_llm(prompt)
    print(f"  [DEBUG] 2nd order raw preview: {raw[:300]}")
    data = extract_json_array(raw)

    if not data or not isinstance(data, list):
        return default_2nd_order_relations(domain)
    return data


def analyze_3rd_order(domain: str) -> list:
    """
    E_inherited + P_structure — Systemic stress factors.
    """
    prompt = f'''Given the domain "{domain}":

Analyze structural systemic stress. Identify:
1. INFRASTRUCTURE DEPENDENCIES: what does this domain rely on systemically?
   Example: smartphones depend on semiconductor supply chains, software ecosystems.
2. SATURATION: is there market or technological saturation?
3. AMPLIFICATION CYCLES: what external forces distort objective evaluation?
   Example: marketing hype, brand premium without real technical value.

Return a JSON array where each element is:
{{
  "type": "infrastructure" | "saturation" | "cycle",
  "name": str,
  "inherited_stress": float (0–1),
  "penalty": float (0–1),
  "explanation": str
}}

IMPORTANT: Your response must start with [ and end with ]. No text before or after. No markdown. Pure JSON array only.'''

    raw  = call_llm(prompt)
    print(f"  [DEBUG] 3rd order raw preview: {raw[:300]}")
    data = extract_json_array(raw)

    if not data or not isinstance(data, list):
        return default_3rd_order_stress(domain)
    return data


def generate_profiles(domain: str, metrics_1st: list, stress_3rd: list) -> list:
    """
    Generate 4–6 buyer/user profiles inferred from systemic stress and 1st-order metrics.
    """
    m_str  = json.dumps(metrics_1st, ensure_ascii=False)[:3000]
    s_str  = json.dumps(stress_3rd,  ensure_ascii=False)[:2000]
    prompt = f'''Given the domain "{domain}", this 3rd-order analysis: {s_str}
and these metrics: {m_str}

Identify 4–6 realistic BUYER/USER PROFILES for this domain.
Use the systemic factors from the 3rd order to infer what types of users exist
and what each one prioritizes.

For example, for "gaming PC":
  — market saturation suggests casual vs. hardcore gamers
  — marketing cycles suggest a "hype-influenced" profile
  — network infrastructure suggests a "competitive online gamer" profile

For each profile return JSON:
[
  {{
    "id": "lowercase_no_spaces",
    "label": "Human-readable name",
    "description": "One sentence describing this buyer type",
    "weight_adjustments": {{
      "exact_metric_name": float between 0.5 and 2.0
    }}
  }}
]

Weight adjustment guide:
  1.5 = this metric matters much more for this profile
  1.0 = normal importance
  0.7 = less important for this profile
  All values MUST be between 0.5 and 2.0.

IMPORTANT: Use metric names EXACTLY as they appear in the metrics list.
Respond ONLY with a pure JSON array. No text before or after.'''

    raw  = call_llm(prompt)
    print(f"  [DEBUG] Profiles raw preview: {raw[:300]}")
    data = extract_json_array(raw)

    if not data or not isinstance(data, list):
        return default_profiles()

    valid = [p for p in data if isinstance(p, dict) and "id" in p and "label" in p]

    # Ensure weight_adjustments key exists
    for p in valid:
        if "weight_adjustments" not in p:
            p["weight_adjustments"] = {}

    # Normalize metric name keys against actual metric names
    metric_names = [m.get("name", "") for m in metrics_1st if isinstance(m, dict)]
    for profile in valid:
        adj = profile.get("weight_adjustments", {})
        normalized = {}
        for key, val in adj.items():
            match = next((n for n in metric_names if n.lower() == key.lower()), key)
            normalized[match] = val
        profile["weight_adjustments"] = normalized

    return valid if len(valid) >= 2 else default_profiles()


def generate_summary(domain: str, lens: dict) -> str:
    """Ask the LLM to produce a concise human-readable summary of the lens."""
    try:
        blob = json.dumps({
            "metrics_1st_order": lens.get("metrics_1st_order", []),
            "relations_2nd_order": lens.get("relations_2nd_order", []),
            "stress_3rd_order": lens.get("stress_3rd_order", []),
        }, ensure_ascii=False)[:4000]

        prompt = f'''Based on this EDGE lens for the domain "{domain}": {blob}

Write a concise summary (3–5 sentences) in plain English explaining:
  — which local metrics were selected and why,
  — which bottlenecks and synergies were detected,
  — which systemic stress factors were considered.

No lists. No JSON. Flowing prose only.'''

        raw = call_llm(prompt)
        return (raw or "").strip()[:800]
    except Exception:
        return (
            f"EDGE lens for '{domain}': aggregated 1st, 2nd, and 3rd order metrics. "
            f"Global admission threshold: {lens.get('global_admission_threshold', 0.85)}."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_lens(domain: str) -> dict:
    """
    Full pipeline:
      1. Knowledge gathering (Wikipedia + web)
      2. 1st-order analysis  (E0)
      3. 2nd-order analysis  (E_upstream)
      4. 3rd-order analysis  (E_inherited + P_structure)
      5. Profile generation
      6. Human summary

    Returns a structured lens dict.
    """
    domain = (domain or "").strip() or "product"

    print("\n[EDGE] Gathering knowledge (Wikipedia + web)...")
    context = gather_knowledge(domain)

    print("[EDGE] 1st-order analysis (E0 — local metrics)...")
    metrics_1st = analyze_1st_order(domain, context)

    print("[EDGE] 2nd-order analysis (E_upstream — bottlenecks & synergies)...")
    relations_2nd = analyze_2nd_order(domain, metrics_1st)

    print("[EDGE] 3rd-order analysis (E_inherited + P_structure)...")
    stress_3rd = analyze_3rd_order(domain)

    print("[EDGE] Generating user profiles...")
    profiles = generate_profiles(domain, metrics_1st, stress_3rd)

    print("[EDGE] Generating human summary...")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lens = {
        "domain":                    domain,
        "generated_at":              timestamp,
        "formula":                   "E_total = E0 + E_upstream + E_inherited + P_structure",
        "block_weights":             {"E0": 0.40, "E_upstream": 0.35, "E_inherited": 0.25},
        "global_admission_threshold": 0.85,
        "metrics_1st_order":         metrics_1st,
        "relations_2nd_order":       relations_2nd,
        "stress_3rd_order":          stress_3rd,
        "profiles":                  profiles,
        "summary":                   "",
    }
    lens["summary"] = generate_summary(domain, lens)

    return lens


def print_lens_summary(lens: dict, output_path: str) -> None:
    """Print a readable summary of the generated lens to stdout."""
    d = lens["domain"]
    sep = "=" * 55

    print(f"\n{sep}")
    print(f"  EDGE LENS: {d.upper()}")
    print(sep)

    print("\n[1st Order] Local Metrics:")
    for m in lens.get("metrics_1st_order", []):
        if isinstance(m, dict):
            print(f"  → {m.get('name', '?')}  (weight: {m.get('weight', 0)}, {m.get('direction', '')})")

    print("\n[2nd Order] Bottlenecks:")
    for r in lens.get("relations_2nd_order", []):
        if isinstance(r, dict) and r.get("type") == "bottleneck":
            print(f"  → {r.get('metrics', [])}: {str(r.get('explanation', ''))[:70]}...")

    print("\n[2nd Order] Synergies:")
    for r in lens.get("relations_2nd_order", []):
        if isinstance(r, dict) and r.get("type") == "synergy":
            print(f"  → {r.get('metrics', [])}")

    print("\n[3rd Order] Systemic Stress:")
    for s in lens.get("stress_3rd_order", []):
        if isinstance(s, dict):
            print(f"  → {s.get('name', '?')} ({s.get('type', '')}): {str(s.get('explanation', ''))[:60]}...")

    print("\n[Profiles]")
    for p in lens.get("profiles", []):
        if isinstance(p, dict):
            print(f"  → {p.get('label', '?')}: {p.get('description', '')}")

    print(f"\nGlobal Admission Threshold : {lens.get('global_admission_threshold', 0.85)}")
    print(f"Lens saved to             : {output_path}")

    if lens.get("summary"):
        print("\nSummary:")
        print(lens["summary"])

    print()


def main() -> None:
    domain = input("Enter domain: ").strip()
    lens   = generate_lens(domain)

    base_dir   = os.path.dirname(os.path.abspath(__file__))
    lenses_dir = os.path.join(base_dir, "lenses")
    os.makedirs(lenses_dir, exist_ok=True)

    safe_name   = re.sub(r'[<>:"/\\|?*\s]', "_", domain) or "domain"
    output_path = os.path.join(lenses_dir, f"{safe_name}_lens.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lens, f, ensure_ascii=False, indent=2)

    print_lens_summary(lens, output_path)


if __name__ == "__main__":
    main()
