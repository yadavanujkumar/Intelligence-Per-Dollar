"""LLM-as-a-Judge evaluator for scoring responses."""

import asyncio
from typing import Dict, Any, Optional
from ..llm_clients import OpenAIClient


class LLMJudge:
    """Evaluates LLM responses using another LLM as a judge."""
    
    EVALUATION_PROMPT = """You are an expert evaluator of AI responses. Rate the following response on a scale of 0.0 to 1.0 based on these criteria:
- Accuracy and correctness
- Completeness and thoroughness
- Clarity and coherence
- Relevance to the prompt
- Overall quality

Prompt Category: {category}
Original Prompt: {prompt}

Response to Evaluate:
{response}

Provide your evaluation in the following format:
Score: [0.0-1.0]
Reasoning: [Your detailed explanation]

Be strict but fair. Only exceptional responses should score above 0.9.
"""
    
    def __init__(self, judge_client: OpenAIClient):
        """Initialize the judge with a capable LLM client."""
        self.judge_client = judge_client
    
    async def evaluate(
        self,
        prompt: str,
        response: str,
        category: str
    ) -> Dict[str, Any]:
        """Evaluate a response and return score with reasoning."""
        
        evaluation_prompt = self.EVALUATION_PROMPT.format(
            category=category,
            prompt=prompt,
            response=response
        )
        
        try:
            judge_response = await self.judge_client.generate(
                evaluation_prompt,
                max_tokens=500,
                temperature=0.3  # Lower temperature for more consistent evaluation
            )
            
            # Parse the response
            score, reasoning = self._parse_evaluation(judge_response.text)
            
            return {
                "intelligence_score": score,
                "judge_reasoning": reasoning
            }
        
        except Exception as e:
            print(f"Error during evaluation: {e}")
            return {
                "intelligence_score": 0.0,
                "judge_reasoning": f"Evaluation failed: {str(e)}"
            }
    
    def _parse_evaluation(self, evaluation_text: str) -> tuple:
        """Parse the judge's evaluation to extract score and reasoning."""
        lines = evaluation_text.strip().split("\n")
        score = 0.0
        reasoning = ""
        
        for line in lines:
            if line.startswith("Score:"):
                try:
                    score_str = line.replace("Score:", "").strip()
                    # Handle various formats: "0.85", "[0.85]", etc.
                    score_str = score_str.strip("[]").strip()
                    score = float(score_str)
                    score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
                except ValueError:
                    score = 0.5  # Default if parsing fails
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()
        
        # If reasoning spans multiple lines, capture it all
        if "Reasoning:" in evaluation_text:
            reasoning = evaluation_text.split("Reasoning:", 1)[1].strip()
        
        return score, reasoning
