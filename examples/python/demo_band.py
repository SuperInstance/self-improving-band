#!/usr/bin/env python3
"""
Self-Improving Band — Full Ensemble Demo
==========================================
Simulates a 5-agent band playing a 12-bar blues progression.

Demonstrates:
  • IntentionField contributions per agent
  • RhythmicEnergy budgets with conservation (γ + H = C)
  • t-minus event timing (local clocks, no master)
  • Hodge decomposition when agents disagree on tempo
  • SIA spectral feedback (eigenvalue ranking of agent quality)
  • Structured MIDI event output to stdout

Uses only the Python standard library (no numpy, no external deps).
"""

import json
import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
C_TOTAL = 1.0          # Total ensemble energy budget
TOLERANCE = 0.05       # 5 % conservation tolerance
BPM_CONSENSUS = 120.0  # Target tempo
BEAT_SEC = 60.0 / BPM_CONSENSUS

# 12-bar blues chord roots (I=0, IV=5, V=7 in semitones from tonic)
BLUES_CHORDS = [0, 0, 0, 0, 5, 5, 0, 0, 7, 5, 0, 7]
CHORD_NAMES = {0: "I", 5: "IV", 7: "V"}

# Role energy weights (fraction of C_TOTAL each role claims)
ROLE_WEIGHTS = {"drums": 0.25, "bass": 0.20, "piano": 0.20,
                "sax": 0.15, "guitar": 0.20}

# MIDI-ish helpers
MIDI_CHANNELS = {"drums": 9, "bass": 0, "piano": 1, "sax": 2, "guitar": 3}
GENERAL_MIDI = {"drums": None, "bass": 32, "piano": 0,
                "sax": 65, "guitar": 26}  # program numbers

# ---------------------------------------------------------------------------
# Tiny math helpers (stdlib only)
# ---------------------------------------------------------------------------

def _mat_vec(M: List[List[float]], v: List[float]) -> List[float]:
    """Multiply matrix M (list-of-rows) by vector v."""
    return [sum(M[i][j] * v[j] for j in range(len(M[i]))) for i in range(len(M))]

def _transpose(M: List[List[float]]) -> List[List[float]]:
    n, m = len(M), len(M[0])
    return [[M[i][j] for i in range(n)] for j in range(m)]

def _solve_ls(A: List[List[float]], b: List[float], lam: float = 1e-4) -> List[float]:
    """Least-squares solve (A^T A + λI)^{-1} A^T b using Gaussian elimination."""
    AT = _transpose(A)
    ATA = [[sum(AT[k][i] * AT[k][j] for k in range(len(AT)))
            for j in range(len(AT[0]))] for i in range(len(AT[0]))]
    ATb = [sum(AT[k][i] * b[k] for k in range(len(AT))) for i in range(len(AT[0]))]
    n = len(ATA)
    # regularise
    for i in range(n):
        ATA[i][i] += lam
    # Gauss elimination with partial pivoting
    aug = [ATA[i][:] + [ATb[i]] for i in range(n)]
    for col in range(n):
        max_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[max_row] = aug[max_row], aug[col]
        for row in range(col + 1, n):
            factor = aug[row][col] / aug[col][col] if aug[col][col] else 0
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (aug[i][n] - sum(aug[i][j] * x[j] for j in range(i + 1, n))) / aug[i][i] if aug[i][i] else 0
    return x

def _eigenvalues_2x2(M: List[List[float]]) -> List[float]:
    """Eigenvalues of a 2×2 symmetric matrix."""
    a, b = M[0][0], M[0][1]
    d = M[1][1]
    tr = a + d
    det = a * d - b * b
    disc = max(tr * tr - 4 * det, 0)
    sq = math.sqrt(disc)
    return [(tr + sq) / 2, (tr - sq) / 2]

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MidiEvent:
    tick: int          # beat number (global)
    channel: int
    note: int          # MIDI note number (drums use GM percussion map)
    velocity: int      # 0-127
    duration: float    # in beats

    def to_dict(self) -> dict:
        return {"tick": self.tick, "ch": self.channel,
                "note": self.note, "vel": self.velocity, "dur": self.duration}


@dataclass
class ConservationState:
    gamma: float = 0.0   # kinetic energy (active playing)
    hamiltonian: float = 0.0  # potential energy (tension/preparation)
    constant: float = 0.0  # budget C

    def check(self) -> bool:
        """True if γ + H ≈ C within tolerance."""
        return abs(self.gamma + self.hamiltonian - self.constant) <= TOLERANCE * self.constant

    def total(self) -> float:
        return self.gamma + self.hamiltonian


@dataclass
class TMinusClock:
    """Local countdown timer — no global sync."""
    period: float = BEAT_SEC  # seconds per beat
    phase: float = 0.0
    next_beat: float = 0.0

    def tick(self, dt: float) -> bool:
        self.phase = (self.phase + dt / self.period) % 1.0
        self.next_beat -= dt
        if self.next_beat <= 0:
            self.next_beat = self.predict_next()
            return True  # fire beat
        return False

    def predict_next(self) -> float:
        return self.period + random.gauss(0, 0.003)  # tiny humanisation


@dataclass
class BandAgent:
    name: str
    role: str
    channel: int
    midi_events: List[MidiEvent] = field(default_factory=list)
    conservation: ConservationState = field(default_factory=ConservationState)
    clock: TMinusClock = field(default_factory=TMinusClock)
    intention_weight: float = 1.0   # how strongly this agent pulls the field
    spectral_scores: List[float] = field(default_factory=list)
    local_tempo: float = BPM_CONSENSUS

    def __post_init__(self):
        self.conservation.constant = C_TOTAL * ROLE_WEIGHTS[self.role]
        self.conservation.hamiltonian = self.conservation.constant  # start at rest
        self.conservation.gamma = 0.0
        self.clock.period = 60.0 / self.local_tempo


# ---------------------------------------------------------------------------
# Intention Field
# ---------------------------------------------------------------------------

class IntentionField:
    """Shared potential field giving the band collective direction."""

    def __init__(self):
        self.tempo = BPM_CONSENSUS
        self.key_root = 0        # C
        self.current_bar = 0

    def chord_root(self) -> int:
        return BLUES_CHORDS[self.current_bar % 12]

    def advance(self):
        self.current_bar += 1

    def report(self) -> str:
        root = self.chord_root()
        return f"Bar {self.current_bar + 1:2d} | {CHORD_NAMES[root]:>2s} | key=root+{root}"


# ---------------------------------------------------------------------------
# Hodge Decomposition (1-D scalar disagreement)
# ---------------------------------------------------------------------------

def hodge_1d(agents: List[BandAgent]) -> Dict[str, float]:
    """Decompose tempo disagreement into gradient / curl / harmonic."""
    n = len(agents)
    tempos = [a.local_tempo for a in agents]
    # Pairwise disagreement on edges of a complete graph
    edges: List[Tuple[int, int]] = []
    x: List[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((i, j))
            x.append(tempos[i] - tempos[j])
    ne = len(edges)
    if ne == 0:
        return {"gradient": 0.0, "curl": 0.0, "harmonic": 0.0}
    # Incidence matrix B (ne × n)
    B = [[0.0] * n for _ in range(ne)]
    for e, (i, j) in enumerate(edges):
        B[e][i] = 1.0
        B[e][j] = -1.0
    BT = _transpose(B)
    # Solve for potential φ
    phi = _solve_ls(B, x)
    G = _mat_vec(B, phi)  # gradient component on edges
    grad_energy = sum(g * g for g in G)
    # Harmonic (constant null-space component)
    mean_x = sum(x) / len(x)
    H_energy = mean_x * mean_x * ne  # simplified harmonic proxy
    curl_energy = max(0.0, sum(v * v for v in x) - grad_energy - H_energy)
    total = grad_energy + curl_energy + H_energy
    return {"gradient": grad_energy / total if total else 0,
            "curl": curl_energy / total if total else 0,
            "harmonic": H_energy / total if total else 0}


# ---------------------------------------------------------------------------
# Spectral Feedback — eigenvalue ranking of agent quality
# ---------------------------------------------------------------------------

def spectral_feedback(agents: List[BandAgent]) -> List[Tuple[str, float]]:
    """Rank agents by eigenvalue-based quality score (higher = better)."""
    scores = []
    for a in agents:
        # Build a 2×2 "performance matrix" from recent events
        n_ev = len(a.midi_events)
        if n_ev < 2:
            scores.append((a.name, 0.5))
            continue
        recent = a.midi_events[-min(20, n_ev):]
        avg_vel = sum(e.velocity for e in recent) / len(recent) / 127.0
        vel_var = sum((e.velocity / 127.0 - avg_vel) ** 2 for e in recent) / len(recent)
        dens = len(recent) / max(1, recent[-1].tick - recent[0].tick + 1) if n_ev > 1 else 0
        # Symmetric 2×2 performance matrix
        M = [[avg_vel, vel_var], [vel_var, dens]]
        ev = _eigenvalues_2x2(M)
        quality = ev[0]  # dominant eigenvalue = quality
        scores.append((a.name, quality))
    scores.sort(key=lambda s: s[1], reverse=True)
    return scores


# ---------------------------------------------------------------------------
# Note generation helpers (minimal, role-specific)
# ---------------------------------------------------------------------------

_DRUM_MAP = {1: 36, 2: 38, 3: 42, 4: 46}  # kick, snare, hihat, open-hat
_BLUES_SCALE = [0, 3, 5, 6, 7, 10]         # C blues scale offsets


def _generate_notes(agent: BandAgent, beat: int, chord_root: int,
                    field: IntentionField) -> List[MidiEvent]:
    """Return a list of MidiEvent for one beat."""
    events: List[MidiEvent] = []
    C = agent.conservation.constant
    # Spend some H → γ this beat
    spend = min(agent.conservation.hamiltonian, C * random.uniform(0.15, 0.35))
    agent.conservation.hamiltonian -= spend
    agent.conservation.gamma += spend
    budget_gamma = agent.conservation.gamma

    if agent.role == "drums":
        for sub, note_id in _DRUM_MAP.items():
            if random.random() < 0.6 * budget_gamma / C:
                vel = int(80 + 47 * budget_gamma / C)
                events.append(MidiEvent(beat, agent.channel, note_id, vel, 0.5))

    elif agent.role == "bass":
        root_midi = 36 + chord_root  # low bass
        if random.random() < 0.85:
            offset = random.choice(_BLUES_SCALE)
            vel = int(70 + 50 * budget_gamma / C)
            events.append(MidiEvent(beat, agent.channel, root_midi + offset, vel, 1.0))

    elif agent.role == "piano":
        for offset in random.sample(_BLUES_SCALE, min(3, len(_BLUES_SCALE))):
            note = 60 + chord_root + offset
            vel = int(50 + 60 * budget_gamma / C)
            events.append(MidiEvent(beat, agent.channel, note, vel, 0.5))

    elif agent.role == "sax":
        if random.random() < 0.6:
            offset = random.choice(_BLUES_SCALE)
            note = 54 + chord_root + offset
            vel = int(60 + 60 * budget_gamma / C)
            events.append(MidiEvent(beat, agent.channel, note, vel, 1.0))

    elif agent.role == "guitar":
        if random.random() < 0.75:
            root_midi = 40 + chord_root
            vel = int(60 + 55 * budget_gamma / C)
            events.append(MidiEvent(beat, agent.channel, root_midi, vel, 0.5))
            if random.random() < 0.4:
                events.append(MidiEvent(beat, agent.channel, root_midi + 7, vel - 10, 0.5))

    # After generating, recover some γ → H (rest)
    recovery = agent.conservation.gamma * random.uniform(0.1, 0.3)
    agent.conservation.gamma -= recovery
    agent.conservation.hamiltonian += recovery

    return events


# ---------------------------------------------------------------------------
# Conservation enforcement
# ---------------------------------------------------------------------------

def enforce_conservation(agents: List[BandAgent]) -> List[str]:
    """Check γ+H=C for every agent; return violation messages."""
    msgs = []
    ensemble_total = sum(a.conservation.total() for a in agents)
    if abs(ensemble_total - C_TOTAL) > TOLERANCE:
        # redistribute proportionally
        scale = C_TOTAL / ensemble_total if ensemble_total else 1
        for a in agents:
            a.conservation.gamma *= scale
            a.conservation.hamiltonian = a.conservation.constant - a.conservation.gamma
            a.conservation.hamiltonian = max(0, a.conservation.hamiltonian)
        msgs.append(f"  ⚠ Ensemble budget drift {ensemble_total:.3f} → corrected to {C_TOTAL}")
    for a in agents:
        if not a.conservation.check():
            # gentle nudge: split budget 50/50
            a.conservation.gamma = a.conservation.constant * 0.5
            a.conservation.hamiltonian = a.conservation.constant * 0.5
            msgs.append(f"  ⚠ {a.name}: γ+H={a.conservation.total():.3f} ≠ C={a.conservation.constant:.3f} → nudged")
    return msgs


# ---------------------------------------------------------------------------
# Main simulation
# ---------------------------------------------------------------------------

def main():
    random.seed(42)
    roles = ["drums", "bass", "piano", "sax", "guitar"]
    names = ["Ringo", "Paul", "Wynton", "Sonny", "Wes"]
    agents = [BandAgent(name=n, role=r, channel=MIDI_CHANNELS[r]) for n, r in zip(names, roles)]

    # Introduce slight tempo disagreements (so Hodge has something to decompose)
    agents[0].local_tempo = 122.0
    agents[1].local_tempo = 119.0
    agents[2].local_tempo = 120.0
    agents[3].local_tempo = 121.5
    agents[4].local_tempo = 117.5
    for a in agents:
        a.clock.period = 60.0 / a.local_tempo

    field = IntentionField()
    all_events: List[MidiEvent] = []
    total_beats = 12 * 4  # 12 bars × 4 beats

    print("=" * 72)
    print("SELF-IMPROVING BAND — 12-Bar Blues Simulation")
    print("=" * 72)

    # --- Hodge decomposition of tempo disagreement ---
    hodge = hodge_1d(agents)
    print(f"\n[Hodge decomposition of tempo disagreement]")
    for comp, frac in hodge.items():
        print(f"  {comp:10s}: {frac:.1%}")
    if hodge["gradient"] > 0.5:
        print("  → Mostly gradient. Direct tempo nudge will fix it.")
    if hodge["harmonic"] > 0.3:
        print("  → Significant harmonic tension (creative tempo feel).")
    # Apply gradient correction: nudge toward consensus
    for a in agents:
        correction = 0.3 * (BPM_CONSENSUS - a.local_tempo)
        a.local_tempo += correction
        a.clock.period = 60.0 / a.local_tempo

    print(f"\n[Tempo after gradient correction]")
    for a in agents:
        print(f"  {a.name:8s} ({a.role:7s}): {a.local_tempo:.1f} BPM")

    # --- Main performance loop ---
    print(f"\n[Performance — {total_beats} beats, 12-bar blues]")
    print("-" * 72)

    global_beat = 0
    for bar in range(12):
        field.current_bar = bar
        chord_root = field.chord_root()
        bar_label = field.report()
        bar_events: List[MidiEvent] = []
        for beat_in_bar in range(4):
            for agent in agents:
                events = _generate_notes(agent, global_beat, chord_root, field)
                agent.midi_events.extend(events)
                bar_events.extend(events)
            global_beat += 1

        # Conservation check every bar
        violations = enforce_conservation(agents)
        bar_energy = {a.name: f"γ={a.conservation.gamma:.2f} H={a.conservation.hamiltonian:.2f}"
                      for a in agents}
        print(f"\n{bar_label}")
        for a in agents:
            ok = "✓" if a.conservation.check() else "✗"
            print(f"  {a.name:8s}: {bar_energy[a.name]}  C={a.conservation.constant:.2f} {ok}")
        for v in violations:
            print(v)

        all_events.extend(bar_events)

    # --- Spectral feedback ---
    print("\n" + "=" * 72)
    print("[SIA Spectral Feedback — Agent Quality Ranking]")
    print("=" * 72)
    ranking = spectral_feedback(agents)
    for rank, (name, score) in enumerate(ranking, 1):
        stars = "★" * int(score * 5) + "☆" * (5 - int(score * 5))
        print(f"  #{rank} {name:8s}: quality={score:.3f}  {stars}")

    # --- Structured MIDI output ---
    print(f"\n[MIDI Events — {len(all_events)} total events]")
    print("-" * 72)
    for ev in all_events[:30]:  # first 30 for brevity
        print(f"  beat={ev.tick:3d} ch={ev.channel} note={ev.note:3d} "
              f"vel={ev.velocity:3d} dur={ev.duration:.1f}")
    if len(all_events) > 30:
        print(f"  ... ({len(all_events) - 30} more events)")
    # Full JSON dump
    json_path = "demo_band_output.json"
    with open(json_path, "w") as f:
        json.dump([e.to_dict() for e in all_events], f, indent=2)
    print(f"\nFull MIDI event JSON → {json_path}")


if __name__ == "__main__":
    main()
