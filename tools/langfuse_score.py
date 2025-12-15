from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

# Method 1: Score via low-level method
# langfuse.create_score(
#     name="correctness",
#     value=0.9,
#     trace_id="d001a1b032b8975791d578e1d82f5649",
#     observation_id="cf2d2f94316b6e6a",  # optional
#     data_type="NUMERIC",  # optional, inferred if not provided
#     comment="Factually correct",  # optional
# )

# Method 2: Score current span/generation (within context)
with langfuse.start_as_current_observation(as_type="span", name="my-operation") as span:
    # Score the current span
    span.score(
        name="correctness", value=0.8, data_type="NUMERIC", comment="Factually correct"
    )

    # Score the trace
    span.score_trace(name="overall_quality", value=0.95, data_type="NUMERIC")


# # Method 3: Score via the current context
# with langfuse.start_as_current_observation(as_type="span", name="my-operation"):
#     # Score the current span
#     langfuse.score_current_span(
#         name="correctness", value=0.9, data_type="NUMERIC", comment="Factually correct"
#     )

#     # Score the trace
#     langfuse.score_current_trace(
#         name="overall_quality", value=0.95, data_type="NUMERIC"
#     )
