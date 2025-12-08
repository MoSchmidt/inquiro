"""Script to evaluate keyword extraction prompts against a dataset."""

import argparse
import asyncio
import importlib.util
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from app.core.config import settings
from app.llm.evaluation.metrics import calculate_keyword_jaccard
from app.llm.openai.provider import OpenAIProvider

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def extract_keywords_with_prompt(
    provider: OpenAIProvider,
    user_input: str,
    prompt: str,
) -> List[str]:
    """
    Extract keywords from user input using a custom prompt.

    Args:
        provider: OpenAIProvider instance
        user_input: User query text
        prompt: Custom prompt for keyword extraction

    Returns:
        List of extracted keywords
    """
    try:
        # Accessing _model is necessary for evaluation scripts
        # pylint: disable=protected-access
        response = await provider.client.responses.create(
            model=provider._model,
            reasoning={"effort": "low"},
            input=[
                {
                    "role": "developer",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
        )

        try:
            keyword_list = json.loads(response.output_text)
            if isinstance(keyword_list, list):
                return keyword_list
            return []
        except json.decoder.JSONDecodeError:
            preview = response.output_text[:100]
            logger.warning("Failed to parse JSON from response: %s", preview)
            return []

    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error("Failed to extract keywords: %s", exc)
        return []


async def evaluate_prompt(  # pylint: disable=too-many-locals
    provider: OpenAIProvider,
    prompt: str,
    dataset: List[Dict],
    delay_seconds: float = 20.0,
) -> Dict:
    """
    Evaluate a prompt against a dataset.

    Args:
        provider: OpenAIProvider instance
        prompt: Prompt to evaluate
        dataset: List of test cases with 'ground_truth_keywords' and 'user_input'
        delay_seconds: Delay between requests to avoid rate limiting
            (default: 20s for 3 RPM limit)

    Returns:
        Evaluation results dictionary
    """
    logger.info("Evaluating prompt against %d test cases...", len(dataset))
    logger.info(
        "Using delay of %.1f seconds between requests to respect rate limits",
        delay_seconds,
    )

    per_case_results = []

    for i, test_case in enumerate(dataset, 1):
        ground_truth = test_case["ground_truth_keywords"]
        user_input = test_case["user_input"]

        user_preview = user_input[:60] + "..." if len(user_input) > 60 else user_input
        logger.info("Test case %d/%d: %s", i, len(dataset), user_preview)

        extracted = await extract_keywords_with_prompt(provider, user_input, prompt)

        jaccard = calculate_keyword_jaccard(extracted, ground_truth)

        per_case_results.append({
            "test_case_idx": i - 1,  # 0-indexed
            "ground_truth_keywords": ground_truth,
            "user_input": user_input,
            "extracted_keywords": extracted,
            "jaccard_score": jaccard,
        })

        logger.info(
            "  Ground truth: %s | Extracted: %s | Jaccard: %.3f",
            ground_truth,
            extracted,
            jaccard,
        )

        # Add delay between requests (except for the last one)
        if i < len(dataset):
            logger.info("Waiting %.1f seconds before next request...", delay_seconds)
            await asyncio.sleep(delay_seconds)

    # Extract scores for aggregate statistics
    per_case_scores = [result["jaccard_score"] for result in per_case_results]

    # Calculate aggregate statistics
    mean_jaccard = sum(per_case_scores) / len(per_case_scores) if per_case_scores else 0.0

    # Calculate standard deviation
    if len(per_case_scores) > 1:
        variance = sum((x - mean_jaccard) ** 2 for x in per_case_scores) / len(per_case_scores)
        std_jaccard = variance ** 0.5
    else:
        std_jaccard = 0.0

    # Accessing _model is necessary for evaluation scripts
    # pylint: disable=protected-access
    results = {
        "prompt": prompt,
        "mean_jaccard": mean_jaccard,
        "std_jaccard": std_jaccard,
        "min_jaccard": min(per_case_scores) if per_case_scores else 0.0,
        "max_jaccard": max(per_case_scores) if per_case_scores else 0.0,
        "num_test_cases": len(dataset),
        "per_case_scores": per_case_results,
        "metadata": {
            "evaluated_at": datetime.utcnow().isoformat(),
            "model": provider._model,
        },
    }

    return results


def load_dataset(dataset_path: Path) -> List[Dict]:
    """
    Load evaluation dataset from JSON file.

    Args:
        dataset_path: Path to dataset JSON file

    Returns:
        List of test cases
    """
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "dataset" in data:
        return data["dataset"]

    # If dataset is a direct list
    if isinstance(data, list):
        return data

    raise ValueError("Invalid dataset format: expected 'dataset' key or list")


def load_prompt(prompt_path: Path) -> str:
    """
    Load prompt from text file or Python file.

    If the file is a Python file (ends with .py), it will try to extract
    KEYWORD_PROMPT from it. Otherwise, it reads the file as plain text.

    Args:
        prompt_path: Path to prompt text file or Python file

    Returns:
        Prompt string
    """
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    # If it's a Python file, try to extract KEYWORD_PROMPT
    if prompt_path.suffix == ".py":
        spec = importlib.util.spec_from_file_location("prompts_module", prompt_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "KEYWORD_PROMPT"):
                return module.KEYWORD_PROMPT.strip()
            raise ValueError(
                f"Python file {prompt_path} does not contain KEYWORD_PROMPT variable"
            )

    # Otherwise, read as plain text
    with prompt_path.open("r", encoding="utf-8") as file:
        return file.read().strip()


async def main() -> None:
    """Main entry point for prompt evaluation script."""
    parser = argparse.ArgumentParser(
        description="Evaluate keyword extraction prompt against dataset"
    )
    parser.add_argument(
        "--prompt-file",
        type=str,
        required=True,
        help="Path to text file containing the prompt to evaluate",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to dataset JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_results/results.json",
        help="Output path for evaluation results JSON file "
        "(default: evaluation_results/results.json)",
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

    # Load prompt
    prompt_path = Path(args.prompt_file)
    prompt = load_prompt(prompt_path)
    logger.info("Loaded prompt from %s", prompt_path)
    logger.info("Prompt preview: %s...", prompt[:100])

    # Load dataset
    dataset_path = Path(args.dataset)
    dataset = load_dataset(dataset_path)
    logger.info("Loaded dataset from %s (%d test cases)", dataset_path, len(dataset))

    # Initialize provider
    provider = OpenAIProvider()

    # Evaluate prompt
    results = await evaluate_prompt(provider, prompt, dataset, delay_seconds=args.delay)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    # Print summary
    logger.info("\n" + "=" * 60)  # pylint: disable=logging-not-lazy
    logger.info("EVALUATION SUMMARY")
    logger.info("=" * 60)  # pylint: disable=logging-not-lazy
    logger.info("Mean Jaccard Score: %.4f", results["mean_jaccard"])
    logger.info("Std Jaccard Score:  %.4f", results["std_jaccard"])
    logger.info("Min Jaccard Score:  %.4f", results["min_jaccard"])
    logger.info("Max Jaccard Score:  %.4f", results["max_jaccard"])
    logger.info("Test Cases:         %d", results["num_test_cases"])
    logger.info("=" * 60)
    # Using % formatting is appropriate here for file path
    logger.info("✓ Results saved to %s", output_path)  # pylint: disable=logging-not-lazy


if __name__ == "__main__":
    asyncio.run(main())
