#!/usr/bin/env python3
"""
Autonomous Scientific Discovery Engine - CLI Entry Point

Usage:
  python main.py --topic "cancer" --domain "oncology" --papers 20
  python main.py --topic "CRISPR" --domain "genetics" --papers 15 --output results.json
  python main.py --demo
"""

import argparse
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def print_banner():
    """Print ASCII banner."""
    banner = """
  _____      _            _   _  __ _
 / ____|    (_)          | | (_)/ _(_)
| (___   ___ _  ___ _ __ | |_ _| |_ _  ___
 \___ \ / __| |/ _ \ '_ \| __| |  _| |/ __|
 ____) | (__| |  __/ | | | |_| | | | | (__
|_____/ \___|_|\___|_| |_|\__|_|_| |_|\___|

   Discovery Engine v1.0 - AI-Powered Research
    """
    print(banner)


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    width = 60
    print("\n" + char * width)
    print(f"  {title}")
    print(char * width)


def run_demo():
    """Run a demo with a predefined scientific topic."""
    print("\n[DEMO MODE] Running with sample topic: CRISPR Gene Editing")
    print("Using mock data to demonstrate the pipeline...\n")

    # Simulate discovery pipeline output
    demo_result = {
        "topic": "CRISPR Gene Editing",
        "domain": "genetics",
        "papers_analyzed": 5,
        "knowledge_gaps": [
            "Limited data on long-term off-target effects in vivo",
            "Unclear delivery mechanisms for CNS cells",
            "Missing cross-study comparison of editing efficiency"
        ],
        "hypotheses": [
            {
                "hypothesis": "Lipid nanoparticle delivery of Cas9 may reduce off-target edits by 40% compared to viral vectors",
                "confidence": 0.78,
                "category": "Mechanistic",
                "testable": True,
                "impact": "High"
            },
            {
                "hypothesis": "Base editing variants show superior specificity in post-mitotic neurons",
                "confidence": 0.72,
                "category": "Comparative",
                "testable": True,
                "impact": "High"
            }
        ],
        "experiments": [
            {
                "title": "LNP vs AAV Delivery Comparison Study",
                "methodology": "In vitro + In vivo",
                "duration": "6 months",
                "feasibility": "High"
            }
        ]
    }

    # Display results
    print_section("KNOWLEDGE GAPS DETECTED", "-")
    for i, gap in enumerate(demo_result["knowledge_gaps"], 1):
        print(f"  {i}. {gap}")

    print_section("GENERATED HYPOTHESES", "-")
    for i, h in enumerate(demo_result["hypotheses"], 1):
        print(f"  Hypothesis {i}: {h['hypothesis']}")
        print(f"    Confidence: {h['confidence']:.0%} | Category: {h['category']} | Impact: {h['impact']}")
        print()

    print_section("PROPOSED EXPERIMENTS", "-")
    for i, exp in enumerate(demo_result["experiments"], 1):
        print(f"  Experiment {i}: {exp['title']}")
        print(f"    Method: {exp['methodology']} | Duration: {exp['duration']} | Feasibility: {exp['feasibility']}")
        print()

    print_section("DEMO COMPLETE")
    print("  Run with --topic to analyze real papers via ArXiv/PubMed!")
    print("  Launch Streamlit UI: streamlit run app.py")
    print()


def run_discovery(topic: str, domain: str, num_papers: int, output_file: str = None):
    """Run the full scientific discovery pipeline."""
    try:
        from engine.discovery_engine import DiscoveryEngine
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("Make sure you have installed requirements: pip install -r requirements.txt")
        sys.exit(1)

    print(f"\n[INIT] Topic: {topic}")
    print(f"[INIT] Domain: {domain}")
    print(f"[INIT] Papers to fetch: {num_papers}")
    print(f"[INIT] LLM: {os.getenv('LLM_PROVIDER', 'openai')}\n")

    engine = DiscoveryEngine(domain=domain)

    print_section("STEP 1: INGESTING RESEARCH PAPERS")
    print(f"  Fetching papers from ArXiv and PubMed...")
    papers = engine.ingest_papers(topic=topic, max_papers=num_papers)
    print(f"  Ingested {len(papers)} papers successfully.")

    print_section("STEP 2: BUILDING KNOWLEDGE GRAPH")
    print("  Extracting entities, concepts, and relationships...")
    graph = engine.build_knowledge_graph(papers)
    print(f"  Nodes: {graph.number_of_nodes()} | Edges: {graph.number_of_edges()}")

    print_section("STEP 3: DETECTING KNOWLEDGE GAPS")
    print("  Analyzing graph for structural gaps...")
    gaps = engine.detect_gaps(graph)
    print(f"  Found {len(gaps)} potential knowledge gaps:")
    for i, gap in enumerate(gaps[:5], 1):
        print(f"    {i}. {gap}")

    print_section("STEP 4: GENERATING HYPOTHESES")
    print("  Using LLM to propose novel hypotheses...")
    hypotheses = engine.generate_hypotheses(topic=topic, gaps=gaps, papers=papers)
    print(f"  Generated {len(hypotheses)} hypotheses:")
    for i, h in enumerate(hypotheses, 1):
        conf = h.get("confidence_score", 0)
        print(f"    {i}. [{conf:.0%}] {h.get('hypothesis', 'N/A')}")

    print_section("STEP 5: DESIGNING EXPERIMENTS")
    print("  Creating experimental protocols...")
    experiments = engine.design_experiments(hypotheses=hypotheses, domain=domain)
    print(f"  Designed {len(experiments)} experimental protocols:")
    for i, exp in enumerate(experiments, 1):
        title = exp.get("experiment_title", "N/A")
        print(f"    {i}. {title}")

    # Compile full report
    timestamp = datetime.now().isoformat()
    result = {
        "metadata": {
            "topic": topic,
            "domain": domain,
            "papers_analyzed": len(papers),
            "timestamp": timestamp
        },
        "knowledge_gaps": gaps,
        "hypotheses": hypotheses,
        "experiments": experiments
    }

    print_section("DISCOVERY PIPELINE COMPLETE")
    print(f"  Papers analyzed: {len(papers)}")
    print(f"  Knowledge gaps found: {len(gaps)}")
    print(f"  Hypotheses generated: {len(hypotheses)}")
    print(f"  Experiments designed: {len(experiments)}")

    if output_file:
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n  Results saved to: {output_file}")
    else:
        print("\n  (Use --output filename.json to save results)")

    print()
    return result


def main():
    """Main CLI entry point."""
    print_banner()

    parser = argparse.ArgumentParser(
        description="Autonomous Scientific Discovery Engine - Generate hypotheses from research papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --demo
  python main.py --topic "Alzheimers disease" --domain "neuroscience" --papers 20
  python main.py --topic "CRISPR" --domain "genetics" --output results.json
  streamlit run app.py
        """
    )

    parser.add_argument("--topic", type=str, help="Scientific topic to research")
    parser.add_argument("--domain", type=str, default="general", help="Scientific domain (oncology, genetics, neuroscience, etc.)")
    parser.add_argument("--papers", type=int, default=10, help="Number of papers to fetch (default: 10)")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample data")
    parser.add_argument("--ui", action="store_true", help="Launch Streamlit web UI")

    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.ui:
        print("Launching Streamlit UI...")
        os.system("streamlit run app.py")
    elif args.topic:
        run_discovery(
            topic=args.topic,
            domain=args.domain,
            num_papers=args.papers,
            output_file=args.output
        )
    else:
        parser.print_help()
        print("\nTip: Try --demo to see it in action!")
        print("     Or: streamlit run app.py  for the web UI")


if __name__ == "__main__":
    main()
