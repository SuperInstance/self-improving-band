# T-Minus Event Simulation — Deep Dive

> *How autonomous agents predict musical events without shared clocks, and why that makes the band swing.*

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Mathematical Formalism](#mathematical-formalism)
3. [The Core Timing Loop](#the-core-timing-loop)
4. [Drift Detection and Correction](#drift-detection-and-correction)
5. [Swing and Groove Offset Calculations](#swing-and-groove-offset-calculations)
6. [Phase Wrapping and Beat/Bar/Phrase Boundaries](#phase-wrapping-and-beatbarphrase-boundaries)
7. [Pseudocode: Complete Timing Engine](#pseudocode-complete-timing-engine)
8. [Timing Properties and Guarantees](#timing-properties-and-guarantees)

---

## Philosophy

In a traditional sequencer, all instruments sync to a single master clock. If the clock says "beat 3," everyone plays beat 3 simultaneously. This is an orchestra model — a conductor with a baton.

**Real bands don't work like that.**

A jazz drummer doesn't check a clock. They *feel* where the beat is. They predict when the next downbeat will land based on internalized tempo, muscle memory, and listening to the bass player. They might be 5ms early or 10ms late — but they're *in the pocket*. That micro-timing is what makes music feel alive.

t-minus event simulation replicates this:

- **No shared clock.** Each agent has its own local time.
- **Prediction, not synchronization.** Agents predict when events should happen.
- **Listening, not commanding.** Agents hear each other and adjust.
- **Drift is tolerated within bounds.** 10-15ms of drift sounds human. 50ms sounds sloppy.

The name comes from rocket launch terminology: **T-minus 5 seconds** means "5 seconds until event." Each agent constantly computes T-minus for every upcoming musical event.

---

## Mathematical Formalism

### Notation

| Symbol | Meaning |
|--------|---------|
| τᵢ(t) | Agent i's local time at real time t |
| β | Agreed-upon tempo (BPM) |
| T = 60/β | Beat period (seconds) |
| φᵢ(t) | Agent i's phase within current cycle, φ ∈ [0, 1) |
| δᵢ(t) | Agent i's drift from ensemble average |
| s | Swing factor ∈ [0, 0.5) |
| B | Beats per bar (time signature numerator) |
| P | Bars per phrase |

### Local Time Model

Each agent maintains its own time as a function of real (wall) time:

```
τᵢ(t) = t + εᵢ(t)
```

where εᵢ(t) is a small, bounded error term. In practice, agents don't know εᵢ — they only know τᵢ.

### Phase Function

An agent's phase within a beat cycle:

```
φᵢ(t) = (τᵢ(t) / T) mod 1.0
```

This gives a value in [0, 1) representing "where am I in the current beat?" At φ = 0, it's a beat boundary. At φ = 0.5, it's the off-beat.

### t-minus Prediction

The core function. For agent i, the time until the next event of type E:

```
t_minus_i(E, t) = t_E - τᵢ(t)
```

where t_E is the predicted local time of event E. Agents compute:

```
t_minus_beat(t)  = T × (1 - φᵢ(t))           // time until next beat
t_minus_bar(t)   = T × (B - φ_bar_i(t))       // time until next bar
t_minus_phrase(t) = T × B × (P - φ_phrase_i(t))  // time until next phrase
```

where φ_bar and φ_phrase are phase functions at the bar and phrase level:

```
φ_bar_i(t)    = (τᵢ(t) / (T × B)) mod 1.0
φ_phrase_i(t) = (τᵢ(t) / (T × B × P)) mod 1.0
```

### Event Prediction Without Shared Clocks

The key insight: agents don't need to agree on *when* events happen in wall-clock time. They need to agree on *what beat it is*. This is a phase agreement problem, not a time synchronization problem.

**Theorem (Phase Convergence):** If agents exchange their phase positions φᵢ at regular intervals and apply the correction:

```
φᵢ ← φᵢ + α × (φ̄ - φᵢ)
```

where φ̄ is the ensemble mean phase and α ∈ (0, 1] is the correction rate, then:

```
max |φᵢ - φⱼ| → 0 as t → ∞
```

Proof: This is a standard consensus protocol. The Lyapunov function V = Σ(φᵢ - φ̄)² decreases monotonically. ∎

**Corollary:** Agents don't need to know the absolute time to agree on relative timing. They only need to exchange phase information through MIDI events (which carry implicit timing).

### Prediction Confidence

Each prediction has an associated confidence based on drift history:

```
confidence_i(E, t) = exp(-|δᵢ(t)| / δ_max) × historical_accuracy_i(E)
```

where:
- δᵢ(t) is current drift from ensemble average
- δ_max is maximum tolerable drift
- historical_accuracy_i(E) is the fraction of predictions that were within tolerance

High confidence (> 0.9): agent is in the pocket. Fire events as predicted.
Medium confidence (0.5-0.9): slight drift. Apply gentle correction.
Low confidence (< 0.5): significant drift. Apply aggressive correction or re-sync.

---

## The Core Timing Loop

### Architecture

```
┌──────────────────────────────────────────────────┐
│                  T-Minus Engine                   │
│                                                   │
│  ┌─────────┐    ┌──────────┐    ┌──────────────┐ │
│  │ Local   │    │ Event    │    │ Swing/Groove │ │
│  │ Clock   │───▶│ Predictor│───▶│ Offset       │ │
│  │ (τᵢ)   │    │          │    │ Calculator   │ │
│  └─────────┘    └──────────┘    └──────┬───────┘ │
│       │                                │          │
│       │          ┌──────────┐          │          │
│       │          │ Drift    │          │          │
│       └─────────▶│ Detector │          │          │
│                  │ & Corrector│◀────────┘          │
│                  └──────┬───┘                     │
│                         │                         │
│                         ▼                         │
│                  ┌──────────────┐                  │
│                  │ Event Queue  │                  │
│                  │ (t-minus     │                  │
│                  │  ordered)    │                  │
│                  └──────────────┘                  │
│                         │                         │
│                         ▼                         │
│                  MIDI Output                       │
└──────────────────────────────────────────────────┘
```

### Tick-by-Tick

```python
def timing_tick(agent: Agent, dt: float) -> list[Event]:
    """
    Advance the agent's t-minus clock by dt seconds.
    Returns any events that should fire during this tick.
    """
    events = []
    
    # 1. Advance local time
    agent.tau += dt
    agent.tick_count += 1
    
    # 2. Compute current phase at all levels
    agent.beat_phase = (agent.tau / agent.beat_period) % 1.0
    agent.bar_phase = (agent.tau / (agent.beat_period * agent.beats_per_bar)) % 1.0
    agent.phrase_phase = (agent.tau / (agent.beat_period * agent.beats_per_bar * agent.bars_per_phrase)) % 1.0
    
    # 3. Decrement t-minus counters
    agent.t_minus_beat -= dt
    agent.t_minus_bar -= dt
    agent.t_minus_phrase -= dt
    
    # 4. Check for beat events
    if agent.t_minus_beat <= 0:
        # A beat boundary has been crossed
        beat_in_bar = agent.current_beat + 1
        if beat_in_bar > agent.beats_per_bar:
            beat_in_bar = 1
            # This is also a bar boundary
        
        # Apply swing offset to this beat
        swing_dt = compute_swing_offset(beat_in_bar, agent.swing)
        
        # Fire the beat event
        event = BeatEvent(
            beat=beat_in_bar,
            bar=agent.current_bar,
            swing_offset=swing_dt,
            phase=agent.beat_phase,
        )
        events.append(event)
        
        # Predict the next beat
        agent.t_minus_beat = agent.beat_period + swing_dt
        agent.current_beat = beat_in_bar
    
    # 5. Check for bar events
    if agent.t_minus_bar <= 0:
        agent.t_minus_bar = agent.beat_period * agent.beats_per_bar
        agent.current_bar += 1
        events.append(BarEvent(bar=agent.current_bar))
    
    # 6. Check for phrase events
    if agent.t_minus_phrase <= 0:
        agent.t_minus_phrase = agent.beat_period * agent.beats_per_bar * agent.bars_per_phrase
        events.append(PhraseEvent(phrase=agent.current_phrase))
        agent.current_phrase += 1
    
    # 7. Drift check (every N ticks to reduce overhead)
    if agent.tick_count % 100 == 0:
        check_and_correct_drift(agent)
    
    return events
```

---

## Drift Detection and Correction

### What Is Drift?

Drift is the difference between an agent's local tempo and the ensemble's consensus tempo. Even without a shared clock, drift is detectable through MIDI events.

### Detecting Drift from MIDI Events

When agent A hears agent B play a note that should be on a beat boundary, A can measure the timing offset:

```
Agent A's local time of B's beat:   τ_A(observed)
Agent A's predicted time for that beat: τ_A(predicted)
Drift detected: δ = τ_A(observed) - τ_A(predicted)
```

If δ is consistently positive, B is running slow (behind). If negative, B is running fast (ahead).

### Multi-Agent Drift Estimation

Each agent maintains a drift estimate for every other agent:

```python
class DriftTracker:
    """Track drift between this agent and all other agents."""
    
    def __init__(self, my_id: AgentId, n_agents: int):
        self.my_id = my_id
        # drift[j] = estimated drift of agent j relative to me
        self.drift = {j: 0.0 for j in range(n_agents) if j != my_id}
        # Exponential moving average weight
        self.ema_alpha = 0.1
        # History for confidence estimation
        self.history = {j: [] for j in range(n_agents) if j != my_id}
    
    def observe(self, other: AgentId, observed_beat_time: float, 
                predicted_beat_time: float):
        """
        Called when we hear another agent play on a beat boundary.
        """
        delta = observed_beat_time - predicted_beat_time
        
        # Exponential moving average
        self.drift[other] = (self.ema_alpha * delta + 
                            (1 - self.ema_alpha) * self.drift[other])
        
        # Track history
        self.history[other].append(delta)
        if len(self.history[other]) > 100:
            self.history[other].pop(0)
    
    def my_drift(self) -> float:
        """
        Estimate my drift relative to the ensemble.
        Average of all pairwise drifts, negated (their drift from me = -my drift from them).
        """
        if not self.drift:
            return 0.0
        # The ensemble "average" drift
        avg_drift = sum(self.drift.values()) / len(self.drift)
        # My drift is the negative (I'm the reference)
        return -avg_drift / (len(self.drift) + 1)  # Weighted by population
    
    def confidence(self, other: AgentId) -> float:
        """How confident are we in our drift estimate for agent `other`?"""
        hist = self.history[other]
        if len(hist) < 5:
            return 0.0
        variance = sum((x - self.drift[other])**2 for x in hist) / len(hist)
        return 1.0 / (1.0 + variance * 1000)  # Higher variance → lower confidence
```

### Correction Algorithms

#### 1. Gradual Phase Correction (Preferred)

The default correction strategy. Slowly nudges the agent's phase toward the ensemble average:

```python
def gradual_correction(agent: Agent, drift: float, alpha: float = 0.05):
    """
    Apply a small phase correction each tick.
    alpha: correction strength (0 = no correction, 1 = instant snap)
    """
    correction = alpha * drift
    agent.tau += correction
    # Don't adjust t_minus counters — they'll catch up naturally
    # This avoids discontinuities in the event stream
```

Properties:
- **Smooth**: no audible jumps in timing
- **Convergent**: α ∈ (0, 1) guarantees convergence (proof: standard EMA)
- **Robust**: resistant to outlier observations
- **Typical α**: 0.03–0.10 (3–10% correction per observation)

#### 2. Immediate Phase Snap (Emergency)

Used only when drift exceeds a hard threshold:

```python
def immediate_snap(agent: Agent, target_phase: float):
    """
    Instantly reset the agent's phase to match the ensemble.
    Use only for large drifts (> 50ms) that would be audible.
    """
    current_phase = agent.beat_phase
    phase_delta = target_phase - current_phase
    # Handle wrap-around
    if phase_delta > 0.5:
        phase_delta -= 1.0
    elif phase_delta < -0.5:
        phase_delta += 1.0
    
    agent.tau += phase_delta * agent.beat_period
    # Recompute all t-minus counters
    agent.t_minus_beat = agent.beat_period * (1.0 - target_phase)
    agent.t_minus_bar = ...  # Recompute from new phase
```

#### 3. Tempo Nudge (Long-term)

For correcting systematic tempo drift (one agent running consistently faster/slower):

```python
def tempo_nudge(agent: Agent, drift_rate: float, beta: float = 0.01):
    """
    Adjust the agent's local tempo to match the ensemble.
    drift_rate: observed drift per bar (seconds)
    beta: adjustment strength
    """
    # drift_rate > 0 means we're getting ahead → slow down
    tempo_correction = -drift_rate * beta * agent.tempo / agent.beat_period
    agent.tempo += tempo_correction
    agent.beat_period = 60.0 / agent.tempo
```

### Correction Decision Tree

```
|drift| < 5ms     → No correction needed (within human feel)
5ms ≤ |drift| < 15ms → Gradual correction (α = 0.03)
15ms ≤ |drift| < 50ms → Strong gradual correction (α = 0.10)
|drift| ≥ 50ms   → Immediate snap + tempo nudge
```

---

## Swing and Groove Offset Calculations

### What Is Swing?

Swing is a systematic timing deviation applied to off-beats (typically beats 2 and 4 in 4/4, or the second eighth note of each beat). Instead of being exactly halfway between beats, off-beats are delayed, creating a "long-short" pattern.

### Swing as a Timing Function

Given a swing factor s ∈ [0, 0.5):

```
For beat position b within a bar (0-indexed):
  
  If b is a downbeat (b = 0, 2, 4, ...):
    swing_offset = 0                    // Downbeats are on time
    
  If b is an off-beat (b = 1, 3, 5, ...):
    swing_offset = s × T                // Delayed by swing factor × beat period
    
  Sub-beat swing (for eighth/sixteenth notes):
    For sub-position p within beat (0, 0.5, 1.0):
      If p = 0:     offset = 0
      If p = 0.5:   offset = s × T × 0.5
      If p = 1.0:   offset = 0 (next beat)
```

### Groove Templates

Beyond simple swing, agents can apply groove templates — predefined timing patterns:

```python
# A shuffle groove (hard swing on every beat)
SHUFFLE = [0.0, 0.0, 0.33, 0.0, 0.33, 0.0, 0.33, 0.0]  # offsets in beat fractions

# A laid-back groove (slightly behind the beat)
LAID_BACK = [-0.02, -0.01, -0.03, -0.01, -0.02, -0.01, -0.03, -0.01]

# A push groove (slightly ahead of the beat)
PUSHED = [0.02, 0.01, 0.03, 0.01, 0.02, 0.01, 0.03, 0.01]

# A funk groove (asymmetric)
FUNK = [0.0, 0.0, 0.33, 0.0, 0.0, 0.0, 0.40, 0.15]

def apply_groove(base_time: float, beat_position: int, groove: list[float], 
                 beat_period: float) -> float:
    """Apply a groove template offset to a note time."""
    idx = beat_position % len(groove)
    return base_time + groove[idx] * beat_period
```

### Agent-Specific Groove

Each agent has its own groove profile based on its `dial_position`:

```python
def compute_groove(dial: DialVector) -> list[float]:
    """
    Generate a groove template from an agent's dial position.
    """
    groove = [0.0] * 8  # 8 sub-beats per bar (2 per beat in 4/4)
    
    # Groove looseness controls swing amount
    swing = dial.groove_looseness * 0.5  # Map [0,1] to [0, 0.5]
    
    # Apply swing to off-beats
    for i in [2, 6]:  # Second eighth note of beats 1 and 2
        groove[i] = swing
    for i in [4, 8]:  # Second eighth note of beats 3 and 4
        groove[i % 8] = swing * 0.8  # Slightly less on beats 3-4
    
    # Complexity adds syncopation
    if dial.complexity > 0.5:
        # Add ahead-of-beat anticipation
        anticipation = (dial.complexity - 0.5) * 0.1
        groove[1] = -anticipation  # Ahead of beat 2
        groove[5] = -anticipation  # Ahead of beat 4
    
    # Dynamics affect laid-back/pushed feel
    if dial.dynamics < 0.3:
        # Laid back (behind the beat)
        laid_back = (0.3 - dial.dynamics) * 0.05
        for i in range(8):
            groove[i] += laid_back
    
    return groove
```

---

## Phase Wrapping and Beat/Bar/Phrase Boundaries

### The Phase Continuity Problem

Phase is a circular quantity: after 0.999... comes 0.0. This wrapping creates edge cases:

1. **Beat boundary**: φ_beat wraps from ~1.0 to 0.0
2. **Bar boundary**: φ_bar wraps when all beats in the bar are complete
3. **Phrase boundary**: φ_phrase wraps when all bars in the phrase are complete

### Phase Arithmetic

All phase operations must account for circularity:

```python
def phase_distance(a: float, b: float) -> float:
    """Shortest distance between two phase values on the unit circle."""
    d = (b - a) % 1.0
    if d > 0.5:
        d -= 1.0
    return d

def phase_advance(current: float, delta: float) -> float:
    """Advance phase by delta, wrapping to [0, 1)."""
    return (current + delta) % 1.0

def phase_weighted_mean(phases: list[float], weights: list[float]) -> float:
    """
    Compute the weighted circular mean of phase values.
    Critical for ensemble phase consensus.
    """
    sin_sum = sum(w * sin(2 * pi * p) for p, w in zip(phases, weights))
    cos_sum = sum(w * cos(2 * pi * p) for p, w in zip(phases, weights))
    return (atan2(sin_sum, cos_sum) / (2 * pi)) % 1.0
```

### Boundary Detection

Agents detect boundaries by watching for phase wrap:

```python
def detect_boundary(prev_phase: float, curr_phase: float) -> Optional[BoundaryType]:
    """
    Detect if a phase wrap occurred during the last tick.
    A wrap means prev_phase > curr_phase (decreasing then jumping to 0).
    """
    if prev_phase > 0.9 and curr_phase < 0.1:
        # Phase wrapped around — boundary crossed
        return BoundaryType.WRAP
    
    # Check if we crossed specific thresholds
    thresholds = {
        0.0: BoundaryType.BEAT,
        0.25: BoundaryType.UPBEAT_16,
        0.5: BoundaryType.OFFBEAT,
        0.75: BoundaryType.UPBEAT_16,
    }
    
    for threshold, btype in thresholds.items():
        if prev_phase < threshold <= curr_phase:
            return btype
        # Handle wrap-around crossing
        if prev_phase > 0.75 and threshold == 0.0 and curr_phase < 0.25:
            return btype
    
    return None
```

### Multi-Level Phase Coordination

```python
class PhaseCoordinator:
    """
    Manages phase at beat, bar, and phrase levels simultaneously.
    Ensures that wrapping at one level correctly triggers events at higher levels.
    """
    
    def __init__(self, beats_per_bar: int, bars_per_phrase: int):
        self.beats_per_bar = beats_per_bar
        self.bars_per_phrase = bars_per_phrase
        
        self.beat_count = 0      # Current beat within bar [0, beats_per_bar)
        self.bar_count = 0       # Current bar within phrase [0, bars_per_phrase)
        self.phrase_count = 0    # Current phrase number
    
    def advance_beat(self) -> list[BoundaryEvent]:
        """Called when a beat boundary is detected."""
        events = []
        
        self.beat_count += 1
        events.append(BoundaryEvent.BEAT(self.beat_count))
        
        if self.beat_count >= self.beats_per_bar:
            self.beat_count = 0
            self.bar_count += 1
            events.append(BoundaryEvent.BAR(self.bar_count))
            
            if self.bar_count >= self.bars_per_phrase:
                self.bar_count = 0
                self.phrase_count += 1
                events.append(BoundaryEvent.PHRASE(self.phrase_count))
        
        return events
    
    def form_position(self) -> FormPosition:
        """Current position in the musical form."""
        return FormPosition(
            beat=self.beat_count,
            bar=self.bar_count,
            phrase=self.phrase_count,
            total_beats=self.bar_count * self.beats_per_bar + self.beat_count,
        )
```

### Form-Aware Phase Tracking

For structured forms (12-bar blues, AABA), phase tracking is form-aware:

```python
class FormPhaseTracker:
    """
    Track phase within a specific musical form (e.g., 12-bar blues).
    Each section has its own harmonic/energetic characteristics.
    """
    
    def __init__(self, form: FormSpec):
        self.form = form
        self.current_section_idx = 0
        self.bar_in_section = 0
        self.repeat_count = 0
    
    @property
    def current_section(self) -> FormSection:
        return self.form.sections[self.current_section_idx]
    
    def advance_bar(self) -> Optional[str]:
        """
        Advance by one bar. Returns the new section label if the section changed.
        """
        self.bar_in_section += 1
        
        section = self.current_section
        if self.bar_in_section >= section.bars:
            self.bar_in_section = 0
            self.repeat_count += 1
            
            if self.repeat_count >= section.repeats:
                self.repeat_count = 0
                self.current_section_idx += 1
                
                if self.current_section_idx >= len(self.form.sections):
                    # Form complete — loop back to start
                    self.current_section_idx = 0
                    return self.form.sections[0].label
                
                return self.current_section.label
        
        return None  # No section change
```

---

## Pseudocode: Complete Timing Engine

Below is the complete, self-contained timing engine for one agent.

```python
"""
T-Minus Timing Engine — Complete Implementation
================================================
A single agent's timing system. Each agent runs this independently.
No shared state. No shared clock. Only MIDI events for coordination.

Dependencies: math, dataclasses, typing (stdlib only)
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum, auto


# ─── Types ───────────────────────────────────────────────────────────────

class BoundaryType(Enum):
    BEAT = auto()
    BAR = auto()
    PHRASE = auto()
    SECTION_CHANGE = auto()


@dataclass
class TimeSignature:
    beats_per_bar: int = 4
    beat_unit: int = 4  # 4 = quarter note beats


@dataclass
class FormSection:
    label: str       # "I", "IV", "V", "A", "B"
    bars: int        # Length in bars
    repeats: int = 1


@dataclass
class FormSpec:
    name: str
    sections: List[FormSection]
    
    @property
    def total_bars(self) -> int:
        return sum(s.bars * s.repeats for s in self.sections)


@dataclass
class GrooveTemplate:
    """Timing offsets per sub-beat position."""
    offsets: List[float]  # In units of beat fraction (e.g., 0.0 to 0.5)
    
    @staticmethod
    def straight(n_sub_beats: int = 8) -> 'GrooveTemplate':
        return GrooveTemplate([0.0] * n_sub_beats)
    
    @staticmethod
    def swing(swing_factor: float = 0.33) -> 'GrooveTemplate':
        """Generate a swing groove template."""
        offsets = []
        for i in range(8):
            if i % 2 == 0:
                offsets.append(0.0)          # Downbeats on time
            else:
                offsets.append(swing_factor)  # Off-beats delayed
        return GrooveTemplate(offsets)


@dataclass
class TimingEvent:
    """An event fired by the timing engine."""
    boundary: BoundaryType
    beat_in_bar: int       # 0-indexed
    bar_in_phrase: int     # 0-indexed
    bar_in_form: int       # 0-indexed
    section: str           # Current form section label
    phrase: int            # Phrase counter
    phase: float           # Current beat phase [0, 1)
    swing_offset: float    # Applied swing offset in seconds
    tick: int              # Monotonic tick counter


@dataclass
class DriftReport:
    """Drift status for this agent."""
    estimated_drift_ms: float
    confidence: float
    correction_applied_ms: float
    n_observations: int


# ─── The Engine ──────────────────────────────────────────────────────────

class TMinusEngine:
    """
    Complete t-minus timing engine for one agent.
    
    Usage:
        engine = TMinusEngine(agent_id=0, tempo=120.0, ...)
        while performing:
            events = engine.tick(dt=0.001)  # 1ms tick
            for event in events:
                handle_musical_event(event)
    """
    
    def __init__(
        self,
        agent_id: int,
        tempo: float = 120.0,
        time_signature: TimeSignature = TimeSignature(),
        form: Optional[FormSpec] = None,
        swing: float = 0.0,
        groove: Optional[GrooveTemplate] = None,
        bars_per_phrase: int = 4,
    ):
        self.agent_id = agent_id
        self.tempo = tempo
        self.time_signature = time_signature
        self.swing = swing
        self.bars_per_phrase = bars_per_phrase
        
        # Derived
        self.beat_period = 60.0 / tempo
        self.bar_period = self.beat_period * time_signature.beats_per_bar
        self.phrase_period = self.bar_period * bars_per_phrase
        
        # Form
        self.form = form or FormSpec("default", [FormSection("A", 4, 1)])
        self.current_section_idx = 0
        self.bar_in_section = 0
        self.section_repeat_count = 0
        
        # Local time
        self.tau = 0.0           # Local time accumulator
        self.tick_count = 0      # Monotonic tick counter
        
        # Phase at each level
        self.beat_phase = 0.0
        self.bar_phase = 0.0
        self.phrase_phase = 0.0
        
        # Position counters
        self.beat_in_bar = 0     # 0-indexed
        self.bar_in_phrase = 0   # 0-indexed
        self.bar_in_form = 0     # 0-indexed
        self.phrase_count = 0
        
        # t-minus counters
        self.t_minus_beat = self.beat_period
        self.t_minus_bar = self.bar_period
        self.t_minus_phrase = self.phrase_period
        
        # Groove
        self.groove = groove or GrooveTemplate.straight()
        
        # Drift tracking
        self.drift_estimates: dict[int, float] = {}  # other_agent_id → drift (seconds)
        self.drift_history: dict[int, List[float]] = {}
        self.my_drift = 0.0
        self.correction_applied = 0.0
        self.ema_alpha = 0.1
        
        # Correction parameters
        self.gradual_alpha = 0.05     # Normal correction strength
        self.strong_alpha = 0.15      # Strong correction
        self.snap_threshold = 0.050   # 50ms → immediate snap
        self.drift_check_interval = 100  # Check every N ticks
    
    # ─── Core Tick ───────────────────────────────────────────────────
    
    def tick(self, dt: float) -> List[TimingEvent]:
        """Advance the engine by dt seconds. Returns fired events."""
        events = []
        
        # Advance local time
        self.tau += dt
        self.tick_count += 1
        
        # Compute phases
        self.beat_phase = (self.tau / self.beat_period) % 1.0
        self.bar_phase = (self.tau / self.bar_period) % 1.0
        self.phrase_phase = (self.tau / self.phrase_period) % 1.0
        
        # Decrement t-minus counters
        self.t_minus_beat -= dt
        self.t_minus_bar -= dt
        self.t_minus_phrase -= dt
        
        # ── Beat boundary ──
        if self.t_minus_beat <= 0:
            self.beat_in_bar += 1
            
            # Compute swing offset for this beat
            swing_offset = self._swing_offset(self.beat_in_bar)
            
            event = TimingEvent(
                boundary=BoundaryType.BEAT,
                beat_in_bar=self.beat_in_bar,
                bar_in_phrase=self.bar_in_phrase,
                bar_in_form=self.bar_in_form,
                section=self.current_section.label,
                phrase=self.phrase_count,
                phase=self.beat_phase,
                swing_offset=swing_offset,
                tick=self.tick_count,
            )
            events.append(event)
            
            # Predict next beat (with swing adjustment)
            self.t_minus_beat = self.beat_period + swing_offset
            
            # Check for bar boundary
            if self.beat_in_bar >= self.time_signature.beats_per_bar:
                self.beat_in_bar = 0
                self._advance_bar(events)
        
        # ── Periodic drift check ──
        if self.tick_count % self.drift_check_interval == 0:
            self._auto_correct_drift()
        
        return events
    
    # ─── Bar/Section/Phrase Advancement ─────────────────────────────
    
    def _advance_bar(self, events: List[TimingEvent]):
        """Handle bar boundary."""
        self.bar_in_phrase += 1
        self.bar_in_form += 1
        
        events.append(TimingEvent(
            boundary=BoundaryType.BAR,
            beat_in_bar=0,
            bar_in_phrase=self.bar_in_phrase,
            bar_in_form=self.bar_in_form,
            section=self.current_section.label,
            phrase=self.phrase_count,
            phase=self.bar_phase,
            swing_offset=0.0,
            tick=self.tick_count,
        ))
        
        # Advance form position
        section_changed = self._advance_form()
        if section_changed:
            events.append(TimingEvent(
                boundary=BoundaryType.SECTION_CHANGE,
                beat_in_bar=0,
                bar_in_phrase=self.bar_in_phrase,
                bar_in_form=self.bar_in_form,
                section=self.current_section.label,
                phrase=self.phrase_count,
                phase=self.bar_phase,
                swing_offset=0.0,
                tick=self.tick_count,
            ))
        
        # Check for phrase boundary
        if self.bar_in_phrase >= self.bars_per_phrase:
            self.bar_in_phrase = 0
            self.phrase_count += 1
            events.append(TimingEvent(
                boundary=BoundaryType.PHRASE,
                beat_in_bar=0,
                bar_in_phrase=0,
                bar_in_form=self.bar_in_form,
                section=self.current_section.label,
                phrase=self.phrase_count,
                phase=self.phrase_phase,
                swing_offset=0.0,
                tick=self.tick_count,
            ))
    
    def _advance_form(self) -> bool:
        """Advance form position. Returns True if section changed."""
        self.bar_in_section += 1
        section = self.current_section
        
        if self.bar_in_section >= section.bars:
            self.bar_in_section = 0
            self.section_repeat_count += 1
            
            if self.section_repeat_count >= section.repeats:
                self.section_repeat_count = 0
                self.current_section_idx += 1
                
                if self.current_section_idx >= len(self.form.sections):
                    self.current_section_idx = 0  # Loop form
                
                return True  # Section changed
        
        return False
    
    # ─── Swing ──────────────────────────────────────────────────────
    
    def _swing_offset(self, beat_in_bar: int) -> float:
        """
        Compute swing offset for the given beat position.
        Off-beats are delayed; downbeats are on time.
        """
        # Map beat position to groove template index
        groove_idx = (beat_in_bar * 2) % len(self.groove.offsets)
        groove_offset = self.groove.offsets[groove_idx]
        
        # Add swing factor for off-beats
        if beat_in_bar % 2 == 1:
            return groove_offset * self.beat_period + self.swing * self.beat_period
        else:
            return groove_offset * self.beat_period
    
    # ─── Drift ──────────────────────────────────────────────────────
    
    def observe_other(self, other_id: int, observed_time: float, 
                       predicted_time: float):
        """
        Called when we hear another agent play on a beat boundary.
        Updates our drift estimate for that agent.
        """
        delta = observed_time - predicted_time
        
        if other_id not in self.drift_estimates:
            self.drift_estimates[other_id] = 0.0
            self.drift_history[other_id] = []
        
        # EMA update
        self.drift_estimates[other_id] = (
            self.ema_alpha * delta + 
            (1 - self.ema_alpha) * self.drift_estimates[other_id]
        )
        
        self.drift_history[other_id].append(delta)
        if len(self.drift_history[other_id]) > 100:
            self.drift_history[other_id].pop(0)
        
        # Update my drift estimate
        self._compute_my_drift()
    
    def _compute_my_drift(self):
        """Estimate my drift relative to the ensemble."""
        if not self.drift_estimates:
            self.my_drift = 0.0
            return
        
        # Average of all pairwise drifts
        avg = sum(self.drift_estimates.values()) / len(self.drift_estimates)
        self.my_drift = -avg / (len(self.drift_estimates) + 1)
    
    def _auto_correct_drift(self):
        """Apply automatic drift correction based on current estimate."""
        abs_drift = abs(self.my_drift)
        
        if abs_drift < 0.005:  # < 5ms: no correction
            return
        
        if abs_drift >= self.snap_threshold:  # >= 50ms: immediate snap
            self.tau -= self.my_drift
            self.correction_applied = -self.my_drift
            self.my_drift = 0.0
            # Recompute t-minus from new phase
            self.t_minus_beat = self.beat_period * (1.0 - self.beat_phase)
        elif abs_drift >= 0.015:  # >= 15ms: strong correction
            correction = self.strong_alpha * self.my_drift
            self.tau -= correction
            self.correction_applied = -correction
        else:  # 5-15ms: gradual correction
            correction = self.gradual_alpha * self.my_drift
            self.tau -= correction
            self.correction_applied = -correction
    
    def drift_report(self) -> DriftReport:
        """Get current drift status."""
        return DriftReport(
            estimated_drift_ms=self.my_drift * 1000,
            confidence=self._drift_confidence(),
            correction_applied_ms=self.correction_applied * 1000,
            n_observations=sum(len(h) for h in self.drift_history.values()),
        )
    
    def _drift_confidence(self) -> float:
        if not self.drift_history:
            return 0.0
        total_var = 0.0
        n = 0
        for hist in self.drift_history.values():
            if len(hist) < 2:
                continue
            mean = sum(hist) / len(hist)
            var = sum((x - mean)**2 for x in hist) / len(hist)
            total_var += var
            n += 1
        if n == 0:
            return 0.0
        avg_var = total_var / n
        return 1.0 / (1.0 + avg_var * 10000)
    
    # ─── Tempo Changes ──────────────────────────────────────────────
    
    def set_tempo(self, new_tempo: float, transition_beats: float = 4.0):
        """
        Smoothly transition to a new tempo over the given number of beats.
        Uses linear interpolation to avoid audible jumps.
        """
        old_tempo = self.tempo
        beats_remaining = transition_beats
        delta_per_beat = (new_tempo - old_tempo) / transition_beats
        
        # For simplicity in this pseudocode, apply immediately
        # A production impl would interpolate over transition_beats
        self.tempo = new_tempo
        self.beat_period = 60.0 / new_tempo
        self.bar_period = self.beat_period * self.time_signature.beats_per_bar
        self.phrase_period = self.bar_period * self.bars_per_phrase
    
    # ─── Properties ─────────────────────────────────────────────────
    
    @property
    def current_section(self) -> FormSection:
        return self.form.sections[self.current_section_idx]
    
    @property
    def form_position(self) -> dict:
        return {
            "beat": self.beat_in_bar,
            "bar": self.bar_in_form,
            "section": self.current_section.label,
            "section_bar": self.bar_in_section,
            "phrase": self.phrase_count,
        }


# ─── Demo ────────────────────────────────────────────────────────────────

def demo_12_bar_blues():
    """Run a t-minus engine through one chorus of 12-bar blues."""
    
    blues_form = FormSpec(
        name="12-bar-blues",
        sections=[
            FormSection("I",  4, 1),   # Bars 1-4:  I chord
            FormSection("IV", 2, 1),   # Bars 5-6:  IV chord
            FormSection("I",  2, 1),   # Bars 7-8:  I chord
            FormSection("V",  1, 1),   # Bar 9:     V chord
            FormSection("IV", 1, 1),   # Bar 10:    IV chord
            FormSection("I",  2, 1),   # Bars 11-12: I chord
        ],
    )
    
    engine = TMinusEngine(
        agent_id=0,
        tempo=120.0,
        form=blues_form,
        swing=0.33,          # Triplet swing
        bars_per_phrase=12,   # One chorus = one phrase
    )
    
    print(f"T-Minus Engine: 12-bar blues at 120 BPM with swing")
    print(f"{'='*60}")
    
    dt = 0.001  # 1ms ticks
    events_fired = []
    
    # Run for 24 seconds (2 choruses at 120 BPM)
    for _ in range(24000):
        events = engine.tick(dt)
        for e in events:
            events_fired.append(e)
            if e.boundary == BoundaryType.SECTION_CHANGE:
                print(f"  Bar {e.bar_in_form+1:2d} → Section {e.section}")
            elif e.boundary == BoundaryType.PHRASE:
                print(f"  --- End of phrase {e.phrase} ---")
    
    print(f"\nTotal events: {len(events_fired)}")
    print(f"Final form position: {engine.form_position}")


if __name__ == "__main__":
    demo_12_bar_blues()
```

---

## Timing Properties and Guarantees

### Property 1: Asynchronous Independence

**Statement**: Each agent's timing engine runs independently. No agent ever blocks waiting for another agent's clock.

**Guarantee**: The `tick()` function depends only on local state. Communication with other agents (drift observation) is asynchronous and non-blocking.

### Property 2: Bounded Drift

**Statement**: With correction enabled, agent drift is bounded.

**Theorem**: If each agent applies gradual correction with α ∈ (0, 1] whenever drift exceeds ε, then:

```
lim sup |δᵢ(t)| ≤ ε / α
```

In practice: with α = 0.05 and ε = 5ms, steady-state drift is bounded by 100ms (though typically much less).

### Property 3: Phase Convergence

**Statement**: The ensemble converges to a shared phase.

**Theorem** (Phase Consensus): Under the correction rule `φᵢ ← φᵢ + α(φ̄ - φᵢ)`, with α ∈ (0, 1/L) where L is the graph Laplacian's spectral radius, the ensemble converges exponentially to phase consensus.

### Property 4: Swing Consistency

**Statement**: All agents applying the same swing factor s will produce consistent off-beat timing.

**Guarantee**: Swing offset is a deterministic function of beat position and s. If two agents agree on s (through intention field consensus), their off-beats will align within drift tolerance.

### Property 5: Form Consistency

**Statement**: All agents following the same form spec will cycle through sections in lockstep.

**Guarantee**: Form position is deterministic given beat/bar counting. If agents agree on the form and start aligned, they stay aligned. Section transitions are triggered by bar boundaries, which are triggered by beat boundaries — all locally computable.

### Property 6: No Timing Discontinuities (Gradual Mode)

**Statement**: Gradual correction never causes an audible timing jump.

**Guarantee**: Maximum single correction is α × δ. With α = 0.05 and δ = 15ms, maximum jump is 0.75ms — well below human perception threshold (~5ms).

---

## Summary

| Aspect | t-minus approach | Traditional approach |
|--------|-----------------|---------------------|
| Clock | Local per-agent | Shared master |
| Sync | Prediction + correction | Lock-step |
| Feel | Human (micro-timing) | Mechanical (quantized) |
| Failure mode | Graceful drift | Hard stop |
| Scalability | O(n) pairwise drift | O(1) but centralized |
| Swing | Per-agent groove template | Global swing setting |
| Recovery | Gradual correction | Re-sync from master |
| Musical quality | Alive, breathing | Perfect but sterile |
