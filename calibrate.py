"""
Calibrate CGT (simulate_chemical) parameters against two targets:

  1. CLASSICAL fit — CGT reproduces the rational equilibrium:
       game always ends in Round 1, acceptance rate ~100%.
       Shows that CGT can recover the theoretical prediction.

  2. EMPIRICAL fit — CGT reproduces Ochs & Roth (1989) lab data:
       3-period symmetric discount-factor cells (Cells 5+7, n=190):
         Round 1: 86.8%  |  Round 2: 8.4%  |  Round 3: 4.7%  |  acc: 97.4%
       Shows that CGT can match real human bargaining behaviour.

The two best-fit parameter sets are printed at the end and can be copied
directly into models.py (CGT_CLASSICAL_PARAMS / CGT_EMPIRICAL_PARAMS).
"""

from __future__ import annotations

import itertools
from collections import Counter
from functools import partial

from models import simulate_chemical

# ── Calibration targets ────────────────────────────────────────────────────

TARGETS = {
    "classical": {
        "label": "Classical GT (Round 1 always)",
        "round_dist": {1: 1.0, 2: 0.0, 3: 0.0},
        "acceptance_rate": 1.0,
    },
    "empirical": {
        "label": "Ochs & Roth (1989) lab data",
        "round_dist": {1: 0.868, 2: 0.084, 3: 0.047},
        "acceptance_rate": 0.974,
    },
}

N_TRIALS = 3_000
MAX_ROUNDS = 3

# ── Parameter grid ─────────────────────────────────────────────────────────

GRID = {
    "rt":             [0.1, 0.3, 0.5, 0.8, 1.0, 1.5],
    "epsilon":        [0.5, 1.0, 2.0, 3.0, 5.0],
    "gamma_y":        [3.0, 5.0, 7.0, 9.0],
    "gamma_n":        [1.0, 2.0, 3.0, 4.0],
    "offer_fraction": [0.40, 0.43, 0.45],
    "delta":          [0.4, 0.6, 0.8],
}


# ── Core helpers ───────────────────────────────────────────────────────────

def _score(rt, epsilon, gamma_y, gamma_n, offer_fraction, delta, target):
    results = [
        simulate_chemical(
            max_rounds=MAX_ROUNDS,
            delta=delta,
            rt=rt,
            epsilon=epsilon,
            gamma_y=gamma_y,
            gamma_n=gamma_n,
            offer_fraction=offer_fraction,
        )
        for _ in range(N_TRIALS)
    ]
    counts = Counter(r.round_ended for r in results)
    sim_dist = {r: counts[r] / N_TRIALS for r in range(1, MAX_ROUNDS + 1)}
    sim_acc = sum(1 for r in results if r.accepted) / N_TRIALS

    mse = sum(
        (sim_dist.get(r, 0.0) - target["round_dist"].get(r, 0.0)) ** 2
        for r in range(1, MAX_ROUNDS + 1)
    )
    mse += (sim_acc - target["acceptance_rate"]) ** 2
    return mse, sim_dist, sim_acc


def _search(target_key: str) -> list:
    target = TARGETS[target_key]
    combos = list(itertools.product(*GRID.values()))
    keys = list(GRID.keys())

    print(f"\n{'─'*60}")
    print(f"Target: {target['label']}")
    print(f"  R1={target['round_dist'][1]:.1%}  "
          f"R2={target['round_dist'][2]:.1%}  "
          f"R3={target['round_dist'][3]:.1%}  "
          f"acc={target['acceptance_rate']:.1%}")
    print(f"Grid: {len(combos)} combinations × {N_TRIALS} trials")

    records = []
    for i, vals in enumerate(combos):
        params = dict(zip(keys, vals))
        mse, sim_dist, sim_acc = _score(**params, target=target)
        records.append((mse, params, sim_dist, sim_acc))
        if (i + 1) % 400 == 0:
            print(f"  {i + 1}/{len(combos)} evaluated …")

    records.sort(key=lambda x: x[0])
    return records


def _report(records: list, top_n: int = 3) -> dict:
    print(f"\nTop {top_n} fits:")
    for rank, (mse, params, sim_dist, sim_acc) in enumerate(records[:top_n], 1):
        print(f"  #{rank}  MSE={mse:.5f}  →  "
              f"R1={sim_dist.get(1,0):.1%}  "
              f"R2={sim_dist.get(2,0):.1%}  "
              f"R3={sim_dist.get(3,0):.1%}  "
              f"acc={sim_acc:.1%}")
        print(f"       {params}")
    return records[0][1]  # return best params dict


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    best_classical = _report(_search("classical"), top_n=3)
    best_empirical = _report(_search("empirical"), top_n=3)

    print(f"\n{'='*60}")
    print("Copy these into models.py:")
    print(f"{'='*60}")
    print(f"\nCGT_CLASSICAL_PARAMS = {best_classical}")
    print(f"\nCGT_EMPIRICAL_PARAMS = {best_empirical}")
