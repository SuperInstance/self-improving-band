#!/usr/bin/env python3
"""
Conservation Law Demo — γ + H = C
===================================
Shows energy conservation enforcement in a musical ensemble.

Demonstrates:
  • Agents start with equal energy budgets
  • γ ↔ H exchange during performance (kinetic ↔ potential)
  • Ensemble-wide Σ(γ+H) = C_total enforcement
  • Violation detection and multi-level recovery

Uses only the Python standard library.
"""

import random
import math
from dataclasses import dataclass
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
N_AGENTS = 5
C_TOTAL = 1.0
TOLERANCE = 0.05  # 5 % band

ROLE_BUDGETS = {
    "drums": 0.25,
    "bass": 0.20,
    "piano": 0.20,
    "sax": 0.15,
    "guitar": 0.20,
}

ROLES = list(ROLE_BUDGETS.keys())


@dataclass
class Agent:
    name: str
    role: str
    gamma: float = 0.0         # kinetic (active playing)
    hamiltonian: float = 0.0   # potential (tension/preparation)
    budget: float = 0.0        # C_i — this agent's energy budget

    def total(self) -> float:
        return self.gamma + self.hamiltonian

    def check(self) -> bool:
        return abs(self.total() - self.budget) <= TOLERANCE * self.budget


def make_agents() -> List[Agent]:
    agents = []
    for i, role in enumerate(ROLES):
        b = C_TOTAL * ROLE_BUDGETS[role]
        agents.append(Agent(name=f"Agent_{i}", role=role,
                            gamma=0.0, hamiltonian=b, budget=b))
    return agents


def print_state(agents: List[Agent], label: str):
    print(f"\n── {label} ──")
    for a in agents:
        ok = "✓" if a.check() else "✗"
        print(f"  {a.name:10s} ({a.role:7s}): "
              f"γ={a.gamma:.4f}  H={a.hamiltonian:.4f}  "
              f"γ+H={a.total():.4f}  C={a.budget:.4f}  {ok}")
    ensemble = sum(a.total() for a in agents)
    ok_all = "✓" if abs(ensemble - C_TOTAL) <= TOLERANCE else "✗"
    print(f"  {'Ensemble':10s}          "
          f"Σ(γ+H)={ensemble:.4f}  C_total={C_TOTAL:.4f}  {ok_all}")


# ---------------------------------------------------------------------------
# Simulation steps
# ---------------------------------------------------------------------------

def step_perform(agents: List[Agent], solo_idx: int):
    """Soloist spends H → γ; others rest (γ → H)."""
    solo = agents[solo_idx]
    spend = solo.hamiltonian * random.uniform(0.4, 0.7)
    solo.hamiltonian -= spend
    solo.gamma += spend

    for i, a in enumerate(agents):
        if i == solo_idx:
            continue
        # accompanists recover: shift γ → H
        recover = a.gamma * random.uniform(0.1, 0.3)
        a.gamma -= recover
        a.hamiltonian += recover


def check_violations(agents: List[Agent]) -> List[str]:
    msgs = []
    for a in agents:
        if not a.check():
            msgs.append(f"  VIOLATION: {a.name} γ+H={a.total():.4f} ≠ C={a.budget:.4f}")
    ensemble = sum(a.total() for a in agents)
    if abs(ensemble - C_TOTAL) > TOLERANCE:
        msgs.append(f"  ENSEMBLE VIOLATION: Σ={ensemble:.4f} ≠ C_total={C_TOTAL:.4f}")
    return msgs


def gentle_nudge(agents: List[Agent]):
    """Level 1: suggest 10 % correction."""
    for a in agents:
        dev = a.total() - a.budget
        if abs(dev) > TOLERANCE * a.budget:
            correction = -dev * 0.1
            a.gamma += correction * 0.5
            a.hamiltonian += correction * 0.5


def mandatory_rebalance(agents: List[Agent]):
    """Level 2: force each agent back to its budget."""
    for a in agents:
        total = a.total()
        if total > a.budget:
            # Over budget: scale gamma down, keep H, trim excess
            excess = total - a.budget
            a.hamiltonian = max(0.0, a.hamiltonian - excess)
            excess2 = a.total() - a.budget
            if excess2 > 0:
                a.gamma = max(0.0, a.gamma - excess2)
        elif total < a.budget * (1 - TOLERANCE):
            # Under budget: add to H
            a.hamiltonian += a.budget - total
    # Final ensemble scale
    ensemble = sum(a.total() for a in agents)
    if ensemble > 0 and abs(ensemble - C_TOTAL) > TOLERANCE:
        scale = C_TOTAL / ensemble
        for a in agents:
            a.gamma *= scale
            a.hamiltonian = max(0.0, a.budget - a.gamma)


def emergency_fix(agents: List[Agent], idx: int):
    """Level 3: silence an agent, reclaim its excess to restore ensemble."""
    a = agents[idx]
    a.gamma = 0.0
    a.hamiltonian = a.budget  # back within budget
    # Now force all agents within their individual budgets
    for ag in agents:
        t = ag.total()
        if t > ag.budget:
            excess = t - ag.budget
            ag.hamiltonian = max(0.0, ag.hamiltonian - excess)
            excess2 = ag.total() - ag.budget
            if excess2 > 0:
                ag.gamma = max(0.0, ag.gamma - excess2)
    # Final ensemble rescale
    ensemble = sum(a.total() for a in agents)
    if ensemble > 0 and abs(ensemble - C_TOTAL) > TOLERANCE:
        scale = C_TOTAL / ensemble
        for ag in agents:
            ag.gamma *= scale
            ag.hamiltonian = max(0.0, ag.budget - ag.gamma)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    random.seed(99)
    agents = make_agents()

    print("=" * 60)
    print("CONSERVATION LAW DEMO — γ + H = C")
    print("=" * 60)

    print_state(agents, "Initial state (all energy in H, nobody playing)")

    # --- Beat 1-4: drums start playing ---
    for _ in range(4):
        step_perform(agents, solo_idx=0)
    print_state(agents, "After 4 beats — drums playing (solo γ ↑)")

    violations = check_violations(agents)
    for v in violations:
        print(v)

    # --- Beat 5-8: bass and piano join, sax stays out ---
    for beat in range(5, 9):
        step_perform(agents, 0)  # drums
        step_perform(agents, 1)  # bass
        step_perform(agents, 2)  # piano
    print_state(agents, "After 8 beats — drums + bass + piano active")

    # --- Force a violation: sax suddenly plays very loud ---
    sax = agents[3]
    sax.hamiltonian = 0.0
    sax.gamma = 0.40  # exceeds budget of 0.15
    print_state(agents, "VIOLATION INJECTED — sax overplaying (γ=0.40, C=0.15)")

    violations = check_violations(agents)
    for v in violations:
        print(v)

    # --- Recovery level 1: gentle nudge ---
    print("\n→ Recovery Level 1: Gentle nudge (10 % correction)")
    gentle_nudge(agents)
    print_state(agents, "After gentle nudge")
    violations = check_violations(agents)
    still_violating = len(violations)
    for v in violations:
        print(v)

    # --- Recovery level 2: mandatory rebalance ---
    if still_violating > 0:
        print("\n→ Recovery Level 2: Mandatory rebalance")
        mandatory_rebalance(agents)
        print_state(agents, "After mandatory rebalance")
        violations = check_violations(agents)
        for v in violations:
            print(v)

    # --- Recovery level 3: emergency (if still broken) ---
    if len(violations) > 0:
        print("\n→ Recovery Level 3: Emergency — silence sax, redistribute")
        emergency_fix(agents, 3)
        print_state(agents, "After emergency fix")
        violations = check_violations(agents)
        for v in violations:
            print(v)

    # --- Final summary ---
    print("\n" + "=" * 60)
    print("FINAL STATE")
    print("=" * 60)
    print_state(agents, "Conservation restored")
    print(f"\n  Agents checked: {len(agents)}")
    print(f"  All within bounds: {all(a.check() for a in agents)}")
    ensemble = sum(a.total() for a in agents)
    print(f"  Ensemble Σ(γ+H)={ensemble:.4f}  C_total={C_TOTAL:.4f}")
    print(f"  Conservation held: {abs(ensemble - C_TOTAL) <= TOLERANCE}")


if __name__ == "__main__":
    main()
