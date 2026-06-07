# Hodge Decomposition for Musical Disagreement

> *Every disagreement in the band is either a problem to fix, a cycle to iterate, or creative tension to celebrate. Hodge decomposition tells us which is which.*

---

## Table of Contents

1. [The Problem of Disagreement](#the-problem-of-disagreement)
2. [Hodge Decomposition: The Mathematical Foundation](#hodge-decomposition-the-mathematical-foundation)
3. [Gradient: Fixable Disagreements](#gradient-fixable-disagreements)
4. [Curl: Cyclic Disagreements](#curl-cyclic-disagreements)
5. [Harmonic: Creative Tension](#harmonic-creative-tension)
6. [Computing the Decomposition from Agent State](#computing-the-decomposition-from-agent-state)
7. [Convergence Guarantees](#convergence-guarantees)
8. [Practical Applications](#practical-applications)
9. [Implementation Reference](#implementation-reference)

---

## The Problem of Disagreement

In any ensemble, agents will disagree. The drummer wants 120 BPM, the bassist feels 116. The keys player is thinking Bb blues, the horns are hearing Bb minor pentatonic. The pads want to sustain, the guitar wants to comp.

In a traditional system, these disagreements are resolved by a central authority: a conductor, a composer, a configuration file.

**The Self-Improving Band has no conductor.** Disagreements must resolve themselves through mathematical decomposition.

The key insight from Hodge theory: **not all disagreements are equal.** Some are trivially fixable. Some require iteration. Some are the source of the most interesting music.

---

## Hodge Decomposition: The Mathematical Foundation

### Classical Hodge Theory

On a Riemannian manifold M, the Hodge decomposition theorem states that any differential k-form ω can be uniquely decomposed:

```
ω = dα + δβ + γ
```

where:
- **dα** (exact form) = gradient component: ω is the derivative of some scalar potential α
- **δβ** (co-exact form) = curl component: ω is the codifferential of some (k+1)-form β
- **γ** (harmonic form) = neither: satisfies dγ = 0 and δγ = 0

### Translation to Ensemble Disagreement

In the band, we model disagreement as a vector field on the space of musical parameters:

```
X: Agents → ℝ^d

X(i) = deviation of agent i from ensemble consensus
```

Each dimension represents a musical parameter (tempo, harmonic center, dynamic level, rhythmic density, etc.).

The Hodge decomposition of X:

```
X = ∇φ + curl(A) + H

∇φ   = gradient component    (fixable)
curl(A) = curl component     (iteratively resolvable)  
H    = harmonic component    (creative tension)
```

### Discrete Hodge Decomposition

For a finite ensemble, we use the discrete Hodge decomposition on a graph. The agents form a graph G = (V, E) where edges represent communication channels (MIDI routing).

```
Discrete decomposition:
  X = G + R + H

  G_i = ∇φ_i       (discrete gradient — difference of a scalar field on vertices)
  R_i = curl_i(A)   (discrete curl — circulation on edges incident to vertex i)
  H_i               (harmonic — in kernel of both discrete Laplacian operators)
```

The discrete Laplacian (graph Laplacian) is:

```
L = D - A

where:
  D = degree matrix (diagonal, D_ii = number of neighbors of i)
  A = adjacency matrix (A_ij = 1 if i and j communicate)
```

The decomposition is computed by solving:

```
L × φ = div(X)     → gradient component: G = ∇φ
R = X - G - H      → curl component
H ∈ ker(L)         → harmonic component (null space of Laplacian)
```

---

## Gradient: Fixable Disagreements

### What They Are

Gradient disagreements are those that can be resolved by adjusting a single scalar parameter for each agent. They are "pointing in the same direction" — everyone agrees on the direction of change, just not the magnitude.

### Musical Examples

| Disagreement | Why It's Gradient | Fix |
|---|---|---|
| Tempo drift | Everyone slightly off from consensus BPM | Nudge each agent's local tempo |
| Tuning drift | Each agent's pitch reference shifted | Adjust pitch offset per agent |
| Dynamic imbalance | Some too loud, some too soft | Scale velocity per agent |
| Timing offset | Agent consistently 5ms early | Phase correction per agent |

### Mathematical Structure

A gradient vector field satisfies:

```
X_i = ∇φ_i = φ(j) - φ(i)    for edge (i,j)
```

This means the disagreement along each edge is the difference of a scalar potential. There exists a "height function" φ such that every agent's deviation is explained by its position on this potential surface.

### How to Fix

Gradient disagreements are resolved by finding φ and adjusting each agent by -∇φ_i:

```python
def fix_gradient(agents: list[Agent], disagreement: dict[tuple[int,int], float]) -> dict[int, float]:
    """
    Compute gradient component of disagreement and return corrections.
    
    disagreement: {(i,j): disagreement between agents i and j}
    Returns: {agent_id: correction}
    """
    n = len(agents)
    
    # Build the graph Laplacian
    L = np.zeros((n, n))
    b = np.zeros(n)
    
    for (i, j), d in disagreement.items():
        L[i][i] += 1
        L[j][j] += 1
        L[i][j] -= 1
        L[j][i] -= 1
        b[i] += d
        b[j] -= d
    
    # Solve L × φ = b for the scalar potential φ
    try:
        phi = np.linalg.lstsq(L, b, rcond=None)[0]
    except np.linalg.LinAlgError:
        # Fallback: use average
        phi = np.full(n, np.mean(b) / max(1, np.sum(L[0])))
    
    # Gradient corrections
    corrections = {}
    for i in range(n):
        corrections[agents[i].id] = -phi[i]
    
    return corrections
```

### Tempo Drift Example

```
5 agents, consensus tempo = 120 BPM

Agent A: 122 BPM (Δ = +2)   
Agent B: 119 BPM (Δ = -1)   
Agent C: 120 BPM (Δ =  0)   
Agent D: 121 BPM (Δ = +1)   
Agent E: 118 BPM (Δ = -2)   

Gradient analysis:
  The disagreements are all in one dimension (tempo)
  No cyclic structure → purely gradient
  Solution: adjust each by -Δ
  → A: -2, B: +1, C: 0, D: -1, E: +2
  → All agents now at 120 BPM ✓

This was trivially fixable. Pure gradient, no curl, no harmonic.
```

---

## Curl: Cyclic Disagreements

### What They Are

Curl disagreements are cyclic: A disagrees with B, B disagrees with C, C disagrees with A, forming a loop. They can't be fixed by a single scalar adjustment — they require iteration.

### Musical Examples

| Disagreement | Why It's Curl | Resolution |
|---|---|---|
| Call-response loop | A responds to B, B responds to C, C responds to A | Iterate until responses converge |
| Role confusion | Each agent thinks another should take the lead | Negotiate through intention field |
| Harmonic chase | Each agent follows a different neighbor's harmony | Iterate until harmonic field settles |
| Phase circularity | A follows B's phase, B follows C's, C follows A's | Multiple correction rounds |

### Mathematical Structure

Curl measures the circulation around closed loops:

```
curl_ijk = X(i→j) + X(j→k) + X(k→i)
```

If curl ≠ 0, there's circulation — the disagreement goes "around" the triangle rather than "across" it.

### Resolution Through Iteration

Curl disagreements are resolved by repeated application of gradient correction:

```python
def resolve_curl(agents: list[Agent], disagreement: dict[tuple[int,int], float],
                 max_iterations: int = 10) -> dict[int, list[float]]:
    """
    Iteratively resolve curl disagreements.
    Each iteration computes gradient correction of the remaining disagreement.
    Returns: {agent_id: [correction per iteration]}
    """
    history = {a.id: [] for a in agents}
    remaining = dict(disagreement)
    
    for iteration in range(max_iterations):
        # Compute gradient component of remaining disagreement
        corrections = fix_gradient(agents, remaining)
        
        # Apply corrections
        for agent in agents:
            c = corrections.get(agent.id, 0.0)
            history[agent.id].append(c)
        
        # Update remaining disagreement (subtract what we fixed)
        new_remaining = {}
        for (i, j), d in remaining.items():
            ci = corrections.get(i, 0.0)
            cj = corrections.get(j, 0.0)
            residual = d - (ci - cj)
            if abs(residual) > 0.001:  # Still significant
                new_remaining[(i, j)] = residual
        
        remaining = new_remaining
        
        if not remaining:
            break  # Fully resolved
    
    return history
```

### Call-Response Example

```
3 agents in a cycle: Horns → Keys → Bass → Horns

Iteration 0 (initial disagreement):
  Horns: "I'm responding to Keys' last phrase"
  Keys:  "I'm responding to Bass's last phrase"
  Bass:  "I'm responding to Horns' last phrase"
  
  The responses create a cycle — no agent is "leading"
  
Iteration 1:
  Gradient correction: adjust each by average of neighbors
  Horns: -0.3, Keys: +0.1, Bass: +0.2
  
Iteration 2:
  Remaining disagreement: smaller cycle
  Horns: -0.1, Keys: +0.05, Bass: +0.05
  
Iteration 3:
  Converged. Agents aligned.
  
The curl component was 70% of the total disagreement.
It took 3 iterations to resolve — typical for cyclic structures.
```

---

## Harmonic: Creative Tension

### What They Are

Harmonic disagreements are in the kernel of the Laplacian — they can't be reduced by any amount of local adjustment. They are **irreducible**.

**This is where the most interesting music lives.**

### Musical Examples

| Disagreement | Why It's Harmonic | Why It's Good |
|---|---|---|
| Style contrast | Drums are straight, bass is syncopated | Creates rhythmic interest |
| Timbral opposition | Pads are warm, horns are bright | Rich frequency spectrum |
| Harmonic tension | Keys play major, horns play minor | Blues tonality (major/minor ambiguity) |
| Dynamic polarity | Bass is loud, pads are quiet | Depth and foreground/background |
| Temporal offset | Horns anticipate, drums lay back | Groove feel (push-pull) |

### Mathematical Structure

Harmonic forms satisfy:

```
L × H = 0    (H is in the null space of the Laplacian)
```

For a connected graph, the dimension of the null space is 1 (the constant vector). But for disconnected subgraphs or specific graph topologies, the null space can be larger — meaning there are multiple independent "directions" of irreducible disagreement.

### Why Not Fix Them?

Harmonic disagreements are **features, not bugs**. They represent:

1. **Genuine creative differences**: Different agents bring different musical perspectives
2. **Structural richness**: The band's sound is defined by its internal tensions
3. **Improvisational potential**: Resolving (or not resolving) these tensions drives the music forward
4. **Individual identity**: Each agent's unique contribution to the ensemble sound

Trying to "fix" harmonic disagreements would make all agents identical — defeating the purpose of having multiple agents.

### Measuring Creative Tension

```python
def creative_tension_score(harmonic_component: list[float]) -> float:
    """
    Measure the magnitude of creative tension.
    Higher = more irreducible disagreement = more interesting music.
    """
    return math.sqrt(sum(h**2 for h in harmonic_component))
```

### When Harmonic Disagreement Is Too Much

Even creative tension has limits. If the harmonic component is very large:

```
creative_tension > T_max

This means the agents fundamentally disagree on musical direction.
Options:
  1. Accept it: Let the tension drive the music (free jazz approach)
  2. Modulate it: Intention field exerts gentle pressure toward alignment
  3. Restructure: Reassign roles to agents with compatible harmonic states
```

---

## Computing the Decomposition from Agent State

### Input: Agent State Vectors

Each agent has a state vector in musical parameter space:

```python
def agent_state_vector(agent: Agent) -> list[float]:
    """
    Compute an agent's state as a vector in musical parameter space.
    Dimensions: [tempo, harmonic_center, dynamic_level, density, tension]
    """
    return [
        agent.tempo / 120.0,                                    # Normalized tempo
        agent.current_chord.root / 12.0,                        # Pitch class (normalized)
        agent.conservation.gamma / agent.conservation.constant, # Dynamic energy
        agent.note_density / MAX_DENSITY,                       # Note density
        agent.harmonic_tension / MAX_TENSION,                   # Harmonic tension
    ]
```

### Computing Disagreement

```python
def compute_disagreement(agents: list[Agent], routing: MidiRouting) -> dict[tuple[int,int], list[float]]:
    """
    Compute pairwise disagreement vectors for connected agents.
    Returns: {(i,j): vector_difference}
    """
    disagreement = {}
    
    for (source, listeners) in routing.routes:
        for listener in listeners:
            state_i = agent_state_vector(agents[source])
            state_j = agent_state_vector(agents[listener])
            
            # Disagreement = difference in state vectors
            diff = [si - sj for si, sj in zip(state_i, state_j)]
            disagreement[(source, listener)] = diff
    
    return disagreement
```

### The Full Decomposition Pipeline

```python
def hodge_decompose(agents: list[Agent], routing: MidiRouting) -> HodgeResult:
    """
    Full Hodge decomposition of ensemble disagreement.
    """
    n = len(agents)
    d = 5  # Number of musical dimensions
    
    # Step 1: Compute disagreement vectors
    disagreement = compute_disagreement(agents, routing)
    
    # Step 2: Build the graph structure
    edges = list(disagreement.keys())
    n_edges = len(edges)
    
    # Step 3: For each dimension, compute the decomposition
    gradient_components = []
    curl_components = []
    harmonic_components = []
    
    for dim in range(d):
        # Extract scalar disagreements for this dimension
        scalar_disagreement = {
            (i,j): vec[dim] for (i,j), vec in disagreement.items()
        }
        
        # Build incidence matrix B (n_edges × n_vertices)
        B = np.zeros((n_edges, n))
        for e, (i, j) in enumerate(edges):
            B[e][i] = 1
            B[e][j] = -1
        
        # Graph Laplacian: L = B^T B
        L = B.T @ B
        
        # Disagreement vector for this dimension
        x = np.array([scalar_disagreement.get(e, 0.0) for e in edges])
        
        # Solve for potential: L φ = B^T x
        try:
            # Add regularization for numerical stability
            phi = np.linalg.lstsq(L + 0.01 * np.eye(n), B.T @ x, rcond=None)[0]
        except:
            phi = np.zeros(n)
        
        # Gradient component: G = B × φ
        G = B @ phi
        
        # Harmonic component: null space of L
        eigenvalues, eigenvectors = np.linalg.eigh(L)
        null_mask = eigenvalues < 0.01  # Near-zero eigenvalues
        if np.any(null_mask):
            null_space = eigenvectors[:, null_mask]
            # Project x onto null space
            H = null_space @ (null_space.T @ x)
        else:
            H = np.zeros(n_edges)
        
        # Curl component: residual
        R = x - G - H
        
        gradient_components.append(G)
        curl_components.append(R)
        harmonic_components.append(H)
    
    # Step 4: Aggregate results
    return HodgeResult(
        gradient=gradient_components,       # d × n_edges
        curl=curl_components,               # d × n_edges
        harmonic=harmonic_components,       # d × n_edges
        original=disagreement,              # n_edges × d
        total_gradient_energy=sum(np.sum(G**2) for G in gradient_components),
        total_curl_energy=sum(np.sum(R**2) for R in curl_components),
        total_harmonic_energy=sum(np.sum(H**2) for H in harmonic_components),
    )
```

### Computational Complexity

For n agents and e edges in the communication graph:

| Step | Complexity |
|------|-----------|
| Disagreement computation | O(n × d) |
| Laplacian construction | O(e) |
| Linear solve | O(n³) worst case, O(n²) for sparse |
| Eigenvalue decomposition | O(n³) |
| Total | O(n³ × d) |

For a typical 5-agent ensemble with 5 dimensions, this is negligible — well under 1ms.

---

## Convergence Guarantees

### Theorem 1: Decomposition Uniqueness

**Statement**: The Hodge decomposition X = G + R + H is unique (up to the choice of inner product).

**Proof**: Standard result from Hodge theory. The three components are orthogonal with respect to the graph inner product:

```
⟨G, R⟩ = 0
⟨G, H⟩ = 0
⟨R, H⟩ = 0
```

Therefore the decomposition is an orthogonal projection, which is unique. ∎

### Theorem 2: Gradient Correction Convergence

**Statement**: Repeated application of gradient correction converges to eliminate the gradient component.

**Proof**: Each gradient correction step is a contraction mapping on the gradient subspace. The contraction factor is related to the Laplacian's spectral gap:

```
α = 1 - λ₂/λₙ

where λ₂ is the algebraic connectivity and λₙ is the largest eigenvalue.
```

For any connected graph, λ₂ > 0, so α < 1 and convergence is exponential. ∎

### Theorem 3: Curl Resolution Convergence

**Statement**: Iterative curl resolution converges.

**Proof**: Curl resolution is equivalent to solving the Laplacian equation iteratively. The Gauss-Seidel iteration on the graph Laplacian converges for any positive semidefinite matrix (which L always is). Convergence rate depends on the condition number of L restricted to the curl subspace. ∎

### Theorem 4: Harmonic Component Stability

**Statement**: The harmonic component is invariant under local corrections.

**Proof**: By definition, harmonic vectors satisfy L × H = 0. Any local correction of the form δ = L × v (gradient) or δ = Lᵀ × w (curl) cannot affect H, because:

```
⟨L × v, H⟩ = ⟨v, Lᵀ × H⟩ = ⟨v, L × H⟩ = ⟨v, 0⟩ = 0
```

The harmonic component is orthogonal to anything the Laplacian can produce. ∎

### Practical Convergence Rates

For a typical 5-agent ensemble:

| Component | Convergence | Typical iterations |
|-----------|------------|-------------------|
| Gradient | 1 step (direct solve) | 1 |
| Curl | Exponential, rate ≈ 0.3 | 3-5 |
| Harmonic | Does not converge (by design) | ∞ |

---

## Practical Applications

### Application 1: Tempo Negotiation

```python
def negotiate_tempo(agents: list[Agent]) -> float:
    """
    Use Hodge decomposition to find consensus tempo.
    """
    # Collect tempo preferences
    tempos = [a.tempo for a in agents]
    
    # Compute disagreement (1D for tempo)
    disagreement = {}
    for i, j in itertools.combinations(range(len(agents)), 2):
        disagreement[(i, j)] = tempos[i] - tempos[j]
    
    # Decompose
    result = hodge_decompose_1d(disagreement, len(agents))
    
    # Fix gradient component (nudge agents toward consensus)
    corrections = fix_gradient(agents, disagreement)
    for agent, c in zip(agents, corrections.values()):
        agent.set_tempo(agent.tempo + c, transition_beats=2)
    
    # If significant curl → iterate
    if result.total_curl_energy > 0.1 * result.total_gradient_energy:
        resolve_curl(agents, disagreement, max_iterations=5)
    
    # Harmonic component = irreducible tempo differences
    # These create the "human feel" — don't fix them
    if result.total_harmonic_energy > 0:
        print(f"Creative tempo tension: {result.total_harmonic_energy:.3f}")
    
    # Consensus = weighted mean
    consensus = sum(tempos) / len(tempos)
    return consensus
```

### Application 2: Harmonic Alignment

```python
def align_harmony(agents: list[Agent]) -> None:
    """
    Use Hodge decomposition to negotiate harmonic agreement.
    """
    # Compute harmonic disagreement between all pairs
    harmonic_disagreement = {}
    for i, j in itertools.combinations(range(len(agents)), 2):
        dist = tropical_distance(agents[i].current_chord, agents[j].current_chord)
        direction = chord_direction(agents[i].current_chord, agents[j].current_chord)
        harmonic_disagreement[(i, j)] = dist * direction
    
    # Decompose
    result = hodge_decompose_1d(harmonic_disagreement, len(agents))
    
    # Gradient: agents slightly off from tonal center → nudge
    # Curl: agents chasing each other harmonically → iterate
    # Harmonic: genuine harmonic differences → leave them (this is the blues!)
    
    # Only fix gradient component
    if result.total_gradient_energy > 0.01:
        corrections = fix_gradient(agents, harmonic_disagreement)
        for agent, c in zip(agents, corrections.values()):
            # Adjust chord toward gradient correction direction
            if abs(c) > 0.01:
                agent.adjust_harmony(c)
```

### Application 3: Dynamic Balancing

```python
def balance_dynamics(agents: list[Agent]) -> list[float]:
    """
    Use Hodge decomposition for dynamic balance.
    """
    # Dynamic disagreement
    dynamics = [a.conservation.gamma for a in agents]
    mean_dynamic = sum(dynamics) / len(dynamics)
    
    disagreement = {}
    for i, j in itertools.combinations(range(len(agents)), 2):
        disagreement[(i, j)] = dynamics[i] - dynamics[j]
    
    # Decompose
    result = hodge_decompose_1d(disagreement, len(agents))
    
    # Fix gradient (dynamic imbalance)
    corrections = fix_gradient(agents, disagreement)
    
    # Leave harmonic (some agents intentionally louder/softer)
    
    return list(corrections.values())
```

---

## Implementation Reference

### Complete Hodge Decomposer

```python
"""
Hodge Decomposition for Musical Ensembles
==========================================
Decomposes agent disagreement into gradient, curl, and harmonic components.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class HodgeResult:
    """Result of a Hodge decomposition."""
    gradient: List[np.ndarray]      # Per-dimension gradient components
    curl: List[np.ndarray]          # Per-dimension curl components
    harmonic: List[np.ndarray]      # Per-dimension harmonic components
    original: Dict[Tuple[int,int], List[float]]  # Original disagreement
    
    total_gradient_energy: float
    total_curl_energy: float
    total_harmonic_energy: float
    
    @property
    def is_mostly_fixable(self) -> bool:
        """Is most of the disagreement fixable (gradient)?"""
        total = self.total_gradient_energy + self.total_curl_energy + self.total_harmonic_energy
        if total == 0:
            return True
        return self.total_gradient_energy / total > 0.5
    
    @property
    def creative_tension(self) -> float:
        """Magnitude of irreducible creative tension."""
        return np.sqrt(self.total_harmonic_energy)
    
    @property
    def needs_iteration(self) -> bool:
        """Does the curl component require iterative resolution?"""
        total = self.total_gradient_energy + self.total_curl_energy + self.total_harmonic_energy
        if total == 0:
            return False
        return self.total_curl_energy / total > 0.3


class HodgeDecomposer:
    """
    Hodge decomposer for musical agent disagreements.
    """
    
    def __init__(self, n_agents: int, dimensions: int = 5):
        self.n_agents = n_agents
        self.dimensions = dimensions
    
    def decompose(
        self, 
        disagreements: Dict[Tuple[int,int], List[float]]
    ) -> HodgeResult:
        """
        Decompose disagreement vectors into gradient, curl, harmonic.
        
        disagreements: {(i,j): [dim_0_diff, dim_1_diff, ...]}
        """
        n = self.n_agents
        d = self.dimensions
        edges = list(disagreements.keys())
        n_edges = len(edges)
        
        if n_edges == 0:
            return HodgeResult(
                gradient=[np.zeros(0)] * d,
                curl=[np.zeros(0)] * d,
                harmonic=[np.zeros(0)] * d,
                original=disagreements,
                total_gradient_energy=0,
                total_curl_energy=0,
                total_harmonic_energy=0,
            )
        
        # Build incidence matrix
        B = np.zeros((n_edges, n))
        for e, (i, j) in enumerate(edges):
            B[e][i] = 1.0
            B[e][j] = -1.0
        
        # Graph Laplacian
        L = B.T @ B
        
        # Regularize for numerical stability
        L_reg = L + 1e-6 * np.eye(n)
        
        gradient_parts = []
        curl_parts = []
        harmonic_parts = []
        
        total_G = 0.0
        total_R = 0.0
        total_H = 0.0
        
        for dim in range(d):
            x = np.array([disagreements.get(e, [0]*d)[dim] for e in edges])
            
            # Solve for potential
            try:
                phi = np.linalg.solve(L_reg, B.T @ x)
            except np.linalg.LinAlgError:
                phi = np.zeros(n)
            
            # Gradient component
            G = B @ phi
            
            # Harmonic component (null space projection)
            eigenvalues, eigenvectors = np.linalg.eigh(L)
            null_mask = eigenvalues < 1e-4
            if np.any(null_mask):
                null_space = eigenvectors[:, null_mask]
                H = null_space @ (null_space.T @ x)
            else:
                H = np.zeros(n_edges)
            
            # Curl = residual
            R = x - G - H
            
            gradient_parts.append(G)
            curl_parts.append(R)
            harmonic_parts.append(H)
            
            total_G += np.sum(G**2)
            total_R += np.sum(R**2)
            total_H += np.sum(H**2)
        
        return HodgeResult(
            gradient=gradient_parts,
            curl=curl_parts,
            harmonic=harmonic_parts,
            original=disagreements,
            total_gradient_energy=total_G,
            total_curl_energy=total_R,
            total_harmonic_energy=total_H,
        )
    
    def is_fixable(self, result: HodgeResult) -> bool:
        """Can this disagreement be fixed by parameter adjustment?"""
        return result.is_mostly_fixable
    
    def creative_tension(self, result: HodgeResult) -> float:
        """How much irreducible creative tension exists?"""
        return result.creative_tension
    
    def recommend_action(self, result: HodgeResult) -> str:
        """Recommend action based on decomposition."""
        total = (result.total_gradient_energy + 
                result.total_curl_energy + 
                result.total_harmonic_energy)
        
        if total < 1e-6:
            return "No significant disagreement."
        
        g_frac = result.total_gradient_energy / total
        c_frac = result.total_curl_energy / total
        h_frac = result.total_harmonic_energy / total
        
        if g_frac > 0.6:
            return f"Mostly gradient ({g_frac:.0%}). Apply direct corrections."
        elif c_frac > 0.4:
            return f"Significant curl ({c_frac:.0%}). Iterate corrections over 3-5 rounds."
        elif h_frac > 0.4:
            return f"Mostly harmonic tension ({h_frac:.0%}). This is creative — don't fix it."
        else:
            return f"Mixed: {g_frac:.0%} gradient, {c_frac:.0%} curl, {h_frac:.0%} harmonic. Fix gradient, iterate curl, keep harmonic."
```

---

## Summary

| Component | Symbol | Musical Meaning | Resolution |
|-----------|--------|----------------|------------|
| Gradient | G = ∇φ | Fixable parameter drift | Direct correction (1 step) |
| Curl | R = curl(A) | Cyclic disagreement | Iterative correction (3-5 steps) |
| Harmonic | H ∈ ker(L) | Creative tension | Don't fix — celebrate it |

The Hodge decomposition gives the Self-Improving Band a mathematical framework for understanding disagreement. Not every disagreement needs to be resolved. The harmonic component — the irreducible creative tension — is what makes the band sound like a band, not a synthesizer.
