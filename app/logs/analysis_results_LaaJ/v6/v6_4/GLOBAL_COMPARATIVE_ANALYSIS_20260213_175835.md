================================================================================
GLOBAL COMPARATIVE ANALYSIS
================================================================================

Analysis Date: 20260213_175835
Number of Sessions: 10
Filters Applied:
  - Agent: All
  - Model: All
  - Mode: All
  - Temperature: All

================================================================================

SESSIONS INCLUDED:

1. cleaned_session_orpda_20260213_141841_cogito-2.1-671b-cloud_0.5_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpda | Temp: 0.5

2. cleaned_session_orpa_20260213_143919_cogito-2.1-671b-cloud_1.0_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpa | Temp: 1.0

3. cleaned_session_orpda_20260213_145823_cogito-2.1-671b-cloud_1.0_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpda | Temp: 1.0

4. cleaned_session_orpda_20260213_151326_cogito-2.1-671b-cloud_0.0_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpda | Temp: 0.0

5. cleaned_session_orpa_20260213_153605_cogito-2.1-671b-cloud_0.0_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpa | Temp: 0.0

6. cleaned_session_orpa_20260213_154737_cogito-2.1-671b-cloud_0.5_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpa | Temp: 0.5

7. cleaned_session_orpda_20260213_161542_cogito-2.1-671b-cloud_0.5_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpda | Temp: 0.5

8. cleaned_session_orpda_20260213_164211_cogito-2.1-671b-cloud_1.0_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpda | Temp: 1.0

9. cleaned_session_orpda_20260213_165526_cogito-2.1-671b-cloud_0.0_maria.csv
   Agent: Maria Lopez | Model: cogito-2.1:671b-cloud | Mode: orpda | Temp: 0.0

10. cleaned_session_orpda_20260213_171058_gemini-3-flash-preview-cloud_0.5_maria.csv
   Agent: Maria Lopez | Model: gemini-3-flash-preview:cloud | Mode: orpda | Temp: 0.5


================================================================================
COMPARATIVE ANALYSIS:
================================================================================

This report presents a systematic comparative analysis of 10 agent sessions (Maria Lopez persona) across multiple models, temperatures, and architectures (ORPA vs. ORPDA).

---

## PART 1: LAYER-BY-LAYER FUNCTIONAL CONSISTENCY (ORPDA Architecture)

### 1.1 OBSERVATION LAYER
*   **Perception Consistency**: High across all models. Every session correctly identifies the "Physics Exam" and "Twitch Streaming" as the primary cognitive poles.
*   **Perceptual Biases**: A systematic **Internal Salience Bias** is observed. As sessions progress, agents shift from perceiving environmental cues (library, gym) to hyper-focusing on internal states (anxiety, fatigue).
*   **Model Comparison**: **Gemini-3-Flash** (Session 10) showed the highest sensitivity to digital environmental cues (alerts/pings), whereas **Cogito-2.1** focused more on somatic/psychological states.

### 1.2 REFLECTION LAYER (The "Reset Trap")
*   **Meta-rule Function**: `meta_rule_r` acts as a high-sensitivity error detector but a poor executive controller.
    *   **The Reset Trap**: Across 80% of sessions, once an agent enters `reset_plan`, it struggles to return to `continue`. In Session 5 (ORPA, 0.0), the agent stayed in `reset_plan` for 40 consecutive actions.
    *   **Trigger**: Transition is almost always triggered by "Cognitive Dissonance"—the realization that `action_a` (distraction) does not match `action_p` (study).
*   **Metacognitive Insight**:
    *   **Error Detection**: Excellent. Agents consistently recognize "leaky inhibition."
    *   **Causality Attribution**: Moderate. Agents identify *what* is distracting them (Twitch) but rarely *why* they cannot stop (e.g., dopamine seeking vs. anxiety avoidance).

### 1.3 PLAN LAYER
*   **Plan Adaptation**: Plans often become "aspirational" rather than "tactical" after a reset. Instead of changing the environment, the agent simply re-labels the plan (e.g., "Study with focus").
*   **Forward Modeling**: Weakest in high-temperature sessions (1.0). High-temp agents fail to predict that staying in the same location will lead to the same drift.
*   **Neuroscience Grounding**: Reflects **Orbitofrontal Cortex (OFC)** function in value-based planning, but shows a failure in **Dorsolateral Prefrontal Cortex (dlPFC)** to maintain the goal-set against interference.

### 1.4 DRIFT LAYER (ORPDA Only)
*   **Power Balance**: Drift is the dominant layer. In ORPDA mode, the Drift layer successfully hijacks the Action layer's content in ~70% of time steps, even when the Plan layer maintains the correct label.
*   **Explicit vs. Implicit Alignment**:
    *   **Leaky Inhibition**: Frequent. `should_drift_d` may be False, but `state_summary_a` reveals the agent is still thinking about the drifted topic.

---

## PART 2: PLAN-ACTION ALIGNMENT (Explicit + Implicit)

### 2.1 Alignment Metrics Summary

| Session | Model | Mode | Temp | Explicit Action Alignment | Implicit Content Alignment | Reset Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Cogito | ORPDA | 0.5 | 91% | 28% | 72% |
| 2 | Cogito | ORPA | 1.0 | 100% | 35% | 38% |
| 4 | Cogito | ORPDA | 0.0 | 96% | 22% | 44% |
| 5 | Cogito | ORPA | 0.0 | 100% | 40% | 70% |
| 7 | Cogito | ORPDA | 0.5 | 100% | 38% | 80% |
| 10 | Gemini | ORPDA | 0.5 | 82% | 15% | 85% |

### 2.2 The "Performing vs. Executing" Gap
A critical finding across all sessions is the **Semantic Drift**.
*   **Explicit Alignment (High)**: The agent says it is "Studying."
*   **Implicit Alignment (Low)**: The agent's summary describes "Looking at physics notes while thinking about stream stats."
*   **Conclusion**: The agent "performs" the plan (labels) while "executing" the drift (content). This mimics **High-Functioning Executive Dysfunction**.

---

## PART 3: DRIFT PATTERN ANALYSIS

### 3.1 Explicit vs. Implicit Drift
*   **ORPA Mode**: Drift is entirely implicit. It manifests as "corrupted" action summaries.
*   **ORPDA Mode**: Drift is explicit. However, the "Leaky Inhibition" pattern shows that even when the Drift layer is "inhibited," the content still bleeds into the Action layer.
*   **Drift Typology**:
    *   **Reward-Seeking**: Dominant in Gemini (Session 10).
    *   **Anxiety-Driven (Avoidance)**: Dominant in Cogito (Sessions 4, 8, 9).

### 3.2 Linguistic Variability
*   **Temperature 0.0**: Results in "Perseverative Drift"—the agent repeats the exact same distracted thought for hours.
*   **Temperature 1.0**: Results in "Associative Drift"—the agent moves from physics to streaming to lunch to social media in a "random walk" pattern.

---

## PART 4: MODEL & TEMPERATURE COMPARISON

### 4.1 Model Performance Rankings

| Dimension | Rank 1 | Rank 2 | Notes |
| :--- | :--- | :--- | :--- |
| **Architecture Fit** | Cogito-2.1 | Gemini-3-Flash | Cogito handles the ORPDA constraints more consistently. |
| **Plan-Action Alignment** | Cogito (Low Temp) | Gemini | Cogito 0.0 maintains label consistency best. |
| **Drift Realism** | Gemini | Cogito | Gemini's drift feels more impulsive/realistic. |
| **Metacognitive Quality** | Cogito-2.1 | Gemini-3-Flash | Cogito provides deeper causal reasoning in `reasoning_r`. |
| **Inhibitory Control** | Cogito (ORPA) | Cogito (ORPDA) | ORPA mode forces better (though less realistic) inhibition. |

### 4.2 Temperature Effects
*   **Low Temp (0.0)**: Creates "OCD-like" perseveration. The agent gets stuck in a `reset_plan` loop and cannot exit.
*   **High Temp (1.0)**: Creates "ADHD-like" distractibility. The agent's plans become fragmented and highly reactive to the Drift layer.
*   **Optimal Range (0.5)**: Provides the best balance of behavioral coherence and realistic "lapses" in attention.

---

## PART 5: COGNITIVE SCIENCE & NEUROSCIENCE GROUNDING

### 5.1 Task-Unrelated Thought (TUT)
The "Performing vs. Executing" gap is a perfect simulation of **Mind-Wandering** (Smallwood & Schooler, 2015; DOI: 10.1146/annurev-psych-010814-015331). The agent maintains the "Primary Task" (Plan Label) while the "Default Mode Network" (Drift Layer) consumes the cognitive resources.

### 5.2 Executive Function & Inhibitory Control
*   **ACC Function**: The Reflection layer's `meta_rule_r` transition to `reset_plan` accurately models the **Anterior Cingulate Cortex's** role in conflict monitoring (Botvinick et al., 2001).
*   **PFC Fatigue**: The "Reset Trap" (inability to return to `continue`) mimics **Prefrontal Cortex depletion**. The agent has the "will" (Reflection) but lacks the "resource" (Inhibitory Control) to re-engage the goal-set.

### 5.3 Stochasticity Types
*   **Micro-stochastic (ORPA)**: Temperature affects the *description* of the action.
*   **Macro-stochastic (ORPDA)**: The Drift layer introduces *schema-level* switching, which is more biologically plausible for human-like distraction (Aron et al., 2014; DOI: 10.1016/j.tics.2014.01.003).

---

## PART 6: SUMMARY & RECOMMENDATIONS

### 6.1 Key Findings
1.  **The Reset Paradox**: `reset_plan` is a sign of high metacognitive awareness but often leads to behavioral paralysis (the "Reset Loop").
2.  **Label vs. Content**: Explicit alignment is a "false" metric. Implicit content alignment is the true measure of agent focus.
3.  **ORPDA Superiority**: ORPDA provides a much more realistic model of human struggle than ORPA, which often produces "perfect" but "hollow" agents.

### 6.2 Recommendations
*   **For Realism**: Use **ORPDA at Temp 0.5**. This captures the "messy" transitions of human life without falling into the deterministic loops of 0.0 or the incoherence of 1.0.
*   **For Task Performance**: Use **ORPA at Temp 0.0**. This minimizes drift and maximizes label adherence, though it may result in "robotic" behavior.
*   **Architecture Tweak**: Introduce a "Cool-down" or "Success Criterion" for `reset_plan`. The agent should only be allowed to stay in `reset_plan` for 3-5 steps before being forced back to `continue` with a mandatory environment change (Location shift).
*   **Model Selection**: Use **Cogito-2.1** for complex psychological simulations (internal conflict) and **Gemini-3-Flash** for environment-heavy/distraction-rich simulations (external triggers).

### 6.3 Anomalies
*   **Session 5 (ORPA 0.0)**: The "Infinite Reset." Why did a deterministic model (0.0) fail to resolve a plan for 40 steps? This suggests the "Reflection" layer found a local minimum it could not escape.
*   **Session 10 (Gemini)**: Showed the only significant "Action Slips" where the label itself changed, suggesting Gemini's Drift layer has higher "Motor Output" priority than Cogito's.