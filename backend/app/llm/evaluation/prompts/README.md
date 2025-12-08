# Alternative Keyword Extraction Prompts

This directory contains various prompt variations for testing keyword extraction performance.

## Prompts

- **prompt_v1_concise.txt**: Very concise, direct instructions
- **prompt_v2_single_words.txt**: Emphasizes single words with examples
- **prompt_v3_strict.txt**: Strict rules, 1-2 words maximum
- **prompt_v4_domain_focused.txt**: Domain-focused with guidelines
- **prompt_v5_minimal.txt**: Extremely minimal prompt
- **prompt_v6_structured.txt**: Structured approach with numbered steps

## Evaluation

To evaluate all prompts against the dataset:

```bash
# Evaluate baseline (current prompt)
python -m app.llm.evaluation.prompt_evaluator \
    --prompt-file app/llm/openai/prompts.py \
    --dataset dataset.json \
    --output results_baseline.json

# Evaluate each variant
for prompt in prompts/prompt_v*.txt; do
    name=$(basename "$prompt" .txt)
    python -m app.llm.evaluation.prompt_evaluator \
        --prompt-file "$prompt" \
        --dataset dataset.json \
        --output "results_${name}.json" \
        --delay 20.0
done
```

## Comparing Results

After evaluation, compare the mean Jaccard scores to identify the best-performing prompt.
