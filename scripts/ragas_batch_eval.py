"""
Ragas nightly batch evaluation for Axioma 2.0.

Pulls a random sample of yesterday's traces from Langfuse, evaluates them
with Ragas (Faithfulness, Answer Relevancy, Context Precision), and uploads
the scores back to Langfuse as trace-level annotations.

Designed to run as a nightly cron job — NOT in the hot path of requests.

Usage:
    python scripts/ragas_batch_eval.py [--sample 100] [--date 2026-04-14]

Required env vars:
    LANGFUSE_PUBLIC_KEY
    LANGFUSE_SECRET_KEY
    LANGFUSE_HOST          (default: https://cloud.langfuse.com)
    OPENAI_API_KEY         (used by Ragas LLM-as-judge)
"""

import argparse
import asyncio
import os
import random
import sys
from datetime import date, timedelta, datetime, timezone

from langfuse import Langfuse
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

RAGAS_METRICS = [faithfulness, answer_relevancy, context_precision]

# Ragas score names to Langfuse score names
SCORE_NAME_MAP = {
    "faithfulness": "ragas/faithfulness",
    "answer_relevancy": "ragas/answer_relevancy",
    "context_precision": "ragas/context_precision",
}


# ─────────────────────────────────────────────
# Trace extraction helpers
# ─────────────────────────────────────────────

def extract_rag_fields(trace) -> dict | None:
    """
    Extract question, answer, and context from a Langfuse trace.

    Looks for spans/observations named 'chat' or 'rag' and extracts:
    - question: trace input
    - answer: trace output
    - contexts: list of retrieved chunk texts

    Returns None if required fields are missing.
    """
    try:
        # Trace input is the user question
        question = None
        if isinstance(trace.input, dict):
            question = trace.input.get("prompt") or trace.input.get("question") or trace.input.get("query")
        elif isinstance(trace.input, str):
            question = trace.input

        # Trace output is the LLM answer
        answer = None
        if isinstance(trace.output, dict):
            answer = trace.output.get("response") or trace.output.get("answer") or trace.output.get("text")
        elif isinstance(trace.output, str):
            answer = trace.output

        if not question or not answer:
            return None

        # Look for context chunks in observations
        contexts: list[str] = []
        for obs in getattr(trace, "observations", []) or []:
            obs_output = getattr(obs, "output", None)
            if isinstance(obs_output, dict):
                results = obs_output.get("results", [])
                if isinstance(results, list):
                    for chunk in results:
                        text = chunk.get("text") if isinstance(chunk, dict) else None
                        if text:
                            contexts.append(text)

        # Ragas requires at least one context chunk for faithfulness and context_precision
        if not contexts:
            return None

        return {
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "trace_id": trace.id,
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
# Main evaluation loop
# ─────────────────────────────────────────────

def run_batch_eval(sample_size: int, eval_date: date) -> None:
    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        print("ERROR: LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set.", file=sys.stderr)
        sys.exit(1)

    langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST,
    )

    # Date window: full day in UTC
    from_ts = datetime(eval_date.year, eval_date.month, eval_date.day, tzinfo=timezone.utc)
    to_ts = from_ts + timedelta(days=1)

    print(f"Fetching traces for {eval_date} (UTC {from_ts} → {to_ts})...")

    # Fetch traces — Langfuse paginates; we collect up to 5x sample_size then subsample
    all_traces = []
    page = 1
    limit = 100
    while len(all_traces) < sample_size * 5:
        result = langfuse.fetch_traces(
            from_timestamp=from_ts,
            to_timestamp=to_ts,
            limit=limit,
            page=page,
        )
        batch = result.data if hasattr(result, "data") else []
        if not batch:
            break
        all_traces.extend(batch)
        if len(batch) < limit:
            break
        page += 1

    print(f"  → {len(all_traces)} traces fetched before filtering")

    # Extract RAG fields and filter incomplete traces
    rag_rows = []
    for trace in all_traces:
        row = extract_rag_fields(trace)
        if row:
            rag_rows.append(row)

    if not rag_rows:
        print("No valid RAG traces found for this date. Nothing to evaluate.")
        return

    # Random sample
    if len(rag_rows) > sample_size:
        rag_rows = random.sample(rag_rows, sample_size)

    print(f"  → {len(rag_rows)} traces selected for evaluation")

    # Build Ragas dataset
    dataset = Dataset.from_list([
        {
            "question": r["question"],
            "answer": r["answer"],
            "contexts": r["contexts"],
        }
        for r in rag_rows
    ])

    print("Running Ragas evaluation (LLM-as-judge)...")
    ragas_result = evaluate(dataset, metrics=RAGAS_METRICS)
    scores_df = ragas_result.to_pandas()

    print("Uploading scores to Langfuse...")
    uploaded = 0
    for i, row in enumerate(rag_rows):
        trace_id = row["trace_id"]
        for ragas_key, langfuse_name in SCORE_NAME_MAP.items():
            score_value = scores_df.iloc[i].get(ragas_key)
            if score_value is not None and not isinstance(score_value, float) or (
                isinstance(score_value, float) and not __import__("math").isnan(score_value)
            ):
                langfuse.score(
                    trace_id=trace_id,
                    name=langfuse_name,
                    value=float(score_value),
                    comment=f"Ragas batch eval — {eval_date}",
                )
                uploaded += 1

    langfuse.flush()
    print(f"Done. Uploaded {uploaded} scores for {len(rag_rows)} traces.")
    print("\nSummary:")
    for ragas_key, langfuse_name in SCORE_NAME_MAP.items():
        if ragas_key in scores_df.columns:
            mean_val = scores_df[ragas_key].mean()
            print(f"  {langfuse_name}: {mean_val:.4f}")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ragas nightly batch evaluation — scores yesterday's traces."
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=100,
        help="Number of traces to evaluate (default: 100)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date to evaluate in YYYY-MM-DD format (default: yesterday)",
    )
    args = parser.parse_args()

    if args.date:
        eval_date = date.fromisoformat(args.date)
    else:
        eval_date = date.today() - timedelta(days=1)

    run_batch_eval(sample_size=args.sample, eval_date=eval_date)


if __name__ == "__main__":
    main()
