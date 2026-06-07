# Conservation Laws in Musical Ensembles

> *γ + H = C: How energy conservation keeps a band of autonomous agents from descending into chaos.*

---

## Table of Contents

1. [The Core Principle](#the-core-principle)
2. [The γ + H = C Formalism](#the-γ--h--c-formalism)
3. [Conservation in Rhythm](#conservation-in-rhythm)
4. [Conservation in Harmony](#conservation-in-harmony)
5. [Conservation in Dynamics](#conservation-in-dynamics)
6. [Energy Transfer Between Agents](#energy-transfer-between-agents)
7. [Equilibrium Conditions](#equilibrium-conditions)
8. [Violations and Recovery](#violations-and-recovery)
9. [The Conservation Matrix](#the-conservation-matrix)
10. [Implementation Reference](#implementation-reference)

---

## The Core Principle

In physics, conservation laws are the deepest constraints on any system. Energy is conserved. Momentum is conserved. These aren't approximations — they're fundamental.

In a musical ensemble, we observe an analogous constraint:

> **The total musical energy of a band is conserved.**

This doesn't mean the music sounds the same volume the whole time. It means:

- If the drummer plays louder, someone else gets quieter — or the overall texture changes
- If the horns play more notes, the rhythm section has room to simplify
- Energy flows between agents; it doesn't appear from nowhere or vanish

This is not an aesthetic preference. It's a **mathematical constraint** that prevents the ensemble from degenerating into noise (too much energy) or silence (too little).

---

## The γ + H = C Formalism

### Definitions

For each agent *i* in the ensemble, we define:

| Symbol | Name | Musical Meaning |
|--------|------|-----------------|
| γᵢ | Kinetic energy | Active playing intensity: note density × velocity |
| Hᵢ | Hamiltonian (potential energy) | Tension, preparation, "about to play" potential |
| Cᵢ | Conservation constant | This agent's energy budget (share of total) |

The conservation law per agent:

```
γᵢ(t) + Hᵢ(t) = Cᵢ    for all t
```

For the ensemble:

```
Σᵢ [γᵢ(t) + Hᵢ(t)] = C_total    for all t
```

where C_total = Σᵢ Cᵢ is the total ensemble energy budget.

### Kinetic Energy (γ)

Kinetic energy represents **active musical output**:

```
γᵢ(t) = α × note_densityᵢ(t) × ⟨velocityᵢ⟩(t) + β × rhythmic_complexityᵢ(t)
```

Where:
- `note_density(t)` = number of active notes per beat
- `⟨velocity⟩(t)` = mean velocity of current notes, normalized to [0, 1]
- `rhythmic_complexity(t)` = syncopation × subdivision_density
- `α, β` are weighting coefficients (typically α = 0.7, β = 0.3)

**High γ**: Agent is playing actively — many notes, high velocity, complex rhythm.
**Low γ**: Agent is resting, sparse, or background.

### Hamiltonian (H)

The Hamiltonian represents **potential energy** — stored musical tension:

```
Hᵢ(t) = tensionᵢ(t) + preparationᵢ(t)
```

Where:
- `tension(t)` = harmonic tension from current chord/interval (computed via tropical distance from tonal center)
- `preparation(t)` = "charging up" energy — an agent preparing to play builds H

**High H**: Agent is building tension, preparing to enter, or holding a dissonant note.
**Low H**: Agent is in a state of resolution, rest, or release.

### Conservation Constant (C)

Each agent's budget is allocated during the tuning phase:

```python
def allocate_budget(n_agents: int, roles: list[AgentRole]) -> list[float]:
    """Distribute energy budget based on roles."""
    # Default weights by role
    weights = {
        AgentRole.Drums:  0.25,  # Rhythm section anchor
        AgentRole.Bass:   0.20,  # Foundation
        AgentRole.Keys:   0.20,  # Harmony + comping
        AgentRole.Horns:  0.15,  # Melodic, intermittent
        AgentRole.Pads:   0.20,  # Textural, sustained
    }
    
    total_weight = sum(weights[r] for r in roles)
    return [C_total * weights[r] / total_weight for r in roles]
```

### The γ ↔ H Exchange

Agents constantly exchange energy between γ and H:

```
When an agent starts playing more (γ ↑):
  → H must decrease by same amount (γ + H = C)
  → Agent "spends" its potential energy on active playing

When an agent rests (γ ↓):
  → H increases (it's "storing" energy)
  → Building tension/preparation for next entrance

This is the musical equivalent of potential ↔ kinetic energy conversion:
  - A ball at the top of a hill = H high, γ low (about to play)
  - A ball rolling down = H → γ conversion (playing intensely)
  - A ball at the bottom = γ low, H low (resting, spent)
```

---

## Conservation in Rhythm

### Rhythmic Energy

Rhythmic conservation governs how many events the ensemble produces per unit time:

```
γ_rhythm_i(t) = density_i(t) × syncopation_i(t)
H_rhythm_i(t) = anticipation_i(t) + silence_weight_i(t)
C_rhythm = Σ C_i
```

### The Constraint

```
Σᵢ density_i(t) ≤ D_max
```

where D_max is the maximum note density the ensemble can produce before becoming muddy.

**Corollary**: If the drummer plays a dense fill (density_drums ↑), other agents should simplify:

```python
def rhythmic_conservation_check(agents: list[Agent]) -> list[float]:
    """
    Check if total rhythmic density exceeds budget.
    Returns suggested density adjustments per agent.
    """
    total_density = sum(a.rhythmic_density for a in agents)
    
    if total_density <= D_MAX:
        return [0.0] * len(agents)  # All clear
    
    # Over budget: distribute the reduction
    excess = total_density - D_MAX
    adjustments = []
    for agent in agents:
        # Agents with higher density contribute more reduction
        share = agent.rhythmic_density / total_density
        reduction = excess * share * 0.5  # Smooth, not abrupt
        adjustments.append(-reduction)
    
    return adjustments
```

### Example: Drum Fill

```
Bar 8 (approaching section change):

Before fill:  Drums: density=0.3  Bass: density=0.4  Keys: density=0.3  Total: 1.0 ✓
During fill:  Drums: density=0.7  Bass: density=0.4  Keys: density=0.3  Total: 1.4 ✗
                                                                    ↓ conservation correction
              Drums: density=0.7  Bass: density=0.2  Keys: density=0.1  Total: 1.0 ✓
                                                       (bass simplifies)  (keys lay out)
After fill:   Drums: density=0.3  Bass: density=0.4  Keys: density=0.3  Total: 1.0 ✓
```

### Polyrhythmic Conservation

When agents play in polyrhythmic ratios, conservation applies to the composite density:

```
Agent A: 3-over-2 pattern → 3 events per 2 beats
Agent B: 4-over-3 pattern → 4 events per 3 beats
Agent C: straight 8ths   → 2 events per beat

Composite density = 3/2 + 4/3 + 2 = 4.17 events per beat

If max composite density = 4.0 events per beat:
  → Agent C should reduce to dotted quarters (1.33 per beat)
  → New composite: 1.5 + 1.33 + 1.33 = 4.16 ≈ 4.0 ✓
```

---

## Conservation in Harmony

### Harmonic Energy

Harmonic conservation governs how much tension the ensemble can sustain:

```
γ_harmony_i(t) = consonance_i(t)     "resolved" harmonic energy
H_harmony_i(t) = dissonance_i(t)     "tense" harmonic energy
C_harmony = total harmonic budget
```

### The PLR-Tropical Constraint

Using the PLR group and tropical semiring, harmonic distance is bounded:

```
For any two agents i, j playing simultaneously:

tropical_distance(chord_i, chord_j) ≤ D_harmonic_max

If violated: one or both agents must adjust chord selection.
```

### Harmonic Energy Transfer

When an agent plays a dissonant chord (high H_harmony), it draws from the harmonic budget:

```python
def harmonic_conservation(agents: list[Agent]) -> bool:
    """
    Check that total harmonic tension is within budget.
    """
    total_tension = sum(
        tropical_distance(agent.current_chord, TONAL_CENTER) 
        for agent in agents
    )
    
    # Also check pairwise tension
    for i, j in itertools.combinations(agents, 2):
        pair_tension = tropical_distance(i.current_chord, j.current_chord)
        if pair_tension > PAIR_TENSION_MAX:
            return False  # Too tense between these two
    
    return total_tension <= HARMONIC_BUDGET
```

### Resolution Dynamics

Dissonance (H_harmonic) naturally resolves to consonance (γ_harmonic) over time:

```
dH_harmonic/dt = -k × H_harmonic    (exponential decay of tension)

The "tension-release" cycle:
  1. Agent introduces dissonance → H ↑, γ ↓ (H + γ = C)
  2. Over 1-4 beats, tension decays → H ↓, γ ↑
  3. Resolution: agent reaches consonant state → H ≈ 0, γ ≈ C
  4. Next phrase: agent builds tension again → H ↑, γ ↓
```

The rate constant k controls how quickly the ensemble resolves:

- **Jazz**: k ≈ 0.3 (tension sustained over multiple bars)
- **Pop**: k ≈ 0.8 (quick resolution, every 1-2 bars)
- **Free improvisation**: k ≈ 0.1 (tension can last entire performance)

---

## Conservation in Dynamics

### Dynamic Energy

```
γ_dynamics_i(t) = loudness_i(t) = ⟨velocity_i⟩(t) / 127
H_dynamics_i(t) = dynamic_range_i(t) = max(velocity) - min(velocity) / 127
C_dynamics = total dynamic budget
```

### Crescendo/Decrescendo Conservation

A crescendo by one agent draws dynamic energy from others:

```python
def dynamic_conservation(agent_changes: dict[int, float]) -> dict[int, float]:
    """
    Given that some agents changed their dynamic level,
    compute compensating changes for others.
    
    agent_changes: {agent_id: delta_velocity}
    Returns: {agent_id: compensation}
    """
    total_delta = sum(agent_changes.values())
    if abs(total_delta) < 0.01:
        return {}  # Net zero, no compensation needed
    
    # Distribute compensation among unchanged agents
    unchanged = {i for i in range(N_AGENTS) if i not in agent_changes}
    if not unchanged:
        return {}  # Everyone changed, accept net shift
    
    compensation_per_agent = -total_delta / len(unchanged)
    return {i: compensation_per_agent for i in unchanged}
```

### Example: Horn Solo

```
Baseline:   All agents at dynamic 0.5 (mezzo-forte)

Horn solo starts:
  Horns: velocity 0.5 → 0.8  (Δ = +0.3)
  Total excess: +0.3
  
  Compensation (distributed to 4 other agents):
  Drums:  0.5 → 0.425  (-0.075)
  Bass:   0.5 → 0.425  (-0.075)
  Keys:   0.5 → 0.425  (-0.075)
  Pads:   0.5 → 0.425  (-0.075)
  
  New total: 0.8 + 4×0.425 = 2.5 = same as 5×0.5 ✓
  The rhythm section "makes room" for the soloist.
```

---

## Energy Transfer Between Agents

### The Transfer Model

Energy transfer happens through the MIDI flux bridge. When agent A plays an event, it implicitly transfers energy:

```python
class EnergyTransfer:
    """
    Models energy transfer between agents through musical interaction.
    """
    
    def compute_transfer(self, event: BandMidiEvent, 
                         listener: AgentId) -> float:
        """
        How much energy does this event transfer from the source 
        to the listener?
        """
        # Direct energy: listener responds with similar intensity
        direct = event.velocity / 127.0 * 0.1  # Small coupling
        
        # Reactive energy: listener may change its own output
        reactive = self._reactive_coupling(event, listener)
        
        return direct + reactive
    
    def _reactive_coupling(self, event: BandMidiEvent, 
                           listener: AgentId) -> float:
        """
        Estimate how much the listener will change its energy
        in response to this event.
        """
        # High energy events from others → listener may reduce (conservation)
        if event.energy_cost > 0.5:
            return -event.energy_cost * 0.05  # Small reduction
        
        # Low energy events → listener has room to increase
        if event.energy_cost < 0.2:
            return (0.2 - event.energy_cost) * 0.03
        
        return 0.0
```

### Transfer Graph

```
          ┌─────── Drums ────────┐
          │       (γ=0.25)       │
          │    ┌─────────┐       │
          ▼    ▼         │       │
       Bass    Keys      │       │
      (γ=0.20) (γ=0.20)  │       │
          │    │         │       │
          ▼    ▼         │       │
        Horns  Pads      │       │
       (γ=0.15)(γ=0.20)  │       │
                         │       │
          Conservation Monitor ◄──┘
          Σ γ = 1.0 = C_total ✓
```

### Energy Flow Patterns

1. **Call-Response**: Energy flows from caller to responder
   - Agent A plays (γ_A ↑) → Agent B hears → Agent B responds (γ_B ↑, γ_A ↓)
   - Net energy conserved; it flows between agents

2. **Crescendo Collective**: All agents build together
   - Each agent shifts H → γ simultaneously
   - Total γ increases, total H decreases
   - γ + H = C still holds

3. **Solo Spotlight**: One agent dominates
   - Soloist: γ ↑↑, H ↓↓
   - Accompanists: γ ↓↓, H ↑↑ (building anticipation for their turn)
   - Energy has been "borrowed" from accompanists

4. **Collective Release**: Resolution after tension
   - All agents: H → γ conversion simultaneously
   - The "drop" or "hit" after a build-up
   - Conservation law ensures the release is proportional to the build-up

---

## Equilibrium Conditions

### Definition

The ensemble is in **conservation equilibrium** when:

```
For all agents i:
  γᵢ(t) + Hᵢ(t) = Cᵢ     (per-agent conservation)

For the ensemble:
  Σᵢ γᵢ(t) + Σᵢ Hᵢ(t) = C_total   (ensemble conservation)

  d(γᵢ + Hᵢ)/dt = 0   for all i    (steady state)
```

### Types of Equilibrium

#### 1. Groove Equilibrium (Stable)

The ensemble has settled into a repeating pattern. Each agent's energy oscillates within bounds:

```
Agent oscillates between:
  γ_min ≤ γᵢ(t) ≤ γ_max   (within its budget)
  H_min ≤ Hᵢ(t) ≤ H_max
  
with γ + H = C always satisfied.
```

This is the normal performing state. Like a rhythm section in the pocket.

**Stability**: Small perturbations (a slightly louder note) are corrected by the conservation law — the agent's H adjusts to compensate.

#### 2. Transitional Equilibrium (Unstable)

During section changes, modulations, or tempo shifts, the equilibrium is temporarily disrupted:

```
Section change:
  Old equilibrium:  γ₁ = 0.3, H₁ = 0.2, C₁ = 0.5
  New equilibrium:  γ₁ = 0.4, H₁ = 0.1, C₁ = 0.5
  
  Transition: γ increases smoothly over 1-2 bars
  During transition: γ + H < C (deficit) or γ + H > C (surplus)
  
  This is allowed for SHORT periods (up to 2 bars).
  Conservation monitor allows temporary violations within tolerance.
```

#### 3. Climax Equilibrium (Maximum γ)

At the peak of intensity, all agents maximize γ simultaneously:

```
For all i: γᵢ ≈ Cᵢ, Hᵢ ≈ 0

This is sustainable for only a few bars (typically 2-4).
After climax, agents must rest: γ ↓, H ↑ (recovery).
```

#### 4. Rest Equilibrium (Maximum H)

Between phrases or during tacet sections:

```
For all i: γᵢ ≈ 0, Hᵢ ≈ Cᵢ

All energy is stored as potential. The "held breath" before the next phrase.
```

### Equilibrium Stability Analysis

Using Lyapunov stability theory:

```python
def is_stable(agents: list[Agent]) -> StabilityReport:
    """
    Analyze the stability of the current ensemble equilibrium.
    """
    deviations = []
    for agent in agents:
        deviation = abs(agent.gamma + agent.hamiltonian - agent.constant)
        deviations.append(deviation)
    
    max_deviation = max(deviations)
    avg_deviation = sum(deviations) / len(deviations)
    
    # Stability criterion: all deviations within tolerance
    is_stable = max_deviation < agent.tolerance
    
    # Trend analysis: are deviations growing or shrinking?
    # (requires history — omitted for clarity)
    
    return StabilityReport(
        is_stable=is_stable,
        max_deviation=max_deviation,
        avg_deviation=avg_deviation,
        least_stable_agent=...,
        recommendation=...,
    )
```

---

## Violations and Recovery

### Types of Violations

#### 1. Individual Over-Budget (γ + H > C)

An agent is spending more energy than its budget allows.

```
Symptoms:
  - Agent playing too many notes
  - Agent playing too loudly
  - Agent playing too complex a rhythm

Causes:
  - Agent's AI model over-generated notes
  - Agent didn't hear the conservation report
  - Agent is in a "solo" that went on too long

Detection:
  if gamma_i + H_i > C_i + tolerance:
      violation!
```

#### 2. Individual Under-Budget (γ + H < C)

An agent isn't using its energy allocation.

```
Symptoms:
  - Agent playing too sparsely
  - Agent at very low velocity
  - Agent in extended tacet

Causes:
  - Agent's AI model became too conservative
  - Agent is "afraid" to play after a violation
  - Agent is stuck in a low-energy eigenmode

Detection:
  if gamma_i + H_i < C_i - tolerance:
      violation!
```

#### 3. Ensemble Over-Budget (Σ(γ + H) > C_total)

The total ensemble energy exceeds the budget.

```
Symptoms:
  - Too many simultaneous notes (muddy texture)
  - Excessive dynamic range (no contrast)
  - Chaotic, overwhelming sound

Causes:
  - Multiple agents over-playing simultaneously
  - Conservation monitor failed to enforce
  - Energy transfer malfunction

Detection:
  if sum(gamma_i + H_i for all i) > C_total + tolerance:
      ensemble_violation!
```

#### 4. Ensemble Under-Budget (Σ(γ + H) < C_total)

The ensemble is playing too quietly or sparsely.

```
Symptoms:
  - Thin texture
  - Weak dynamic presence
  - "Holes" in the sound

Causes:
  - All agents simultaneously at low energy
  - Agents over-compensating after a loud section
  - Intention field in "resolution" phase for too long
```

### Recovery Algorithms

#### Algorithm 1: Gentle Nudge (First Offense)

```python
def gentle_nudge(agent: Agent, direction: str):
    """Suggest a small energy adjustment. Agent decides whether to comply."""
    if direction == "reduce":
        # Suggest reducing velocity by 10%
        agent.suggested_velocity_scale = 0.9
        # Suggest reducing note density by 10%
        agent.suggested_density_scale = 0.9
    elif direction == "increase":
        agent.suggested_velocity_scale = 1.1
        agent.suggested_density_scale = 1.1
```

#### Algorithm 2: Mandatory Rebalance (Repeated Violations)

```python
def mandatory_rebalance(agents: list[Agent], total_budget: float):
    """
    Force all agents back into conservation.
    Redistributes energy proportionally.
    """
    # Compute each agent's fair share
    total_current = sum(a.gamma + a.hamiltonian for a in agents)
    
    if total_current == 0:
        return  # Nothing to rebalance
    
    scale = total_budget / total_current
    
    for agent in agents:
        # Scale both γ and H proportionally
        agent.gamma *= scale * (agent.constant / total_budget * len(agents))
        agent.hamiltonian = agent.constant - agent.gamma
        
        # Ensure non-negative
        agent.gamma = max(0, agent.gamma)
        agent.hamiltonian = max(0, agent.hamiltonian)
```

#### Algorithm 3: Emergency Shutdown (Critical Violation)

```python
def emergency_shutdown(agent: Agent):
    """
    Immediately silence an agent that is critically violating conservation.
    This is the "pull the plug" option — use only as last resort.
    """
    # Force γ to 0
    agent.gamma = 0.0
    agent.hamiltonian = agent.constant  # All energy → potential
    
    # Send all notes off
    agent.emit(MidiMessage.AllNotesOff(channel=agent.channel))
    
    # Enter recovery mode
    agent.status = AgentStatus.Tacet(bars_remaining=2)
    
    # After recovery, gradually reintroduce with reduced budget
    agent.constant *= 0.8  # 20% budget reduction
```

#### Algorithm 4: Gradual Redistribution (Continuous)

The default algorithm running every bar:

```python
def continuous_redistribution(agents: list[Agent], total_budget: float):
    """
    Smoothly redistribute energy each bar.
    This runs continuously and handles small deviations before they grow.
    """
    # Step 1: Check each agent
    for agent in agents:
        total = agent.gamma + agent.hamiltonian
        if total > agent.constant * 1.1:  # 10% over
            excess = total - agent.constant
            # Convert excess H → reduce (if H is high)
            if agent.hamiltonian > excess:
                agent.hamiltonian -= excess
            else:
                # Must reduce γ (play less)
                reduce = excess - agent.hamiltonian
                agent.gamma -= reduce
                agent.hamiltonian = 0
        
        elif total < agent.constant * 0.9:  # 10% under
            deficit = agent.constant - total
            # Add to H (store as potential)
            agent.hamiltonian += deficit
    
    # Step 2: Check ensemble total
    ensemble_total = sum(a.gamma + a.hamiltonian for a in agents)
    if abs(ensemble_total - total_budget) > total_budget * 0.05:
        # Redistribute proportionally
        mandatory_rebalance(agents, total_budget)
```

### Recovery Timeline

```
Violation Detected
    │
    ├─ t = 0:      Gentle nudge (suggest adjustment)
    │
    ├─ t = 1 bar:  Check if agent adjusted
    │   ├─ Yes → OK, continue
    │   └─ No → Mandatory rebalance (force adjustment)
    │
    ├─ t = 2 bars: Check again
    │   ├─ Stable → Return to normal monitoring
    │   └─ Still violating → Reduce agent's budget
    │
    └─ t = 4 bars: If still violating
        └─ Emergency: agent enters tacet, 
           energy redistributed to others
```

---

## The Conservation Matrix

### Formal Definition

For an ensemble of n agents, the **conservation matrix** M is:

```
M_ij = coupling strength between agent i and agent j

M is symmetric (M_ij = M_ji) and positive semidefinite.
Diagonal: M_ii = agent i's self-regulation strength
Off-diagonal: M_ij = energy transfer rate between i and j
```

### Dynamics

The ensemble's energy dynamics follow:

```
dγ/dt = -M × (γ - γ_target)
```

where γ is the vector of agent energies and γ_target is the target allocation.

This is a linear system with guaranteed convergence (M is positive semidefinite → all eigenvalues ≥ 0 → exponential convergence).

### Computing M

```python
def compute_conservation_matrix(
    agents: list[Agent],
    routing: MidiRouting,
) -> np.ndarray:
    """
    Compute the conservation matrix from agent roles and routing.
    """
    n = len(agents)
    M = np.zeros((n, n))
    
    for i, agent_i in enumerate(agents):
        # Self-regulation: stronger for high-budget agents
        M[i][i] = 2.0 * agent_i.constant
        
        # Cross-coupling: based on MIDI routing
        for j, agent_j in enumerate(agents):
            if i == j:
                continue
            
            if agent_j.id in routing.listeners_of(agent_i.id):
                # These agents hear each other → coupling
                # Role similarity increases coupling
                role_similarity = compute_role_similarity(
                    agent_i.role, agent_j.role
                )
                M[i][j] = 0.5 * role_similarity
            else:
                M[i][j] = 0.01  # Weak background coupling
    
    # Ensure positive semidefinite
    eigenvalues = np.linalg.eigvalsh(M)
    if np.any(eigenvalues < 0):
        M += np.eye(n) * abs(min(eigenvalues))
    
    return M
```

### Role Similarity

```python
def compute_role_similarity(role_a: AgentRole, role_b: AgentRole) -> float:
    """How much do these roles interact?"""
    # Rhythm section members interact strongly
    rhythm_section = {AgentRole.Drums, AgentRole.Bass}
    if role_a in rhythm_section and role_b in rhythm_section:
        return 1.0
    
    # Melodic agents interact with rhythm section
    melodic = {AgentRole.Horns, AgentRole.Keys}
    if (role_a in rhythm_section and role_b in melodic) or \
       (role_b in rhythm_section and role_a in melodic):
        return 0.6
    
    # Pads interact weakly with everyone
    if role_a == AgentRole.Pads or role_b == AgentRole.Pads:
        return 0.3
    
    return 0.5  # Default moderate coupling
```

---

## Implementation Reference

### Pseudocode: Conservation Monitor

```python
class ConservationMonitor:
    """
    Ensemble-wide conservation monitor.
    Runs every bar to check and enforce γ + H = C.
    """
    
    def __init__(self, total_budget: float, agents: list[Agent]):
        self.total_budget = total_budget
        self.agent_budgets = {a.id: a.constant for a in agents}
        self.tolerance = 0.05  # 5% tolerance
        self.violation_counts = {a.id: 0 for a in agents}
        self.violation_history = []
    
    def check_and_enforce(self, agents: list[Agent]) -> list[Correction]:
        """
        Run conservation check and return any corrections.
        Call this once per bar.
        """
        corrections = []
        
        # Per-agent check
        for agent in agents:
            total = agent.gamma + agent.hamiltonian
            budget = self.agent_budgets[agent.id]
            deviation = total - budget
            
            if abs(deviation) > budget * self.tolerance:
                self.violation_counts[agent.id] += 1
                
                # Determine correction strength
                n_violations = self.violation_counts[agent.id]
                if n_violations >= 4:
                    strength = CorrectionStrength.EMERGENCY
                elif n_violations >= 2:
                    strength = CorrectionStrength.MANDATORY
                else:
                    strength = CorrectionStrength.GENTLE
                
                corrections.append(Correction(
                    agent_id=agent.id,
                    deviation=deviation,
                    strength=strength,
                    suggested_gamma=budget * 0.5,
                    suggested_hamiltonian=budget * 0.5,
                ))
            else:
                # Within tolerance: reset violation count
                self.violation_counts[agent.id] = max(
                    0, self.violation_counts[agent.id] - 1
                )
        
        # Ensemble check
        ensemble_total = sum(a.gamma + a.hamiltonian for a in agents)
        ensemble_deviation = ensemble_total - self.total_budget
        
        if abs(ensemble_deviation) > self.total_budget * self.tolerance:
            # Distribute correction across all agents
            per_agent_correction = ensemble_deviation / len(agents)
            for agent in agents:
                corrections.append(Correction(
                    agent_id=agent.id,
                    deviation=per_agent_correction,
                    strength=CorrectionStrength.GENTLE,
                    suggested_gamma=agent.gamma - per_agent_correction * 0.5,
                    suggested_hamiltonian=agent.hamiltonian - per_agent_correction * 0.5,
                ))
        
        self.violation_history.append({
            "tick": agents[0].tick_count,
            "corrections": len(corrections),
            "ensemble_deviation": ensemble_deviation,
        })
        
        return corrections


class CorrectionStrength(Enum):
    GENTLE = "gentle"        # Suggest adjustment
    MANDATORY = "mandatory"  # Force adjustment
    EMERGENCY = "emergency"  # Silence agent, redistribute


@dataclass
class Correction:
    agent_id: int
    deviation: float
    strength: CorrectionStrength
    suggested_gamma: float
    suggested_hamiltonian: float
```

### Integration with Agent Loop

```python
# In the agent's main performance loop:
def agent_performance_tick(agent: Agent, dt: float) -> list[MidiEvent]:
    events = []
    
    # 1. Advance t-minus clock
    clock_events = agent.tminus.tick(dt)
    
    # 2. For each clock event, generate musical response
    for ce in clock_events:
        if ce.boundary == BoundaryType.BEAT:
            # Compute desired energy for this beat
            desired_energy = agent.compute_energy(ce)
            
            # Check conservation before generating notes
            if desired_energy > agent.gamma + 0.1:
                # Would exceed budget — check if H can convert
                if agent.hamiltonian > desired_energy - agent.gamma:
                    # Convert H → γ
                    delta = desired_energy - agent.gamma
                    agent.hamiltonian -= delta
                    agent.gamma = desired_energy
                else:
                    # Not enough H — cap at budget
                    desired_energy = agent.gamma  # Stay at current level
            
            # Generate notes within energy budget
            notes = agent.generate_notes(ce, energy_budget=desired_energy)
            events.extend(notes)
            
            # Update energy
            actual_energy = sum(n.velocity / 127.0 for n in notes) / max(1, len(notes))
            agent.gamma = actual_energy
    
    return events
```

---

## Summary

| Concept | Formula | Musical Meaning |
|---------|---------|-----------------|
| Per-agent conservation | γᵢ + Hᵢ = Cᵢ | Each agent has fixed energy budget |
| Ensemble conservation | Σ(γᵢ + Hᵢ) = C | Total band energy is constant |
| Kinetic energy (γ) | density × velocity × complexity | How actively an agent is playing |
| Potential energy (H) | tension + preparation | Stored musical energy ready to release |
| γ ↔ H exchange | dγ = -dH | Active playing ↔ stored tension |
| Rhythmic conservation | Σ densityᵢ ≤ D_max | Can't all play busy at once |
| Harmonic conservation | Σ tensionᵢ ≤ H_max | Can't all be dissonant at once |
| Dynamic conservation | Σ loudnessᵢ = L_total | Soloist gets louder, others make room |
| Recovery (gentle) | Suggest 10% adjustment | First violation |
| Recovery (mandatory) | Force proportional rebalance | Repeated violations |
| Recovery (emergency) | Silence agent, redistribute | Critical violations |
| Conservation matrix | dγ/dt = -M(γ - γ_target) | Linear dynamics, guaranteed convergence |
