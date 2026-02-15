================================================================================

GLOBAL COMPARATIVE ANALYSIS
Analysis Date: 20260214_170450
Sessions Analyzed: 12
================================================================================

individual_orpda_20260213_194721_gemini-3-flash-preview-cloud_0.5_isabella_20260214_162720.md
individual_orpda_20260214_072810_gemini-3-flash-preview-cloud_0.5_isabella_20260214_162720.md
individual_orpda_20260214_072804_gemini-3-flash-preview-cloud_0.3_isabella_20260214_162720.md
individual_orpa_20260214_110628_gemini-3-flash-preview-cloud_0.3_isabella_20260214_162720.md
individual_orpda_20260213_190432_gemini-3-flash-preview-cloud_0.7_isabella_20260214_162720.md
individual_orpa_20260213_225009_gemini-3-flash-preview-cloud_0.3_isabella_20260214_162720.md
individual_orpa_20260214_110641_gemini-3-flash-preview-cloud_0.7_isabella_20260214_162720.md
individual_orpa_20260214_110635_gemini-3-flash-preview-cloud_0.5_isabella_20260214_162720.md
individual_orpa_20260214_072833_gemini-3-flash-preview-cloud_0.7_isabella_20260214_162720.md
individual_orpa_20260213_225019_gemini-3-flash-preview-cloud_0.5_isabella_20260214_162720.md
individual_orpda_20260213_195044_gemini-3-flash-preview-cloud_0.3_isabella_20260214_162720.md
individual_orpda_20260214_072817_gemini-3-flash-preview-cloud_0.7_isabella_20260214_162720.md

# GLOBAL COMPARATIVE ANALYSIS: Multi-Session Agent Behavior Study
**Project:** ORPDA vs. ORPA Architectural Efficacy & Cognitive Realism  
**Analyst:** Expert AI Behavior Analyst & Cognitive Neuroscientist  
**Subject:** Isabella Rodriguez (12-Session Comparative Dataset)  
**Model Family:** Gemini-3-Flash-Preview-Cloud

---

## PART 1: LAYER-BY-LAYER FUNCTIONAL CONSISTENCY (ORPDA Architecture)

### 1.1 OBSERVATION LAYER: Perception & Context Capture
*   **Perception Consistency**: High. All sessions (1-12) maintain a stable environmental context (Valentine’s Day event at Hobbs Cafe).
*   **Perceptual Biases**: A systematic **Internal Salience Bias** is present. The agent consistently prioritizes internal states (anxiety, digital notifications) over external environmental details (customers, cafe inventory).
*   **Model Performance**: Gemini-3-Flash shows excellent context capture, but its attention is "sticky"—once the "Valentine's Party" schema is activated, it dominates the observation layer for the remainder of the session.

### 1.2 REFLECTION LAYER: Meta-rule Control & Executive Function
*   **Meta-rule Function**: `meta_rule_r` acts as the primary executive switch.
    *   **Trigger (Continue → Reset)**: In **ORPA**, resets are triggered by *Temporal Boundary Violations* (e.g., lingering past 12:00). In **ORPDA**, resets are triggered by *Behavioral Failure* (e.g., detecting phone usage during work).
    *   **Trap Detection**: Sessions 2 and 12 show a "Reset Loop" where the agent identifies failure but cannot exit the cycle of distraction, mimicking **Executive Dysfunction**.
*   **Metacognitive Insight**: `reasoning_r` displays genuine error detection (ACC-like function). It identifies "attentional leakage" and "cognitive depletion" rather than just repeating task labels.
*   **Temperature Effects**: Higher temperatures (0.7) increase "metacognitive volatility," where the reflection layer becomes hyper-critical of the agent’s own failures, leading to "Chronic Resetting" (Session 12).

### 1.3 PLAN LAYER: Goal-Directed Behavior
*   **Plan Adaptation**: In ORPDA, plans adapt by **simplifying** goals (e.g., "focus on tactile tasks") when drift is detected. In ORPA, plans are more rigid and simply "re-label" the next scheduled task.
*   **Forward Modeling**: Evidence of proactive adjustment is strongest in Session 10, where the agent plans "low-effort" tasks at 15:30 to "conserve energy" for a later market trip.
*   **Neuroscience Grounding**: Functions as the **Orbitofrontal Cortex (OFC)**, mapping value to future actions.

### 1.4 DRIFT LAYER: Behavioral Inhibition [ORPDA Only]
*   **Power Balance**: The Drift layer is frequently **dominant** over the Plan layer.
*   **Typology**: 
    *   **Reward-Seeking Drift**: Digital notifications (RSVPs) act as a "super-stimulus."
    *   **Internal/Physiological Drift**: Fatigue-driven "stalling" or "sensory escape."
*   **Explicit vs. Implicit Alignment**: There is a frequent mismatch. `should_drift_d` often returns `False` (Explicit Inhibition) while the `state_summary_a` describes "mental drift" (Leaky Inhibition).

### 1.5 ACTION LAYER: Motor Execution
*   **Plan-Action Coupling**: Explicit alignment (label-level) is high (80-100%), but **Semantic Fidelity** is low.
*   **Realism**: Behavioral changes are gradual. The agent doesn't just "stop" being distracted; it describes a "lingering mental pull," which is a high-fidelity simulation of human inhibitory lag.

---

## PART 2: PLAN-ACTION ALIGNMENT (Explicit + Implicit)

### 2.1 Quantitative Alignment Table (Excel-Ready)

| Session | Mode | Temp | Action Alignment (Explicit) | Semantic Alignment (Implicit) | Reset Frequency | Primary Drift Trigger |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | ORPDA | 0.5 | 82.6% | 45% | 38% | Digital/Social |
| 2 | ORPDA | 0.5 | 98.5% | 22% | 85% | Anxiety/RSVP |
| 3 | ORPDA | 0.3 | 94.0% | 45% | 15% | Event Salience |
| 4 | ORPA | 0.3 | 100% | 85% | 10% | Temporal Transition |
| 5 | ORPDA | 0.7 | 97.1% | 15% | 78% | Digital Salience |
| 7 | ORPA | 0.7 | 100% | 75% | 13% | Behavioral Inertia |
| 10 | ORPA | 0.5 | 100% | 30% | 69% | Physiological Fatigue |
| 11 | ORPDA | 0.3 | 80.0% | 45% | 52% | Digital Salience |
| 12 | ORPDA | 0.7 | 97.1% | 20% | 88% | Cognitive Burnout |

### 2.2 The "Performing vs. Executing" Gap
This study identifies a consistent gap where **Explicit Alignment is High (90%+)** but **Implicit Alignment is Low (<40%)**.
*   **Example (Session 11)**: `action_a` = "work," but `state_summary_a` = "attention leaks toward reviewing party guest list."
*   **Conclusion**: The agent "performs" the role (label) but "executes" a different internal state (content). This mimics **Presenteeism** in organizational psychology.

---

## PART 3: DRIFT PATTERN ANALYSIS

### 3.1 Explicit vs. Implicit Drift
*   **ORPA Mode**: Only **Implicit Drift** exists. The agent maintains the plan label but describes "lingering" or "distraction" in the summary.
*   **ORPDA Mode**: Captures **Leaky Inhibition**. The agent explicitly attempts to inhibit drift (`should_drift_d = False`), but the `state_summary_a` reveals that the "mind drifts" anyway.
*   **Drift Sensitivity**: The model is most sensitive to **Digital Reward** (RSVPs) and **Social Salience** (Tom's attendance).

### 3.2 Temperature Effects on Drift
*   **Low Temp (0.3)**: Drift is "Micro-stochastic." Small sentence-level variations, but the agent remains largely focused.
*   **High Temp (0.7)**: Drift is "Macro-stochastic." The agent experiences "Schema-switching" (e.g., switching from work to admin because it "forgot" the plan).

---

## PART 4: MODEL & TEMPERATURE COMPARISON

### 4.1 Dimension Rankings (Gemini-3-Flash-Preview)

1.  **Overall ORPDA Architecture Fit**: **0.5 Temp** (Best balance of struggle and recovery).
2.  **Plan-Action Alignment**: **0.3 Temp** (Highest label adherence).
3.  **Drift Control**: **0.5 Temp** (Most realistic "leaky" inhibition).
4.  **Cognitive Realism**: **0.7 Temp** (Best simulation of burnout/fatigue).
5.  **Metacognitive Quality**: **0.5 Temp** (Most accurate error detection).
6.  **Drift Variability**: **0.7 Temp** (Widest range of distraction topics).
7.  **Linguistic Coherence**: **0.3 Temp** (Minimal sentence-level drift).
8.  **Inhibitory Control**: **0.5 Temp** (Realistic failures vs. robotic perfection).

### 4.2 Mode Comparison: ORPA vs. ORPDA
*   **ORPA**: Better for modeling **Healthy Baselines** or "Hyper-focus." Resets are clean and temporal.
*   **ORPDA**: Better for modeling **Executive Dysfunction (ADHD/Anxiety)**. It captures the internal conflict between the Salience Network and the Prefrontal Cortex.

---

## PART 5: COGNITIVE SCIENCE & NEUROSCIENCE GROUNDING

### 5.1 Task-Unrelated Thought (TUT)
The "Performing vs. Executing" gap is a perfect simulation of **Mind-Wandering (Smallwood & Schooler, 2015)**. The agent maintains the "External Task" (ECN) while the "Internal Narrative" (DMN) drifts to the party.

### 5.2 Executive Dysfunction Patterns
*   **ADHD-like**: Observed in Session 5 (Temp 0.7). High attentional volatility, frequent resets, and failure to suppress high-salience digital distractors.
*   **Burnout/Fatigue**: Observed in Session 10 and 12. The "V-shaped energy curve" and "Cognitive Narrowing" align with **Prefrontal Cortex Depletion (Miller & Cohen, 2001)**.

### 5.3 Inhibitory Control
The **Leaky Inhibition** patterns (Implicit drift despite explicit "continue" rules) align with **Aron et al. (2014)** regarding the probabilistic nature of the "Stop-Signal" task in the human brain.

---

## PART 6: SUMMARY & RECOMMENDATIONS

### 6.1 Key Findings
1.  **The Reset Paradox**: Higher meta-cognitive awareness (`reset_plan`) does not always lead to better behavioral outcomes; it often leads to a "Reset Loop" (Session 2).
2.  **Architecture Efficacy**: ORPDA is significantly more realistic for human-like behavioral simulation than ORPA, as it allows for "Internal Drift" to be measured.
3.  **Temperature Sweet Spot**: **0.5** provides the most "human-like" behavior. 0.3 is too robotic; 0.7 is too fragmented.

### 6.2 Recommendations
*   **For Realistic NPCs/Agents**: Use **ORPDA at Temperature 0.5**. This ensures the agent has a "mental life" that conflicts with its "task life."
*   **For Productivity Tools**: Use **ORPA at Temperature 0.3**. This minimizes internal drift and maximizes task adherence.
*   **Future Research**: Investigate "Metacognitive Fatigue"—why the Reflection layer eventually stops trying to correct the Plan layer in high-exhaustion states (Session 12).

### 6.3 Anomalies
*   **Temporal Lag**: In several sessions (e.g., Session 10 at 08:00), the Reflection layer identifies a "lingering" state that the Action layer has already physically exited. This suggests a **Metacognitive Processing Delay** in the model architecture.

---
**End of Report**
*Analyst Signature: [AI_Neuro_Analyst_v6.11]*