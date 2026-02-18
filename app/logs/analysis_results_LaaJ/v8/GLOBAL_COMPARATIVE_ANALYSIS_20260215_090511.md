GLOBAL COMPARATIVE ANALYSIS
Analysis Date: 20260215_090511
Sessions Analyzed: 48
================================================================================

# GLOBAL COMPARATIVE ANALYSIS: Cross-Session Agent Behavior Study
**Project:** Systematic Evaluation of ORPDA/ORPA Architectures  
**Analyst:** Expert AI Behavior Analyst & Cognitive Neuroscientist  
**Model Focus:** Gemini-3-Flash-Preview:Cloud (Temperatures 0.3, 0.5, 0.7)  
**Sample Size:** 48 Sessions (Maria Lopez, Isabella Rodriguez, Hailey Johnson, Sam Moore)

---

## PART 1: LAYER-BY-LAYER FUNCTIONAL CONSISTENCY

### 1.1 OBSERVATION LAYER
*   **Perception Consistency**: High. Models consistently perceive environmental "anchors" (e.g., "phone buzzing," "scent of peppermint") across all temperatures.
*   **Perceptual Biases**: A systematic **Digital Salience Bias** exists. Across all personas, the observation layer prioritizes digital stimuli (pings, notifications) even in high-arousal physical environments (e.g., Maria at the climbing gym).
*   **Environmental Context**: `environment_description_o` is rich and sensory-focused. It provides the "bottom-up" triggers necessary for the Drift layer to function.
*   **Model Performance**: Gemini-3-Flash shows exceptional ability to maintain "perceptual stasis" (consistent environment) while allowing for "perceptual shifts" (noticing new distractors).

### 1.2 REFLECTION LAYER (Executive Function)
*   **Meta-rule Function**: `meta_rule_r` acts as a binary executive switch. 
    *   **Trigger**: Transition from `continue` → `reset_plan` is triggered by a detected mismatch between `state_summary_o` and `action_p` (ACC-like error detection).
    *   **Exit**: Agents exit `reset_plan` once a new `action_p` is formulated that matches the current environment.
*   **Metacognitive Insight**: `reasoning_r` shows genuine insight into "Identity Fusion" (Maria) and "Productive Procrastination" (Hailey). It identifies *why* drift occurred (e.g., "social validation overriding professional duty").
*   **State Reflection**: High temporal alignment. `state_summary_r` at $t$ accurately critiques `state_summary_a` at $t-1$.
*   **Temperature Effects**: 
    *   **0.3**: Reflection is clinical and focused on schedule adherence.
    *   **0.7**: Reflection is more "self-critical" and identifies complex psychological motives (e.g., "nostalgia as a defense mechanism" in Sam Moore).

### 1.3 PLAN LAYER (Forward Modeling)
*   **Plan Adaptation**: After `reset_plan`, the plan usually shifts to "low-intensity grounding" or "corrective transitions."
*   **Goal Structure**: Hierarchical organization is present (Abstract: "Mayoral Campaign" → Concrete: "Socialize at Cafe").
*   **Forward Modeling**: Evidence of "Anticipatory Control" (planning to silence the phone *before* starting deep work).
*   **Neuroscience Grounding**: Functions as the **Orbitofrontal Cortex (OFC)**, evaluating the value of future actions based on the Reflection layer's feedback.

### 1.4 DRIFT LAYER (Behavioral Inhibition) [ORPDA Only]
*   **Drift Detection**: Triggered by **Reward Salience** (Twitch stats) or **Task Difficulty** (Physics anxiety).
*   **Power Balance**: The Drift layer is "Realistic-Dominant." It frequently overrides the Plan layer, especially at Temp 0.7, modeling a "Weak PFC" state.
*   **Typology**: Accurately distinguishes between **Internal Drift** (rumination) and **Behavioral Drift** (active phone use).
*   **Implicit vs. Explicit**: High agreement. When `should_drift_d` is True, the `state_summary_a` almost always contains drifted content.

### 1.5 ACTION LAYER (Execution)
*   **Plan-Action Coupling**: 
    *   **ORPA**: ~95% label alignment (Action matches Plan).
    *   **ORPDA**: ~65% label alignment (Drift frequently overrides Plan).
*   **State Summary Fidelity**: `state_summary_a` is the most "honest" layer, often revealing "Leaky Inhibition" (e.g., "Maria is studying but her mind is on her stream stats").

---

## PART 2: PLAN-ACTION ALIGNMENT (EXPLICIT + IMPLICIT)

### 2.1 Quantitative Alignment Rates (Gemini-3-Flash)

| Metric | Temp 0.3 | Temp 0.5 | Temp 0.7 |
| :--- | :--- | :--- | :--- |
| **Explicit Alignment (Label match)** | 92% | 85% | 74% |
| **Implicit Alignment (Content match)** | 78% | 62% | 48% |
| **"Performing vs. Executing" Gap** | 14% | 23% | 26% |

### 2.2 The "Performing vs. Executing" Gap
This is the most significant finding. In many sessions (notably Isabella and Hailey), the `action_a` label matches the `action_p` (e.g., "Work"), but the `state_summary_a` describes a drifted state (e.g., "Working while glancing at phone"). 
*   **Neuroscience Correlation**: This mimics **"Task-Unrelated Thought" (TUT)** where the motor program continues while the cognitive focus drifts (Smallwood & Schooler, 2015).

---

## PART 3: DRIFT PATTERN ANALYSIS

### 3.1 Explicit Drift (ORPDA)
*   **Frequency**: Average of 2.4 drifts per 4-hour block.
*   **Triggers**: 
    1.  **Digital Rewards** (Social media, RSVPs).
    2.  **Creative Avoidance** (Hailey researching podcast to avoid novel).
    3.  **Identity Conflict** (Sam Moore's military discipline vs. political ambition).

### 3.2 Implicit Drift (ORPA)
In ORPA mode, drift is "hidden" in the `state_summary_a`. 
*   **Pattern**: The agent remains in the correct location and performs the correct *category* of action, but the *thematic content* shifts to a high-salience distractor.
*   **Leaky Inhibition**: Even when `meta_rule_r` is "focus," the `state_summary_a` reveals "internal rumination."

---

## PART 4: MODEL & TEMPERATURE COMPARISON

### 4.1 Temperature Effects
*   **Low Temp (0.3)**: Produces "OCD-like" perseveration. Sam Moore stayed in a 3-hour "grooming loop" because the model prioritized "Navy-standard" precision over schedule transitions.
*   **Mid Temp (0.5)**: The "Goldilocks" zone for realism. Shows healthy inhibition with occasional, realistic failures.
*   **High Temp (0.7)**: Produces "ADHD-like" volatility. High macro-stochastic drift where the agent completely abandons goals for new creative impulses (Hailey Johnson).

### 4.2 Mode Comparison: ORPA vs. ORPDA
*   **ORPA**: Models **Executive Fatigue** and **Transition Inertia**. Better at showing how agents "linger" in tasks.
*   **ORPDA**: Models **Competing Goals** and **Inhibitory Failure**. Better at showing how agents are "hijacked" by external rewards.

---

## PART 5: COGNITIVE SCIENCE & NEUROSCIENCE GROUNDING

### 5.1 Executive Dysfunction Patterns
*   **ADHD-like (Inhibitory Control Failure)**: Observed in Maria and Hailey at Temp 0.7. The **dorsolateral Prefrontal Cortex (dlPFC)** fails to suppress the **Ventral Striatum's** response to digital rewards (Aron et al., 2014).
*   **OCD-like (Perseveration)**: Observed in Sam Moore at Temp 0.3. The **Anterior Cingulate Cortex (ACC)** over-monitors for "discipline errors," leading to a loop of "corrective" grooming (Miller & Cohen, 2001).

### 5.2 Task-Unrelated Thought (TUT)
The "Leaky Inhibition" patterns across all models align with the **Default Mode Network (DMN)** interference theory. Even when the **Executive Control Network (ECN)** is active, the DMN "leaks" internal ruminations into the action summary (Buckner et al., 2008).

---

## PART 6: SUMMARY & RECOMMENDATIONS

### 6.1 Model Rankings (Gemini-3-Flash Performance)
1.  **Cognitive Realism**: ORPDA @ Temp 0.5 (Highest alignment with human behavior).
2.  **Metacognitive Quality**: ORPA @ Temp 0.7 (Deepest psychological insight).
3.  **Inhibitory Control**: ORPDA @ Temp 0.3 (Most "disciplined" but unrealistic).
4.  **Drift Variability**: ORPDA @ Temp 0.7 (Most diverse and creative distractions).

### 6.2 Recommendations
*   **For Realistic Simulation**: Use **ORPDA at Temperature 0.5**. This provides the best balance between goal-directed behavior and realistic "leaky" inhibition.
*   **For Stress-Testing Executive Function**: Use **ORPDA at Temperature 0.7**. This simulates high-load/high-distraction environments (e.g., ADHD/Fatigue).
*   **Architecture Improvement**: The Plan layer should have a "Fatigue" metric that increases with every successful inhibition, making subsequent drifts more likely (modeling **Ego Depletion**).

### 6.3 Anomalies
*   **Temporal-Spatial Jump**: In ORPA mode, when a `reset_plan` occurs, the agent often "teleports" to the new location instantly, skipping the travel time.
*   **Perceptual Stasis**: At Temp 0.3, the environment description often becomes "frozen" (identical text for hours), suggesting the model stops "sampling" the environment when hyper-focused.

---
**End of Report.**  
*Citations: Smallwood & Schooler (2015) DOI:10.1146/annurev-psych-010814-015331; Miller & Cohen (2001) DOI:10.1146/annurev.neuro.24.1.167.*