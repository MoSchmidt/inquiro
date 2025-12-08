# Prompt Evaluation System

This module provides tools for benchmarking and comparing different keyword extraction prompts.

## Overview

The evaluation system works in two stages:

1. **Dataset Generation**: Create ground truth test cases (keywords → user inputs)
2. **Prompt Evaluation**: Test prompts against the dataset and calculate Jaccard similarity scores

## Quick Start

### 1. Generate Evaluation Dataset

First, create a keywords file with one keyword set per line (comma-separated):

```bash
# keywords.txt
transformer, attention mechanism, BERT
reinforcement learning, Q-learning, DQN
convolutional neural network, CNN, image classification
```

Then generate the dataset:

```bash
cd backend
python -m app.llm.evaluation.dataset_generator \
    --keywords-file keywords.txt \
    --output evaluation_data/dataset.json
```

Note: The default output is `evaluation_data/dataset.json` (directories are created automatically).

This will create the dataset file with test cases containing:
- `ground_truth_keywords`: The original keywords
- `user_input`: Generated natural language query
- `metadata`: Generation info

### 2. Evaluate a Prompt

Create a prompt file (e.g., `my_prompt.txt`):

```
You are an expert in academic information retrieval. Extract 5 short search queries...
```

Then evaluate it:

```bash
python -m app.llm.evaluation.prompt_evaluator \
    --prompt-file my_prompt.txt \
    --dataset evaluation_data/dataset.json \
    --output evaluation_results/results.json
```

Note: The default output is `evaluation_results/results.json` (directories are created automatically).

The results will include:
- `mean_jaccard`: Average Jaccard similarity score
- `std_jaccard`: Standard deviation
- `min_jaccard` / `max_jaccard`: Score range
- `per_case_scores`: Detailed results for each test case

## Metrics

**Jaccard Similarity**: Measures overlap between extracted and ground truth keywords
- Formula: `|A ∩ B| / |A ∪ B|`
- Range: 0.0 (no overlap) to 1.0 (perfect match)
- Keywords are normalized (lowercase, stripped) before comparison

## File Structure

```
app/llm/evaluation/
├── __init__.py
├── metrics.py              # Jaccard similarity calculation
├── dataset_generator.py     # Generate test dataset
├── prompt_evaluator.py      # Evaluate prompts
└── README.md               # This file
```

## Example Workflow

```bash
# 1. Create keywords file
cat > keywords.txt << EOF
transformer, attention, BERT
reinforcement learning, DQN, policy gradient
CNN, image classification, ResNet
EOF

# 2. Generate dataset
python -m app.llm.evaluation.dataset_generator \
    --keywords-file keywords.txt \
    --output evaluation/dataset.json \
    --delay 20.0

# 3. Evaluate a single prompt
python -m app.llm.evaluation.prompt_evaluator \
    --prompt-file app/llm/openai/prompts.py \
    --dataset dataset.json \
    --output results_baseline.json \
    --delay 20.0

# 4. Evaluate all prompts and compare (RECOMMENDED)
python -m app.llm.evaluation.evaluate_all_prompts \
    --prompts-dir app/llm/evaluation/prompts \
    --dataset evaluation_data/dataset.json \
    --output-dir evaluation_results \
    --delay 20.0 \
    --include-baseline
```

## Evaluating Multiple Prompts

The `evaluate_all_prompts.py` script evaluates all prompts in a directory and generates a comparison report:

```bash
python -m app.llm.evaluation.evaluate_all_prompts \
    --prompts-dir app/llm/evaluation/prompts \
    --dataset evaluation_data/dataset.json \
    --output-dir evaluation_results \
    --delay 20.0 \
    --include-baseline
```

This will:
- Evaluate all prompts matching the pattern (default: `prompt_*.txt`)
- Save individual results for each prompt
- Generate a comparison report ranking prompts by mean Jaccard score
- Optionally include the baseline prompt from `app/llm/openai/prompts.py`

## Notes

- Requires `OPENAI_API_KEY` to be set in your environment
- Dataset generation uses the same OpenAI model as production
- Evaluation runs sequentially (one test case at a time)
- Results are saved as JSON for programmatic analysis
