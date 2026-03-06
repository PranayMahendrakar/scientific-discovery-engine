"""
🛰️ Autonomous Scientific Discovery Engine - Streamlit Web UI
"""

import os
import json
import streamlit as st
from engine import DiscoveryEngine

st.set_page_config(
    page_title="🛰️ Scientific Discovery Engine",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .hero {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1c2128 100%);
        padding: 2.5rem; border-radius: 16px; text-align: center;
        border: 1px solid #30363d; margin-bottom: 2rem;
    }
    .hypothesis-card {
        background: #161b22; border: 1px solid #21262d;
        border-radius: 12px; padding: 1.2rem; margin: 0.8rem 0;
    }
    .score-badge {
        background: #1f6feb; color: white; padding: 0.2rem 0.7rem;
        border-radius: 20px; font-size: 0.8em; margin: 0.2rem;
    }
    .gap-card {
        background: #1c1c2e; border-left: 3px solid #e94560;
        padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1 style="color:white;font-size:2.8em;">🛰️ Autonomous Scientific Discovery Engine</h1>
    <p style="color:#8b949e;font-size:1.1em;">
        AI that reads research papers, detects knowledge gaps,<br>
        generates novel hypotheses, and designs experiments &mdash; automatically.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    use_ollama = st.checkbox("Use Ollama (Local LLM)")
    if use_ollama:
        ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")
        ollama_model = st.text_input("Model", value="llama3.2")
    st.divider()
    st.header("📊 Parameters")
    papers_per_source = st.slider("📚 Papers per Source", 3, 15, 5)
    num_hypotheses = st.slider("💡 Hypotheses to Generate", 3, 10, 5)
    sources = st.multiselect(
        "🌐 Data Sources",
        options=["arxiv", "pubmed"],
        default=["arxiv", "pubmed"]
    )
    st.divider()
    st.markdown("### 🔄 Pipeline Steps")
    st.markdown("""
    1. 📚 Ingest research papers
    2. 🧬 Extract concepts & entities
    3. 🕸️  Build knowledge graph
    4. 🔍 Detect knowledge gaps
    5. 💡 Generate novel hypotheses
    6. 🧪 Design experiments
    """)

# ── Main Input ───────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    domain = st.text_input(
        "🔬 Research Domain",
        placeholder="e.g., cancer immunotherapy, protein misfolding, CRISPR gene editing...",
        label_visibility="collapsed"
    )
with col2:
    run_btn = st.button("🚀 Discover", type="primary", use_container_width=True)

research_question = st.text_input(
    "Specific Research Question (optional)",
    placeholder="e.g., How does PD-L1 expression affect T-cell exhaustion?"
)

# ── Example domains ──────────────────────────────────────────
st.markdown("**⚡ Quick Examples:**")
examples = ["🧬 Cancer Immunotherapy", "🦠 Alzheimer protein aggregation", "🌿 CRISPR off-target effects", "🧪 Antibiotic resistance"]
ex_cols = st.columns(len(examples))
for i, (col, ex) in enumerate(zip(ex_cols, examples)):
    if col.button(ex, use_container_width=True):
        domain = ex.split(" ", 1)[1] if " " in ex else ex

# ── Run Discovery ────────────────────────────────────────────
if run_btn and domain.strip():
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    if use_ollama:
        os.environ["USE_OLLAMA"] = "true"
        os.environ["OLLAMA_BASE_URL"] = ollama_url + "/v1"
        os.environ["OLLAMA_MODEL"] = ollama_model
    if not os.getenv("OPENAI_API_KEY") and not use_ollama:
        st.error("⚠️ Please enter an OpenAI API Key or enable Ollama in the sidebar.")
        st.stop()

    st.markdown("---")
    progress_bar = st.progress(0)
    status = st.empty()

    def update(pct, msg):
        progress_bar.progress(pct)
        status.markdown(f"**{msg}**")

    try:
        update(5, "🛰️ Initializing discovery engine...")
        engine = DiscoveryEngine(config={"papers_per_source": papers_per_source})

        update(15, f"📚 Ingesting papers from {len(sources)} sources...")
        update(35, "🧬 Extracting concepts and building knowledge graph...")
        update(55, "🔍 Detecting knowledge gaps...")
        update(70, "💡 Generating novel scientific hypotheses...")
        update(85, "🧪 Designing experiments...")

        results = engine.discover(
            domain=domain,
            research_question=research_question or domain,
            papers_per_source=papers_per_source,
            num_hypotheses=num_hypotheses,
        )

        update(100, "✅ Discovery complete!")
        st.session_state["results"] = results
        st.session_state["engine"] = engine
    except Exception as e:
        st.error(f"❌ Discovery failed: {e}")
        st.exception(e)

elif run_btn:
    st.warning("⚠️ Please enter a research domain.")

# ── Display Results ──────────────────────────────────────────
if "results" in st.session_state:
    r = st.session_state["results"]
    engine = st.session_state.get("engine")
    meta = r.get("metadata", {})
    graph_stats = r.get("graph_stats", {})

    st.markdown("---")

    # Metrics row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📚 Papers", meta.get("papers_analyzed", 0))
    c2.metric("🕸️ Concepts", graph_stats.get("total_nodes", 0))
    c3.metric("🔗 Relationships", graph_stats.get("total_edges", 0))
    c4.metric("🔍 Gaps Found", meta.get("gaps_found", 0))
    c5.metric("💡 Hypotheses", meta.get("hypotheses_generated", 0))

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💡 Hypotheses", "🔍 Knowledge Gaps",
        "🧪 Experiments", "📚 Papers", "📋 Full Report"
    ])

    with tab1:
        st.markdown("### 💡 Novel Scientific Hypotheses")
        for i, h in enumerate(r.get("hypotheses", []), 1):
            score = h.get("composite_score", 0)
            color = "#22c55e" if score > 0.7 else "#f59e0b" if score > 0.5 else "#ef4444"
            with st.expander(f"H{i}: {h.get(chr(39)one_liner chr(39), h.get(chr(39)statement chr(39), chr(39)chr(39))[:80])}", expanded=(i==1)):
                st.markdown(f"**Full Statement:**\n> {h.get(chr(39)statement chr(39), chr(39)chr(39))}")
                st.markdown(f"**Rationale:** {h.get(chr(39)rationale chr(39), chr(39)chr(39))}")
                st.markdown(f"**Supporting Evidence:** {h.get(chr(39)supporting_evidence chr(39), chr(39)chr(39))}")
                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("Novelty", f"{h.get(chr(39)novelty_score chr(39),0):.0%}")
                sc2.metric("Feasibility", f"{h.get(chr(39)feasibility_score chr(39),0):.0%}")
                sc3.metric("Impact", f"{h.get(chr(39)impact_score chr(39),0):.0%}")
                sc4.metric("Composite", f"{score:.0%}")

    with tab2:
        st.markdown("### 🔍 Knowledge Gaps Identified")
        for i, g in enumerate(r.get("knowledge_gaps", []), 1):
            with st.expander(f"Gap {i}: {g.get(chr(39)description chr(39), chr(39)chr(39))[:70]}"):
                st.markdown(f"**Type:** {g.get(chr(39)gap_type chr(39), chr(39)chr(39))}")
                st.markdown(f"**Significance:** {g.get(chr(39)significance chr(39), chr(39)chr(39))}")
                st.markdown(f"**Evidence:** {g.get(chr(39)evidence_from_literature chr(39), chr(39)chr(39))}")
                concepts = g.get("involved_concepts", [])
                if concepts:
                    st.markdown("**Concepts:** " + " • ".join(concepts))

    with tab3:
        st.markdown("### 🧪 Experimental Designs")
        for exp in r.get("experiments", []):
            with st.expander(f"🧪 {exp.get(chr(39)experiment_title chr(39), chr(39)Experiment chr(39))}"):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Approach", exp.get("approach", "").replace("_", " ").title())
                col_b.metric("Timeline", f"{exp.get(chr(39)timeline_weeks chr(39), chr(39)?chr(39))} weeks")
                col_c.metric("Est. Cost", f"${exp.get(chr(39)estimated_cost_usd chr(39), 0):,}")
                st.markdown(f"**Model System:** {exp.get(chr(39)model_system chr(39), chr(39)chr(39))}")
                st.markdown("**Protocol Steps:**")
                for step in exp.get("protocol_steps", []):
                    st.markdown(f"  - {step}")
                if exp.get("materials"):
                    st.markdown("**Materials:** " + ", ".join(exp["materials"][:5]))

    with tab4:
        st.markdown("### 📚 Source Papers")
        for i, p in enumerate(r.get("papers", []), 1):
            url = p.get("url", "#")
            title = p.get("title", "Unknown")
            year = p.get("year", "")
            source = p.get("source", "").upper()
            finding = p.get("main_finding", "")
            st.markdown(f"**{i}.** [{title}]({url}) ({year}) [{source}]")
            if finding:
                st.caption(finding[:200])

    with tab5:
        st.markdown("### 📋 Full Discovery Report")
        if engine:
            report = engine.generate_report()
            st.markdown(report)
            st.download_button(
                "⬇️ Download Report (Markdown)",
                data=report,
                file_name=f"discovery_report_{r.get(chr(39)session_id chr(39), chr(39)output chr(39))}.md",
                mime="text/markdown"
            )
            st.download_button(
                "⬇️ Download Raw JSON",
                data=json.dumps(r, indent=2, default=str),
                file_name=f"discovery_results_{r.get(chr(39)session_id chr(39), chr(39)output chr(39))}.json",
                mime="application/json"
            )
