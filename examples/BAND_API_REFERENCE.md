# Self-Improving Band — API Reference

> Complete reference for all 10 core crates of the Self-Improving Band architecture.

---

## Table of Contents

1. [band-protocol](#band-protocol)
2. [band-agent](#band-agent)
3. [band-ensemble](#band-ensemble)
4. [band-midi](#band-midi)
5. [band-tminus](#band-tminus)
6. [harmonic-plr](#harmonic-plr)
7. [tropical-harmony](#tropical-harmony)
8. [conservation-rhythm](#conservation-rhythm)
9. [hodge-music](#hodge-music)
10. [intention-field](#intention-field)
11. [Cross-Crate Integration Map](#cross-crate-integration-map)

---

## band-protocol

**Purpose:** Wire protocol for all inter-agent communication. Defines the message envelope that carries MIDI events, t-minus timestamps, conservation metadata, and provenance tags.

### Key Types

| Type | Description |
|------|-------------|
| `BandMessage` | Top-level envelope: `{sender, recipient, timestamp, payload, conservation_tag, provenance_id}` |
| `MessagePayload` | Enum: `Midi(MidiPayload)`, `Conservation(ConservationReport)`, `Alignment(AlignmentCheck)`, `Intention(IntentionUpdate)` |
| `ConservationTag` | Lightweight conservation metadata attached to every message: `{gamma, hamiltonian, budget}` |
| `ProvenanceId` | UUID tracing which agent generated a musical decision and why |
| `WireFormat` | Serialization: `Bincode` (default, low-latency) or `Json` (debugging) |

### Key Methods

```rust
// Construct a message
BandMessage::new(sender: AgentId, recipient: AgentId, payload: MessagePayload) -> Self

// Serialize for transport
BandMessage::encode(&self, format: WireFormat) -> Vec<u8>

// Deserialize from wire
BandMessage::decode(data: &[u8], format: WireFormat) -> Result<Self, ProtocolError>

// Verify conservation tag is consistent
BandMessage::verify_conservation(&self) -> bool
```

### Usage Example

```rust
use band_protocol::{BandMessage, MessagePayload, MidiPayload, WireFormat};

let midi = MidiPayload {
    channel: 0,
    note: 60,
    velocity: 100,
    duration_beats: 1.0,
};

let msg = BandMessage::new(
    AgentId::new("bass"),
    AgentId::new("drums"),
    MessagePayload::Midi(midi),
);

let wire = msg.encode(WireFormat::Bincode);
let decoded = BandMessage::decode(&wire, WireFormat::Bincode)?;
assert!(decoded.verify_conservation());
```

### Connections

- **band-midi**: `MidiPayload` is defined in `band-midi` and re-exported here.
- **conservation-rhythm**: `ConservationTag` uses `conservation-rhythm` types internally.
- **band-tminus**: `timestamp` field uses `band-tminus::TMinusTimestamp`.
- **intention-field**: `IntentionUpdate` variant carries `intention-field` updates.

---

## band-agent

**Purpose:** A single autonomous instrument agent. Wraps SIA spectral identity, t-minus clock, conservation state, and MIDI I/O into a self-contained performer.

### Key Types

| Type | Description |
|------|-------------|
| `BandAgent` | Main agent struct: identity + clock + conservation + spectral state + MIDI output |
| `AgentConfig` | Configuration: `{name, role, channel, energy_budget, tempo, dial_position}` |
| `AgentRole` | Enum: `Drums`, `Bass`, `Keys`, `Horns`, `Pads`, `Guitar`, `Custom(String)` |
| `AgentState` | Enum: `Initializing`, `Tuning`, `Performing`, `Tacet { bars_remaining }`, `Improving` |
| `SpectralIdentity` | Eigenvalue decomposition of the agent's performance tensor |

### Key Methods

```rust
// Create a new agent from config
BandAgent::new(config: AgentConfig) -> Self

// Main tick: advance clock, generate events, check conservation
BandAgent::tick(&mut self, dt: f64) -> Vec<BandMessage>

// Receive a message from another agent
BandAgent::receive(&mut self, msg: BandMessage)

// Query spectral state
BandAgent::spectral_profile(&self) -> &SpectralIdentity

// Query conservation state
BandAgent::conservation_state(&self) -> (gamma: f64, hamiltonian: f64, budget: f64)

// Force state transition (e.g., emergency tacet)
BandAgent::set_state(&mut self, state: AgentState)

// Apply spectral improvement (from SIA feedback loop)
BandAgent::apply_improvement(&mut self, gradient: ImprovementGradient)
```

### Usage Example

```rust
use band_agent::{BandAgent, AgentConfig, AgentRole};

let config = AgentConfig {
    name: "paul".into(),
    role: AgentRole::Bass,
    channel: 0,
    energy_budget: 0.20,
    tempo: 120.0,
    dial_position: DialVector::jazz_traditional(),
};

let mut bass = BandAgent::new(config);

// Performance loop
loop {
    let dt = 0.01; // 10ms tick
    let outgoing = bass.tick(dt);
    for msg in outgoing {
        midi_bridge.send(msg);
    }
}
```

### Connections

- **band-protocol**: Agent sends/receives `BandMessage`.
- **band-tminus**: Internal clock is a `band-tminus::TMinusClock`.
- **conservation-rhythm**: Conservation state uses `conservation-rhythm::ConservationState`.
- **harmonic-plr**: Harmonic vocabulary built from `harmonic-plr` transformations.
- **intention-field**: Agent reads field updates and contributes its intention weight.

---

## band-ensemble

**Purpose:** Manages the full ensemble of agents. Handles spawning, MIDI routing, alignment verification, and the self-improvement cycle.

### Key Types

| Type | Description |
|------|-------------|
| `Ensemble` | Collection of agents + routing table + conservation monitor + spectral analyzer |
| `EnsembleConfig` | `{agents: Vec<AgentConfig>, routing: RoutingStrategy, total_budget: f64}` |
| `RoutingStrategy` | Enum: `AllToAll`, `Section { rhythm: Vec<AgentId>, melodic: Vec<AgentId> }`, `Custom(RoutingTable)` |
| `AlignmentReport` | `{max_drift_ms, mean_drift_ms, aligned: bool}` |
| `ImprovementCycle` | Config for SIA²: `{frequency_bars, convergence_threshold, max_iterations}` |

### Key Methods

```rust
// Initialize ensemble from config
Ensemble::new(config: EnsembleConfig) -> Self

// Advance all agents by dt, route messages, return mixed output
Ensemble::tick(&mut self, dt: f64) -> Vec<BandMessage>

// Run alignment check (are all agents on the same tempo?)
Ensemble::check_alignment(&self) -> AlignmentReport

// Run conservation check across all agents
Ensemble::check_conservation(&self) -> ConservationReport

// Run one SIA improvement cycle
Ensemble::run_improvement(&mut self) -> ImprovementReport

// Query spectral state of the whole ensemble
Ensemble::spectral_snapshot(&self) -> EnsembleSpectrum

// Add/remove agents dynamically
Ensemble::add_agent(&mut self, config: AgentConfig) -> AgentId
Ensemble::remove_agent(&mut self, id: AgentId)
```

### Usage Example

```rust
use band_ensemble::{Ensemble, EnsembleConfig, RoutingStrategy};

let config = EnsembleConfig {
    agents: vec![
        AgentConfig::new("ringo", AgentRole::Drums, 0.25),
        AgentConfig::new("paul", AgentRole::Bass, 0.20),
        AgentConfig::new("wynton", AgentRole::Keys, 0.20),
        AgentConfig::new("sonny", AgentRole::Horns, 0.15),
        AgentConfig::new("wes", AgentRole::Guitar, 0.20),
    ],
    routing: RoutingStrategy::AllToAll,
    total_budget: 1.0,
};

let mut band = Ensemble::new(config);

// Run performance
for _ in 0..(12 * 4) {  // 12 bars of 4 beats
    let events = band.tick(BEAT_SEC);
    midi_out.send_all(events);

    if beat % 4 == 0 {
        let report = band.check_conservation();
        if !report.all_ok() {
            report.apply_corrections(&mut band);
        }
    }
}

// Post-performance improvement
let improvement = band.run_improvement();
println!("Agent quality deltas: {:?}", improvement.deltas);
```

### Connections

- **band-agent**: Wraps multiple `BandAgent` instances.
- **band-protocol**: Routes `BandMessage` between agents.
- **conservation-rhythm**: `ConservationReport` comes from here.
- **hodge-music**: Uses Hodge decomposition for alignment negotiation.
- **intention-field**: The shared intention field lives here.

---

## band-midi

**Purpose:** MIDI event representation, parsing, and rendering. Converts between `BandMessage` payloads and concrete MIDI bytes.

### Key Types

| Type | Description |
|------|-------------|
| `BandMidiEvent` | Structured MIDI: `{tick, channel, note, velocity, duration_beats, provenance}` |
| `MidiPayload` | Protocol-level MIDI for `band-protocol`: `{channel, note, velocity, duration_beats}` |
| `SwingProfile` | Swing timing: `{ratio, delay_fraction, humanize_ms}` |
| `MidiRenderer` | Converts `BandMidiEvent` → raw MIDI bytes with swing applied |

### Key Methods

```rust
// Convert between representations
BandMidiEvent::from_payload(payload: &MidiPayload, tick: u32, provenance: ProvenanceId) -> Self

// Render to raw MIDI with swing
MidiRenderer::render(events: &[BandMidiEvent], swing: &SwingProfile) -> Vec<u8>

// Apply humanization (random micro-timing)
MidiRenderer::humanize(events: &mut [BandMidiEvent], jitter_ms: f64)

// Merge overlapping events on the same channel
MidiRenderer::deduplicate(events: &mut Vec<BandMidiEvent>)
```

### Usage Example

```rust
use band_midi::{BandMidiEvent, MidiRenderer, SwingProfile};

let events = vec![
    BandMidiEvent::new(0, 9, 36, 100, 0.5),  // kick on beat 1
    BandMidiEvent::new(1, 9, 38, 95, 0.5),   // snare on beat 2
    BandMidiEvent::new(2, 9, 36, 100, 0.5),  // kick on beat 3
    BandMidiEvent::new(3, 9, 38, 95, 0.5),   // snare on beat 4
];

let swing = SwingProfile::triplet_swing(0.67); // classic jazz swing
let midi_bytes = MidiRenderer::render(&events, &swing);
```

### Connections

- **band-protocol**: `MidiPayload` is the wire representation.
- **band-tminus**: Timing in `BandMidiEvent` uses t-minus ticks.
- **conservation-rhythm**: Velocity values are bounded by energy budgets.

---

## band-tminus

**Purpose:** The timing layer. Each agent has a local t-minus clock instead of syncing to a global conductor. Events are predicted, not triggered.

### Key Types

| Type | Description |
|------|-------------|
| `TMinusClock` | Local countdown timer: `{period, phase, next_beat, next_bar, next_phrase}` |
| `TMinusTimestamp` | `{local_beat, local_bar, global_tick_offset}` — timestamp for events |
| `BoundaryType` | Enum: `Beat`, `Bar`, `Phrase`, `Section` |
| `ClockEvent` | `{boundary: BoundaryType, phase: f64, timestamp: TMinusTimestamp}` |
| `TempoProposal` | Used during alignment: `{proposed_bpm, confidence, agent_id}` |

### Key Methods

```rust
// Create a clock at a given tempo
TMinusClock::new(bpm: f64) -> Self

// Advance time by dt seconds; returns triggered boundary events
TMinusClock::tick(&mut self, dt: f64) -> Vec<ClockEvent>

// Predict next beat time (with humanization)
TMinusClock::predict_next_beat(&self) -> f64

// Adjust tempo (e.g., after gradient correction from Hodge)
TMinusClock::set_tempo(&mut self, bpm: f64, transition_beats: u32)

// Query current phase within the beat
TMinusClock::phase(&self) -> f64

// Compare two clocks for alignment
TMinusClock::drift_from(&self, other: &TMinusClock) -> f64  // milliseconds
```

### Usage Example

```rust
use band_tminus::TMinusClock;

let mut clock = TMinusClock::new(120.0);
let dt = 0.01;  // 10ms tick

loop {
    let events = clock.tick(dt);
    for ev in &events {
        match ev.boundary {
            BoundaryType::Beat => { /* trigger note generation */ }
            BoundaryType::Bar  => { /* check conservation */ }
            BoundaryType::Phrase => { /* check alignment */ }
            _ => {}
        }
    }
}
```

### Connections

- **band-agent**: Each agent owns a `TMinusClock`.
- **band-protocol**: `TMinusTimestamp` is used in message envelopes.
- **hodge-music**: Tempo proposals are decomposed via Hodge.
- **conservation-rhythm**: Timing accuracy affects γ computation.

---

## harmonic-plr

**Purpose:** The PLR (Parallel-Lead-Relative) group for harmonic transformations. Every chord move is a group operation — musically valid by construction.

### Key Types

| Type | Description |
|------|-------------|
| `Chord` | `{root: PitchClass, quality: ChordQuality}` — e.g., C major, F7 |
| `PLRTransform` | Enum: `Parallel`, `Lead`, `Relative` and their compositions |
| `HarmonicRing` | The full group structure for a given key/mode |
| `ChordQuality` | Enum: `Major`, `Minor`, `Dominant7`, `Diminished`, `Augmented`, `Sus4`, `Custom` |
| `PitchClass` | `u8` in 0..12 representing C through B |

### Key Methods

```rust
// Create a harmonic ring in a key
HarmonicRing::new(root: PitchClass, mode: Mode) -> Self

// Apply a PLR transformation to a chord
PLRTransform::apply(&self, chord: &Chord) -> Chord

// Compose transformations (group operation)
PLRTransform::compose(&self, other: &PLRTransform) -> PLRTransform

// Get all valid next chords from the current one
HarmonicRing::successors(&self, chord: &Chord) -> Vec<Chord>

// Distance between two chords in group-theoretic terms
HarmonicRing::word_distance(&self, from: &Chord, to: &Chord) -> usize

// Generate a valid chord progression of N chords
HarmonicRing::generate_progression(&self, length: usize) -> Vec<Chord>
```

### Usage Example

```rust
use harmonic_plr::{HarmonicRing, PLRTransform, Chord, PitchClass, Mode};

let ring = HarmonicRing::new(PitchClass::C, Mode::Major);
let c_major = Chord::new(PitchClass::C, ChordQuality::Major);

// Parallel: C major → C minor
let c_minor = PLRTransform::Parallel.apply(&c_major);

// Relative: C major → A minor
let a_minor = PLRTransform::Relative.apply(&c_major);

// Lead: C major → E minor (mediant)
let e_minor = PLRTransform::Lead.apply(&c_major);

// Compose: P then L
let pl = PLRTransform::Parallel.compose(&PLRTransform::Lead);
let result = pl.apply(&c_major);

// Generate a 12-bar blues
let blues = ring.generate_progression(12);
```

### Connections

- **tropical-harmony**: Distances between chords use tropical metrics.
- **band-agent**: Each agent's harmonic vocabulary is a `HarmonicRing`.
- **intention-field**: Key/modulation changes update the ring.
- **conservation-rhythm**: Harmonic tension contributes to H (Hamiltonian).

---

## tropical-harmony

**Purpose:** Tropical semiring (max-plus algebra) for measuring harmonic distance. Prevents agents from making harmonic jumps that are too large.

### Key Types

| Type | Description |
|------|-------------|
| `TropicalSemiring` | The tropical structure: addition = max, multiplication = + |
| `HarmonicDistance` | Tropical distance metric between chords |
| `TonalCenter` | Reference point in pitch-class space |
| `TensionBudget` | Maximum total harmonic tension the ensemble can sustain |

### Key Methods

```rust
// Tropical distance between two chords
TropicalHarmony::distance(a: &Chord, b: &Chord) -> f64

// Distance from tonal center (tension measure)
TropicalHarmony::tension(chord: &Chord, center: &TonalCenter) -> f64

// Nearest chord to a target within a max distance
TropicalHarmony::nearest_within(chord: &Chord, candidates: &[Chord], max_dist: f64) -> Option<Chord>

// Check if a progression stays within tension budget
TropicalHarmony::validate_progression(progression: &[Chord], budget: &TensionBudget) -> bool
```

### Usage Example

```rust
use tropical_harmony::TropicalHarmony;

let c_maj = Chord::new(PitchClass::C, ChordQuality::Major);
let g7 = Chord::new(PitchClass::G, ChordQuality::Dominant7);
let fsus = Chord::new(PitchClass::Fs, ChordQuality::Sus4);

let d1 = TropicalHarmony::distance(&c_maj, &g7);    // close: 5 semitones
let d2 = TropicalHarmony::distance(&c_maj, &fsus);  // further: 6 semitones

let center = TonalCenter::new(PitchClass::C, Mode::Major);
let tension_g = TropicalHarmony::tension(&g7, &center);  // moderate tension
let tension_f = TropicalHarmony::tension(&fsus, &center); // higher tension
```

### Connections

- **harmonic-plr**: Provides the chord types and group structure.
- **conservation-rhythm**: Harmonic tension feeds into the Hamiltonian (H).
- **hodge-music**: Harmonic disagreements are decomposed via Hodge.

---

## conservation-rhythm

**Purpose:** Enforces γ + H = C across the ensemble. The foundational stability layer that prevents chaos.

### Key Types

| Type | Description |
|------|-------------|
| `ConservationState` | Per-agent: `{gamma, hamiltonian, constant, tolerance}` |
| `ConservationMonitor` | Ensemble-wide checker, runs every bar |
| `Correction` | `{agent_id, deviation, strength, suggested_gamma, suggested_hamiltonian}` |
| `CorrectionStrength` | Enum: `Gentle` (10%), `Mandatory` (proportional), `Emergency` (silence) |
| `ConservationMatrix` | N×N coupling matrix M where `dγ/dt = -M(γ - γ_target)` |
| `ConservationReport` | Per-bar report: `{deviations, corrections, ensemble_total, is_stable}` |

### Key Methods

```rust
// Create monitor with total budget and agents
ConservationMonitor::new(total_budget: f64, agent_budgets: Vec<f64>) -> Self

// Run check + enforcement cycle (call once per bar)
ConservationMonitor::check_and_enforce(&mut self, states: &mut [ConservationState]) -> Vec<Correction>

// Compute the conservation matrix
ConservationMatrix::compute(agents: &[AgentRole], routing: &RoutingTable) -> Self

// Check single agent
ConservationState::check(&self) -> bool  // γ + H ≈ C?

// Energy transfer between agents
ConservationState::transfer(&mut self, other: &mut ConservationState, amount: f64)
```

### Usage Example

```rust
use conservation_rhythm::{ConservationMonitor, ConservationState};

let budgets = vec![0.25, 0.20, 0.20, 0.15, 0.20]; // drums, bass, keys, horns, guitar
let mut monitor = ConservationMonitor::new(1.0, budgets);

let mut states: Vec<ConservationState> = budgets.iter()
    .map(|&b| ConservationState::new(b))
    .collect();

// Each bar:
let corrections = monitor.check_and_enforce(&mut states);
for c in &corrections {
    println!("Agent {} deviation: {:.3} ({:?})", c.agent_id, c.deviation, c.strength);
}
```

### Connections

- **band-agent**: Each agent has a `ConservationState`.
- **band-ensemble**: Runs the `ConservationMonitor` every bar.
- **band-protocol**: `ConservationTag` in every message.
- **tropical-harmony**: Harmonic tension contributes to H.

---

## hodge-music

**Purpose:** Hodge decomposition of musical disagreement. Separates disagreements into gradient (fixable), curl (iteratively resolvable), and harmonic (creative tension).

### Key Types

| Type | Description |
|------|-------------|
| `HodgeDecomposer` | Main decomposer: takes disagreement vectors, returns components |
| `HodgeResult` | `{gradient, curl, harmonic, original, total_energies}` |
| `DisagreementVector` | Per-edge disagreement: `{edge: (AgentId, AgentId), values: Vec<f64>}` |
| `CorrectionPlan` | Which agents to nudge, by how much, in how many iterations |
| `Recommendation` | Enum: `Nudge`, `Iterate { rounds: u32 }`, `Celebrate` (harmonic = good) |

### Key Methods

```rust
// Create decomposer for N agents
HodgeDecomposer::new(n_agents: usize, dimensions: usize) -> Self

// Decompose pairwise disagreements
HodgeDecomposer::decompose(&self, disagreements: Vec<DisagreementVector>) -> HodgeResult

// Generate a correction plan from the result
HodgeDecomposer::recommend(&self, result: &HodgeResult) -> CorrectionPlan

// Check if a disagreement is mostly fixable
HodgeResult::is_mostly_fixable(&self) -> bool

// Measure irreducible creative tension
HodgeResult::creative_tension(&self) -> f64

// Does the curl need iteration?
HodgeResult::needs_iteration(&self) -> bool
```

### Usage Example

```rust
use hodge_music::{HodgeDecomposer, DisagreementVector};

let decomposer = HodgeDecomposer::new(5, 3); // 5 agents, 3 musical dimensions

// Tempo disagreement: each agent wants a different BPM
let disagreements = vec![
    DisagreementVector::new(0, 1, vec![2.0, 0.0, 0.0]),  // drums vs bass
    DisagreementVector::new(1, 2, vec![-1.0, 0.0, 0.0]), // bass vs keys
    // ... all pairs
];

let result = decomposer.decompose(disagreements);
println!("Gradient: {:.1%}", result.gradient_fraction());
println!("Curl:     {:.1%}", result.curl_fraction());
println!("Harmonic: {:.1%}", result.harmonic_fraction());

let plan = decomposer.recommend(&result);
match plan.primary_recommendation() {
    Recommendation::Nudge => println!("Apply direct corrections"),
    Recommendation::Iterate { rounds } => println!("Iterate {} rounds", rounds),
    Recommendation::Celebrate => println!("This is creative tension — don't fix it!"),
}
```

### Connections

- **band-tminus**: Tempo disagreements are decomposed.
- **harmonic-plr** + **tropical-harmony**: Harmonic disagreements are decomposed.
- **intention-field**: Field updates are informed by Hodge analysis.
- **band-ensemble**: Runs Hodge during alignment phase.

---

## intention-field

**Purpose:** Shared potential field giving the ensemble collective direction without a leader. Agents are attracted toward musical goals through the field, not through commands.

### Key Types

| Type | Description |
|------|-------------|
| `IntentionField` | The shared field: `{tempo, key, form, phase, drift_vector}` |
| `FieldContribution` | Each agent's pull on the field: `{weight, direction, confidence}` |
| `PhaseTransition` | Enum: `Groove`, `Build`, `Climax`, `Release`, `Transition` |
| `FormSpec` | Musical form: `{bars, chords, sections}` — e.g., 12-bar blues, AABA |
| `ConsensusState` | `{aligned_agents: u32, total_agents: u32, resolution_bars: f64}` |

### Key Methods

```rust
// Create field from initial form
IntentionField::new(tempo: f64, key: PitchClass, form: FormSpec) -> Self

// Agent contributes to the field (pulls in its direction)
IntentionField::contribute(&mut self, agent_id: AgentId, contribution: FieldContribution)

// Advance the field by one bar
IntentionField::advance(&mut self)

// Get current chord root
IntentionField::chord_root(&self) -> PitchClass

// Query phase state
IntentionField::phase(&self) -> PhaseTransition

// Query consensus
IntentionField::consensus(&self) -> ConsensusState

// Check if field is pulling agents toward a modulation
IntentionField::drift_target(&self) -> Option<(PitchClass, f64)>
```

### Usage Example

```rust
use intention_field::{IntentionField, FieldContribution, FormSpec};

let form = FormSpec::twelve_bar_blues(PitchClass::Bb);
let mut field = IntentionField::new(118.0, PitchClass::Bb, form);

// Keys agent proposes modulation to Ab
field.contribute(
    AgentId::new("keys"),
    FieldContribution {
        direction: vec![0.0, 8.0, 0.0],  // drift toward Ab (8 semitones)
        weight: 0.6,
        confidence: 0.8,
    },
);

// Check consensus
let consensus = field.consensus();
println!("{}/{} agents aligned", consensus.aligned_agents, consensus.total_agents);
println!("Resolution in {:.1} bars", consensus.resolution_bars);

// Advance
for _ in 0..12 {
    field.advance();
    println!("Bar {}: chord root = {:?}", field.current_bar(), field.chord_root());
}
```

### Connections

- **band-agent**: Each agent reads and contributes to the field.
- **hodge-music**: Field disagreements are decomposed to plan resolution.
- **harmonic-plr**: Form specs use PLR group for valid progressions.
- **conservation-rhythm**: Phase transitions affect energy budgets.

---

## Cross-Crate Integration Map

```
                    ┌─────────────────────────────────────────┐
                    │         band-protocol (wire format)      │
                    └────────────┬──────────┬─────────────────┘
                                 │          │
              ┌──────────────────┤          │
              │                  │          │
    ┌─────────▼────────┐  ┌─────▼──────┐   │
    │   band-ensemble   │  │  band-midi  │   │
    │  (orchestrator)   │  │  (render)   │   │
    └──┬───┬───┬───┬───┘  └────────────┘   │
       │   │   │   │                        │
       │   │   │   │   ┌────────────────────┘
       │   │   │   │   │
  ┌────▼┐  │  ┌▼───▼───▼──┐
  │band- │  │  │ intention- │
  │agent │  │  │   field    │
  └──┬───┘  │  └─────┬─────┘
     │      │        │
  ┌──▼──────▼──┐  ┌──▼──────────┐
  │ band-tminus │  │ hodge-music │
  └─────────────┘  └─────────────┘
         │                │
  ┌──────▼──────┐  ┌──────▼──────────┐
  │conservation- │  │ harmonic-plr    │
  │   rhythm     │  │ tropical-       │
  └──────────────┘  │   harmony       │
                    └─────────────────┘
```

### Data Flow During Performance

1. **Tick** → `band-ensemble` calls `tick(dt)` on every `band-agent`
2. **Clock** → Each agent's `band-tminus::TMinusClock` fires boundary events
3. **Generate** → Agent generates MIDI using `harmonic-plr` vocabulary
4. **Constrain** → `conservation-rhythm` checks γ+H=C; applies corrections
5. **Route** → `band-protocol` wraps events, routes via the ensemble
6. **Render** → `band-midi` renders events with swing/humanization
7. **Negotiate** → `hodge-music` decomposes disagreements; `intention-field` pulls consensus
8. **Improve** → SIA spectral feedback updates agent models (Banach-convergent)

### Dependency Summary

| Crate | Depends On |
|-------|-----------|
| `band-protocol` | (none — foundational) |
| `band-midi` | `band-protocol` |
| `band-tminus` | `band-protocol` |
| `harmonic-plr` | (none — pure math) |
| `tropical-harmony` | `harmonic-plr` |
| `conservation-rhythm` | `band-protocol` |
| `hodge-music` | `band-protocol` |
| `intention-field` | `harmonic-plr`, `hodge-music` |
| `band-agent` | `band-protocol`, `band-tminus`, `conservation-rhythm`, `harmonic-plr`, `intention-field` |
| `band-ensemble` | `band-agent`, `band-midi`, `conservation-rhythm`, `hodge-music`, `intention-field` |

---

## Quick-Start: Minimal Band in 20 Lines

```rust
use band_ensemble::{Ensemble, EnsembleConfig, RoutingStrategy};

fn main() {
    let band = Ensemble::new(EnsembleConfig {
        agents: vec![
            AgentConfig::new("drums",  AgentRole::Drums,  0.25),
            AgentConfig::new("bass",   AgentRole::Bass,   0.20),
            AgentConfig::new("keys",   AgentRole::Keys,   0.20),
            AgentConfig::new("horns",  AgentRole::Horns,  0.15),
            AgentConfig::new("guitar", AgentRole::Guitar, 0.20),
        ],
        routing: RoutingStrategy::AllToAll,
        total_budget: 1.0,
    });

    let mut band = band;
    let dt = 60.0 / 120.0;  // one beat at 120 BPM

    for bar in 0..12 {
        for _ in 0..4 {
            let events = band.tick(dt);
            // send events to MIDI output
        }
        band.check_conservation().apply_corrections(&mut band);
        println!("Bar {}: {}", bar + 1, band.check_alignment());
    }

    let report = band.run_improvement();
    println!("Post-gig improvement: {:?}", report.deltas);
}
```

---

## See Also

- [ARCHITECTURE.md](../ARCHITECTURE.md) — Full architecture overview
- [docs/CONSERVATION-LAWS.md](../docs/CONSERVATION-LAWS.md) — γ+H=C deep dive
- [docs/HODGE-MUSIC.md](../docs/HODGE-MUSIC.md) — Hodge decomposition theory
- [docs/SIA-SPECTRAL.md](../docs/SIA-SPECTRAL.md) — Spectral identity and self-improvement
- [docs/TMINUS-TIMING.md](../docs/TMINUS-TIMING.md) — t-minus event simulation
