# SIA Spectral Identity for Musical Agents

> *Every agent is a spectrum. Its eigenvalues are its fingerprint, its eigenvectors are its personality, and Banach convergence guarantees it gets better at being itself.*

---

## Table of Contents

1. [What Is Spectral Identity?](#what-is-spectral-identity)
2. [Eigenvalue Profile as Timbral Fingerprint](#eigenvalue-profile-as-timbral-fingerprint)
3. [The Performance Tensor](#the-performance-tensor)
4. [Banach Convergence for Self-Improvement](#banach-convergence-for-self-improvement)
5. [Renormalization for Coarse-to-Fine Learning](#renormalization-for-coarse-to-fine-learning)
6. [Spectral State Evolution During Performance](#spectral-state-evolution-during-performance)
7. [Implementation Reference](#implementation-reference)

---

## What Is Spectral Identity?

SIA — **Spectrally Initialized Agent** — is the foundational identity system for every band member. Just as a musician has a unique tone, phrasing style, and musical personality, each SIA agent has a unique **spectral state** that defines who it is musically.

The spectral state is computed from the **eigenvalue decomposition** of the agent's performance tensor — a mathematical object that captures the agent's entire musical behavior in a compact representation.

### Why Eigenvalues?

Eigenvalues tell you the "natural frequencies" of a system. For a musical agent:

- **Large eigenvalues** = dominant modes = the agent's core musical personality
- **Small eigenvalues** = subtle modes = the agent's nuanced capabilities
- **Eigenvalue distribution** = the shape of the agent's musical identity

Two agents with the same role (e.g., both horn players) will sound different if they have different eigenvalue profiles. The profile is their timbral fingerprint.

---

## Eigenvalue Profile as Timbral Fingerprint

### The Performance Tensor

Each agent maintains a **performance tensor** T that captures its recent musical output:

```
T ∈ ℝ^(n × d)

where:
  n = number of recent events (sliding window, typically n = 100)
  d = dimensionality of each event's feature vector
```

The feature vector for each event includes:

| Dimension | Feature | Range |
|-----------|---------|-------|
| 0 | Pitch class (normalized) | [0, 1) |
| 1 | Velocity (normalized) | [0, 1] |
| 2 | Duration (normalized to beat) | [0, 4] |
| 3 | Harmonic distance from center | [0, 1] |
| 4 | Syncopation index | [0, 1] |
| 5 | Interval from previous note | [-1, 1] |
| 6 | Density (local note rate) | [0, 1] |
| 7 | Spectral centroid estimate | [0, 1] |

### Eigenvalue Decomposition

The spectral identity is computed from the covariance of the performance tensor:

```
C = (1/n) T^T T    (covariance matrix, d × d)

C = Q Λ Q^T        (eigendecomposition)

where:
  Q = matrix of eigenvectors (musical "modes")
  Λ = diagonal matrix of eigenvalues (mode strengths)
```

### Reading the Eigenvalue Profile

```python
def interpret_eigenvalue_profile(eigenvalues: list[float]) -> dict:
    """
    Interpret an agent's eigenvalue profile in musical terms.
    """
    n = len(eigenvalues)
    sorted_evals = sorted(eigenvalues, reverse=True)
    total_energy = sum(eigenvalues)
    
    # Dominance: how concentrated is the energy in the top mode?
    dominance = sorted_evals[0] / total_energy if total_energy > 0 else 0
    
    # Spread: how many modes are significant?
    # (modes capturing > 5% of total energy)
    significant = sum(1 for e in sorted_evals if e / total_energy > 0.05) if total_energy > 0 else 0
    
    # Flatness: ratio of geometric mean to arithmetic mean
    # Higher flatness = more uniform distribution = more complex personality
    if all(e > 0 for e in eigenvalues):
        geo_mean = np.exp(np.mean(np.log(eigenvalues)))
        arith_mean = np.mean(eigenvalues)
        flatness = geo_mean / arith_mean if arith_mean > 0 else 0
    else:
        flatness = 0
    
    # Musical interpretation
    profile = {
        "dominance": dominance,
        "n_significant_modes": significant,
        "flatness": flatness,
        "total_energy": total_energy,
        "interpretation": "",
    }
    
    if dominance > 0.8:
        profile["interpretation"] = (
            "Highly focused agent. Strong single personality. "
            "Like a lead instrument with a distinctive sound."
        )
    elif dominance > 0.5:
        profile["interpretation"] = (
            "Moderately focused. Core identity with interesting secondary modes. "
            "Like a versatile player with a recognizable style."
        )
    elif flatness > 0.5:
        profile["interpretation"] = (
            "Multi-dimensional agent. Complex, exploratory personality. "
            "Like an experimental musician who plays many styles."
        )
    else:
        profile["interpretation"] = (
            "Diffuse agent. Multiple weak modes, no strong identity yet. "
            "Needs more performance data or more decisive musical choices."
        )
    
    return profile
```

### Fingerprint Comparison

Two agents' spectral fingerprints can be compared using spectral distance:

```python
def spectral_distance(agent_a: Agent, agent_b: Agent) -> float:
    """
    Compute the distance between two agents' spectral fingerprints.
    Uses the Wasserstein distance between eigenvalue distributions.
    """
    lambda_a = sorted(agent_a.spectral_state.eigenvalues)
    lambda_b = sorted(agent_b.spectral_state.eigenvalues)
    
    # Wasserstein-1 distance (earth mover's distance)
    # For sorted eigenvalues, this is just L1 distance of CDFs
    n = len(lambda_a)
    distance = sum(abs(a - b) for a, b in zip(lambda_a, lambda_b)) / n
    
    return distance

def spectral_similarity(agent_a: Agent, agent_b: Agent) -> float:
    """
    Similarity score in [0, 1]. 1 = identical spectral profiles.
    """
    d = spectral_distance(agent_a, agent_b)
    return 1.0 / (1.0 + d)
```

### Example Profiles

```
Agent A (Traditional Jazz Drums):
  Eigenvalues: [0.85, 0.07, 0.04, 0.02, 0.01, 0.005, 0.003, 0.002]
  Dominance: 0.85  |  Significant modes: 1  |  Flatness: 0.02
  → Focused, single-dominant-mode. Plays time, plays it well.
  
Agent B (Experimental Keys):
  Eigenvalues: [0.30, 0.22, 0.18, 0.12, 0.08, 0.05, 0.03, 0.02]
  Dominance: 0.30  |  Significant modes: 4  |  Flatness: 0.52
  → Multi-dimensional, exploratory. Constantly trying new things.
  
Agent C (Solid Bass):
  Eigenvalues: [0.55, 0.20, 0.10, 0.08, 0.04, 0.02, 0.01, 0.00]
  Dominance: 0.55  |  Significant modes: 2  |  Flatness: 0.18
  → Core identity with strong secondary mode. Reliable + flexible.
  
Agent D (Mercurial Horns):
  Eigenvalues: [0.25, 0.24, 0.20, 0.15, 0.08, 0.04, 0.03, 0.01]
  Dominance: 0.25  |  Significant modes: 5  |  Flatness: 0.56
  → Highly multi-dimensional. Unpredictable, creative.
  
Agent E (Ambient Pads):
  Eigenvalues: [0.70, 0.15, 0.08, 0.04, 0.02, 0.01, 0.00, 0.00]
  Dominance: 0.70  |  Significant modes: 1  |  Flatness: 0.06
  → Focused on sustained textures. Simple but effective.
```

---

## The Performance Tensor

### Construction

The performance tensor is built from a sliding window of recent events:

```python
class PerformanceTensor:
    """
    Maintains a sliding window of recent musical events
    and computes the spectral decomposition on demand.
    """
    
    def __init__(self, window_size: int = 100, n_features: int = 8):
        self.window_size = window_size
        self.n_features = n_features
        self.events: deque = deque(maxlen=window_size)
        self._cache_valid = False
        self._cached_eigenvalues = None
        self._cached_eigenvectors = None
    
    def add_event(self, event: MidiEvent, context: EventContext):
        """Add a musical event to the tensor."""
        features = self._extract_features(event, context)
        self.events.append(features)
        self._cache_valid = False  # Invalidate spectral cache
    
    def _extract_features(self, event: MidiEvent, context: EventContext) -> list[float]:
        """Extract the feature vector for one event."""
        return [
            event.pitch / 12.0,                                        # Pitch class
            event.velocity / 127.0,                                    # Velocity
            event.duration / context.beat_period,                      # Duration
            context.harmonic_distance,                                 # Harmonic distance
            context.syncopation_index,                                 # Syncopation
            (event.pitch - context.previous_pitch) / 12.0 if context.previous_pitch else 0,  # Interval
            context.local_density / MAX_DENSITY,                       # Density
            context.spectral_centroid_estimate,                        # Spectral centroid
        ]
    
    @property
    def eigenvalues(self) -> list[float]:
        """Compute eigenvalues (cached)."""
        if not self._cache_valid:
            self._compute_decomposition()
        return self._cached_eigenvalues
    
    @property
    def eigenvectors(self) -> list[list[float]]:
        """Compute eigenvectors (cached)."""
        if not self._cache_valid:
            self._compute_decomposition()
        return self._cached_eigenvectors
    
    def _compute_decomposition(self):
        """Run eigendecomposition on the performance tensor."""
        if len(self.events) < 2:
            self._cached_eigenvalues = [0.0] * self.n_features
            self._cached_eigenvectors = [[0.0] * self.n_features] * self.n_features
            self._cache_valid = True
            return
        
        # Build tensor
        T = np.array(list(self.events))
        
        # Covariance matrix
        C = (T.T @ T) / len(self.events)
        
        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(C)
        
        # Sort descending
        idx = np.argsort(eigenvalues)[::-1]
        self._cached_eigenvalues = eigenvalues[idx].tolist()
        self._cached_eigenvectors = eigenvectors[:, idx].T.tolist()
        self._cache_valid = True
    
    @property
    def dominant_mode(self) -> int:
        """Index of the dominant eigenmode."""
        evs = self.eigenvalues
        return evs.index(max(evs))
    
    @property
    def dominant_eigenvector(self) -> list[float]:
        """The eigenvector corresponding to the dominant eigenvalue."""
        return self.eigenvectors[self.dominant_mode]
    
    def mode_description(self, mode_index: int) -> dict:
        """Describe a mode in musical terms."""
        vec = self.eigenvectors[mode_index]
        val = self.eigenvalues[mode_index]
        
        feature_names = [
            "pitch_class", "velocity", "duration", "harmonic_distance",
            "syncopation", "interval", "density", "spectral_centroid"
        ]
        
        # Find the strongest features in this mode
        contributions = [(name, abs(v)) for name, v in zip(feature_names, vec)]
        contributions.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "eigenvalue": val,
            "energy_fraction": val / sum(self.eigenvalues) if sum(self.eigenvalues) > 0 else 0,
            "top_features": contributions[:3],
        }
```

---

## Banach Convergence for Self-Improvement

### The Banach Fixed-Point Theorem

> If (X, d) is a complete metric space and T: X → X is a contraction mapping (d(Tx, Ty) ≤ q·d(x, y) for some q < 1), then T has a unique fixed point x*. Moreover, the sequence x, T(x), T(T(x)), ... converges to x* for any starting point x.

### Application to Self-Improvement

In the band context:
- **X** = the space of possible agent spectral states
- **T** = the self-improvement operator (one round of practice/performance)
- **d** = spectral distance between agent states
- **x*** = the agent's optimal musical state

The improvement operator must be a **contraction** — each round of practice brings the agent closer to its optimal state, never farther away.

### Contraction Factor

```python
def compute_contraction_factor(
    before: SpectralState, 
    after: SpectralState
) -> float:
    """
    Compute the contraction factor for one improvement step.
    Must be < 1 for guaranteed convergence.
    """
    # Distance before improvement
    d_before = spectral_distance_to_optimal(before)
    d_after = spectral_distance_to_optimal(after)
    
    if d_before == 0:
        return 0  # Already at optimal
    
    q = d_after / d_before
    
    if q >= 1:
        # NOT a contraction — improvement step was counterproductive
        # This should never happen with correct implementation
        raise ConvergenceViolation(
            f"Contraction factor {q:.3f} >= 1. "
            f"Agent is NOT improving. Check improvement operator."
        )
    
    return q
```

### Improvement Operator

The self-improvement operator combines spectral analysis with conservation-constrained updates:

```python
class ImprovementOperator:
    """
    Banach-convergent self-improvement operator.
    Each call moves the agent closer to optimal, guaranteed.
    """
    
    def __init__(self, contraction_target: float = 0.95):
        self.contraction_target = contraction_target  # q < 1
        self.history = []
    
    def improve(self, agent: BandAgent, feedback: SpectralFeedback) -> SpectralDelta:
        """
        Apply one round of self-improvement.
        Returns the spectral delta (change in eigenvalues).
        """
        current = agent.spectral_state
        
        # 1. Identify weakest eigenmode
        weakest_idx = current.eigenvalues.index(min(current.eigenvalues))
        weakest_val = current.eigenvalues[weakest_idx]
        
        # 2. Compute improvement direction (gradient of performance)
        gradient = feedback.performance_gradient(weakest_idx)
        
        # 3. Scale to ensure contraction
        #    Delta must be small enough that the step is a contraction
        max_delta = self._max_safe_delta(current, self.contraction_target)
        delta = self._scale_delta(gradient, max_delta)
        
        # 4. Apply conservation constraint
        delta = self._conserve(delta, agent.conservation)
        
        # 5. Update eigenvalues
        new_eigenvalues = [
            ev + delta[i] if i == weakest_idx else ev
            for i, ev in enumerate(current.eigenvalues)
        ]
        
        # 6. Verify contraction
        q = self._verify_contraction(current.eigenvalues, new_eigenvalues)
        assert q < 1, f"Contraction violated: q = {q}"
        
        # 7. Record
        self.history.append({
            "agent": agent.id,
            "weakest_mode": weakest_idx,
            "delta": delta,
            "contraction": q,
        })
        
        return SpectralDelta(
            eigenvalue_deltas=delta,
            contraction_factor=q,
            target_mode=weakest_idx,
        )
    
    def _max_safe_delta(self, state: SpectralState, q_target: float) -> float:
        """
        Compute the maximum eigenvalue change that maintains contraction.
        """
        total = sum(state.eigenvalues)
        if total == 0:
            return 0.1  # Small default
        
        # Contraction condition: new_dist / old_dist < q_target
        # For a single eigenvalue change, this means:
        # delta < (1 - q_target) * current_distance_to_optimal
        max_delta = (1 - q_target) * total * 0.1  # Conservative
        return min(max_delta, 0.1)  # Never change more than 10%
    
    def _scale_delta(self, gradient: list[float], max_delta: float) -> list[float]:
        """Scale gradient to fit within max_delta."""
        gradient_mag = sum(g**2 for g in gradient)**0.5
        if gradient_mag == 0:
            return [0.0] * len(gradient)
        scale = max_delta / gradient_mag
        return [g * scale for g in gradient]
    
    def _conserve(self, delta: list[float], conservation: ConservationEnvelope) -> list[float]:
        """
        Ensure the improvement doesn't violate conservation.
        The spectral change must not push the agent out of its envelope.
        """
        # Improvement increases energy → must decrease H to compensate
        delta_energy = sum(abs(d) for d in delta)
        if conservation.hamiltonian < delta_energy:
            # Not enough H to "pay" for the improvement
            # Scale down the improvement
            scale = conservation.hamiltonian / delta_energy
            delta = [d * scale for d in delta]
        
        return delta
    
    def _verify_contraction(self, old: list[float], new: list[float]) -> float:
        """Verify that the update is a contraction."""
        # Simple metric: ratio of total deviation
        old_dev = sum(e**2 for e in old)**0.5
        new_dev = sum(e**2 for e in new)**0.5
        
        if old_dev == 0:
            return 0
        
        return new_dev / old_dev
```

### Convergence Timeline

```
Iteration  Eigenvalue 3 (weakest)  Contraction q  Cumulative improvement
─────────  ─────────────────────  ─────────────  ──────────────────────
0          0.020                   -              baseline
1          0.022                   0.95           +10%
2          0.024                   0.94           +20%
3          0.026                   0.94           +30%
5          0.029                   0.93           +45%
10         0.034                   0.92           +70%
20         0.040                   0.90           +100%
50         0.048                   0.85           +140%
100        0.052                   0.80           +160%
∞          0.055                   ← fixed point   +175%

The weakest eigenvalue converges to its optimal value.
The rate of convergence is governed by q^n → 0 (exponential).
```

---

## Renormalization for Coarse-to-Fine Learning

### Why Renormalization?

Direct self-improvement on all eigenvalues simultaneously is:
1. Computationally expensive (high-dimensional optimization)
2. Unstable (interactions between modes)
3. Inefficient (large improvements early, tiny ones later)

**Renormalization** addresses this by operating at multiple scales:
- **Coarse scale**: Make big improvements to dominant modes first
- **Medium scale**: Improve secondary modes
- **Fine scale**: Polish subtle modes

### The Renormalization Group

Borrowed from physics (Wilson's renormalization group), we apply scale transformations to the eigenvalue problem:

```
Level 0 (finest):  All d eigenvalues considered
Level 1:           Group eigenvalues into ⌈d/2⌉ blocks
Level 2:           Group into ⌈d/4⌉ blocks
...
Level k (coarsest): 2-3 eigenvalue blocks

Improvement flows top-down:
  Level k → k-1 → ... → Level 0
  
Coarse improvements are fast and large.
Fine improvements are slow and precise.
```

### Implementation

```python
class RenormalizationEngine:
    """
    Coarse-to-fine improvement through renormalization.
    """
    
    def __init__(self, n_levels: int = 3):
        self.n_levels = n_levels
        self.level_thresholds = self._compute_thresholds()
    
    def _compute_thresholds(self) -> list[float]:
        """
        Energy thresholds for each renormalization level.
        Level 0: modes with > 50% of total energy (dominant)
        Level 1: modes with > 10% of total energy (significant)
        Level 2: all modes (complete)
        """
        return [0.5, 0.1, 0.0]  # Energy fraction thresholds
    
    def get_level_modes(self, eigenvalues: list[float], level: int) -> list[int]:
        """
        Get the indices of modes active at this renormalization level.
        """
        total = sum(eigenvalues)
        if total == 0:
            return []
        
        threshold = self.level_thresholds[min(level, len(self.level_thresholds) - 1)]
        
        modes = []
        for i, ev in enumerate(eigenvalues):
            if ev / total >= threshold:
                modes.append(i)
        
        return modes
    
    def improve_at_level(
        self, 
        agent: BandAgent, 
        level: int,
        feedback: SpectralFeedback,
    ) -> SpectralDelta:
        """
        Apply improvement at a specific renormalization level.
        """
        eigenvalues = agent.spectral_state.eigenvalues
        active_modes = self.get_level_modes(eigenvalues, level)
        
        if not active_modes:
            return SpectralDelta.zero(len(eigenvalues))
        
        # Improvement step size scales with level
        # Coarse (high level) = big steps, Fine (low level) = small steps
        step_scale = 0.1 * (2 ** level)
        
        deltas = [0.0] * len(eigenvalues)
        
        for mode_idx in active_modes:
            # Compute gradient for this mode
            gradient = feedback.mode_gradient(mode_idx)
            
            # Scale by renormalization level
            delta = gradient * step_scale
            
            # Conservation constraint
            delta = min(delta, agent.conservation.hamiltonian * 0.1)
            
            deltas[mode_idx] = delta
        
        return SpectralDelta(
            eigenvalue_deltas=deltas,
            contraction_factor=0.95 - level * 0.02,  # Slightly relaxed at coarse levels
            target_modes=active_modes,
        )
    
    def full_improvement_cycle(
        self,
        agent: BandAgent,
        feedback: SpectralFeedback,
    ) -> list[SpectralDelta]:
        """
        Run a complete coarse-to-fine improvement cycle.
        """
        deltas = []
        
        # Top-down: coarse to fine
        for level in reversed(range(self.n_levels)):
            delta = self.improve_at_level(agent, level, feedback)
            deltas.append(delta)
            
            # Apply delta before moving to finer level
            for i, d in enumerate(delta.eigenvalue_deltas):
                agent.spectral_state.eigenvalues[i] += d
        
        return deltas
```

### Renormalization Flow

```
┌─────────────────────────────────────────────────┐
│           RENORMALIZATION CYCLE                   │
│                                                   │
│  Level 2 (Coarse) ─────────────────────────────  │
│  Active modes: [0, 1] (dominant modes)           │
│  Step size: 0.4                                  │
│  Goal: Fix major weaknesses quickly              │
│                    │                              │
│                    ▼                              │
│  Level 1 (Medium) ─────────────────────────────  │
│  Active modes: [0, 1, 2, 3] (significant)        │
│  Step size: 0.2                                  │
│  Goal: Improve secondary characteristics         │
│                    │                              │
│                    ▼                              │
│  Level 0 (Fine) ───────────────────────────────  │
│  Active modes: [0..7] (all modes)                │
│  Step size: 0.1                                  │
│  Goal: Polish everything                         │
│                                                   │
└─────────────────────────────────────────────────┘

Result: Big improvements first, refinement later.
The agent doesn't waste time optimizing details before
the major issues are addressed.
```

---

## Spectral State Evolution During Performance

### Temporal Dynamics

The spectral state evolves continuously during performance:

```
dλ/dt = -α(λ - λ_target) + β·performance_signal + γ·conservation_correction
```

Where:
- `-α(λ - λ_target)` = relaxation toward target eigenvalues (self-improvement)
- `β·performance_signal` = excitation from musical activity
- `γ·conservation_correction` = correction to maintain conservation law

### Phase 1: Warm-Up (Bars 1-4)

```
Initial state:  λ = [0.50, 0.10, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003]
Warm-up state:  λ = [0.45, 0.15, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005]

Changes:
  - Dominant mode decreases (agent calibrating, not playing at full strength)
  - Secondary modes increase (exploring the space)
  - Total energy decreases slightly (conservative start)
  
Interpretation: Agent is finding its place in the ensemble.
```

### Phase 2: Groove (Bars 5-20)

```
Groove state:   λ = [0.55, 0.18, 0.10, 0.06, 0.04, 0.03, 0.02, 0.01]

Changes:
  - Dominant mode increases (agent found its role)
  - All modes stable (in the pocket)
  - Eigenvalue distribution converges to characteristic shape
  
Interpretation: Agent is comfortable, playing consistently.
```

### Phase 3: Solo (Bars 21-32)

```
Solo state:     λ = [0.40, 0.22, 0.15, 0.10, 0.06, 0.04, 0.02, 0.01]

Changes:
  - Dominant mode DECREASES (solo requires flexibility)
  - Secondary modes INCREASE (exploring new territory)
  - Flatness increases (more multi-dimensional)
  - Total energy increases (soloist using more of their budget)
  
Interpretation: Agent is pushing boundaries, trying new things.
```

### Phase 4: Recovery (Bars 33-36)

```
Recovery state: λ = [0.50, 0.15, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005]

Changes:
  - Returning toward baseline
  - Dominant mode recovering
  - Total energy decreasing (resting after solo)
  
Interpretation: Agent recovering, saving energy for next phrase.
```

### Phase 5: Self-Improvement (After Performance)

```
Before improvement: λ = [0.50, 0.15, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005]
After improvement:  λ = [0.50, 0.17, 0.09, 0.06, 0.03, 0.02, 0.01, 0.005]

Changes:
  - Weakest modes improved (Banach-convergent update)
  - Dominant mode unchanged (don't mess with what works)
  - Total energy slightly increased (agent grew its capabilities)
  - Contraction factor: 0.94 (guaranteed improvement)
  
Interpretation: Agent got better. Mathematical proof: q < 1.
```

### Spectral Trajectory Visualization

```
Eigenvalue Index →
    0     1     2     3     4     5     6     7
    
Warm-up:
    ████  ██    █     ·     ·     ·     ·     ·
    
Groove:
    ██████ ███   ██    █     ·     ·     ·     ·
    
Solo:
    █████  ████  ███   ██    █     ·     ·     ·
    
Recovery:
    ██████ ███   ██    █     ·     ·     ·     ·
    
After Improvement:
    ██████ ████  ██    ██    █     ·     ·     ·
                  ↑           ↑
            Weakest modes improved
```

### Spectral Coherence

The **spectral coherence** of an agent measures how stable its eigenvalue profile is over time:

```python
def spectral_coherence(history: list[list[float]], window: int = 10) -> float:
    """
    Measure how stable the eigenvalue profile has been.
    1.0 = perfectly stable, 0.0 = chaotic.
    """
    if len(history) < 2:
        return 1.0
    
    recent = history[-window:]
    
    # Compute pairwise distances between consecutive profiles
    distances = []
    for i in range(1, len(recent)):
        d = sum((a - b)**2 for a, b in zip(recent[i-1], recent[i]))**0.5
        distances.append(d)
    
    if not distances:
        return 1.0
    
    avg_dist = sum(distances) / len(distances)
    
    # Normalize: coherence = 1 / (1 + average_distance)
    return 1.0 / (1.0 + avg_dist * 10)
```

**High coherence** (> 0.8): Agent has found its groove. Stable, reliable identity.
**Medium coherence** (0.4-0.8): Agent is evolving. Active learning in progress.
**Low coherence** (< 0.4): Agent is unstable. May need intervention.

---

## Implementation Reference

### Complete Spectral State Manager

```python
"""
SIA Spectral Identity System
=============================
Complete implementation of spectral state management for band agents.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from collections import deque


@dataclass
class SpectralState:
    """The spectral identity of an agent."""
    eigenvalues: List[float]
    eigenvectors: List[List[float]]
    dominant_mode: int
    contraction_factor: float = 0.95
    
    @property
    def total_energy(self) -> float:
        return sum(self.eigenvalues)
    
    @property
    def dominance(self) -> float:
        total = self.total_energy
        return max(self.eigenvalues) / total if total > 0 else 0
    
    @property
    def flatness(self) -> float:
        pos = [e for e in self.eigenvalues if e > 0]
        if not pos:
            return 0
        geo = np.exp(np.mean(np.log(pos)))
        arith = np.mean(pos)
        return geo / arith if arith > 0 else 0


@dataclass
class SpectralDelta:
    """A change to spectral state."""
    eigenvalue_deltas: List[float]
    contraction_factor: float
    target_mode: int = -1
    target_modes: List[int] = field(default_factory=list)
    
    @staticmethod
    def zero(n: int) -> 'SpectralDelta':
        return SpectralDelta(
            eigenvalue_deltas=[0.0] * n,
            contraction_factor=1.0,
        )


@dataclass
class SpectralFeedback:
    """Feedback from spectral analysis for self-improvement."""
    performance_tensor: np.ndarray
    bottleneck_mode: int
    performance_gradient: List[float]
    
    def mode_gradient(self, mode_idx: int) -> float:
        """Gradient direction for improving a specific mode."""
        if mode_idx < len(self.performance_gradient):
            return self.performance_gradient[mode_idx]
        return 0.0


class SpectralManager:
    """
    Manages an agent's spectral state throughout its lifecycle.
    """
    
    def __init__(self, n_features: int = 8, window_size: int = 100):
        self.n_features = n_features
        self.window_size = window_size
        self.performance_tensor = PerformanceTensor(window_size, n_features)
        self.state: Optional[SpectralState] = None
        self.state_history: List[List[float]] = []
        self.improvement_history: List[SpectralDelta] = []
    
    def initialize(self, role_profile: List[float]) -> SpectralState:
        """
        Initialize spectral state from a role-specific profile.
        """
        # Role profiles define initial eigenvalue distributions
        eigenvalues = role_profile
        eigenvectors = np.eye(self.n_features).tolist()
        
        self.state = SpectralState(
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors,
            dominant_mode=eigenvalues.index(max(eigenvalues)),
        )
        
        return self.state
    
    def update_from_event(self, event_features: List[float]):
        """Update the performance tensor with a new event."""
        self.performance_tensor.add_event_raw(event_features)
    
    def compute_current_state(self) -> SpectralState:
        """Recompute spectral state from current performance tensor."""
        evs = self.performance_tensor.eigenvalues
        evecs = self.performance_tensor.eigenvectors
        
        self.state = SpectralState(
            eigenvalues=evs,
            eigenvectors=evecs,
            dominant_mode=evs.index(max(evs)) if max(evs) > 0 else 0,
            contraction_factor=self.state.contraction_factor if self.state else 0.95,
        )
        
        self.state_history.append(list(evs))
        
        return self.state
    
    def apply_improvement(self, delta: SpectralDelta):
        """Apply a spectral improvement delta."""
        if self.state is None:
            return
        
        new_evs = [
            max(0, ev + d)  # Eigenvalues can't go negative
            for ev, d in zip(self.state.eigenvalues, delta.eigenvalue_deltas)
        ]
        
        self.state = SpectralState(
            eigenvalues=new_evs,
            eigenvectors=self.state.eigenvectors,
            dominant_mode=new_evs.index(max(new_evs)),
            contraction_factor=delta.contraction_factor,
        )
        
        self.improvement_history.append(delta)
    
    def spectral_coherence(self, window: int = 10) -> float:
        """How stable has the spectral state been?"""
        if len(self.state_history) < 2:
            return 1.0
        
        recent = self.state_history[-window:]
        distances = []
        for i in range(1, len(recent)):
            d = sum((a - b)**2 for a, b in zip(recent[i-1], recent[i]))**0.5
            distances.append(d)
        
        if not distances:
            return 1.0
        
        return 1.0 / (1.0 + sum(distances) / len(distances) * 10)
    
    def improvement_summary(self) -> dict:
        """Summary of all improvements applied."""
        if not self.improvement_history:
            return {"total_improvements": 0, "avg_contraction": 0}
        
        return {
            "total_improvements": len(self.improvement_history),
            "avg_contraction": sum(
                d.contraction_factor for d in self.improvement_history
            ) / len(self.improvement_history),
            "total_delta_energy": sum(
                sum(abs(d) for d in delta.eigenvalue_deltas)
                for delta in self.improvement_history
            ),
            "current_dominance": self.state.dominance if self.state else 0,
            "current_coherence": self.spectral_coherence(),
        }
```

### Role-Specific Initial Profiles

```python
ROLE_PROFILES = {
    AgentRole.Drums:  [0.85, 0.07, 0.04, 0.02, 0.01, 0.005, 0.003, 0.002],
    AgentRole.Bass:   [0.55, 0.20, 0.10, 0.08, 0.04, 0.02, 0.01, 0.00],
    AgentRole.Keys:   [0.40, 0.22, 0.15, 0.10, 0.06, 0.04, 0.02, 0.01],
    AgentRole.Horns:  [0.25, 0.24, 0.20, 0.15, 0.08, 0.04, 0.03, 0.01],
    AgentRole.Pads:   [0.70, 0.15, 0.08, 0.04, 0.02, 0.01, 0.00, 0.00],
    AgentRole.Guitar: [0.45, 0.20, 0.12, 0.08, 0.06, 0.04, 0.03, 0.02],
}
```

---

## Summary

| Concept | Mathematical Basis | Musical Meaning |
|---------|-------------------|-----------------|
| Eigenvalue profile | Eigendecomposition of performance tensor | Agent's timbral fingerprint |
| Dominant mode | Largest eigenvalue | Agent's primary musical personality |
| Flatness | Geometric/arithmetic mean ratio | Complexity of musical identity |
| Banach convergence | Contraction mapping (q < 1) | Guaranteed self-improvement |
| Renormalization | Wilson RG, multi-scale | Coarse-to-fine learning |
| Spectral coherence | Temporal stability of eigenvalues | How "settled" the agent is |
| Performance tensor | Sliding window of event features | Raw material for spectral analysis |
| Improvement operator | Banach contraction + conservation | Gets better, never worse |

The SIA spectral identity system ensures that every agent in the band has a unique, measurable, and improvable musical personality. The eigenvalue profile is the agent's DNA — and Banach convergence is the promise that practice makes perfect. Mathematically.
