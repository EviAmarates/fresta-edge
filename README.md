# EDGE — Domain Evaluation Lens Generator

> Built on the [Fresta Lens Framework](./FRESTA.md) — a unified structural theory of evaluation, entropy, and system coherence.

**EDGE** generates structured, domain-specific evaluation criteria using a three-order structural analysis engine. Given any domain (e.g. *gaming laptop*, *noise-cancelling headphones*, *electric car*), it produces a **lens** — a JSON file containing weighted metrics, interdependency maps, systemic stress factors, and buyer profiles.

The underlying formula:

```
E_total = E0 + E_upstream + E_inherited + P_structure
```

| Component | Description |
|---|---|
| `E0` | **1st order** — Local, intrinsic, measurable metrics |
| `E_upstream` | **2nd order** — Bottlenecks & synergies between metrics |
| `E_inherited` | **3rd order** — Systemic stress (infrastructure, saturation, cycles) |
| `P_structure` | Structural penalty derived from the above |

---

## How It Works

```
Domain input
    │
    ▼
Knowledge gathering (Wikipedia + web scraping)
    │
    ▼
1st Order — local metrics (E0)
    │
    ▼
2nd Order — bottlenecks & synergies (E_upstream)
    │
    ▼
3rd Order — systemic stress (E_inherited + P_structure)
    │
    ▼
Profile generation (buyer types inferred from systemic factors)
    │
    ▼
Human summary
    │
    ▼
Lens JSON  →  ./lenses/<domain>_lens.json
```

---

## Requirements

Python 3.9+

### Required

```bash
pip install requests beautifulsoup4
```

### Optional (for knowledge gathering & LLM backends)

```bash
pip install wikipedia-api googlesearch-python ollama
```

### LLM Backend

EDGE works with any **OpenAI-compatible local LLM server**, such as:
- [LM Studio](https://lmstudio.ai/)
- [llama.cpp server](https://github.com/ggerganov/llama.cpp)
- [Ollama](https://ollama.com/) (automatic fallback)

---

## Usage

```bash
python edge.py
```

You will be prompted to enter a domain. EDGE then runs the full pipeline and saves the lens to `./lenses/<domain>_lens.json`.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `EDGE_LLM_URL` | `http://127.0.0.1:1234` | Base URL of the LLM server |
| `EDGE_LLM_MODEL` | `meta-llama-3-8b-instruct` | Model name to use |

Example:

```bash
EDGE_LLM_URL=http://127.0.0.1:11434 EDGE_LLM_MODEL=llama3 python edge.py
```

---

## Output Format

```json
{
  "domain": "gaming laptop",
  "generated_at": "2025-03-01T12:00:00Z",
  "formula": "E_total = E0 + E_upstream + E_inherited + P_structure",
  "block_weights": { "E0": 0.40, "E_upstream": 0.35, "E_inherited": 0.25 },
  "global_admission_threshold": 0.85,
  "metrics_1st_order": [ ... ],
  "relations_2nd_order": [ ... ],
  "stress_3rd_order": [ ... ],
  "profiles": [ ... ],
  "summary": "..."
}
```

### Metrics (1st order)
```json
{
  "name": "thermal_management",
  "order": 1,
  "direction": "maximize",
  "weight": 0.18,
  "threshold": 0.6,
  "justification": "Sustained performance depends on thermal headroom."
}
```

### Relations (2nd order)
```json
{
  "type": "bottleneck",
  "metrics": ["gpu_performance", "display_refresh_rate"],
  "intensity": 0.75,
  "penalty_or_bonus": 0.6,
  "explanation": "High refresh rate is wasted if the GPU cannot push frames."
}
```

### Systemic Stress (3rd order)
```json
{
  "type": "cycle",
  "name": "gpu_hype_cycles",
  "inherited_stress": 0.45,
  "penalty": 0.30,
  "explanation": "Marketing around GPU generations distorts perceived value."
}
```

### Profiles
```json
{
  "id": "competitive_esports",
  "label": "Competitive Esports Player",
  "description": "Prioritizes frame rate and input latency above all else.",
  "weight_adjustments": {
    "display_refresh_rate": 1.8,
    "input_latency": 1.7,
    "battery_life": 0.5
  }
}
```

---

## Graceful Degradation

EDGE is designed to work even when dependencies are missing:

- No `wikipedia` → skips Wikipedia lookup
- No `googlesearch` / `beautifulsoup4` → skips web scraping
- No LLM server reachable → uses built-in default fallback values for all three orders

---

## Theoretical Background

EDGE is the first practical implementation of the **Fresta Lens Framework**.

📄 [Read about the framework →](./FRESTA.md)  
📚 [Full 5-volume work on Zenodo →](https://doi.org/10.5281/zenodo.18251304)

---

## Support

This project is developed independently, without institutional funding.  
If it's useful to you, consider supporting its continued development.

☕ [Support on Ko-fi →](https://ko-fi.com/tiagosantos20582)  
⭐ Or simply star the repo — it helps more than you'd think.

[→ See all ways to help](./SUPPORT.md)

---

## License

EDGE is released under the **MIT License**.  
The underlying Fresta Framework uses a dual license (AGPLv3 + Enterprise). See [FRESTA.md](./FRESTA.md) for details.
