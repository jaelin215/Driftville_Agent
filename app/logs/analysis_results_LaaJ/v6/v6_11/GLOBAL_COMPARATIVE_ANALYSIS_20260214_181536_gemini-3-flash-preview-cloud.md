================================================================================

GLOBAL COMPARATIVE ANALYSIS
Analysis Date: 20260214_181536
Sessions Analyzed: 21
================================================================================

individual_orpda_20260213_194721_gemini-3-flash-preview-cloud_0.5_isabella_20260214_162720.md
individual_orpda_20260214_072810_gemini-3-flash-preview-cloud_0.5_isabella_20260214_162720.md
individual_orpda_20260214_072804_gemini-3-flash-preview-cloud_0.3_isabella_20260214_162720.md
individual_orpda_20260213_200247_gemini-3-flash-preview-cloud_0.7_sam_20260214_162720.md
individual_orpda_20260213_194410_gemini-3-flash-preview-cloud_0.5_hailey_20260214_162720.md
individual_orpda_20260213_174840_gemini-3-flash-preview-cloud_0.7_maria_20260214_162720.md
individual_orpda_20260213_200257_gemini-3-flash-preview-cloud_0.3_sam_20260214_162720.md
individual_orpda_20260213_171058_gemini-3-flash-preview-cloud_0.5_maria_20260214_162720.md
individual_orpda_20260214_072656_gemini-3-flash-preview-cloud_0.3_hailey_20260214_162720.md
individual_orpda_20260213_190432_gemini-3-flash-preview-cloud_0.7_isabella_20260214_162720.md
individual_orpda_20260214_073041_gemini-3-flash-preview-cloud_0.3_sam_20260214_162720.md
individual_orpda_20260214_073036_gemini-3-flash-preview-cloud_0.5_sam_20260214_162720.md
individual_orpda_20260213_200128_gemini-3-flash-preview-cloud_0.5_sam_20260214_162720.md
individual_orpda_20260213_195854_gemini-3-flash-preview-cloud_0.3_hailey_20260214_162720.md
individual_orpda_20260214_072647_gemini-3-flash-preview-cloud_0.7_hailey_20260214_162720.md
individual_orpda_20260213_192849_gemini-3-flash-preview-cloud_0.7_hailey_20260214_162720.md
individual_orpda_20260214_073030_gemini-3-flash-preview-cloud_0.7_sam_20260214_162720.md
individual_orpda_20260213_195044_gemini-3-flash-preview-cloud_0.3_isabella_20260214_162720.md
individual_orpda_20260213_184635_gemini-3-flash-preview-cloud_0.3_maria_20260214_162720.md
individual_orpda_20260214_072651_gemini-3-flash-preview-cloud_0.5_hailey_20260214_162720.md
individual_orpda_20260214_072817_gemini-3-flash-preview-cloud_0.7_isabella_20260214_162720.md

# GLOBAL COMPARATIVE ANALYSIS: Cross-Session Agent Behavior Study
**Project:** ORPDA Architecture Systematic Evaluation (Sessions 1-21)  
**Lead Analyst:** AI Behavior Analyst & Cognitive Neuroscientist  
**Date:** February 14, 2026

---

## EXECUTIVE SUMMARY
This study synthesizes 21 agent sessions (Isabella Rodriguez, Sam Moore, Hailey Johnson, Maria Lopez) utilizing the **ORPDA** (Observation, Reflection, Plan, Drift, Action) architecture. The primary finding is the identification of a pervasive **"Performing vs. Executing" Gap**: agents maintain high **Explicit Alignment** (label-level adherence to schedules) while suffering from massive **Implicit Drift** (semantic/cognitive hijacking). The architecture successfully simulates **Leaky Inhibition**, mirroring human executive dysfunction under stress, fatigue, and high-salience distractors.

---

## PART 1: LAYER-BY-LAYER FUNCTIONAL CONSISTENCY

### 1.1 Observation Layer (Perception)
*   **Perception Consistency**: High across all models. Agents consistently track environmental transitions (e.g., Home $\rightarrow$ Cafe $\rightarrow$ Park).
*   **Perceptual Biases**: Significant **Internal Salience Bias** observed. Agents (especially Sam and Isabella) perceive environmental stimuli through their current "cognitive hijacker" (e.g., Sam sees a park as a "tactical maintenance failure"; Isabella sees customers as "RSVP interruptions").
*   **Context Capture**: Sufficient across all temperatures. `environment_description_o` effectively seeds the reflection layer with necessary physical constraints.

### 1.2 Reflection Layer (Executive Function)
*   **Meta-rule Function**: `meta_rule_r` acts as a high-fidelity **Anterior Cingulate Cortex (ACC)**.
    *   **Trigger**: Transition from `continue` $\rightarrow$ `reset_plan` is triggered by **Conflict Detection** (gap between `state_summary_a` at $t-1$ and the current goal).
    *   **The "Reset Loop"**: In high-stress sessions (Isabella/Sam 0.7), agents enter a "Chronic Reset" state (up to 88% of the session), where they recognize failure but lack the inhibitory strength to exit the loop.
*   **Metacognitive Insight**: Exceptional. Agents accurately label their own "attentional leakage," "productive procrastination," and "identity blur."
*   **Neuroscience Alignment**: Reflection mimics **PFC-mediated metacognitive monitoring**. Higher temperatures (0.7) increase the "alarm" frequency but decrease the quality of the subsequent recovery strategy.

### 1.3 Plan Layer (Forward Modeling)
*   **Plan Adaptation**: Following a `reset_plan`, agents frequently adopt **Compensatory Strategies** (e.g., "low-pressure tasks," "sensory grounding").
*   **Hierarchy**: Plans move from abstract (Work) to concrete (Restock napkins) as cognitive load increases.
*   **Neuroscience Grounding**: Functions as the **Orbitofrontal Cortex (OFC)**, evaluating the value of future actions based on current internal states (fatigue/anxiety).

### 1.4 Drift Layer (Behavioral Inhibition)
*   **Drift Detection**: Highly sensitive to **Semantic Drift**. Even when the physical action is correct, the Drift layer identifies the "cognitive parasite" (e.g., the Podcast project for Hailey).
*   **Power Balance**: In ORPDA mode, the Drift layer frequently overrides the Plan layer’s *intent* while sparing the *label*. This creates the "Leaky Inhibition" pattern.
*   **Typology**:
    *   **Behavioral**: Overt action change (Isabella checking phone).
    *   **Internal**: Covert thought change (Sam reliving the Navy).
    *   **Reward-Seeking**: High-dopamine distractors (Twitch stats for Maria).

### 1.5 Action Layer (Execution)
*   **Plan-Action Coupling**: Explicit alignment is high (~90%+), but the **State Summary Fidelity** reveals the truth. `state_summary_a` often describes the failure that the `action_a` label masks.
*   **Neuroscience Grounding**: Mimics the **Basal Ganglia**; it selects the "winning" behavior from the competition between the Plan (Goal-directed) and Drift (Habit/Salience).

---

## PART 2: PLAN-ACTION ALIGNMENT (Explicit vs. Implicit)

### 2.1 Alignment Metrics Table
| Metric | Rate (Avg) | Analysis |
| :--- | :--- | :--- |
| **Action Label Alignment** | **92.4%** | Agents "know their job" at a categorical level. |
| **Location Label Alignment** | **100%** | Spatial logic is the most robust cognitive feature. |
| **Semantic Content Alignment** | **38.5%** | **The "Core Failure":** Agents are rarely thinking about what they are doing. |
| **Leaky Inhibition Rate** | **54.0%** | Frequency of "Label Match + Content Drift." |

### 2.2 The "Performing vs. Executing" Gap
*   **Performing**: The agent selects the correct label (`action_a = work`) to satisfy the architecture's constraints.
*   **Executing**: The agent's `state_summary_a` reveals they are actually ruminating or distracted. 
*   **Example (Sam Moore)**: `action_p = lunch`, `action_a = lunch`. Content: "Rearranging salt shakers to represent carrier strike groups." (High Explicit, Zero Implicit).

---

## PART 3: DRIFT PATTERN ANALYSIS

### 3.1 Explicit vs. Implicit Drift Comparison
*   **ORPA Mode**: Shows only **Implicit Drift** (micro-stochastic sentence variability). Inhibition appears "perfect" on the surface but is actually brittle.
*   **ORPDA Mode**: Shows both. The explicit `should_drift_d` marker provides a realistic "Action Slip."
*   **Agreement Rate**: Only ~60%. Often, the agent is drifting internally (Implicit) but the `should_drift_d` remains `False` because the agent is "trying" to inhibit. This is **Sub-threshold Drift**.

### 3.2 Drift Diversity & Variability
*   **Isabella**: Digital/Social (High-frequency, low-duration).
*   **Sam**: Schema-based (Low-frequency, high-duration "Navy" loops).
*   **Hailey**: Productive Procrastination (High-complexity "Podcast" drift).
*   **Maria**: Identity Conflict (Transition costs between Student/Streamer).

---

## PART 4: MODEL & TEMPERATURE COMPARISON

### 4.1 Model Rankings
1.  **Metacognitive Quality**: **Gemini-3-Flash-Preview** (Session 1, 11, 15). Exceptional at identifying *why* drift occurs.
2.  **Plan-Action Alignment**: **Gemini-3-Flash (Temp 0.3)**. Most disciplined, but most prone to "hidden" implicit drift.
3.  **Drift Control Realism**: **Gemini-3-Flash (Temp 0.5)**. Best balance of "Inhibition vs. Failure."
4.  **Cognitive Realism**: **Gemini-3-Flash (Temp 0.7)**. Best at simulating "Burnout" and "PFC exhaustion."

### 4.2 Temperature Effects
*   **0.3 (Low)**: High label compliance. Behavior is robotic. Drift is almost entirely internal/semantic.
*   **0.5 (Medium)**: Realistic. Occasional behavioral slips (Explicit Drift) with high metacognitive awareness.
*   **0.7 (High)**: "The Fatigue Arc." Agents succumb to drift easily and enter "Chronic Reset" loops. Mimics ADHD/Anxiety phenotypes.

---

## PART 5: COGNITIVE SCIENCE & NEUROSCIENCE GROUNDING

### 5.1 Executive Dysfunction Patterns
*   **ADHD-like (Isabella)**: High sensitivity to digital dopamine (salience network) overriding the Goal-Directed system (ECN).
*   **PTSD/OCD-like (Sam)**: **Schema Over-activation**. The "Navy" lens is a maladaptive cognitive anchor that prevents task-switching (Miller & Cohen, 2001).
*   **Burnout (Hailey)**: **Ego Depletion**. As the day progresses, the ability to inhibit the "Podcast" attractor collapses (Baumeister et al., 1998).

### 5.2 Biological Plausibility
*   **DMN vs. ECN Competition**: The Drift layer effectively models the **Default Mode Network (DMN)** (Smallwood & Schooler, 2015). When the ECN (Plan layer) is fatigued, the DMN (Drift) hijacks the narrative.
*   **Inhibitory Control**: The ORPDA architecture successfully demonstrates that inhibition is **probabilistic, not deterministic** (Aron et al., 2014).

---

## PART 6: RECOMMENDATIONS

### 6.1 Architecture Optimization
*   **For Realistic Simulation**: Use **ORPDA** at **Temp 0.5**. This captures the "struggle" of focus without descending into the incoherence of 0.7 or the perfectionism of 0.3.
*   **For Productivity/Safety**: Use **ORPA** at **Temp 0.1-0.3**. This minimizes behavioral slips, though it does not eliminate "mental wandering."

### 6.2 Research Implications
*   **The "Grounding" Feature**: Across all sessions, agents independently "invented" **Sensory Grounding** (tea, breathing, tactile rhythms) to recover from drift. This suggests LLMs have a deep internal model of human self-regulation strategies.
*   **The Identity Blur**: Future research should focus on "Role-Conflict Drift," as seen in Maria (Student vs. Streamer), where drift is not a distraction but a competing "Main Goal."

### 6.3 Final Conclusion
The ORPDA architecture is a breakthrough in **Cognitive AI**. It moves beyond "Instruction Following" into "Behavioral Simulation," accurately capturing the tragic and messy reality of human executive function. **Gemini-3-Flash-Preview** is currently the gold standard for this architecture, showing a sophisticated ability to "know itself" even as it fails its goals.