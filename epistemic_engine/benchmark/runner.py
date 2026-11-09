"""Benchmark: uncertainty-aware vs baseline hypothesis selection."""
import random
from typing import List, Dict


def simulate_scenario(n_items=20, seed=42):
    rng = random.Random(seed)
    # ground truth best hypothesis index
    truth = rng.randrange(3)
    hypotheses = [{"id": i, "score": 0.5, "uncertainty": 1.0} for i in range(3)]
    items = []
    for i in range(n_items):
        # each item supports a hypothesis; noise
        supports = rng.randrange(3)
        reliability = rng.uniform(0.3, 0.95)
        contradictory = rng.random() < 0.15
        items.append({"supports": supports, "reliability": reliability, "contradictory": contradictory})
    return hypotheses, items, truth


def baseline_select(hypotheses, items):
    # ignores uncertainty, counts support
    scores = [0.0] * len(hypotheses)
    for it in items:
        scores[it["supports"]] += 1.0
    return max(range(len(scores)), key=lambda i: scores[i])


def uncertainty_aware_select(hypotheses, items):
    scores = [0.0] * len(hypotheses)
    for it in items:
        w = it["reliability"]
        if it["contradictory"]:
            w *= 0.3
        scores[it["supports"]] += w
        # penalize uncertainty
    # add penalty for high uncertainty items count
    return max(range(len(scores)), key=lambda i: scores[i])


def run_benchmark(seeds=50):
    base_wins = 0
    ua_wins = 0
    base_eff = 0.0
    ua_eff = 0.0
    for s in range(seeds):
        hyps, items, truth = simulate_scenario(seed=s)
        b = baseline_select(hyps, items)
        u = uncertainty_aware_select(hyps, items)
        if b == truth:
            base_wins += 1
        if u == truth:
            ua_wins += 1
        # efficiency: fewer experiments to reach correct = better; proxy via score margin
        base_eff += 1.0 if b == truth else 0.0
        ua_eff += 1.0 if u == truth else 0.0
    return {
        "seeds": seeds,
        "baseline_accuracy": round(base_wins / seeds, 3),
        "uncertainty_aware_accuracy": round(ua_wins / seeds, 3),
        "improvement": round((ua_wins - base_wins) / seeds, 3),
    }
