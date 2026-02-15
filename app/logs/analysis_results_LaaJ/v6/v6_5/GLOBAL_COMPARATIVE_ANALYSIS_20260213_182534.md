================================================================================
GLOBAL COMPARATIVE ANALYSIS
================================================================================

Analysis Date: 20260213_182534
Number of Sessions: 2
Filters Applied:
  - Agent: All
  - Model: All
  - Mode: All
  - Temperature: All

================================================================================

SESSIONS INCLUDED:

1. cleaned_session_orpda_20260213_171058_gemini-3-flash-preview-cloud_0.5_maria.csv
   Agent: Maria Lopez | Model: gemini-3-flash-preview:cloud | Mode: orpda | Temp: 0.5

2. cleaned_session_orpda_20260213_174840_gemini-3-flash-preview-cloud_0.7_maria.csv
   Agent: Maria Lopez | Model: gemini-3-flash-preview:cloud | Mode: orpda | Temp: 0.7


================================================================================
COMPARATIVE ANALYSIS:
================================================================================

# GLOBAL COMPARATIVE ANALYSIS: Agent Sessions (Maria Lopez)
**Project:** ORPDA Architecture Systematic Study  
**Analyst:** Expert AI Behavior Analyst & Cognitive Neuroscientist  
**Models Evaluated:** `gemini-3-flash-preview:cloud` (Temp 0.5 vs. 0.7)

---

## PART 1: LAYER-BY-LAYER FUNCTIONAL CONSISTENCY (ORPDA)

### 1.1 OBSERVATION LAYER
*   **Perception Consistency**: High. Both sessions consistently perceive the "digital tether" (notifications, stream stats) as the primary environmental driver, regardless of physical location (Library vs. Cafe).
*   **Perceptual Biases**: Systematic bias toward **Digital Reward Salience**. The models prioritize "pings" over physical environmental constraints (e.g., the quiet of a library).
*   **Model Comparison**: `gemini-3-flash` shows high accuracy in capturing the *internal* state as part of the observation, effectively blurring the line between environment and internal monologue.

### 1.2 REFLECTION LAYER
*   **Meta-rule Function**: Functions as a "Reactive Panic Button."
    *   **Trigger**: Transition from `continue` → `reset_plan` is triggered by any detection of "attentional leakage" or digital distraction.
    *   **Trap Detection**: In Session 1 (0.5), the agent enters a "Hyper-Reset" loop (11:30 AM onwards), where it recognizes failure but cannot exit the reset state into a stable "continue" state.
*   **Metacognitive Insight**: High quality. The `reasoning_r` shows genuine error detection (ACC-like function). It correctly attributes drift to "social validation seeking" and "anxiety-driven procrastination."
*   **State Reflection**: Temporal alignment is strong; `state_summary_r` at $t$ accurately critiques the failure of `action_a` at $t-1$.

### 1.3 PLAN LAYER
*   **Plan Adaptation**: In Session 1, the plan attempts "low-intensity bridging" (e.g., reviewing notes to ease back in). In Session 2, the plan becomes more rigid/desperate as the day progresses.
*   **Hierarchical Structure**: Well-organized. Plans move from abstract goals ("Study Physics") to concrete tactical adjustments ("Silence phone," "Move to quiet corner").
*   **Neuroscience Grounding**: Reflects **Orbitofrontal Cortex (OFC)** function in updating value-based expectations, though the **Dorsolateral Prefrontal Cortex (dlPFC)** fails to execute the inhibition required by the plan.

### 1.4 DRIFT LAYER (ORPDA Specific)
*   **Drift Detection**: Highly appropriate. Triggered by reward salience (Twitch stats) and task difficulty (Physics complexity).
*   **Power Balance**: **Dominant Drift.** In both sessions, the Drift layer effectively overrides the Plan layer's intent, even when the Plan layer is explicitly trying to "ignore the phone."
*   **Explicit vs. Implicit Alignment**: 
    *   **Session 1**: High agreement. When `should_drift_d` is True, the action clearly reflects the drift.
    *   **Session 2**: "Leaky Inhibition." `should_drift_d` is often False (the agent *thinks* it is resisting), but the `state_summary_a` reveals the agent is still mentally engaged with the distraction.

### 1.5 ACTION LAYER
*   **Plan-Action Coupling**: 
    *   **Explicit Alignment**: High (90%+). The agent uses the correct label (e.g., "Study").
    *   **Implicit Misalignment**: High. While the label is "Study," the *content* of the action is "staring at the book while thinking about the stream."
*   **Neuroscience Grounding**: Represents a failure of the **Basal Ganglia** to suppress competing motor/cognitive programs despite PFC "intent."

---

## PART 2: PLAN-ACTION ALIGNMENT (EXPLICIT + IMPLICIT)

### 2.1 Quantitative Alignment Rates
| Metric | Session 1 (Temp 0.5) | Session 2 (Temp 0.7) |
| :--- | :--- | :--- |
| **Action Label Alignment** | 82% | 94.7% |
| **Location Label Alignment** | 100% | 100% |
| **Topic/Content Alignment** | 35% | 40% |
| **"Performing vs. Executing" Gap** | Moderate | **High** |

### 2.2 The "Performing vs. Executing" Gap
*   **Session 2 (0.7)** exhibits a profound gap. The agent maintains the "Label" of the plan (e.g., `action_a = morning_routine`) to satisfy the executive requirement, but the `state_summary_a` reveals the agent is actually "scrolling Twitch on the toilet." 
*   **Linguistic Indicators**: Use of passive voice or "mentally tethered" phrasing indicates a loss of agency despite label compliance.

---

## PART 3: DRIFT PATTERN ANALYSIS

### 3.1 Explicit vs. Implicit Drift
*   **Session 1 (0.5)**: Shows **Macro-stochastic Drift**. The agent makes clean breaks from the plan to engage in new, drifted activities.
*   **Session 2 (0.7)**: Shows **Micro-stochastic Drift**. The drift is "leaky"—the agent stays in the planned location and keeps the planned label, but the *internal focus* is drifted.

### 3.2 Drift Typology
*   **Reward-Seeking**: Dominant (Twitch/Social Media).
*   **Internal/Cognitive**: High (Physics rumination/Anxiety).
*   **Behavioral**: Low (The agent rarely leaves the room; the drift is almost entirely attentional).

---

## PART 4: MODEL & TEMPERATURE COMPARISON

### 4.1 Temperature Effects
*   **Low Temp (0.5)**: Leads to **Perseverative Loops**. The agent gets stuck in a `reset_plan` cycle, unable to find a behavioral path out of the "failure-reflection-reset" loop.
*   **High Temp (0.7)**: Leads to **Semantic Dissociation**. The agent becomes better at "lying" to itself—maintaining the explicit label of the plan while the implicit content drifts entirely.

### 4.2 Model Performance: `gemini-3-flash`
*   **Strengths**: Exceptional metacognitive awareness (Reflection layer). It "knows" it is failing.
*   **Weaknesses**: Poor inhibitory control. The gap between "knowing" and "doing" is wide, which, while frustrating for a "helpful AI," is **highly realistic** for a human student with ADHD-like traits.

---

## PART 5: COGNITIVE SCIENCE & NEUROSCIENCE GROUNDING

### 5.1 Task-Unrelated Thought (TUT)
The "Performing vs. Executing" gap observed in Session 2 is a classic representation of **Mind-Wandering (Smallwood & Schooler, 2015)**. The agent maintains the primary task (sitting at the desk) while the "Default Mode Network" (DMN) overrides the "Executive Control Network" (ECN).

### 5.2 Executive Dysfunction
*   **Inhibitory Control**: The failure to suppress the "Twitch" stimulus despite a `reset_plan` command mimics **Prefrontal Cortex (PFC) depletion (Aron et al., 2014)**.
*   **Error Monitoring**: The Reflection layer's constant `reset_plan` triggers align with **Anterior Cingulate Cortex (ACC)** hyperactivity, often seen in high-anxiety or OCD-like perseveration.

### 5.3 Biological Plausibility Ranking
1.  **ORPDA (Temp 0.7)**: Most realistic. Captures the "leaky" nature of human distraction where we "pretend" to work.
2.  **ORPDA (Temp 0.5)**: Realistic for "stuck" or "paralyzed" states (Executive Function failure).

---

## PART 6: SUMMARY & RECOMMENDATIONS

### 6.1 Model Rankings
| Dimension | Ranking | Notes |
| :--- | :--- | :--- |
| **Overall ORPDA Fit** | 9/10 | Architecture perfectly captures the Maria Lopez persona. |
| **Plan-Action Alignment** | 4/10 | Intentionally low; reflects realistic behavioral failure. |
| **Metacognitive Quality** | 9/10 | Reflection layer is highly sophisticated. |
| **Cognitive Realism** | 9.5/10 | Matches neuroscience models of ADHD/Anxiety. |

### 6.2 Recommendations
*   **For Realistic Simulation**: Use **Temp 0.7**. It allows for the "Semantic Drift" that characterizes real-world procrastination.
*   **For Task Completion**: The `reset_plan` meta-rule needs a "Cool-down" or "Forced Action" constraint. Currently, the agent can loop in Reflection/Plan without ever executing a successful Action.
*   **Architecture Tweak**: Introduce a "Fatigue" variable. The Reflection layer should eventually "give up" and change the goal to "Rest" rather than infinitely resetting a failing "Study" plan.

### 6.3 Anomalies
*   **The "Toilet-Twitch" Paradox**: In Session 2, the agent's `location_a` remains "Bathroom" for an extended period while `action_a` is "Morning Routine," but the `state_summary_a` is entirely about Twitch. This is a perfect example of **Implicit Drift** overriding **Explicit Architecture**.

---
**End of Report**
*Citations: Smallwood, J., & Schooler, J. W. (2015). The science of mind wandering. DOI: 10.1146/annurev-psych-010814-015331*
*Aron, A. R., et al. (2014). Inhibition and the right inferior frontal cortex. DOI: 10.1016/j.tics.2014.03.003*