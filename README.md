# 🎵 The Self-Improving Band

> *5 AI agents that make music together, with mathematical guarantees that they get better over time.*

**The Self-Improving Band** is an autonomous musical ensemble — five independent AI agents that self-align, self-improve, and swing. There is no conductor, no master clock, no central score. Each agent is a full musician: it has its own identity, its own sense of time, and its own harmonic vocabulary. The music emerges from mathematical constraints — conservation laws, spectral feedback, and Hodge decomposition — not from a script.

This is the simplest non-trivial system that exercises all 10 pillars of the [SuperInstance AGI thesis](AGI_VISION.md): constraint-aware systems, self-improvement, temporal coordination, musical mathematics, spectral methods, topology, distributed cognition, conservation, voice interface, and compilation. If five agents can self-organize into a functioning band with provable improvement guarantees, the architecture generalizes far beyond music.

---

## Why Music?

A jazz band is the most sophisticated distributed system humans have ever built — and we mean that mathematically, not metaphorically.

| Property | Jazz Band | Distributed System |
|---|---|---|
| No central coordinator | No conductor | No leader / master |
| Real-time constraints | Tempo, groove | Latency bounds, deadlines |
| Self-healing | Missed beat? Others cover | Node failure? Peers compensate |
| Emergent behavior | Music > sum of parts | Correctness from local rules |
| Continuous improvement | Musicians get better by playing | Agents improve via spectral feedback |

Music is the ideal AGI proof-of-concept because it is **falsifiable**. You can hear when the band is together. You can measure when it improves. The output is concrete — MIDI events with timestamps, velocities, and provenance chains — not a philosophical argument about intelligence. Either five independent agents converge on a shared tempo, negotiate a key, distribute energy, and produce music that gets measurably better over time, or they don't. The math either works or it doesn't.

Every concept here — conservation laws, spectral decomposition, t-minus timing, Hodge analysis — is domain-independent. Music is the test case. Everything else is the application.

---

## The 7-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 7: MUSICAL OUTPUT                    │
│            MIDI events, audio, provenance chains             │
│                     (band-midi, band-protocol)               │
├─────────────────────────────────────────────────────────────┤
│                    Layer 6: INTENTION FIELD                   │
│          Collective direction without a leader               │
│                   (intention-field, hodge-music)             │
├─────────────────────────────────────────────────────────────┤
│                  Layer 5: HODGE DECOMPOSITION                 │
│       Gradient (fix) · Curl (iterate) · Harmonic (celebrate) │
│                       (hodge-music)                          │
├─────────────────────────────────────────────────────────────┤
│                    Layer 4: TEMPORAL FLOW                     │
│           t-minus clocks: predict, don't sync                │
│                      (band-tminus)                           │
├─────────────────────────────────────────────────────────────┤
│                  Layer 3: CATEGORY THEORY                    │
│         PLR groups · Tropical harmony · Constraint algebra   │
│            (harmonic-plr, tropical-harmony)                  │
├─────────────────────────────────────────────────────────────┤
│                    Layer 2: SPECTRAL IDENTITY                 │
│       Eigenvalue profiles · Banach convergence · SIA²       │
│              (band-agent, conservation-rhythm)               │
├─────────────────────────────────────────────────────────────┤
│                Layer 1: CONSERVATION LAWS                     │
│                  γ + H = C (the physics)                     │
│                (conservation-rhythm, band-protocol)          │
└─────────────────────────────────────────────────────────────┘
```

Each layer builds on the one below. Conservation laws (Layer 1) are the foundation — the physics that makes everything else stable. Spectral identity (Layer 2) gives each agent a mathematical "personality." Category theory (Layer 3) provides the harmonic language. Temporal flow (Layer 4) keeps everyone on tempo without a shared clock. Hodge decomposition (Layer 5) separates fixable disagreements from creative tension. The intention field (Layer 6) gives the band collective direction. And Layer 7 is the music itself.

For the full architecture reference with sequence diagrams, state machines, and data flow, see [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/SuperInstance/self-improving-band.git
cd self-improving-band

# Run the full ensemble demo (Python, no dependencies)
python3 examples/python/demo_band.py
```

**Expected output:**

```
========================================================================
SELF-IMPROVING BAND — 12-Bar Blues Simulation
========================================================================

[Hodge decomposition of tempo disagreement]
  gradient  : 82.3%
  curl      : 12.1%
  harmonic  : 5.6%
  → Mostly gradient. Direct tempo nudge will fix it.

[Tempo after gradient correction]
  Ringo    (drums  ): 120.6 BPM
  Paul     (bass   ): 119.7 BPM
  Wynton   (piano  ): 120.0 BPM
  Sonny    (sax    ): 120.5 BPM
  Wes      (guitar ): 119.3 BPM

[Performance — 48 beats, 12-bar blues]
--------------------------------------------------------------------

 Bar  1 |  I | key=root+0
  Ringo   : γ=0.07 H=0.18  C=0.25 ✓
  Paul    : γ=0.06 H=0.14  C=0.20 ✓
  ...

[SIA Spectral Feedback — Agent Quality Ranking]
  #1 Wynton  : quality=0.843  ★★★★☆
  #2 Paul     : quality=0.791  ★★★☆☆
  ...

[MIDI Events — 147 total events]
  beat=  0 ch=9 note= 36 vel=100 dur=0.5
  beat=  0 ch=0 note= 36 vel= 94 dur=1.0
  ...

Full MIDI event JSON → demo_band_output.json
```

All three demos use **only the Python standard library** — no numpy, no external dependencies:

```bash
python3 examples/python/demo_band.py           # Full 5-agent ensemble
python3 examples/python/demo_conservation.py   # γ + H = C deep dive
python3 examples/python/demo_hodge.py          # Musical disagreement decomposition
```

---

## The 10 Band Crates

| Crate | What It Does |
|---|---|
| [`band-protocol`](examples/BAND_API_REFERENCE.md#band-protocol) | Wire format for all inter-agent messages — MIDI events, conservation metadata, provenance tags |
| [`band-agent`](examples/BAND_API_REFERENCE.md#band-agent) | A single autonomous instrument: identity + clock + conservation + spectral state + MIDI I/O |
| [`band-ensemble`](examples/BAND_API_REFERENCE.md#band-ensemble) | Orchestrates the full band: spawning, routing, alignment, and the self-improvement cycle |
| [`band-midi`](examples/BAND_API_REFERENCE.md#band-midi) | MIDI event representation, rendering with swing/humanization, and raw byte encoding |
| [`band-tminus`](examples/BAND_API_REFERENCE.md#band-tminus) | Local countdown clocks — agents predict when to play instead of syncing to a master |
| [`harmonic-plr`](examples/BAND_API_REFERENCE.md#harmonic-plr) | PLR group (Parallel-Lead-Relative): chord transformations as group operations, always musically valid |
| [`tropical-harmony`](examples/BAND_API_REFERENCE.md#tropical-harmony) | Tropical semiring (max-plus algebra) for harmonic distance — prevents jarring chord jumps |
| [`conservation-rhythm`](examples/BAND_API_REFERENCE.md#conservation-rhythm) | Enforces γ + H = C: kinetic energy + potential energy = budget, per agent and ensemble-wide |
| [`hodge-music`](examples/BAND_API_REFERENCE.md#hodge-music) | Hodge decomposition of disagreement: gradient (fix), curl (iterate), harmonic (celebrate) |
| [`intention-field`](examples/BAND_API_REFERENCE.md#intention-field) | Shared potential field: agents are attracted toward musical goals, not commanded |

Full API reference with types, methods, and examples: [`BAND_API_REFERENCE.md`](examples/BAND_API_REFERENCE.md)

---

## Key Concepts

### γ + H = C (Conservation Law)

Every agent in the band operates under a strict energy budget. **γ** (gamma) is kinetic energy — how actively the agent is playing right now (note density × velocity). **H** (Hamiltonian) is potential energy — stored tension, preparation for the next entrance. Their sum equals **C**, a constant allocated during the tuning phase. When the drummer plays a loud fill (γ↑), its potential energy drops (H↓). When the sax rests, it stores energy for the next solo. The ensemble total is also conserved: Σ(γ + H) = C_total. This prevents the band from either exploding into noise or collapsing into silence.

*Analogy: Think of a pendulum. At the top of the swing, all energy is potential (H high, γ low — the sax is resting, building tension). At the bottom, all energy is kinetic (γ high, H low — the sax is wailing). The total never changes.*

### Hodge Decomposition

When agents disagree — on tempo, on harmonic direction, on dynamics — Hodge decomposition separates the disagreement into three orthogonal components. **Gradient** disagreements are fixable with a simple parameter nudge (one agent is slightly sharp, just tune it). **Curl** disagreements are cyclic and resolve through iteration (call-response loops). **Harmonic** disagreements are irreducible — they represent genuine creative differences, and they're where the most interesting music lives. The band doesn't try to eliminate harmonic disagreement. It celebrates it.

*Analogy: In a real band, if the bassist is rushing slightly, that's gradient — a gentle nudge fixes it. If the drummer and pianist are in a rhythmic conversation that keeps looping without resolving, that's curl — they iterate until they find the pocket. But if the saxophonist hears a chord as tense while the pianist hears it as resolved — that's harmonic disagreement, and it's what makes the music alive.*

### Spectral Feedback (SIA²)

After each performance, the ensemble's output is decomposed into eigenmodes — the "frequency spectrum" of the band's quality. The weakest eigenmode identifies the bottleneck (which agent or interaction needs improvement). A Banach-contraction update is applied: a mathematical procedure guaranteed to bring the agent closer to optimal without overshooting. Because the contraction factor is strictly less than 1, the improvement process converges. The band mathematically cannot get worse.

*Analogy: Imagine a coach watching game tape. They don't just say "do better." They identify the single weakest aspect of performance, prescribe a targeted drill, and guarantee that the drill makes the player objectively better — with a mathematical proof that no drill can accidentally make them worse. That's spectral feedback.*

### Intention Fields

The band has no leader, but it has direction. The intention field is a shared potential field — like a gravitational well in musical space. Each agent contributes a "pull" based on its musical preferences, and the field settles into a consensus direction. When the pianist proposes a modulation to Ab, that creates a gradient in the field. Other agents feel the pull and gradually align. If three out of five agents agree, the field will gently draw the remaining two within a few bars. No votes, no commands — just physics.

*Analogy: A flock of starlings doesn't have a leader. Each bird follows a few simple rules about spacing and direction relative to its neighbors. The flock moves as one — turning, diving, reforming — with no individual in charge. The intention field is the mathematical structure that makes this work for music.*

### t-minus Timing

Agents don't sync to a shared clock. Instead, each agent maintains a local countdown timer — **t-minus** — that predicts when the next beat should land. When the countdown hits zero, the agent plays. The prediction is updated based on what the agent hears from others, but there's no global coordination. Agents converge on tempo through listening, not through a master clock. This means the system scales to any number of agents, works asynchronously, and gracefully handles latency.

*Analogy: In a string quartet, nobody watches a metronome. Each player has an internal sense of time, listens to the others, and subtly adjusts. They converge on a shared pulse through empathy, not through a conductor's baton. t-minus is that internal sense of time, formalized.*

---

## Examples

### `demo_band.py` — Full Ensemble
The complete 5-agent simulation: Ringo (drums), Paul (bass), Wynton (piano), Sonny (sax), and Wes (guitar) play a 12-bar blues. Demonstrates Hodge tempo negotiation, per-bar conservation enforcement, and SIA spectral ranking. Outputs structured MIDI events as JSON.

### `demo_conservation.py` — γ + H = C Deep Dive
Isolates the conservation law. Shows how agents exchange kinetic (γ) and potential (H) energy during performance, how violations are detected, and the three-level recovery system: gentle nudge → mandatory rebalance → emergency silence. Forces a violation by having the sax overplay and watches the system self-correct.

### `demo_hodge.py` — Musical Disagreement
Five agents rate a chord progression differently. Their disagreements are decomposed into gradient (fixable by nudge), curl (needs iteration), and harmonic (creative tension — a feature, not a bug). Shows how Hodge analysis produces actionable recommendations: fix gradient, iterate curl, celebrate harmonic.

---

## API Reference

The complete crate-by-crates reference with types, methods, usage examples, and dependency maps:

→ [`examples/BAND_API_REFERENCE.md`](examples/BAND_API_REFERENCE.md)

---

## Ecosystem

The Self-Improving Band is the integration point for the wider [SuperInstance](https://github.com/SuperInstance) ecosystem — 300+ crates that share a common mathematical language. Each band crate connects to foundational infrastructure:

| Band Crate | Ecosystem Foundation |
|---|---|
| `band-protocol` | [`conservation-law`](https://github.com/SuperInstance/conservation-law) — the γ+H=C invariant |
| `band-agent` | [`sia`](https://github.com/SuperInstance/sia) — Spectrally Initialized Agents with Banach convergence |
| `band-tminus` | [`t-minus`](https://github.com/SuperInstance/t-minus) — event simulation, [`vector-clock-rs`](https://github.com/SuperInstance/vector-clock-rs) for causal ordering |
| `harmonic-plr` | [`flux-algebra`](https://github.com/SuperInstance/flux-algebra) — PLR group, tropical semiring |
| `conservation-rhythm` | [`conservation-matrix`](https://github.com/SuperInstance/conservation-matrix), [`agent-homeostasis`](https://github.com/SuperInstance/agent-homeostasis) |
| `hodge-music` | [`hodge-consensus`](https://github.com/SuperInstance/hodge-consensus) — distributed agreement |
| `intention-field` | [`dial-ecology`](https://github.com/SuperInstance/dial-ecology), [`provenance-chain`](https://github.com/SuperInstance/provenance-chain) |
| `band-midi` | [`Turing-tensor-midi`](https://github.com/SuperInstance/Turing-tensor-midi) — voice interface, [`midi-flux-bridge`](https://github.com/SuperInstance/midi-flux-bridge) |
| `band-ensemble` | [`cuda-oxide`](https://github.com/SuperInstance/cuda-oxide) — Rust→PTX for GPU-accelerated audio |

The AGI thesis connecting all these pieces: [`AGI_VISION.md`](AGI_VISION.md)

---

## Contributing

### Add a New Instrument

1. Define an `AgentRole` variant in `band-agent` (e.g., `Trombone`, `Vibraphone`)
2. Specify its energy weight, MIDI channel, and register range
3. Add note-generation logic in the agent's tick handler
4. Run the ensemble and check spectral feedback — the new agent should appear in the quality ranking

### Add a New Layer

The architecture is designed for extension. To add an 8th layer (e.g., emotional dynamics, timbral evolution):

1. Define the mathematical structure — what's conserved? What's the decomposition?
2. Create a new crate following the `band-*` naming convention
3. Add it to the `band-ensemble` dependency graph
4. Wire it into the performance tick: the new layer should constrain, measure, or transform agent output
5. Update the conservation check if the new layer introduces budget constraints

### Add a New Analysis

Spectral feedback is one analysis method. To add another (e.g., topological persistence, information-theoretic complexity):

1. Implement the analysis as a function `analyze(ensemble_output) -> ImprovementGradient`
2. The gradient must be Banach-contracting (contraction factor < 1)
3. Wire it into the `band-ensemble::self_improve` cycle
4. Add a demo in `examples/python/` showing the analysis on a simple case

### Ground Rules

- **Conservation is non-negotiable.** Every change must preserve γ + H = C.
- **Improvement must converge.** Every update must be a contraction mapping.
- **No central authority.** No conductor, no master clock, no single point of failure.
- **Pure Python demos.** Demos use only the standard library — zero external dependencies.

---

## Documentation Index

| Document | Description |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | High-level architecture, integration map, performance walkthrough |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Detailed technical reference with sequence diagrams and state machines |
| [`AGI_VISION.md`](AGI_VISION.md) | The AGI thesis: how 10 pillars converge toward general intelligence |
| [`docs/CONSERVATION-LAWS.md`](docs/CONSERVATION-LAWS.md) | Deep dive on γ + H = C: formalism, violations, recovery |
| [`docs/HODGE-MUSIC.md`](docs/HODGE-MUSIC.md) | Hodge decomposition theory applied to musical disagreement |
| [`docs/SIA-SPECTRAL.md`](docs/SIA-SPECTRAL.md) | Spectral identity, eigenvalue profiles, and self-improvement |
| [`docs/TMINUS-TIMING.md`](docs/TMINUS-TIMING.md) | t-minus event simulation and asynchronous timing |
| [`docs/AI-ENGINE-SPEC.md`](docs/AI-ENGINE-SPEC.md) | AI provider configuration |
| [`examples/BAND_API_REFERENCE.md`](examples/BAND_API_REFERENCE.md) | Complete crate API reference |

---

## License

MIT

---

*The band plays itself. We just give it the instruments.*
