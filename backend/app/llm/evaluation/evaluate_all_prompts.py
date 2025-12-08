"""Script to evaluate multiple prompts against a dataset and compare results."""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List

from app.core.config import settings
from app.llm.evaluation.prompt_evaluator import evaluate_prompt, load_dataset, load_prompt
from app.llm.openai.provider import OpenAIProvider

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def evaluate_all_prompts(
    prompt_files: List[Path],
    dataset_path: Path,
    output_dir: Path,
    delay_seconds: float = 20.0,
) -> None:
    """
    Evaluate multiple prompts and generate a comparison report.
    
    Args:
        prompt_files: List of paths to prompt files
        dataset_path: Path to evaluation dataset
        output_dir: Directory to save individual results and comparison
        delay_seconds: Delay between API requests
    """
    if settings.OPENAI_API_KEY is None:
        logger.error("OPENAI_API_KEY is not set. Please configure it in your environment.")
        return
    
    # Load dataset once
    logger.info("Loading dataset from %s...", dataset_path)
    dataset = load_dataset(dataset_path)
    logger.info("Loaded %d test cases", len(dataset))
    
    # Initialize provider
    provider = OpenAIProvider()
    
    # Evaluate each prompt
    all_results = []
    
    for i, prompt_file in enumerate(prompt_files, 1):
        logger.info("\n" + "=" * 60)
        logger.info("Evaluating prompt %d/%d: %s", i, len(prompt_files), prompt_file.name)
        logger.info("=" * 60)
        
        try:
            prompt = load_prompt(prompt_file)
            
            # Evaluate
            results = await evaluate_prompt(provider, prompt, dataset, delay_seconds=delay_seconds)
            
            # Save individual results
            output_file = output_dir / f"results_{prompt_file.stem}.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            with output_file.open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            all_results.append({
                "prompt_file": str(prompt_file),
                "prompt_name": prompt_file.stem,
                "mean_jaccard": results["mean_jaccard"],
                "std_jaccard": results["std_jaccard"],
                "min_jaccard": results["min_jaccard"],
                "max_jaccard": results["max_jaccard"],
                "num_test_cases": results["num_test_cases"],
            })
            
            logger.info("✓ Saved results to %s", output_file)
            
        except Exception as e:
            logger.error("Failed to evaluate %s: %s", prompt_file, e)
            continue
    
    # Generate comparison report
    if all_results:
        # Sort by mean Jaccard score (descending)
        all_results.sort(key=lambda x: x["mean_jaccard"], reverse=True)
        
        comparison_file = output_dir / "comparison_report.json"
        with comparison_file.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "dataset": str(dataset_path),
                    "num_test_cases": len(dataset),
                    "prompts_evaluated": len(all_results),
                    "results": all_results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("COMPARISON SUMMARY")
        logger.info("=" * 60)
        logger.info("%-30s %10s %10s %10s %10s", "Prompt", "Mean", "Std", "Min", "Max")
        logger.info("-" * 60)
        
        for result in all_results:
            logger.info(
                "%-30s %10.4f %10.4f %10.4f %10.4f",
                result["prompt_name"][:30],
                result["mean_jaccard"],
                result["std_jaccard"],
                result["min_jaccard"],
                result["max_jaccard"],
            )
        
        logger.info("=" * 60)
        logger.info("Best performing prompt: %s (Mean Jaccard: %.4f)", 
                   all_results[0]["prompt_name"], 
                   all_results[0]["mean_jaccard"])
        logger.info("✓ Comparison report saved to %s", comparison_file)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate multiple prompts against a dataset and compare results"
    )
    parser.add_argument(
        "--prompts-dir",
        type=str,
        default="app/llm/evaluation/prompts",
        help="Directory containing prompt files to evaluate",
    )
    parser.add_argument(
        "--prompt-pattern",
        type=str,
        default="prompt_*.txt",
        help="Glob pattern to match prompt files (default: prompt_*.txt)",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to dataset JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="evaluation_results",
        help="Directory to save results and comparison report (default: evaluation_results/)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=20.0,
        help="Delay in seconds between API requests (default: 20.0 for 3 RPM limit)",
    )
    parser.add_argument(
        "--include-baseline",
        action="store_true",
        help="Include the baseline prompt from app/llm/openai/prompts.py",
    )
    
    args = parser.parse_args()
    
    # Find prompt files
    prompts_dir = Path(args.prompts_dir)
    if not prompts_dir.exists():
        logger.error("Prompts directory not found: %s", prompts_dir)
        return
    
    prompt_files = list(prompts_dir.glob(args.prompt_pattern))
    
    if args.include_baseline:
        baseline_prompt = Path("app/llm/openai/prompts.py")
        if baseline_prompt.exists():
            prompt_files.insert(0, baseline_prompt)
            logger.info("Including baseline prompt: %s", baseline_prompt)
    
    if not prompt_files:
        logger.error("No prompt files found matching pattern '%s' in %s", 
                    args.prompt_pattern, prompts_dir)
        return
    
    logger.info("Found %d prompt files to evaluate:", len(prompt_files))
    for pf in prompt_files:
        logger.info("  - %s", pf)
    
    # Evaluate all prompts
    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    
    await evaluate_all_prompts(
        prompt_files=prompt_files,
        dataset_path=dataset_path,
        output_dir=output_dir,
        delay_seconds=args.delay,
    )


if __name__ == "__main__":
    asyncio.run(main())
