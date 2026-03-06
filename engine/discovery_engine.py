"""
🛰️ Autonomous Scientific Discovery Engine - Main Orchestrator
Coordinates all modules: ingestion -> extraction -> graph -> gaps -> hypotheses -> experiments
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from .paper_ingestion import PaperIngestion
from .knowledge_graph import KnowledgeGraph
from .hypothesis_generator import HypothesisGenerator
from .experiment_designer import ExperimentDesigner

load_dotenv()


class DiscoveryEngine:
    """
    Autonomous Scientific Discovery Engine.

    Full pipeline:
    1. Ingest papers from ArXiv/PubMed
    2. Extract concepts and relationships using LLM
    3. Build knowledge graph
    4. Detect knowledge gaps
    5. Generate novel hypotheses
    6. Design experiments to test hypotheses
    7. Output structured scientific report
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.ingestion = PaperIngestion()
        self.graph = KnowledgeGraph()
        self.hypothesis_gen = HypothesisGenerator()
        self.experiment_designer = ExperimentDesigner()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}

    def discover(
        self,
        domain: str,
        research_question: str = "",
        papers_per_source: int = 5,
        num_hypotheses: int = 5,
        manual_papers: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Run the full autonomous discovery pipeline.

        Args:
            domain: Scientific domain (e.g. "cancer immunotherapy")
            research_question: Optional specific question to focus on
            papers_per_source: Papers to fetch per source (arxiv, pubmed)
            num_hypotheses: Number of hypotheses to generate
            manual_papers: Optional pre-loaded papers

        Returns:
            Complete discovery results dict
        """
        query = research_question or domain
        print(f"\n🛰️  AUTONOMOUS SCIENTIFIC DISCOVERY ENGINE")
        print("=" * 60)
        print(f"  Domain: {domain}")
        print(f"  Query:  {query}")
        print("=" * 60)

        # ── STEP 1: Ingest Papers ──────────────────────────────────
        print("\n📚 Step 1: Ingesting scientific papers...")
        if manual_papers:
            papers = manual_papers
            print(f"   Using {len(papers)} manually provided papers")
        else:
            papers = self.ingestion.fetch_multi_source(
                query, max_per_source=papers_per_source
            )

        if not papers:
            return {"error": "No papers found for: " + query}

        # ── STEP 2: Extract Concepts ───────────────────────────────
        print(f"\n🧬 Step 2: Extracting concepts from {len(papers)} papers...")
        extractions = []
        for i, paper in enumerate(papers):
            print(f"   [{i+1}/{len(papers)}] {paper.get(chr(39)title chr(39), chr(39)Unknown chr(39))[:50]}...")
            extraction = self.hypothesis_gen.extract_concepts(paper)
            extractions.append(extraction)
            # Enrich paper with extracted data
            paper["main_finding"] = extraction.get("main_finding", "")
            paper["research_area"] = extraction.get("research_area", domain)

        # ── STEP 3: Build Knowledge Graph ─────────────────────────
        print("\n🕸️  Step 3: Building knowledge graph...")
        self.graph.build_from_papers(papers, extractions)
        graph_stats = self.graph.get_statistics()
        print(f"   Nodes: {graph_stats[chr(39)total_nodes chr(39)]}, Edges: {graph_stats[chr(39)total_edges chr(39)]}")

        # ── STEP 4: Detect Knowledge Gaps ─────────────────────────
        print("\n🔍 Step 4: Detecting knowledge gaps...")
        graph_gaps = self.graph.find_missing_connections()
        llm_gaps = self.hypothesis_gen.detect_gaps(papers, graph_gaps, domain)
        all_gaps = llm_gaps or [{"description": "Unexplored connections in " + domain}]
        print(f"   Found {len(all_gaps)} knowledge gaps")

        # ── STEP 5: Generate Hypotheses ───────────────────────────
        print(f"\n💡 Step 5: Generating {num_hypotheses} scientific hypotheses...")
        raw_hypotheses = self.hypothesis_gen.generate_hypotheses(
            all_gaps, papers, domain, num_hypotheses=num_hypotheses
        )
        hypotheses = self.hypothesis_gen.rank_hypotheses(raw_hypotheses)
        print(f"   Generated {len(hypotheses)} hypotheses")

        # ── STEP 6: Design Experiments ────────────────────────────
        print("\n🧪 Step 6: Designing experiments for top hypotheses...")
        experiments = self.experiment_designer.design_batch(
            hypotheses, domain, top_n=min(3, len(hypotheses))
        )
        print(f"   Designed {len(experiments)} experiments")

        print("\n✅ Discovery pipeline complete!")
        print("=" * 60)

        # ── Build Results ──────────────────────────────────────────
        self.results = {
            "session_id": self.session_id,
            "domain": domain,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "papers": papers,
            "graph_stats": graph_stats,
            "knowledge_gaps": all_gaps,
            "hypotheses": hypotheses,
            "experiments": experiments,
            "metadata": {
                "papers_analyzed": len(papers),
                "gaps_found": len(all_gaps),
                "hypotheses_generated": len(hypotheses),
                "experiments_designed": len(experiments),
            },
        }
        return self.results

    def get_top_hypothesis(self) -> Optional[Dict]:
        """Get the highest-scoring hypothesis from the last run."""
        hypotheses = self.results.get("hypotheses", [])
        return hypotheses[0] if hypotheses else None

    def generate_report(self) -> str:
        """Generate a full Markdown research report from the discovery results."""
        if not self.results:
            return "No results available. Run discover() first."

        r = self.results
        domain = r.get("domain", "")
        timestamp = r.get("timestamp", "")[:10]
        meta = r.get("metadata", {})
        papers = r.get("papers", [])
        gaps = r.get("knowledge_gaps", [])
        hypotheses = r.get("hypotheses", [])
        experiments = r.get("experiments", [])
        graph_stats = r.get("graph_stats", {})

        # Paper list
        papers_md = "\n".join([
            f"{i+1}. **{p.get(chr(39)title chr(39), chr(39)Unknown chr(39))}** — {p.get(chr(39)year chr(39), chr(39)chr(39))} [{p.get(chr(39)source chr(39), chr(39)chr(39)).upper()}]({p.get(chr(39)url chr(39), chr(39)#chr(39))})"
            for i, p in enumerate(papers)
        ])

        # Gaps section
        gaps_md = "\n\n".join([
            f"**Gap {i+1}:** {g.get(chr(39)description chr(39), chr(39)chr(39))}\n"
            f"- *Type:* {g.get(chr(39)gap_type chr(39), chr(39)chr(39))}\n"
            f"- *Significance:* {g.get(chr(39)significance chr(39), chr(39)chr(39))}"
            for i, g in enumerate(gaps[:5])
        ])

        # Hypotheses section
        hyp_md = "\n\n".join([
            f"### Hypothesis {h.get(chr(39)hypothesis_id chr(39), f chr(39)H{i+1} chr(39))}: {h.get(chr(39)one_liner chr(39), h.get(chr(39)statement chr(39), chr(39)chr(39))[:80])}\n\n"
            f"**Full Statement:** {h.get(chr(39)statement chr(39), chr(39)chr(39))}\n\n"
            f"**Rationale:** {h.get(chr(39)rationale chr(39), chr(39)chr(39))}\n\n"
            f"**Supporting Evidence:** {h.get(chr(39)supporting_evidence chr(39), chr(39)chr(39))}\n\n"
            f"| Novelty | Feasibility | Impact | Composite |\n"
            f"|---------|------------|--------|-----------|\n"
            f"| {h.get(chr(39)novelty_score chr(39),0):.0%} | {h.get(chr(39)feasibility_score chr(39),0):.0%} | {h.get(chr(39)impact_score chr(39),0):.0%} | {h.get(chr(39)composite_score chr(39),0):.0%} |"
            for i, h in enumerate(hypotheses)
        ])

        # Experiments section
        exp_md = "\n\n".join([
            self.experiment_designer.format_as_protocol(e)
            for e in experiments
        ])

        return (
            f"# 🛰️ Autonomous Scientific Discovery Report\n\n"
            f"**Domain:** {domain}\n"
            f"**Generated:** {timestamp} | **Session:** {r.get(chr(39)session_id chr(39), chr(39)chr(39))}\n\n"
            f"---\n\n"
            f"## Executive Summary\n\n"
            f"This report was generated autonomously by an AI discovery engine. "
            f"Analysis of **{meta.get(chr(39)papers_analyzed chr(39),0)} papers** from the {domain} literature "
            f"revealed **{meta.get(chr(39)gaps_found chr(39),0)} knowledge gaps** and produced "
            f"**{meta.get(chr(39)hypotheses_generated chr(39),0)} novel hypotheses**, with "
            f"**{meta.get(chr(39)experiments_designed chr(39),0)} experimental designs** ready for laboratory validation.\n\n"
            f"**Knowledge Graph:** {graph_stats.get(chr(39)total_nodes chr(39),0)} concept nodes, "
            f"{graph_stats.get(chr(39)total_edges chr(39),0)} relationships detected.\n\n"
            f"---\n\n"
            f"## Papers Analyzed\n\n{papers_md}\n\n"
            f"---\n\n"
            f"## Knowledge Gaps Identified\n\n{gaps_md}\n\n"
            f"---\n\n"
            f"## Novel Hypotheses\n\n{hyp_md}\n\n"
            f"---\n\n"
            f"## Experimental Designs\n\n{exp_md}\n\n"
            f"---\n\n"
            f"*Generated by Autonomous Scientific Discovery Engine v1.0 | {timestamp}*\n"
        )

    def save_results(self, output_dir: str = "outputs") -> str:
        """Save all results to files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        sid = self.session_id

        # Save JSON results
        json_file = f"{output_dir}/{sid}_results.json"
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save Markdown report
        report = self.generate_report()
        report_file = f"{output_dir}/{sid}_report.md"
        with open(report_file, "w") as f:
            f.write(report)

        print(f"\n💾 Results saved to {output_dir}/")
        return report_file
