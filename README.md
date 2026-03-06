# 🛰️ Autonomous Scientific Discovery Engine

> **AI that generates scientific hypotheses automatically** — reads research papers, detects knowledge gaps, proposes novel hypotheses, and designs experiments.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai)](https://openai.com)
[![ArXiv](https://img.shields.io/badge/ArXiv-API-red)](https://arxiv.org)
[![PubMed](https://img.shields.io/badge/PubMed-API-blue)](https://pubmed.ncbi.nlm.nih.gov)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 💡 Example Output

Input: *"protein interaction and cancer progression"*

> **Hypothesis H1 (Composite Score: 87%):**
> "The post-translational modification of BRCA1 by PARP1 at residue K1286 may regulate homologous recombination efficiency in triple-negative breast cancer cells under oxidative stress conditions, representing a novel therapeutic vulnerability."
> 
> *Novelty: 89% | Feasibility: 75% | Impact: 91%*

**Designed Experiment:** CRISPR knockin of BRCA1-K1286A mutation in MDA-MB-231 cells, followed by comet assay and PARP inhibitor sensitivity testing. Timeline: 14 weeks. Cost: $18,000.

---

## 🔄 Full Pipeline

```
Domain: "cancer immunotherapy"
        ↓
📚 Step 1: Ingest papers from ArXiv + PubMed (no API keys needed)
        ↓
🧬 Step 2: Extract concepts, entities (genes/proteins/diseases) via LLM
        ↓
🕸️  Step 3: Build knowledge graph (nodes = concepts, edges = relationships)
        ↓
🔍 Step 4: Detect knowledge gaps (missing connections, unexplored bridges)
        ↓
💡 Step 5: Generate novel, testable hypotheses (ranked by novelty/impact)
        ↓
🧪 Step 6: Design experiments (protocol, materials, timeline, cost)
        ↓
📋 Output: Structured scientific discovery report (Markdown + JSON)
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📚 **Paper Ingestion** | Free APIs: ArXiv (XML) + PubMed/Entrez — no keys required |
| 🧬 **Concept Extraction** | LLM extracts genes, proteins, diseases, methods, relationships |
| 🕸️ **Knowledge Graph** | Maps concept relationships and co-occurrences across papers |
| 🔍 **Gap Detection** | Finds unexplored connections and unanswered questions |
| 💡 **Hypothesis Generation** | Creates novel, falsifiable, mechanistically grounded hypotheses |
| 🏆 **Scoring** | Ranks by novelty × feasibility × impact composite score |
| 🧪 **Experiment Design** | Protocol steps, controls, materials, stats, timeline, cost |
| 📋 **Report Export** | Full Markdown research report + JSON results |
| 🖥️ **Streamlit UI** | Interactive web interface with 5-tab result explorer |
| 🦛 **Ollama Support** | Run 100% locally with Llama3.2, Mistral, etc. |

---

## 🏗️ Architecture

```
scientific-discovery-engine/
├── engine/
│   ├── __init__.py              # Package exports
│   ├── discovery_engine.py      # 🛰️ Main orchestrator
│   ├── paper_ingestion.py       # 📚 ArXiv/PubMed ingestion
│   ├── knowledge_graph.py       # 🕸️ Concept graph builder
│   ├── hypothesis_generator.py  # 💡 LLM hypothesis engine
│   └── experiment_designer.py   # 🧪 Experiment protocol designer
├── app.py                       # 🖥️ Streamlit Web UI
├── main.py                      # 💻 CLI entry point
├── requirements.txt             # 📦 Dependencies
├── .env.example                 # ⚙️ Environment variables
└── outputs/                     # 📁 Discovery reports
```

---

## ⚡ Quick Start

### 1. Clone
```bash
git clone https://github.com/PranayMahendrakar/scientific-discovery-engine.git
cd scientific-discovery-engine
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Configure
```bash
cp .env.example .env
# Add your OPENAI_API_KEY
```

### 4. Run Web UI
```bash
streamlit run app.py
```

### 5. Or use CLI
```bash
# Basic discovery
python main.py --domain "cancer immunotherapy"

# With specific question
python main.py --domain "protein misfolding" --question "How does tau aggregation trigger neuroinflammation?"

# More papers, more hypotheses
python main.py --domain "CRISPR" --papers 10 --hypotheses 8

# Use local Ollama
python main.py --domain "antibiotic resistance" --ollama
```

---

## 🦛 Run Locally with Ollama (Free!)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2

# Run with local LLM
python main.py --domain "quantum biology" --ollama --ollama-model llama3.2
```

---

## 📊 Hypothesis Scoring

Each hypothesis is scored on three dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Novelty** | 35% | How different from existing literature |
| **Feasibility** | 20% | How practical to test experimentally |
| **Impact** | 45% | Potential significance if hypothesis is true |

**Composite Score** = (Impact × 0.45) + (Novelty × 0.35) + (Feasibility × 0.20)

---

## 📤 Output Format

The engine generates:

**1. Structured JSON** with all hypotheses, experiments, graph data, and metadata

**2. Markdown Report** including:
- Executive summary
- List of analyzed papers
- Knowledge gaps (with evidence)
- Ranked hypotheses (with scores and rationale)
- Experimental protocols (with protocol steps, materials, costs)

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `OPENAI_MODEL` | gpt-4o-mini | Model (gpt-4o for best results) |
| `USE_OLLAMA` | false | Use local Ollama |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server URL |
| `OLLAMA_MODEL` | llama3.2 | Ollama model name |

---

## 🧬 Scientific Domains Examples

- `cancer immunotherapy` — immune checkpoint interactions
- `Alzheimer disease protein aggregation` — amyloid/tau mechanisms
- `CRISPR off-target effects` — gene editing safety
- `antibiotic resistance mechanisms` — AMR strategies
- `RNA splicing cancer` — splicing regulation
- `mitochondrial dysfunction aging` — longevity research
- `quantum effects photosynthesis` — quantum biology

---

## 🌟 Potential Impact

This engine could:
- Accelerate hypothesis generation from weeks to minutes
- Surface non-obvious cross-domain connections
- Democratize access to AI-assisted research ideation
- Prioritize experimental resources on highest-impact directions

> *"The most important discoveries come from unexpected connections between fields."*

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Add more paper sources (Semantic Scholar, bioRxiv, ChemRxiv)
- Implement graph visualization with NetworkX/PyVis
- Add PDF ingestion with pdfplumber
- Build citation network analysis
- Train specialized scientific embeddings

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ by [Pranay M Mahendrakar](https://sonytech.in/pranay/) | Powered by LLM Agents + Knowledge Graphs + Scientific APIs*
