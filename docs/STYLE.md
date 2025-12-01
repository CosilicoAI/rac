# Cosilico style guide

## Core principles

### Epistemic rigor

We build foundational epistemic technology. Our writing reflects this.

1. **Every falsifiable claim must be corroborated.** If you state a number, cite the source. If you claim X causes Y, show the evidence.

2. **Avoid unfalsifiable claims.** Don't write "our approach is better" - write "our approach reduces calculation time from 200ms to 15ms (benchmark: test_suite_v1)."

3. **Frame uncertainty as prediction.** Instead of "this will improve performance," write "we expect this to improve performance because [mechanism]. We will measure via [metric]."

4. **Distinguish fact from expectation.** Use explicit markers:
   - Fact: "PolicyEngine processes 100M households in 3 minutes."
   - Expectation: "We expect the DSL to reduce rule-writing time by 50% based on [similar project data]."
   - Hypothesis: "If we implement caching, we predict 10x speedup on repeated calculations."

### Directness

1. **No filler.** Cut "in order to," "it should be noted that," "as mentioned above."

2. **Active voice.** "The engine calculates taxes" not "taxes are calculated by the engine."

3. **Lead with the point.** Don't build up - state the conclusion first, then support it.

4. **Short sentences.** If a sentence has more than one comma, split it.

### Precision over persuasion

1. **No unsupported adjectives/adverbs.** Remove words like:
   - "significant" → state the number
   - "fast" → state the latency
   - "robust" → state what failure modes it handles
   - "comprehensive" → state coverage percentage
   - "intuitive" → cite user testing results or remove
   - "powerful" → describe the specific capability
   - "seamless" → describe the integration mechanism

2. **Quantify or remove.**
   - Bad: "significantly faster than alternatives"
   - Good: "15ms vs 200ms (13x faster)"
   - Bad: "comprehensive coverage of federal benefits"
   - Good: "covers 47 federal benefit programs (see list)"

3. **Avoid marketing language.** We don't need to convince - we need to inform. Let the facts speak.

## Formatting

### Headings

Use sentence case for all headings:
- Good: "## Parameter tiers"
- Bad: "## Parameter Tiers"

Exception: proper nouns and acronyms retain capitalization:
- "## Using the DSL with Python"
- "## EITC implementation example"

### Code examples

1. Show real, runnable code. No pseudocode unless explicitly labeled.

2. Include expected output when helpful.

3. Keep examples minimal - show only what's needed to illustrate the point.

### Lists

1. Use numbered lists for sequences or ranked items.

2. Use bullet points for unordered collections.

3. Keep list items parallel in structure.

### Tables

Use tables for comparisons and structured data. Include sources in a row or footnote.

## Writing process

### Before writing

1. Identify the single main point.
2. List the evidence that supports it.
3. Note any claims that need corroboration - find sources or remove.

### During writing

1. Write the main point first.
2. Add supporting evidence.
3. Remove unnecessary words.

### Before committing

1. Read aloud. If it sounds promotional, rewrite.
2. Check every number has a source.
3. Verify every comparison is fair and documented.
4. Remove adjectives that aren't backed by data.

## Examples

### Bad

> Our innovative rules engine provides comprehensive, blazing-fast calculations with an intuitive developer experience. The robust architecture seamlessly handles millions of households.

Problems:
- "innovative" - compared to what?
- "comprehensive" - what coverage?
- "blazing-fast" - how fast?
- "intuitive" - says who?
- "robust" - handles what failures?
- "seamlessly" - what does this mean?
- "millions" - exactly how many?

### Good

> The rules engine calculates federal income tax, EITC, and SNAP eligibility for 100M households in 180 seconds on a 32-core machine. It processes single households in 12ms median (p99: 45ms). Coverage: 47 federal programs, 50 state income tax systems. See benchmarks in `tests/benchmarks/`.

Why it works:
- Specific programs named
- Exact performance numbers
- Hardware context provided
- Coverage quantified
- Source referenced

## Common fixes

| Instead of | Write |
|------------|-------|
| "significantly" | [the number] |
| "state-of-the-art" | [specific comparison] |
| "easy to use" | [user testing data or specific UX claim] |
| "powerful" | [specific capability] |
| "flexible" | [what configurations it supports] |
| "scalable" | [tested scale + resource requirements] |
| "efficient" | [specific efficiency metric] |
| "modern" | [specific technology choices] |

## Tone

Direct. Precise. Neutral. We inform, we don't persuade. The evidence persuades.

If you find yourself trying to convince the reader, step back. Either the facts support the claim (state them) or they don't (reconsider the claim).
