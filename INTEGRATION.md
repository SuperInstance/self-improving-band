# Integration Guide: self-improving-band

## What This Crate Provides

The Self-Improving Band is NOT a single crate — it is the **integration archetype** for the entire SuperInstance ecosystem. It is 5 AI agents that make music together with mathematical guarantees of self-improvement. It exercises all 10 pillars of the SuperInstance AGI thesis simultaneously.

### The 7-Layer Architecture

| Layer | Concept | Crates |
|-------|---------|--------|
| **1: Conservation** | γ + H = C (the physics) | conservation-law, entropy-conservation |
| **2: Spectral Identity** | Eigenvalue profiles, Banach convergence | spectral-fleet, sia |
| **3: Category Theory** | PLR groups, tropical harmony, constraint algebra | categorical-agents |
| **4: Temporal Flow** | Predict, don't sync | t-minus |
| **5: Hodge Decomposition** | Gradient (fix) · Curl (iterate) · Harmonic (celebrate) | hodge-music |
| **6: Intention Field** | Collective direction without a leader | intention-field |
| **7: Musical Output** | MIDI events, audio, provenance chains | band-midi, band-protocol |

### Key Concepts

- **Band Agent**: An SIA instance with spectral identity, conservation envelope, improvement trajectory, and dial position
- **T-Minus Clock**: Each agent predicts when to play — no shared clock, no conductor
- **Conservation Envelope**: γ + H = C constrains every agent action
- **Self-Improvement Loop**: Spectral feedback → categorical improvement → conservation validation → Wasserstein measurement → the loop improves itself

## How to Use This Repository

```bash
git clone https://github.com/SuperInstance/self-improving-band.git
cd self-improving-band
python3 examples/python/demo_band.py
```

The demo runs 5 agents that converge on shared tempo, negotiate key, distribute energy, and produce music that measurably improves over time.

## Integration Points

### ALL Band Crates

This repository integrates with every crate in the band ecosystem. The integration pattern is the 7-layer stack:

#### conservation-law (Layer 1)

- **Why**: The conservation law γ + H = C is the foundation. Every musical action — every note played, every rest taken — must respect the energy budget.
- **How**: Each band agent tracks its energy via `ConservationDetector`. Notes that would violate conservation are suppressed.

```rust
use conservation_law::fleet_integration::CircuitState;

// Before a band agent plays a note, check conservation
let state: CircuitState = agent.conservation_check();
if state == CircuitState::Closed {
    agent.play_note(pitch, velocity);
} else {
    agent.rest(); // conserve energy
}
```

#### spectral-fleet (Layer 2)

- **Why**: Each band agent's "timbral personality" is defined by its eigenvalue profile. Spectral decomposition reveals which agents are converging and which are diverging.
- **How**: Compute the fleet Laplacian of the band's current state. The Fiedler vector reveals natural voice-grouping; the spectral gap measures ensemble cohesion.

#### categorical-agents (Layer 3)

- **Why**: Musical phrases are morphisms in a category. PLR groups (Parallel/Leading-tone/Relative) are algebraic structures on chord progressions. Categorical composition guarantees correct harmonic movement.
- **How**: Each harmonic move is a `Morphism<Chord, Chord>`. Composing moves via monadic `bind` produces phrase structures that are provably correct.

#### t-minus (Layer 4)

- **Why**: Band agents don't sync to a metronome — they predict the next beat using t-minus event simulation. This enables groove, swing, and human-like timing.
- **How**: Each agent runs a local `TMinus` clock. `tick(dt)` advances local time. When `next_beat <= 0`, the agent plays and predicts the next beat.

```python
class TMinus:
    next_beat: float = 0.0
    phase: float = 0.0

    def tick(self, dt: float):
        self.next_beat -= dt
        self.phase = (self.phase + dt / self.period) % 1.0
        if self.next_beat <= 0:
            self.on_beat()
            self.next_beat = self.predict_next_beat()
```

#### wasserstein-agents (Improvement Measurement)

- **Why**: The Wasserstein distance measures how much the band's distribution of musical states has shifted. This IS the improvement metric: W₂ before practice vs. after practice quantifies progress.
- **How**: Before and after each rehearsal cycle, compute the W₂ distance between agent distributions. Monotone decrease confirms self-improvement.

#### persistent-sheaf (Layer 5 context)

- **Why**: Hodge decomposition of the band's "disagreement field" separates fixable errors (gradient) from productive creative tension (harmonic) from things to iterate on (curl).
- **How**: Build a cellular sheaf on the band's communication graph. The sheaf Laplacian eigenvalues reveal which modes of disagreement are constructive.

#### lattice-crypto (Identity & Handshake)

- **Why**: Band agents need cryptographic identities for provenance chains — every note must be attributable to a specific agent. Post-quantum security ensures long-term integrity.
- **How**: Each agent generates a `RingLWE` key pair. The public key signs every MIDI event. The provenance chain is a cryptographically verifiable record of who played what, when.

## For AI Agents

- **Context needed**: Number of band agents (default 5), musical style/dial position, conservation budget, tempo range
- **Key pattern**: Initialize SIA agents → wire conservation envelope → start t-minus clocks → run self-improvement loop → output MIDI
- **The improvement loop**: Watch (spectral eigenvalues) → Identify (weakest eigenmode) → Generate (categorical composition) → Validate (conservation check) → Deploy (t-minus timing) → Measure (Wasserstein distance) → Loop

## For Humans

- **Prerequisites**: The Self-Improving Band is a capstone project — learn the individual crates first
- **Learning path**:
  1. Read `ARCHITECTURE.md` for the full 7-layer model
  2. Run `examples/python/demo_band.py` to hear the output
  3. Learn each layer's crate independently (conservation-law → spectral-fleet → categorical-agents → t-minus)
  4. Study the integration code to see how layers compose
  5. Modify agent parameters and observe emergent behavior changes
- **Common pitfalls**:
  - The band is NOT a sequencer — there is no score. Music emerges from constraints.
  - Conservation violations produce silence, not errors. If the band stops playing, check the conservation budget.
  - T-minus timing produces groove, not mechanical precision. Don't try to "fix" the timing.
  - The self-improvement loop converges but slowly. Run for 100+ cycles to see measurable improvement.
