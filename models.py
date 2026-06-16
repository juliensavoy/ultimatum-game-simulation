from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import numpy as np

# --- Shared game parameters (adjust these when presenting to teammates) ---

TOTAL_PIE = 100.0  # Total surplus split between players A and B
DELTA = 0.8        # Per-round discount factor (pie shrinks by 20% each rejection)
MAX_ROUNDS = 3     # Finite horizon: A proposes in odd rounds, B in even rounds


@dataclass
class TrialResult:
    """Outcome of a single simulated game."""

    round_ended: int
    accepted: bool
    offer_to_responder: float
    pie_at_round: float


def _pie_at_round(round_num: int, total_pie: float = TOTAL_PIE, delta: float = DELTA) -> float:
    """Remaining pie at the start of a given round (after prior rejections)."""
    return total_pie * (delta ** (round_num - 1))


def simulate_classical(
    max_rounds: int = MAX_ROUNDS,
    total_pie: float = TOTAL_PIE,
    delta: float = DELTA,
) -> TrialResult:
    """
    Classical Rubinstein solution via backward induction.

    Player A opens in Round 1. In equilibrium the first offer is accepted immediately,
    so every trial ends in Round 1 with acceptance.
    """
    # At the final round the proposer keeps the entire (discounted) pie.
    responder_minimum = 0.0

    # Walk backward: each responder must receive at least their discounted
    # continuation value from rejecting and becoming proposer next round.
    for round_num in range(max_rounds - 1, 0, -1):
        pie_next = _pie_at_round(round_num + 1, total_pie, delta)
        proposer_payoff_if_rejected = pie_next - responder_minimum
        responder_minimum = delta * proposer_payoff_if_rejected

    offer_to_responder = responder_minimum
    return TrialResult(
        round_ended=1,
        accepted=True,
        offer_to_responder=offer_to_responder,
        pie_at_round=total_pie,
    )


def simulate_behavioral(
    max_rounds: int = MAX_ROUNDS,
    total_pie: float = TOTAL_PIE,
    delta: float = DELTA,
    acceptance_threshold: float = 0.30,
    initial_offer_fraction: float = 0.25,
    concession_per_round: float = 0.05,
) -> TrialResult:
    """
    Behavioral model with fixed human-like thresholds.

    Parameters
    ----------
    acceptance_threshold : float
        Minimum share of the *current* pie the responder requires (e.g. 0.30 = 30%).
    initial_offer_fraction : float
        Opening offer as a fraction of the current pie (often below the threshold).
    concession_per_round : float
        How much the proposer increases their offer after each rejection.
    """
    for round_num in range(1, max_rounds + 1):
        pie = _pie_at_round(round_num, total_pie, delta)
        offer_fraction = initial_offer_fraction + (round_num - 1) * concession_per_round
        offer = offer_fraction * pie

        if offer_fraction >= acceptance_threshold:
            return TrialResult(
                round_ended=round_num,
                accepted=True,
                offer_to_responder=offer,
                pie_at_round=pie,
            )

    # Final round reached without agreement (responder never satisfied).
    pie = _pie_at_round(max_rounds, total_pie, delta)
    final_fraction = initial_offer_fraction + (max_rounds - 1) * concession_per_round
    return TrialResult(
        round_ended=max_rounds,
        accepted=False,
        offer_to_responder=final_fraction * pie,
        pie_at_round=pie,
    )


def simulate_chemical(
    max_rounds: int = MAX_ROUNDS,
    total_pie: float = TOTAL_PIE,
    delta: float = DELTA,
    rt: float = 1.0,
    epsilon: float = 2.0,
    gamma_y: float = 5.0,
    gamma_n: float = 2.0,
    offer_fraction: float = 0.40,
    rng: Optional[random.Random] = None,
) -> TrialResult:
    """
    Chemical Game Theory (CGT): probabilistic acceptance from Boltzmann weights.

    Parameters
    ----------
    rt : float
        Thermal noise / temperature (higher => more random decisions).
    epsilon : float
        Intrinsic cooperative bias (stabilizes "yes" when offers are reasonable).
    gamma_y, gamma_n : float
        Gains for accepting vs. rejecting, scaled by offer share m and (1 - m).
    offer_fraction : float
        Share m of the current pie offered to the responder each round.
    """
    rng = rng or random

    for round_num in range(1, max_rounds + 1):
        pie = _pie_at_round(round_num, total_pie, delta)
        m = offer_fraction  # Responder's share of the current pie

        # Free-energy terms (lower ΔG => more favorable state).
        dg_yes = -gamma_y * m - epsilon
        dg_no = -gamma_n * (1.0 - m)

        # Boltzmann probabilities: P(state) ∝ exp(-ΔG / RT)
        exp_yes = np.exp(-dg_yes / rt)
        exp_no = np.exp(-dg_no / rt)
        p_accept = exp_yes / (exp_yes + exp_no)

        accepted = rng.random() < p_accept
        offer = m * pie

        if accepted:
            return TrialResult(
                round_ended=round_num,
                accepted=True,
                offer_to_responder=offer,
                pie_at_round=pie,
            )

    pie = _pie_at_round(max_rounds, total_pie, delta)
    return TrialResult(
        round_ended=max_rounds,
        accepted=False,
        offer_to_responder=offer_fraction * pie,
        pie_at_round=pie,
    )
