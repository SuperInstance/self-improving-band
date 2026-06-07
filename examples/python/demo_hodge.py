#!/usr/bin/env python3
"""
Hodge Decomposition Demo — Musical Disagreement
=================================================
5 agents rate a chord progression. Their disagreements are decomposed into:
  • Gradient (resolvable by parameter nudge)
  • Curl (cyclic, requires iteration)
  • Harmonic (irreducible creative tension — a feature, not a bug)

Uses only the Python standard library.
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ---------------------------------------------------------------------------
# Agent & rating setup
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    name: str
    role: str
    ratings: List[float]  # 1-10 rating per chord in the progression


# A 12-bar blues progression (simplified to 4 chords for clarity)
CHORDS = ["C7", "F7", "C7", "G7"]
N_CHORDS = len(CHORDS)

# Each agent rates each chord 1-10 based on their musical perspective
AGENTS = [
    Agent("Ringo", "drums",
          [6.0, 4.0, 6.5, 7.5]),    # drums like driving chords
    Agent("Paul",  "bass",
          [8.0, 7.0, 8.0, 6.0]),    # bass loves I and IV
    Agent("Wynton", "piano",
          [7.0, 8.0, 7.0, 9.0]),    # piano loves the V turnaround
    Agent("Sonny", "sax",
          [5.0, 6.0, 5.5, 8.5]),    # sax thrives on dominant chords
    Agent("Wes",  "guitar",
          [7.5, 5.5, 7.0, 7.0]),    # guitar likes I
]
N_AGENTS = len(AGENTS)


# ---------------------------------------------------------------------------
# Tiny linear algebra (stdlib)
# ---------------------------------------------------------------------------

def mat_vec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]

def transpose(M):
    return [[M[i][j] for i in range(len(M))] for j in range(len(M[0]))]

def solve_ls(A, b, lam=1e-4):
    AT = transpose(A)
    n = len(AT)
    ATA = [[sum(AT[k][i]*AT[k][j] for k in range(len(AT))) for j in range(n)] for i in range(n)]
    ATb = [sum(AT[k][i]*b[k] for k in range(len(AT))) for i in range(n)]
    for i in range(n):
        ATA[i][i] += lam
    aug = [ATA[i][:] + [ATb[i]] for i in range(n)]
    for col in range(n):
        mx = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[mx] = aug[mx], aug[col]
        for row in range(col+1, n):
            f = aug[row][col] / aug[col][col] if aug[col][col] else 0
            for j in range(col, n+1):
                aug[row][j] -= f * aug[col][j]
    x = [0.0]*n
    for i in range(n-1, -1, -1):
        x[i] = (aug[i][n] - sum(aug[i][j]*x[j] for j in range(i+1,n))) / aug[i][i] if aug[i][i] else 0
    return x


# ---------------------------------------------------------------------------
# Hodge decomposition
# ---------------------------------------------------------------------------

def hodge_decompose(agents: List[Agent]) -> Dict:
    """
    For each chord, compute pairwise rating disagreement,
    decompose into gradient / curl / harmonic.
    Returns per-chord and aggregate results.
    """
    results = {}
    total_g = total_r = total_h = 0.0

    for c_idx in range(N_CHORDS):
        ratings = [a.ratings[c_idx] for a in agents]
        mean = sum(ratings) / len(ratings)

        # Pairwise disagreement on edges of complete graph
        edges = []
        x = []
        for i in range(N_AGENTS):
            for j in range(i+1, N_AGENTS):
                edges.append((i, j))
                x.append(ratings[i] - ratings[j])

        ne = len(edges)
        if ne == 0:
            results[CHORDS[c_idx]] = {"gradient": 0, "curl": 0, "harmonic": 0,
                                       "mean": mean, "verdict": ""}
            continue

        # Incidence matrix B (ne × N_AGENTS)
        B = [[0.0]*N_AGENTS for _ in range(ne)]
        for e, (i, j) in enumerate(edges):
            B[e][i] = 1.0
            B[e][j] = -1.0

        # Solve for scalar potential φ
        phi = solve_ls(B, x)
        G = mat_vec(B, phi)  # gradient on edges

        grad_energy = sum(g*g for g in G)
        mean_x = sum(x)/len(x) if x else 0
        harm_energy = mean_x*mean_x*ne  # harmonic proxy
        total_x = sum(v*v for v in x)
        curl_energy = max(0.0, total_x - grad_energy - harm_energy)

        g_frac = grad_energy / total_x if total_x else 0
        r_frac = curl_energy / total_x if total_x else 0
        h_frac = harm_energy / total_x if total_x else 0

        if g_frac > 0.6:
            verdict = "Mostly gradient → nudge fixes it"
        elif r_frac > 0.4:
            verdict = "Significant curl → iterate to resolve"
        elif h_frac > 0.4:
            verdict = "Creative tension → don't fix, celebrate!"
        else:
            verdict = "Mixed → fix gradient, iterate curl, keep harmonic"

        results[CHORDS[c_idx]] = {
            "gradient": g_frac,
            "curl": r_frac,
            "harmonic": h_frac,
            "mean": mean,
            "verdict": verdict,
        }
        total_g += g_frac
        total_r += r_frac
        total_h += h_frac

    n_c = max(1, N_CHORDS)
    return {
        "per_chord": results,
        "aggregate": {
            "gradient": total_g / n_c,
            "curl": total_r / n_c,
            "harmonic": total_h / n_c,
        }
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 64)
    print("HODGE DECOMPOSITION DEMO — Musical Disagreement")
    print("=" * 64)

    print(f"\nChord progression: {' - '.join(CHORDS)}")
    print(f"Agents: {', '.join(a.name for a in AGENTS)}\n")

    # Show ratings
    header = f"{'Agent':10s} {'Role':8s} " + " ".join(f"{c:>5s}" for c in CHORDS)
    print(header)
    print("-" * len(header))
    for a in AGENTS:
        row = f"{a.name:10s} {a.role:8s} " + " ".join(f"{r:5.1f}" for r in a.ratings)
        print(row)

    # Compute decomposition
    result = hodge_decompose(AGENTS)

    print("\n" + "=" * 64)
    print("PER-CHORD HODGE DECOMPOSITION")
    print("=" * 64)

    for chord, info in result["per_chord"].items():
        print(f"\n  Chord {chord}  (mean rating: {info['mean']:.2f})")
        print(f"    Gradient : {info['gradient']:.1%}  ← fixable by parameter nudge")
        print(f"    Curl     : {info['curl']:.1%}  ← cyclic, needs iteration")
        print(f"    Harmonic : {info['harmonic']:.1%}  ← creative tension (feature!)")
        print(f"    Verdict  : {info['verdict']}")

    agg = result["aggregate"]
    print("\n" + "=" * 64)
    print("AGGREGATE ACROSS ALL CHORDS")
    print("=" * 64)
    print(f"  Gradient : {agg['gradient']:.1%}  — resolvable disagreements")
    print(f"  Curl     : {agg['curl']:.1%}  — cyclic disagreements")
    print(f"  Harmonic : {agg['harmonic']:.1%}  — irreducible creative tension")

    print("\n" + "-" * 64)
    print("INTERPRETATION")
    print("-" * 64)
    if agg["gradient"] > agg["harmonic"] and agg["gradient"] > agg["curl"]:
        print("  The band mostly agrees on direction — small nudges align them.")
        print("  This is a well-rehearsed ensemble with minor tuning differences.")
    elif agg["harmonic"] > agg["gradient"]:
        print("  Strong creative tension — agents genuinely hear the music differently.")
        print("  This produces the most interesting music. Don't 'fix' it.")
    elif agg["curl"] > 0.3:
        print("  Cyclic disagreements — agents are responding to each other in loops.")
        print("  A few rounds of call-response iteration will converge.")
    else:
        print("  Mixed disagreement profile — a healthy, balanced ensemble.")

    print("\n  Key insight: Harmonic disagreements are FEATURES, not bugs.")
    print("  They're why a band sounds like a band, not a synthesizer.\n")


if __name__ == "__main__":
    main()
