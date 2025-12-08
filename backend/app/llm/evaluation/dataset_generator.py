"""Script to generate evaluation dataset: keywords → user inputs."""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from app.core.config import settings
from app.llm.openai.provider import OpenAIProvider

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# Prompt for generating user inputs from keywords
DATASET_GENERATION_PROMPT = """You are helping to create a dataset for evaluating keyword extraction systems.

Given a list of keywords, generate a natural language research query that a user might submit to a research paper search system. The query should:
- Be written as if a researcher is asking for papers
- Naturally incorporate the given keywords
- Sound like a real research question or interest
- Be 1-3 sentences long
- Use academic language appropriate for scientific databases

Keywords: {keywords}

Generate only the user query text, nothing else."""


async def generate_user_input(provider: OpenAIProvider, keywords: List[str]) -> str:
    """
    Generate a user input query from a list of keywords using an LLM.
    
    Args:
        provider: OpenAIProvider instance
        keywords: List of keywords to incorporate into the query
        
    Returns:
        Generated user input string
    """
    keywords_str = ", ".join(keywords)
    prompt = DATASET_GENERATION_PROMPT.format(keywords=keywords_str)
    
    try:
        response = await provider.client.responses.create(
            model=provider._model,
            reasoning={"effort": "low"},
            input=[
                {
                    "role": "developer",
                    "content": prompt,
                },
            ],
        )
        return response.output_text.strip()
    except Exception as e:
        logger.error("Failed to generate user input for keywords %s: %s", keywords, e)
        raise


async def generate_dataset(
    provider: OpenAIProvider,
    seed_keywords: List[List[str]],
    output_path: Path,
    delay_seconds: float = 20.0,
) -> None:
    """
    Generate evaluation dataset from seed keywords.
    
    Args:
        provider: OpenAIProvider instance
        seed_keywords: List of keyword lists (each list becomes one test case)
        output_path: Path to save the dataset JSON file
        delay_seconds: Delay between requests to avoid rate limiting (default: 20s for 3 RPM limit)
    """
    import asyncio
    
    dataset = []
    
    logger.info("Generating dataset from %d keyword sets...", len(seed_keywords))
    logger.info("Using delay of %.1f seconds between requests to respect rate limits", delay_seconds)
    
    for i, keywords in enumerate(seed_keywords, 1):
        logger.info("Processing keyword set %d/%d: %s", i, len(seed_keywords), keywords)
        
        try:
            user_input = await generate_user_input(provider, keywords)
            
            test_case = {
                "ground_truth_keywords": keywords,
                "user_input": user_input,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "model": provider._model,
                },
            }
            
            dataset.append(test_case)
            logger.info("✓ Generated: %s", user_input[:80] + "..." if len(user_input) > 80 else user_input)
            
            # Add delay between requests (except for the last one)
            if i < len(seed_keywords):
                logger.info("Waiting %.1f seconds before next request...", delay_seconds)
                await asyncio.sleep(delay_seconds)
            
        except Exception as e:
            logger.error("Failed to generate test case for keywords %s: %s", keywords, e)
            # Still wait even on error to respect rate limits
            if i < len(seed_keywords):
                logger.info("Waiting %.1f seconds before next request...", delay_seconds)
                await asyncio.sleep(delay_seconds)
            continue
    
    # Save dataset
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "dataset": dataset,
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "num_cases": len(dataset),
                    "model": provider._model,
                },
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    
    logger.info("✓ Dataset saved to %s (%d test cases)", output_path, len(dataset))


def load_keywords_from_file(keywords_file: Path) -> List[List[str]]:
    """
    Load keyword sets from a file.
    
    Expected format: One keyword set per line, keywords separated by commas.
    Example:
        transformer, attention, BERT
        reinforcement learning, Q-learning, DQN
        convolutional neural network, CNN, image classification
    
    Args:
        keywords_file: Path to keywords file
        
    Returns:
        List of keyword lists
    """
    if not keywords_file.exists():
        raise FileNotFoundError(f"Keywords file not found: {keywords_file}")
    
    keyword_sets = []
    with keywords_file.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            keywords = [kw.strip() for kw in line.split(",") if kw.strip()]
            if keywords:
                keyword_sets.append(keywords)
            else:
                logger.warning("Skipping empty line %d", line_num)
    
    return keyword_sets


async def main() -> None:
    """Main entry point for dataset generation script."""
    parser = argparse.ArgumentParser(
        description="Generate evaluation dataset: keywords → user inputs"
    )
    parser.add_argument(
        "--keywords-file",
        type=str,
        required=True,
        help="Path to file containing keyword sets (one per line, comma-separated)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_data/dataset.json",
        help="Output path for generated dataset JSON file (default: evaluation_data/dataset.json)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=20.0,
        help="Delay in seconds between API requests (default: 20.0 for 3 RPM limit)",
    )
    
    args = parser.parse_args()
    
    # Validate OpenAI API key
    if settings.OPENAI_API_KEY is None:
        logger.error("OPENAI_API_KEY is not set. Please configure it in your environment.")
        return
    
    # Load keywords
    keywords_file = Path(args.keywords_file)
    seed_keywords = load_keywords_from_file(keywords_file)
    
    if not seed_keywords:
        logger.error("No valid keyword sets found in %s", keywords_file)
        return
    
    logger.info("Loaded %d keyword sets from %s", len(seed_keywords), keywords_file)
    
    # Initialize provider
    provider = OpenAIProvider()
    
    # Generate dataset
    output_path = Path(args.output)
    await generate_dataset(provider, seed_keywords, output_path, delay_seconds=args.delay)
    
    logger.info("✓ Dataset generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
