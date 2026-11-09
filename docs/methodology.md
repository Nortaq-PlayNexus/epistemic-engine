# Methodology

## Epistemic categories
Known, Unknown, Uncertain, Contradictory, Unsupported.

## Uncertainty distinction
- Statistical uncertainty: derived from data variance/CI (0..1, higher = more uncertain).
- Subjective LM confidence: model self-reported confidence (0..1).
- Combined = 0.6*statistical + 0.4*(1 - lm_confidence). Statistical dominates.

## Contradiction detection
Polarity mismatch on shared entity tokens.

## Missing information
Items without sources, unverified, high uncertainty, unvalidated, unresolved contradictions.

## Experiment prioritization
Sort gaps by severity; expected info gain decays by rank.

## Benchmark
Baseline counts support; uncertainty-aware weights by source reliability and contradiction penalty.
