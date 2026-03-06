"""
💡 Hypothesis Generator Module
The core AI engine: generates novel scientific hypotheses using LLM agents.
"""

import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


HYPOTHESIS_TYPES = {
    "mechanistic": "Proposes a specific biological/chemical mechanism",
    "causal": "Suggests a causal relationship between phenomena",
    "predictive": "Makes a testable prediction about future observations",
    "interventional": "Proposes an intervention that could alter an outcome",
}


class HypothesisGenerator:
    """
    LLM-powered scientific hypothesis generator.

    Pipeline:
    1. Analyze paper abstracts and knowledge graph
    2. Extract key concepts, entities, and relationships
    3. Identify knowledge gaps (unexplored connections)
    4. Generate novel, testable hypotheses
    5. Score hypotheses for novelty, feasibility, and impact
    """

    def __init__(self):
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        if self.use_ollama:
            self.client = OpenAI(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                api_key="ollama",
            )
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def extract_concepts(self, paper: Dict) -> Dict:
        """Extract scientific concepts, entities, and relationships from a paper."""
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")
        combined = ("Title: " + title + "\n\nAbstract: " + abstract)[:3000]

        prompt = (
            "Analyze this scientific paper and extract structured information.\n\n"
            "PAPER:\n" + combined + "\n\n"
            "Extract and return as JSON with keys:\n"
            "- concepts: list of key scientific concepts\n"
            "- entities: dict with genes, proteins, diseases, chemicals, methods, organisms\n"
            "- relationships: list of {subject, predicate, object} triples\n"
            "- main_finding: one sentence summary\n"
            "- research_area: field of study\n\n"
            "Return ONLY valid JSON."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scientific knowledge extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
                temperature=0.1,
            )
            raw = response.choices[0].message.content.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            return json.loads(raw)
        except Exception as e:
            print(f"   Extraction error: {e}")
            return {
                "concepts": [],
                "entities": {},
                "relationships": [],
                "main_finding": abstract[:200] if abstract else "",
                "research_area": "unknown",
            }

    def detect_gaps(self, papers: List[Dict], graph_gaps: List[Dict], domain: str) -> List[Dict]:
        """Use LLM to detect knowledge gaps from papers and graph analysis."""
        findings = []
        for p in papers[:10]:
            finding = p.get("main_finding") or p.get("abstract", "")[:200]
            if finding:
                t = p.get("title", "Unknown")[:60]
                findings.append("- " + t + ": " + finding)

        findings_text = "\n".join(findings[:10])
        graph_gaps_text = "\n".join([
            "- " + g["concept_a"] + " <-> " + g["concept_b"] + " (confidence: " + str(round(g["confidence"], 2)) + ")"
            for g in graph_gaps[:8]
        ]) if graph_gaps else "No graph gaps detected yet."

        prompt = (
            "You are an expert scientific researcher analyzing the frontier of " + domain + " research.\n\n"
            "CURRENT RESEARCH FINDINGS:\n" + findings_text + "\n\n"
            "POTENTIALLY UNEXPLORED CONNECTIONS (from co-occurrence analysis):\n" + graph_gaps_text + "\n\n"
            "Identify the TOP 5 most important knowledge gaps. Return as JSON array:\n"
            "[{\n"
            "  \"gap_id\": \"gap_1\",\n"
            "  \"description\": \"clear description of what is not yet known\",\n"
            "  \"involved_concepts\": [\"concept1\", \"concept2\"],\n"
            "  \"gap_type\": \"mechanistic|methodological|translational\",\n"
            "  \"significance\": \"why this gap matters\",\n"
            "  \"evidence_from_literature\": \"what existing papers hint at this gap\"\n"
            "}]\nReturn ONLY valid JSON array."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a brilliant scientist identifying research gaps. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.4,
            )
            raw = response.choices[0].message.content.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            return json.loads(raw)
        except Exception as e:
            print(f"   Gap detection error: {e}")
            return []

    def generate_hypotheses(
        self, gaps: List[Dict], papers: List[Dict], domain: str, num_hypotheses: int = 5
    ) -> List[Dict]:
        """Generate novel scientific hypotheses from detected knowledge gaps."""
        gaps_text = "\n".join([
            "Gap " + str(i+1) + ": " + g.get("description", "") +
            " (Concepts: " + ", ".join(g.get("involved_concepts", [])[:3]) + ")"
            for i, g in enumerate(gaps[:5])
        ])

        key_findings = []
        for p in papers[:8]:
            finding = p.get("main_finding") or p.get("abstract", "")[:150]
            if finding:
                key_findings.append("- " + finding)
        findings_text = "\n".join(key_findings[:8])

        prompt = (
            "You are a Nobel Prize-caliber scientist in " + domain + ".\n\n"
            "Based on these knowledge gaps:\n" + gaps_text + "\n\n"
            "And these key findings from recent literature:\n" + findings_text + "\n\n"
            "Generate " + str(num_hypotheses) + " novel, specific, testable scientific hypotheses.\n\n"
            "Each hypothesis must be:\n"
            "- Specific and falsifiable\n"
            "- Novel (not already established)\n"
            "- Mechanistically grounded\n"
            "- Significant if true\n\n"
            "Return as JSON array:\n"
            "[{\n"
            "  \"hypothesis_id\": \"H1\",\n"
            "  \"statement\": \"Full hypothesis statement (1-2 sentences)\",\n"
            "  \"one_liner\": \"Catchy press-release version\",\n"
            "  \"type\": \"mechanistic|causal|predictive|interventional\",\n"
            "  \"involved_concepts\": [\"concept1\", \"concept2\"],\n"
            "  \"rationale\": \"Scientific reasoning (2-3 sentences)\",\n"
            "  \"supporting_evidence\": \"What from existing literature supports this\",\n"
            "  \"novelty_score\": 0.85,\n"
            "  \"feasibility_score\": 0.70,\n"
            "  \"impact_score\": 0.90,\n"
            "  \"domain\": \"" + domain + "\",\n"
            "  \"confidence\": \"low|medium|high\"\n"
            "}]\nReturn ONLY valid JSON array."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a visionary scientist generating groundbreaking hypotheses. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3000,
                temperature=0.7,
            )
            raw = response.choices[0].message.content.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            hypotheses = json.loads(raw)
            for h in hypotheses:
                h["gap_sources"] = [g.get("gap_id", "") for g in gaps[:3]]
                h["paper_count"] = len(papers)
            return hypotheses
        except Exception as e:
            print(f"   Hypothesis generation error: {e}")
            return []

    def rank_hypotheses(self, hypotheses: List[Dict]) -> List[Dict]:
        """Rank hypotheses by composite score (novelty x feasibility x impact)."""
        for h in hypotheses:
            novelty = float(h.get("novelty_score", 0.5))
            feasibility = float(h.get("feasibility_score", 0.5))
            impact = float(h.get("impact_score", 0.5))
            h["composite_score"] = (impact * 0.45) + (novelty * 0.35) + (feasibility * 0.20)
        return sorted(hypotheses, key=lambda x: x.get("composite_score", 0), reverse=True)
