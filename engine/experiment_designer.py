"""
🧪 Experiment Designer Module
Designs experiments to test AI-generated scientific hypotheses.
"""

import os
import json
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ExperimentDesigner:
    """
    AI-powered experiment designer.
    For each hypothesis, generates: experimental approach, protocol steps,
    required materials, controls, expected outcomes, statistical analysis,
    timeline/cost estimates, and risk assessment.
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

    def design_experiment(self, hypothesis: Dict, domain: str) -> Dict:
        """Design a detailed experiment to test a hypothesis."""
        statement = hypothesis.get("statement", "")
        h_type = hypothesis.get("type", "mechanistic")
        concepts = ", ".join(hypothesis.get("involved_concepts", [])[:5])
        rationale = hypothesis.get("rationale", "")

        prompt = (
            "You are an expert experimental scientist in " + domain + ".\n\n"
            "Design a rigorous experiment to test this hypothesis:\n"
            "HYPOTHESIS: " + statement + "\n"
            "TYPE: " + h_type + "\n"
            "CONCEPTS: " + concepts + "\n\n"
            "Return a JSON object with these keys:\n"
            "experiment_title, approach (in_vitro/in_vivo/computational/clinical), "
            "model_system, hypothesis_test, protocol_steps (list of 5-8 steps), "
            "independent_variable, dependent_variable, controls (list), "
            "materials (list), statistical_analysis, expected_results_if_true, "
            "expected_results_if_false, timeline_weeks (int), estimated_cost_usd (int), "
            "difficulty (low/medium/high), risks (list), alternative_approaches (list)"
            "\nReturn ONLY valid JSON."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Expert experimental scientist. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            experiment = json.loads(raw)
            experiment["hypothesis_id"] = hypothesis.get("hypothesis_id", "H?")
            experiment["hypothesis_statement"] = statement
            return experiment
        except Exception as e:
            print(f"   Experiment design error: {e}")
            return self._fallback_experiment(hypothesis, domain)

    def _fallback_experiment(self, hypothesis: Dict, domain: str) -> Dict:
        """Generate a basic experiment template if LLM fails."""
        statement = hypothesis.get("statement", "")
        concepts = hypothesis.get("involved_concepts", [])
        return {
            "experiment_title": "Validation of: " + statement[:60],
            "approach": "in_vitro",
            "model_system": "Appropriate model system for " + domain,
            "hypothesis_test": "Test whether: " + statement,
            "protocol_steps": [
                "Step 1: Prepare experimental materials and controls",
                "Step 2: Set up experimental and control conditions",
                "Step 3: Apply treatment or intervention",
                "Step 4: Collect measurements at defined timepoints",
                "Step 5: Analyze data using appropriate statistical tests",
                "Step 6: Validate findings with biological replicates",
            ],
            "independent_variable": concepts[0] if concepts else "variable",
            "dependent_variable": concepts[1] if len(concepts) > 1 else "outcome",
            "controls": ["Positive control", "Negative control", "Vehicle control"],
            "materials": ["Standard lab reagents", "Appropriate assay kits"],
            "statistical_analysis": "ANOVA with post-hoc tests, n=3 biological replicates",
            "expected_results_if_true": "Significant change in dependent variable",
            "expected_results_if_false": "No significant difference between groups",
            "timeline_weeks": 12,
            "estimated_cost_usd": 10000,
            "difficulty": "medium",
            "risks": ["Technical variability", "Reagent availability"],
            "alternative_approaches": ["Computational validation"],
            "hypothesis_id": hypothesis.get("hypothesis_id", "H?"),
            "hypothesis_statement": statement,
        }

    def design_batch(self, hypotheses: List[Dict], domain: str, top_n: int = 3) -> List[Dict]:
        """Design experiments for the top N hypotheses."""
        experiments = []
        for i, hypothesis in enumerate(hypotheses[:top_n]):
            h_id = hypothesis.get("hypothesis_id", f"H{i+1}")
            print(f"   Designing experiment for {h_id}...")
            exp = self.design_experiment(hypothesis, domain)
            experiments.append(exp)
        return experiments

    def format_as_protocol(self, experiment: Dict) -> str:
        """Format experiment design as readable Markdown."""
        h_id = experiment.get("hypothesis_id", "H?")
        title = experiment.get("experiment_title", "Experiment")
        approach = experiment.get("approach", "").replace("_", " ").title()
        steps = experiment.get("protocol_steps", [])
        materials = experiment.get("materials", [])
        controls = experiment.get("controls", [])
        timeline = experiment.get("timeline_weeks", "?")
        cost = experiment.get("estimated_cost_usd", "?")
        difficulty = experiment.get("difficulty", "?").title()
        risks = experiment.get("risks", [])
        alt = experiment.get("alternative_approaches", [])

        steps_md = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
        materials_md = "\n".join([f"- {m}" for m in materials])
        controls_md = "\n".join([f"- {c}" for c in controls])
        risks_md = "\n".join([f"- {r}" for r in risks])
        alt_md = "\n".join([f"- {a}" for a in alt])

        cost_str = f"${cost:,}" if isinstance(cost, int) else str(cost)

        return (
            f"## Experiment {h_id}: {title}\n\n"
            f"**Approach:** {approach}\n"
            f"**Model System:** {experiment.get(chr(39)model_system chr(39), chr(39)chr(39))}\n"
            f"**Difficulty:** {difficulty} | **Timeline:** {timeline} weeks | **Cost:** {cost_str}\n\n"
            f"### Hypothesis\n> {experiment.get(chr(39)hypothesis_statement chr(39), chr(39)chr(39))}\n\n"
            f"### Protocol Steps\n{steps_md}\n\n"
            f"### Variables\n"
            f"- **Independent:** {experiment.get(chr(39)independent_variable chr(39), chr(39)chr(39))}\n"
            f"- **Dependent:** {experiment.get(chr(39)dependent_variable chr(39), chr(39)chr(39))}\n\n"
            f"### Controls\n{controls_md}\n\n"
            f"### Materials\n{materials_md}\n\n"
            f"### Statistics\n{experiment.get(chr(39)statistical_analysis chr(39), chr(39)chr(39))}\n\n"
            f"### Expected Outcomes\n"
            f"- If TRUE: {experiment.get(chr(39)expected_results_if_true chr(39), chr(39)chr(39))}\n"
            f"- If FALSE: {experiment.get(chr(39)expected_results_if_false chr(39), chr(39)chr(39))}\n\n"
            f"### Risks\n{risks_md}\n\n"
            f"### Alternatives\n{alt_md}\n\n---\n"
        )
