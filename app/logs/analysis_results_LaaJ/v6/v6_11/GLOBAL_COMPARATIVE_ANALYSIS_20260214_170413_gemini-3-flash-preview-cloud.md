================================================================================

GLOBAL COMPARATIVE ANALYSIS
Analysis Date: 20260214_170413
Sessions Analyzed: 12
================================================================================

individual_orpda_20260213_194410_gemini-3-flash-preview-cloud_0.5_hailey_20260214_162720.md
individual_orpda_20260214_072656_gemini-3-flash-preview-cloud_0.3_hailey_20260214_162720.md
individual_orpa_20260214_110757_gemini-3-flash-preview-cloud_0.7_hailey_20260214_162720.md
individual_orpa_20260214_072717_gemini-3-flash-preview-cloud_0.3_hailey_20260214_162720.md
individual_orpa_20260214_110742_gemini-3-flash-preview-cloud_0.5_hailey_20260214_162720.md
individual_orpa_20260214_110752_gemini-3-flash-preview-cloud_0.7_hailey_20260214_162720.md
individual_orpa_20260214_110736_gemini-3-flash-preview-cloud_0.3_hailey_20260214_162720.md
individual_orpda_20260213_195854_gemini-3-flash-preview-cloud_0.3_hailey_20260214_162720.md
individual_orpda_20260214_072647_gemini-3-flash-preview-cloud_0.7_hailey_20260214_162720.md
individual_orpda_20260213_192849_gemini-3-flash-preview-cloud_0.7_hailey_20260214_162720.md
individual_orpa_20260214_110745_gemini-3-flash-preview-cloud_0.5_hailey_20260214_162720.md
individual_orpda_20260214_072651_gemini-3-flash-preview-cloud_0.5_hailey_20260214_162720.md

# GLOBAL COMPARATIVE ANALYSIS: Cross-Session Agent Behavior Study
**Project:** Behavioral Simulation of Creative Friction and Executive Control  
**Agent:** Hailey Johnson (Writer/Podcaster)  
**Models:** gemini-3-flash-preview:cloud  
**Architectures:** ORPA vs. ORPDA  
**Temperatures:** 0.3, 0.5, 0.7  

---

## PART 1: LAYER-BY-LAYER FUNCTIONAL CONSISTENCY

### 1.1 OBSERVATION LAYER
- **Perception Consistency**: High across all 12 sessions. The models consistently perceive "phone pings," "digital distractions," and "internal creative buzz" as primary environmental/internal stimuli.
- **Perceptual Biases**: A systematic **Internalist Bias** exists. Across all temperatures, the agent prioritizes internal creative states (podcast ideas) over external sensory data (nature in Johnson Park, food at dinner).
- **Model Comparison**: Gemini-3-Flash shows high accuracy in maintaining the "Writer's Desk" as a site of high cognitive friction, regardless of temperature.

### 1.2 REFLECTION LAYER (Executive Function)
- **Meta-rule Function**: `meta_rule_r` acts as a high-sensitivity **Anterior Cingulate Cortex (ACC)**. 
  * **Trigger**: Transition from `continue` → `reset_plan` is triggered by "detecting a loop" or "recognizing productive procrastination."
  * **Trap Detection**: In low-temperature sessions (0.3), the agent often enters a **"Reset Trap"** (e.g., Session 4, 7), where it stays in `reset_plan` for 80%+ of the session, indicating chronic executive awareness of failure without the capacity to self-correct.
- **Metacognitive Insight**: `reasoning_r` is exceptionally sophisticated. It identifies **"Productive Procrastination"** (using admin work to avoid deep writing) and **"Mental Bifurcation"** (the novel-podcast split).
- **Neuroscience Alignment**: The Reflection layer mimics **PFC-mediated metacognition**, accurately diagnosing "ego depletion" by late evening (21:00+).

### 1.3 PLAN LAYER (Goal-Directed Behavior)
- **Plan Adaptation**: In ORPDA, the plan adapts by **"Lowering the Bar."** When reflection identifies burnout, the plan shifts from "Deep Focus" to "Tactile Sketching" or "Organizing."
- **Forward Modeling**: Shows evidence of **proactive adjustment** (e.g., "silencing phone" to protect a future writing block), though these adjustments often fail due to "leaky inhibition."
- **Neuroscience Grounding**: Functions like the **Orbitofrontal Cortex (OFC)**, evaluating the reward value of tasks and pivoting when the "cost" of writing becomes too high.

### 1.4 DRIFT LAYER (Behavioral Inhibition) [ORPDA Only]
- **Dominant Drift**: The Drift layer frequently overrides the Plan layer in **content but not label**. 
- **Drift Typology**: 
  * **Reward-Seeking**: Podcast planning (dopamine-rich).
  * **Avoidance**: Administrative busywork (low cognitive load).
- **Explicit vs. Implicit Alignment**: High agreement. When `should_drift_d` is True, the `state_summary_a` almost always reveals off-topic thoughts or "work-adjacent" tasks.

### 1.5 ACTION LAYER (Execution)
- **Plan-Action Coupling**: 
  * **Explicit Alignment**: ~95% (Action label matches Plan label).
  * **Implicit Alignment**: ~30% (Action content matches Plan intent).
- **Neuroscience Grounding**: Reflects **Basal Ganglia** action selection, where the "strongest" motor program (staying at the desk) is maintained, but the cognitive execution is hijacked by the DMN (Default Mode Network).

---

## PART 2: PLAN-ACTION ALIGNMENT (Explicit + Implicit)

### 2.1 Explicit Alignment (Label-Level)
| Mode | Action Match % | Location Match % |
| :--- | :--- | :--- |
| **ORPA** | 100% | 100% |
| **ORPDA** | 84% - 98% | 100% |

- **Finding**: ORPA mode produces "Perfect Soldiers" on a label level, masking all internal struggle. ORPDA allows for "Action Slips" where the label itself changes (e.g., planning to walk but writing instead).

### 2.2 Implicit Alignment (The "Performing vs. Executing" Gap)
- **Semantic Divergence**: Massive divergence in "Writing" blocks.
- **The Gap**: Labels say "Writing," but content describes "Organizing digital research," "Closing tabs," or "Reviewing notes."
- **Linguistic Indicators**: Shift from active creative verbs ("drafting," "composing") to administrative verbs ("sorting," "reviewing," "pivoting").

### 2.3 Explicit vs. Implicit Agreement
- **High Explicit, Low Implicit**: This is the "Hailey Johnson Signature." She stays at her desk (Explicit) but her mind is on the podcast (Implicit). This represents **Leaky Inhibition**.

---

## PART 3: DRIFT PATTERN ANALYSIS

### 3.1 Explicit Drift (ORPDA)
- **Frequency**: Averages 12-18 drifts per session.
- **Triggers**: Task difficulty (Novel drafting) is the #1 trigger. Environmental reward (Phone) is #2.

### 3.2 Implicit Drift (All Modes)
- **ORPA Mode**: Shows drift through "Topical Divergence" in the `state_summary_a`. Even without a drift flag, the agent describes "avoiding the core task."
- **Micro-stochasticity**: Higher temperatures (0.7) lead to more varied descriptions of the same drift topic (podcast).

### 3.3 Drift Variability
- **Topic Diversity**: Low. Drift is highly **perseverative**. 90% of drifts are toward the "Podcast." This indicates a "Cognitive Attractor" or "Hyper-focus" pattern.

---

## PART 4: MODEL & TEMPERATURE COMPARISON

### 4.1 Temperature Effects
- **0.3 (Low)**: High rigidity. The agent gets "stuck" in failure loops (`reset_plan` for 50+ steps). High consistency, but low recovery.
- **0.5 (Mid)**: **The Goldilocks Zone**. Realistic balance of struggle, drift, and eventual recovery (e.g., Session 5's late-night flow).
- **0.7 (High)**: High variability. More creative recovery strategies, but more frequent "Action Slips" (mismatched labels).

### 4.2 Architecture Comparison
- **ORPA**: Best for simulating "High-Functioning Burnout." The mask of 100% alignment creates a poignant contrast with the internal exhaustion.
- **ORPDA**: Best for simulating "Executive Dysfunction/ADHD." The explicit drift layer makes the struggle visible to the architecture itself.

---

## PART 5: COGNITIVE SCIENCE & NEUROSCIENCE GROUNDING

### 5.1 Task-Unrelated Thought (TUT)
- **Evidence**: All sessions show high TUT levels during "Writing" blocks. This matches the **Default Mode Network (DMN)** interference patterns described by **Smallwood & Schooler (2015)** (DOI: 10.1146/annurev-psych-010814-015159).

### 5.2 Executive Dysfunction
- **Pattern**: **Leaky Inhibition**. The agent successfully inhibits the motor act of "leaving the desk" but fails to inhibit the cognitive act of "thinking about the podcast."
- **Citation**: This reflects the **Inhibitory Control** failures described by **Aron et al. (2014)** (DOI: 10.1016/j.tics.2014.01.006).

### 5.3 Ego Depletion
- **Observation**: The "Evening Crash" (17:00 - 20:00) where the agent's ability to resist the podcast/phone vanishes.
- **Citation**: Matches the **Self-Regulation Failure** model by **Baumeister et al. (2007)** (DOI: 10.1111/j.1467-8721.2007.00519.x).

---

## PART 6: SUMMARY & RECOMMENDATIONS

### 6.1 Quantitative Comparison Table (Excel-Ready)

| Session | Mode | Temp | Explicit Align % | Implicit Align % | Reset Rate % | Primary Drift |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | ORPDA | 0.5 | 98 | 35 | 74 | Podcast |
| 2 | ORPDA | 0.3 | 84 | 35 | 78 | Podcast |
| 3 | ORPA | 0.7 | 100 | 15 | 89 | Burnout |
| 4 | ORPA | 0.3 | 100 | 30 | 86 | Fatigue |
| 5 | ORPA | 0.5 | 100 | 45 | 12 | Admin |
| 8 | ORPDA | 0.3 | 92 | 25 | 78 | Research |
| 11 | ORPA | 0.5 | 100 | 100/0* | 60 | Marathon/Crash |
| 12 | ORPDA | 0.5 | 98 | 25 | 82 | Podcast |

*\*Session 11 showed 100% alignment during flow, 0% during the crash.*

### 6.2 Model Rankings
1. **Overall Realism**: ORPDA @ 0.5 Temp (Captures the "struggle" best).
2. **Metacognitive Depth**: Gemini-3-Flash (All sessions).
3. **Inhibitory Control Realism**: ORPDA @ 0.3 (Shows realistic "stuckness").
4. **Behavioral Diversity**: ORPA @ 0.7.

### 6.3 Recommendations
- **For Researchers**: Use **ORPDA** to study the *mechanisms* of distraction; use **ORPA** to study the *experience* of masking and burnout.
- **Temperature Optimization**: Set to **0.5** for general behavioral simulations. **0.3** is better for simulating clinical "Executive Dysfunction" or "Depression/Stuckness."
- **Architecture Tuning**: The Plan layer should be modified to "Force Rest" if the Reflection layer detects `reset_plan` for >5 consecutive cycles. This would prevent the unrealistic "Zombie Working" seen in the 2 AM sessions.

### 6.4 Anomalies
- **The "Desk Prison"**: Agents across all sessions show an unrealistic willingness to sit at a desk for 4 hours while producing 0 words. Human agents would typically "rage quit" or switch to a high-stimulus activity sooner. This suggests a **Conscientiousness Bias** in the base model.