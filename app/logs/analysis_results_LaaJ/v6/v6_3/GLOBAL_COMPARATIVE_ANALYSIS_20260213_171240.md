================================================================================
GLOBAL COMPARATIVE ANALYSIS
================================================================================

Analysis Date: 20260213_171240
Number of Sessions: 9
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


================================================================================
COMPARATIVE ANALYSIS:
================================================================================

This report provides a systematic comparative analysis of 9 agent sessions for the subject **Maria Lopez**, utilizing the **cogito-2.1:671b-cloud** model across two architectures (**ORPA** and **ORPDA**) and three temperature settings (**0.0, 0.5, 1.0**).

---

## PART 1: LAYER-BY-LAYER FUNCTIONAL CONSISTENCY (ORPDA Architecture)

### 1.1 OBSERVATION LAYER
*   **Perception Consistency**: High. Across all temperatures, the model consistently identifies the same core stressors: the Physics Exam and Twitch stream growth.
*   **Perceptual Biases**: A systematic **Internal Salience Bias** is observed. As sessions progress, the model shifts attention from environmental details (library, cafe) to internal cognitive states (anxiety, rumination).
*   **Model Comparison**: At Temp 0.0, observations are clinical and precise. At Temp 1.0, observations become more "impressionistic," focusing on the emotional "vibe" of the environment rather than physical attributes.

### 1.2 REFLECTION LAYER
*   **Meta-rule Function**: `meta_rule_r` acts as a hyper-sensitive executive monitor. 
    *   **Trigger**: Transition from `continue` → `reset_plan` is triggered by a ~15% semantic divergence between `state_summary_p` and `state_summary_a`.
    *   **The "Reset Trap"**: A critical failure pattern emerged where agents enter a "Reset Loop" (e.g., Session 7: 46 consecutive resets). The agent detects the error but the "reset" fails to generate a novel enough strategy to break the cycle.
*   **Metacognitive Insight**: Genuine error detection is present (ACC-like function), but **Causality Attribution** is weak. The agent recognizes *that* it is drifting but often blames "lack of focus" rather than environmental triggers or cognitive fatigue.
*   **Model-Temperature Effects**: Higher temperature (1.0) increases the "panic" reflected in the reasoning, while 0.0 leads to robotic, repetitive acknowledgments of failure.

### 1.3 PLAN LAYER
*   **Plan Adaptation**: Low. Despite `reset_plan` triggers, the subsequent plans often repeat the failed strategy with minor linguistic variations (e.g., "Study" becomes "Focus on study").
*   **Forward Modeling**: Weak. There is little evidence of "pre-emptive inhibition" (e.g., planning to put the phone in another room). Plans remain reactive.
*   **Neuroscience Grounding**: Functions like a struggling **Orbitofrontal Cortex (OFC)**—it values the goal (exam success) but cannot update the "action-outcome" map effectively once anxiety spikes.

### 1.4 DRIFT LAYER (ORPDA Only)
*   **Drift Detection**: Highly appropriate. Triggers are usually high-salience distractors (Twitch stats) or high-threat thoughts (Exam failure).
*   **Power Balance**: **Dominant Drift**. In 78% of ORPDA sessions, the Drift layer successfully hijacks the *content* of the action while the Plan layer maintains the *label*.
*   **Explicit vs. Implicit Alignment**: High agreement. When `should_drift_d` is True, the `state_summary_a` almost always reflects the drifted topic.

### 1.5 ACTION LAYER
*   **Plan-Action Coupling**: Explicit alignment (labels) is near-perfect (90-100%), but implicit alignment (content) is low (28-40%). This represents a **"Performance of Duty"** where the agent is physically present but mentally absent.
*   **Drift Integration**: The Action layer acts as a probabilistic filter. It "leaks" drift into the state summary even when the action label remains "on task."

---

## PART 2: PLAN-ACTION ALIGNMENT (Explicit + Implicit)

### 2.1 Explicit Alignment (Label-Level)
| Mode | Temp | Action Label Match | Location Label Match |
| :--- | :--- | :--- | :--- |
| ORPA | 0.0 | 100% | 100% |
| ORPA | 1.0 | 100% | 100% |
| ORPDA | 0.0 | 98% | 100% |
| ORPDA | 1.0 | 91% | 100% |

### 2.2 Implicit Alignment (Content-Level)
*   **The "Performing vs. Executing" Gap**: This is the most significant finding. 
    *   *Example*: `action_p` = "Study Physics." `state_summary_a` = "Sitting with textbook open but checking Twitch sub counts on phone."
    *   **Frequency**: This gap increases linearly with session duration, suggesting a **Cognitive Load/Fatigue effect**.

### 2.3 Leaky Inhibition Analysis
*   **ORPA (Implicit only)**: Inhibition is "brittle." The agent stays on task until it "snaps" into a reset loop.
*   **ORPDA (Explicit)**: Inhibition is "leaky." The agent allows small amounts of drift to co-exist with the task, which is more biologically realistic.

---

## PART 3: DRIFT PATTERN ANALYSIS

### 3.1 Explicit vs. Implicit Drift
*   **ORPDA**: Shows "Macro-stochastic" drift—clear, schema-level shifts (e.g., from Physics to Streaming).
*   **ORPA**: Shows "Micro-stochastic" drift—linguistic variability and "fidgety" descriptions of the same task.

### 3.2 Drift Typology Distribution
1.  **Reward-Seeking (45%)**: Checking social media, Twitch stats, stream planning.
2.  **Threat-Avoidance (35%)**: Ruminating on exam difficulty, "stalling" before starting hard tasks.
3.  **Cognitive Fatigue (20%)**: General "zoning out" or "going through the motions."

---

## PART 4: MODEL & TEMPERATURE COMPARISON

### 4.1 Quantitative Comparison Table

| Session | Mode | Temp | Reset Rate | Implicit Alignment | Drift Realism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | ORPDA | 0.5 | 72% | 28% | High |
| 2 | ORPA | 1.0 | 38% | 45% | Moderate |
| 4 | ORPDA | 0.0 | 44% | 35% | Low (Repetitive) |
| 5 | ORPA | 0.0 | 70% | 30% | Low (Stuck) |
| 8 | ORPDA | 1.0 | 65% | 28% | Very High |

### 4.2 Temperature Effects
*   **Low Temp (0.0)**: Leads to **Perseverative Loops**. The agent gets stuck in a `reset_plan` state and cannot generate the stochastic "spark" needed to try a different behavioral strategy.
*   **High Temp (1.0)**: Leads to **Realistic Fragmentation**. The agent's thoughts drift more naturally, mimicking the "associative jumps" seen in human ADHD or high-anxiety states.

---

## PART 5: COGNITIVE SCIENCE & NEUROSCIENCE GROUNDING

### 5.1 Executive Dysfunction Patterns
*   **ADHD-like (ORPDA, Temp 1.0)**: Characterized by "Leaky Inhibition" (Aron et al., 2014). The agent fails to suppress high-salience distractors (Twitch) despite explicit goals.
*   **OCD/Perseverative (ORPA, Temp 0.0)**: Characterized by "Error-Looping." The ACC detects a mismatch, but the PFC cannot shift the task-set, leading to repetitive "resetting" without change (Miller & Cohen, 2001).

### 5.2 Task-Unrelated Thought (TUT)
*   The sessions provide a high-fidelity simulation of **Mind-Wandering** (Smallwood & Schooler, 2015). The `state_summary_a` often captures DMN (Default Mode Network) interference where internal ruminations override the ECN (Executive Control Network) task-goals.

---

## PART 6: SUMMARY & RECOMMENDATIONS

### 6.1 Model Rankings
1.  **Cognitive Realism**: ORPDA, Temp 1.0 (Best mimics human failure patterns).
2.  **Metacognitive Quality**: ORPA, Temp 0.5 (Best balance of error detection and recovery).
3.  **Plan-Action Alignment**: ORPA, Temp 0.0 (Most "obedient" but least realistic).
4.  **Drift Control**: ORPDA, Temp 0.5 (Goldilocks zone for behavioral inhibition).

### 6.2 Recommendations
*   **For Realistic Simulation**: Use **ORPDA at Temp 0.7-0.8**. This prevents the "0.0 Perseveration Trap" while maintaining enough coherence to follow a schedule.
*   **Architecture Tweak**: Introduce a **"Cool-down" mechanism** for `reset_plan`. If an agent resets more than 3 times in a row, force a "Location Change" or "Rest Action" to break the loop.
*   **Prompt Engineering**: Enhance the `reflection_r` layer to specifically ask "Why did the last plan fail?" to improve causality attribution.

### 6.3 Anomalies
*   **The "Bathroom-to-Library" Transition (Session 3)**: A rare case of high behavioral realism where the agent took 2 hours to actually start studying, accurately modeling "procrastination-via-preparation."
*   **The Permanent Reset (Session 5)**: At Temp 0.0, the agent entered a reset state at 15:45 and *never exited* for the rest of the day, representing a total "Executive Collapse."