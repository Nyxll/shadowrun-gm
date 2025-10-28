# Prompt Management System

## Overview

This directory contains prompt templates for different AI operations in the Shadowrun GM training system. Each prompt is designed to guide the AI in generating responses that match Rick's GM style and teaching methodology.

## Prompt Files

### 1. gm-response.txt
**Purpose:** Generate GM responses to player queries

**Variables:**
- `{query_text}` - The player's query
- `{intent}` - Detected intent classification
- `{expected_intent}` - Expected intent (for training)
- `{training_examples}` - Similar examples from training corpus

**Usage:** Main prompt for generating GM responses during training sessions

**Key Features:**
- Incorporates Rick's GM style profile (73.6% rule citations, 31% mechanics)
- Uses training corpus examples for context
- Matches established voice and teaching patterns
- Includes dice notation guidelines

### 2. classify-intent.txt
**Purpose:** Classify player queries into intent categories

**Variables:**
- `{query_text}` - The player's query
- `{context}` - Additional context if available

**Usage:** Intent classification before generating responses

**Key Features:**
- 10 core intent categories
- Clear classification guidelines
- Confidence scoring
- Reasoning explanation

## Prompt Template Format

All prompts follow this structure:

```
[System Role Definition]

## [Section 1: Guidelines/Profile]
[Detailed instructions and context]

## [Section 2: Current Input]
{variable_placeholders}

## [Section 3: Task Definition]
[What the AI should do]

[Output format specification]
```

## Adding New Prompts

### 1. Create Prompt File

```bash
# Create new prompt in train/prompts/
touch train/prompts/your-prompt-name.txt
```

### 2. Define Variables

Use `{variable_name}` format for placeholders:
```
**Player Query:** {query_text}
**Character:** {character_name}
**Context:** {game_context}
```

### 3. Document in This README

Add entry to "Prompt Files" section above.

### 4. Register in Prompt Loader

Update `tools/training-processor.py` to load your prompt:
```python
def load_prompt(self, prompt_name: str, **variables) -> str:
    """Load and populate prompt template"""
    # Add your prompt to the loader
```

## Prompt Design Guidelines

### 1. Be Specific
- Define the AI's role clearly
- Provide concrete examples
- Specify output format

### 2. Include Context
- Rick's GM style profile
- Training corpus examples
- Relevant game rules

### 3. Use Variables
- Make prompts reusable
- Allow dynamic content
- Support different scenarios

### 4. Specify Output
- Define expected format
- Include examples
- Set constraints

## Example Prompt Usage

### In Training Processor

```python
# Load prompt template
prompt_template = self.load_prompt('gm-response')

# Populate variables
prompt = prompt_template.format(
    query_text=query['query_text'],
    intent=classification['intent'],
    expected_intent=query['expected_intent'],
    training_examples=self.get_training_examples(intent)
)

# Send to AI
response = self.call_ai(prompt)
```

### Preview Before Sending

```python
# Show user what will be sent to AI
print("\n" + "="*80)
print("PROMPT TO BE SENT TO AI:")
print("="*80)
print(prompt)
print("="*80)

# Confirm before sending
if input("Send this prompt? (y/n): ").lower() == 'y':
    response = self.call_ai(prompt)
```

## Prompt Categories

### Training Prompts
- `gm-response.txt` - Generate GM responses
- `classify-intent.txt` - Classify player intents

### Future Prompts (Planned)
- `dice-rolls.txt` - Generate dice roll requirements
- `rule-lookup.txt` - Find relevant rules
- `combat-resolution.txt` - Resolve combat actions
- `magic-resolution.txt` - Resolve magic actions
- `matrix-resolution.txt` - Resolve Matrix actions
- `character-advice.txt` - Character creation/advancement
- `narrative-generation.txt` - Generate narrative descriptions

## Prompt Versioning

When updating prompts:

1. **Save old version:**
   ```bash
   cp train/prompts/gm-response.txt train/prompts/archive/gm-response-v1.txt
   ```

2. **Update prompt file**

3. **Document changes:**
   ```
   # Changelog
   v2 (2025-10-19): Added dice notation examples
   v1 (2025-10-19): Initial version
   ```

4. **Test thoroughly** before deploying

## Prompt Testing

### Test Prompt Loading
```python
python -c "
from tools.training_processor import TrainingProcessor
tp = TrainingProcessor()
prompt = tp.load_prompt('gm-response', 
    query_text='Test query',
    intent='ROLEPLAY_ACTION',
    expected_intent='ROLEPLAY_ACTION',
    training_examples='Example 1\nExample 2'
)
print(prompt)
"
```

### Test AI Response
```bash
# Run training processor with prompt preview
python tools/training-processor.py --preview-prompts
```

## Best Practices

### 1. Keep Prompts Focused
- One prompt per task
- Clear, single purpose
- Avoid mixing concerns

### 2. Use Rick's Voice
- Incorporate GM style profile
- Reference training corpus
- Match established patterns

### 3. Provide Examples
- Show desired output format
- Include edge cases
- Demonstrate style

### 4. Make Prompts Maintainable
- Use clear variable names
- Document purpose
- Version control

### 5. Test Thoroughly
- Test with various inputs
- Verify output quality
- Check edge cases

## Integration with Training System

The prompt system integrates with the training processor:

1. **Load prompt template** from file
2. **Populate variables** with current context
3. **Preview prompt** (optional - show user)
4. **Send to AI** for generation
5. **Display response** for review
6. **Allow editing** before saving

This ensures transparency and control over what's sent to the AI.

## Future Enhancements

- [ ] Prompt A/B testing
- [ ] Prompt performance metrics
- [ ] Dynamic prompt selection based on intent
- [ ] Prompt optimization based on results
- [ ] Multi-language prompt support
- [ ] Prompt templates for different AI models
