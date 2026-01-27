# Alternative Keyword Extraction Prompts

This directory contains various prompt variations for testing keyword extraction performance. The prompts are organized
to systematically test prompt engineering best practices.

## Original Prompts (v1-v6)

- **prompt_v1_concise.txt**: Very concise, direct instructions
- **prompt_v2_single_words.txt**: Emphasizes single words with examples
- **prompt_v3_strict.txt**: Strict rules, 1-2 words maximum
- **prompt_v4_domain_focused.txt**: Domain-focused with guidelines
- **prompt_v5_minimal.txt**: Extremely minimal prompt
- **prompt_v6_structured.txt**: Structured approach with numbered steps

## Best Practice Testing Prompts (v7-v16)

These prompts systematically test individual and combined prompt engineering best practices:

### Individual Best Practices

- **prompt_v7_persona.txt**: Tests persona/adopting a role ("You are an expert...")
- **prompt_v8_delimiters.txt**: Tests using delimiters to indicate distinct parts of input
- **prompt_v9_explicit_steps.txt**: Tests specifying steps required to complete the task
- **prompt_v10_few_shot.txt**: Tests providing multiple detailed examples (few-shot learning)
- **prompt_v11_detailed_instructions.txt**: Tests writing clear, detailed instructions
- **prompt_v12_format_specification.txt**: Tests specifying desired format and length of output

### Best Practice Combinations

- **prompt_v13_persona_examples.txt**: Persona + Examples
- **prompt_v14_steps_delimiters.txt**: Explicit Steps + Delimiters
- **prompt_v15_persona_steps_examples.txt**: Persona + Steps + Examples
- **prompt_v16_all_best_practices.txt**: All best practices combined (Persona + Steps + Examples + Delimiters + Detailed
  Instructions + Format Specification)

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

After evaluation, compare the metrics (Jaccard, Precision, Recall, F1) to identify the best-performing prompt. The
evaluation system now calculates all metrics automatically.

## Best Practices Tested

The prompts systematically test the following prompt engineering best practices:

1. **Write clear instructions**: Detailed, unambiguous instructions (v11)
2. **Include details**: Comprehensive requirements and guidelines (v11, v16)
3. **Adopt a persona**: Role-based prompting (v7, v13, v15, v16)
4. **Use delimiters**: Clear indication of input sections (v8, v14, v16)
5. **Specify output format**: Detailed format specifications (v12, v16)
6. **Specify steps**: Step-by-step task breakdown (v9, v14, v15, v16)
7. **Provide examples**: Few-shot learning with examples (v10, v13, v15, v16)

## Evaluation Metrics

The evaluation system calculates:

- **Jaccard Similarity**: Overlap between extracted and ground truth keywords
- **Precision**: Proportion of extracted keywords that are correct
- **Recall**: Proportion of ground truth keywords that were extracted
- **F1 Score**: Harmonic mean of precision and recall
