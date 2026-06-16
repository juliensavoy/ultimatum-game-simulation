# Rubinstein Ultimatum Game Simulation

A small Python project comparing three approaches to the **Rubinstein alternating-offers ultimatum game**:

1. **Classical** — rational backward induction (Rubinstein-style equilibrium)
2. **Behavioral** — fixed fairness thresholds and concessions
3. **Chemical Game Theory (CGT)** — probabilistic acceptance via Boltzmann weights

The game runs for up to 3 rounds. After each rejection, the pie shrinks by the discount factor `DELTA` (default 0.8).

## Project structure

| File | Purpose |
|------|---------|
| `models.py` | Core simulation engines (`simulate_classical`, `simulate_behavioral`, `simulate_chemical`) and shared parameters |
| `simulation.py` | Runs 1,000 Monte Carlo trials per model and prints summary statistics |
| `app.py` | Plots a grouped bar chart comparing ending-round distributions |
| `requirements.txt` | Python dependencies (`numpy`, `matplotlib`) |

## Setup

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

## How to run

**Print simulation results** (average rounds, acceptance rate, round distribution):

```bash
python simulation.py
```

**Show the comparison chart**:

```bash
python app.py
```

The chart opens in a Matplotlib window. To save it instead, pass a path when calling `plot_round_distributions(save_path="results.png")` from Python.

## The three models (short version)

### Classical (`simulate_classical`)

Uses backward induction on a finite 3-round game. Under perfect rationality, the equilibrium offer is accepted immediately — every trial ends in **Round 1**.

Key parameters: `TOTAL_PIE`, `DELTA`, `MAX_ROUNDS` (top of `models.py`).

### Behavioral (`simulate_behavioral`)

A simple stand-in for non-rational play: the responder has a minimum acceptable share, and the proposer starts low and increases the offer after each rejection.

Key parameters:

- `acceptance_threshold` — minimum share the responder requires (e.g. 0.30 = 30%)
- `initial_offer_fraction` — opening offer
- `concession_per_round` — how much the proposer raises the offer each round

This model is **deterministic** with the default parameters (every trial ends in the same round). Monte Carlo mainly matters for the CGT model unless behavioral is extended with randomness.

### Chemical / CGT (`simulate_chemical`)

Acceptance is **probabilistic**. Each round computes free-energy terms ΔG for accept vs. reject, then draws accept/reject from a Boltzmann distribution.

Key parameters:

- `RT` — noise / temperature (higher → more random)
- `epsilon` — cooperative bias
- `gamma_y`, `gamma_n` — weights on accepting vs. rejecting
- `offer_fraction` — share of the pie offered each round

## Tuning parameters

Edit the defaults at the top of `models.py`, or pass keyword arguments when calling the simulate functions from your own scripts. Comments in `models.py` describe each parameter.

## Next steps (for the team)

- Pick empirical targets (e.g. share of games ending in Round 1 vs. 2 vs. 3)
- Tune `DELTA` in the classical model to match **splits**; tune behavioral/CGT parameters to match **round distributions**
- Consider making the behavioral model probabilistic for richer Monte Carlo output
