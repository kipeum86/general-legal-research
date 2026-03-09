# Counter-Analysis Checklist

Every key conclusion in Step 5 must be tested against at least one of the following counter-analysis dimensions before proceeding to Step 6.

## Mandatory Check: Per-Conclusion Counter-Analysis

For each conclusion, ask:

### 1. Alternative Interpretation
- Is there a plausible alternative reading of the statute/regulation text?
- Has any court, regulator, or commentary adopted a different interpretation?
- Could the provision be read more narrowly or more broadly?

### 2. Minority / Dissenting View
- Are there dissenting opinions in relevant case law?
- Does any credible secondary source argue the opposite position?
- Has any regulatory body taken a different stance from the majority view?

### 3. Jurisdictional Risk
- Would this conclusion hold if a different court or regulator reviewed it?
- Are there pending legislative amendments or regulatory guidance that could change the outcome?
- Is there a split between lower and higher courts, or between agencies?

### 4. Factual Sensitivity
- Would the conclusion change if key facts were slightly different?
- What factual assumptions does the conclusion depend on?
- Are there threshold conditions (monetary, temporal, scope) that could shift the analysis?

### 5. Practical Enforcement Risk
- Is the provision actively enforced, or is it largely dormant?
- What is the realistic enforcement probability?
- Are there safe harbors, compliance programs, or mitigating factors?

## Output Format

For each key conclusion in the deliverable, include a **Counter-Analysis** subsection:

```
### [Conclusion]
[Main analysis...]

**Counter-Analysis:**
- **Alternative interpretation:** [description] — [source if available]
- **Risk level:** High / Medium / Low
- **Mitigant:** [what reduces this risk, if anything]
```

## When Counter-Analysis Finds a Material Risk

If the counter-analysis reveals a risk rated **High**:
1. Flag it with `[Material Risk]` inline.
2. Ensure the executive summary / conclusion summary reflects this risk.
3. In Mode A (Executive Brief), include it in the Risk / Priority Ranking.
4. In Mode D (Black-letter), add a dedicated "Risk Considerations" paragraph under the affected article commentary.

## Minimum Requirements

- Mode A: At least 1 counter-argument per key conclusion (brief).
- Mode B: At least 1 counter-argument per jurisdiction comparison point where jurisdictions diverge.
- Mode C: At least 1 dissenting or minority view per enforcement trend.
- Mode D: At least 1 counter-argument per article-level conclusion (detailed).
