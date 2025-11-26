# app/config/config.py
import yaml
from pathlib import Path


ROOT = Path.cwd()
print(ROOT)


CONFIG_PATH = ROOT / "app/config/config.yaml"


def load_config():
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


config = load_config()
MODEL_NAME = config.get("model", {}).get("name", "gemini-2.5-flash-lite")
MODEL_NAME_2 = config.get("model2", {}).get("name", "gemini-2.5-flash-lite")


# event_log = {
#     "timestamp": timestamp,
#     "type": "conversation",
#     "context": context,
#     "author": author,
#     "text": text,
#     "importance": score,
# }


# def event_log_to_file(self, event_log, agent_name):
#     """event_log to event_logs.jsonl"""
#     with open(EVENT_LOG_PATH, "a", encoding="utf-8") as f:
#         f.write(json.dumps(event_log) + "\n")


# async def main():
#     days, recency = calc_recency_score(datetime.date(2025, 11, 20))
#     print(f"Days since: {days}, recency score: {recency:.4f}")

#     async with InMemoryRunner(agent=importance_agent) as runner:
#         await run_and_log(
#             "I spend a lot of time percolating ideas to build a multi-agent RPG town 2.0",
#             runner,
#         )
#         await run_and_log("Hi. How are you?", runner)
#         await run_and_log(
#             "I have a presentation coming up this Friday. I am very nervous.", runner
#         )
#         await run_and_log(
#             "I am going to have dinner in an hour with my boyfriend. I am exhausted from working 12 hours today.",
#             runner,
#         )
