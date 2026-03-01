# Structural Domain Analysis (SDA): A New Category for Multi-Order Evaluation Systems

**Tiago J. C. dos Santos** — Independent Researcher, Coimbra, Portugal  
Fresta Lens Framework · Zenodo: [10.5281/zenodo.18251304](https://doi.org/10.5281/zenodo.18251304)  
Implementation: [github.com/EviAmarates/fresta-edge](https://github.com/EviAmarates/fresta-edge)

---

## Abstract

We introduce **Structural Domain Analysis (SDA)**, a computational approach to automated evaluation framework generation. Unlike traditional Multi-Criteria Decision Analysis (MCDA) methods that require manual criterion definition, or generic LLM prompting that produces inconsistent outputs, SDA operationalizes a three-order structural theory to generate domain-specific evaluation lenses from minimal input.

We present **EDGE** (Evaluation Domain Generator Engine) as the first implementation, demonstrating automated generation of weighted metrics, bottleneck detection, and systemic stress modeling for arbitrary domains. EDGE runs entirely locally in a single Python script with graceful degradation, requiring no external APIs or configuration beyond a locally-running LLM.

---

## 1. The Problem Space

Current approaches to evaluation framework generation suffer from three critical gaps:

| Approach | Limitation |
|---|---|
| Manual MCDA (AHP, TOPSIS) | Requires domain expertise to define criteria and weights; not scalable across domains |
| Generic LLM prompting | Unstructured output; no guaranteed consistency in metric relationships or normalization |
| Static product databases | Fixed domains; cannot adapt to emerging categories or specific user contexts |

**What is missing:** a lightweight, automated system that generates structured, theory-grounded evaluation frameworks for any domain, with explicit modeling of how metrics interact and how external systemic forces influence what "good" means in a given market.

---

## 2. Structural Domain Analysis (SDA)

SDA is defined by three core principles:

### P1 — Multi-Order Analysis

Evaluation must operate at three distinct structural orders:

- **1st order (E0):** Local, intrinsic, measurable attributes of the object itself
- **2nd order (E_upstream):** Interdependencies — bottlenecks and synergies — between 1st-order metrics
- **3rd order (E_inherited):** Systemic stress inherited from infrastructure dependencies, market saturation, and external amplification cycles

Most existing evaluation systems operate exclusively at the 1st order. This is not a simplification — it is a structural blindness to the forces that most determine real-world outcomes.

### P2 — Structural Non-Additivity

The value of a system is not the sum of its parts. A critical bottleneck can nullify an otherwise excellent metric profile. SDA models this explicitly:

```
E_total = E0 + E_upstream + E_inherited + P_structure
```

Where `P_structure` encodes the penalty imposed by the system's own architectural weaknesses — not just individual metric scores, but how they fail each other.

### P3 — Domain Autogeneration

Given only a domain string (e.g., `"gaming laptop"`), the system must autonomously gather contextual knowledge, infer appropriate metrics, and construct valid interdependency maps — without human curation at any stage.

---

## 3. EDGE: Reference Implementation

EDGE implements SDA through a four-stage pipeline:

```
Domain Input
    │
    ├──► Knowledge Gathering (Wikipedia + Web scraping)
    │
    ├──► 1st Order Analysis  → weighted metrics (Σ weights = 1.0)
    │
    ├──► 2nd Order Analysis  → bottleneck / synergy detection
    │
    ├──► 3rd Order Analysis  → systemic stress modeling
    │
    └──► Profile Generation  → user archetypes inferred from stress factors
```

### Key Technical Properties

| Property | Implementation |
|---|---|
| Local execution | OpenAI-compatible HTTP endpoint or Ollama fallback |
| Graceful degradation | Built-in defaults for all stages if LLM is unavailable |
| Deterministic output | Structured JSON schema with validated weight normalization |
| Single-file deployment | ~600 lines of Python, zero configuration required |
| Model efficiency | Validated on 8B parameter models (Llama 3, Qwen 2.5) |

---

## 4. Validation: The Smartphone Case

To assess EDGE's output quality, we generated a lens for the domain `"smartphone"` and compared its outputs against established expert review sources (RTings, GSMArena, AnandTech).

| EDGE Output | Expert Consensus | Alignment |
|---|---|---|
| Top 3 metrics: processor, battery, camera | Processor, battery, camera universally prioritized | ✅ Exact match |
| Critical bottleneck: processor ↔ thermal management | Throttling under sustained load widely reported | ✅ Confirmed |
| Systemic stress: semiconductor supply chain concentration | Documented extensively in industry analysis | ✅ Confirmed |
| Systemic stress: camera megapixel hype cycle (penalty: 0.55) | Widely acknowledged as marketing distortion | ✅ Confirmed |
| Profile: "Longevity Buyer" prioritizes software support lifespan | Emerging as dominant concern in 2024–2025 reviews | ✅ Predictive |

The full smartphone lens is available in the repository at [`/lenses/smartphone_lens.json`](./lenses/smartphone_lens.json).

---

## 5. Why This Is a New Category

SDA is not adequately described by any existing framework:

| What SDA is not | Why |
|---|---|
| Not MCDA | Does not require manual criterion definition; generates criteria autonomously |
| Not RAG | Does not retrieve existing frameworks; constructs novel ones from domain semantics |
| Not prompt engineering | Has fixed theoretical structure (three orders, non-additivity formula) independent of any prompt |
| Not an expert system | Does not use hard-coded domain rules; infers structure from minimal input |

SDA is the **automated synthesis of evaluation theory from minimal input**, grounded in a structural account of how systems fail and how external forces distort value.

---

## 6. Theoretical Grounding

EDGE is the first practical implementation of the **Fresta Lens Framework**, a five-volume theoretical work (~500 pages) addressing fundamental problems in evaluation theory, thermodynamics of systems, and structural incompleteness.

The framework derives the three-order decomposition from first principles: any evaluation system that ignores upstream interdependencies and inherited structural stress is not merely incomplete — it is systematically biased toward the forces that benefit most from that blindness (marketing cycles, brand premium amplification, supply chain incumbents).

Full theoretical work: [doi.org/10.5281/zenodo.18251304](https://doi.org/10.5281/zenodo.18251304)

---

## 7. Future Work

- Empirical calibration of block weights (`E0`, `E_upstream`, `E_inherited`) across 100+ domains
- Chrome extension for real-time product comparison using generated lenses
- EDGE API — expose lens generation as a web service
- Formal analysis of structural incompleteness bounds in metric selection

---

## Citation

```bibtex
@software{edge_sda_2026,
  author    = {Santos, Tiago J. C. dos},
  title     = {EDGE: Structural Domain Analysis Engine},
  year      = {2026},
  url       = {https://github.com/EviAmarates/fresta-edge},
  note      = {Based on the Fresta Lens Framework. Zenodo: 10.5281/zenodo.18251304}
}
```
