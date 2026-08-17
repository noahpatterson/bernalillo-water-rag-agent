"""Simple Eve LLM-as-judge eval, ported from agent_evaluation_simple.ipynb.

Asks a running Eve agent ground-truth questions, caches answers, then judges
relevance the same way as the Zoomcamp RAG eval lesson.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import cast

import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI
from tqdm.auto import tqdm

from utils.utils import DEFAULT_GROUND_TRUTH, GroundTruthQuery

load_dotenv()

DEFAULT_EVE_HOST = os.getenv("EVE_HOST", "http://127.0.0.1:3000")
DEFAULT_EVE_MODEL = os.getenv("OPENAI_MODEL_DEV", "gpt-5.4-mini")
DEFAULT_JUDGE_MODEL = "gpt-5.4-mini"
DEFAULT_RESULTS_CSV = Path("evaluation/agent_evaluation_results.csv")
DEFAULT_DATA_CSV = Path("evaluation/agent_evaluation_data.csv")

prompt2_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as 'NON_RELEVANT', 'PARTLY_RELEVANT', or 'RELEVANT'.

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer_llm}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  'Relevance': 'NON_RELEVANT' | 'PARTLY_RELEVANT' | 'RELEVANT',
  'Explanation': '[Provide a brief explanation for your evaluation]'
}}
""".strip()


@dataclass(frozen=True)
class EveResponse:
    question: str
    document: int
    answer_llm: str
    session_id: str


def ask_eve__get_session(question: str, eve_host: str = DEFAULT_EVE_HOST) -> str | None:
    eve_health_url = f"{eve_host}/eve/v1/health"

    health_check = False
    try:
        health_check = requests.get(eve_health_url).status_code == 200
    except Exception:
        print("Eve service doesn't appear to be running")
        raise ConnectionError

    if not health_check:
        return None

    eve_session_url = f"{eve_host}/eve/v1/session"
    payload = {"message": question}
    session = None
    try:
        session = requests.post(eve_session_url, json=payload)
    except Exception:
        print("Issue creating Eve session")
        raise ConnectionError

    session_json = session.json()
    session_id = session_json["sessionId"]

    return session_id


def reset_eve_session(session_id: str, eve_host: str = DEFAULT_EVE_HOST) -> None:
    """Retire a one-shot eval session so Eve does not re-queue it on the next boot."""
    try:
        requests.post(
            f"{eve_host}/eve/v1/session/{session_id}/reset",
            json={"reason": "eval complete"},
            timeout=10,
        )
    except Exception:
        print(f"Issue resetting Eve session {session_id}")


def ask_eve(
    ground_truth: GroundTruthQuery, eve_host: str = DEFAULT_EVE_HOST
) -> EveResponse | None:
    session_id = ask_eve__get_session(ground_truth["question"], eve_host)

    if not session_id:
        return None

    stream_url = f"{eve_host}/eve/v1/session/{session_id}/stream"
    response = None
    try:
        response = requests.get(stream_url, stream=True)
        response.raise_for_status()

        completed_messages = []
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            event = json.loads(line)
            if (
                event["type"] == "message.completed"
                and event["data"]["finishReason"] == "stop"
            ):
                completed_messages.append(event["data"]["message"])
            if event["type"] in (
                "session.waiting",
                "session.completed",
                "turn.failed",
            ):
                if not completed_messages:
                    return None
                return EveResponse(
                    ground_truth["question"],
                    ground_truth["document"],
                    completed_messages[-1],
                    session_id,
                )
        return None
    except Exception:
        print("error reading eve session stream")
        return None
    finally:
        if response is not None:
            response.close()
        reset_eve_session(session_id, eve_host)


def cache_eve_call(
    ground_truth: GroundTruthQuery,
    store: list[EveResponse],
    eve_host: str = DEFAULT_EVE_HOST,
):
    response = ask_eve(ground_truth, eve_host)
    if response:
        store.append(response)


def collect_eve_answers(
    ground_truth: list[GroundTruthQuery],
    eve_host: str = DEFAULT_EVE_HOST,
) -> list[EveResponse]:
    """Ask Eve each ground-truth question and cache the answers."""
    store: list[EveResponse] = []
    for truth in tqdm(ground_truth):
        cache_eve_call(cast(GroundTruthQuery, truth), store, eve_host)
    return store


def save_eve_answers(
    store: list[EveResponse],
    path: Path,
    eve_model: str,
) -> Path:
    """Write cached Eve answers, tagging the Eve model used to generate them."""
    df_eve_responses = pd.DataFrame(store)
    df_eve_responses["eve_model"] = eve_model
    path.parent.mkdir(parents=True, exist_ok=True)
    df_eve_responses.to_csv(path, index=False)
    return path


def load_eve_answers(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def judge_eve_responses(
    eve_responses: pd.DataFrame,
    judge_model: str,
    openai_client: OpenAI | None = None,
) -> list[tuple[dict, dict]]:
    """Judge each cached answer with the Zoomcamp relevance prompt."""
    if openai_client is None:
        openai_client = OpenAI()

    sample = eve_responses.to_dict(orient="records")
    evaluations = []

    for record in tqdm(sample):
        question = record["question"]
        answer_llm = record["answer_llm"]

        prompt = prompt2_template.format(
            question=question,
            answer_llm=answer_llm,
        )

        evaluation = openai_client.responses.create(model=judge_model, input=prompt)

        evaluations.append((record, json.loads(evaluation.output_text)))

    return evaluations


def build_eval_df(evaluations: list[tuple[dict, dict]]) -> pd.DataFrame:
    """Turn judge tuples into the notebook's relevance table."""
    df_eval = pd.DataFrame(evaluations, columns=["record", "evaluation"])
    categories = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]

    df_eval["id"] = df_eval.record.apply(lambda d: d["document"])
    df_eval["question"] = df_eval.record.apply(lambda d: d["question"])
    df_eval["answer_llm"] = df_eval.record.apply(lambda d: d["answer_llm"])
    df_eval["session_id"] = df_eval.record.apply(lambda d: d["session_id"])
    df_eval["relevance"] = df_eval.evaluation.apply(lambda d: d["Relevance"])
    df_eval["explanation"] = df_eval.evaluation.apply(lambda d: d["Explanation"])

    df_eval["relevance"] = pd.Categorical(
        df_eval["relevance"],
        categories=categories,
    )
    return df_eval


def save_results(
    df_eval: pd.DataFrame,
    eve_model: str,
    judge_model: str,
    path: Path = DEFAULT_RESULTS_CSV,
) -> Path:
    """Append judged rows. ``run_date``, Eve model, and judge model key the run."""
    run_date = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = df_eval[
        ["id", "question", "answer_llm", "session_id", "relevance", "explanation"]
    ].copy()
    rows.insert(0, "run_date", run_date)
    rows.insert(1, "eve_model", eve_model)
    rows.insert(2, "judge_model", judge_model)

    if path.exists():
        existing = pd.read_csv(path)
        out = pd.concat([existing, rows], ignore_index=True)
    else:
        out = rows
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    return path


def print_last_run_metrics(path: Path = DEFAULT_RESULTS_CSV) -> None:
    """Print relevance counts for the most recently appended eval run."""
    df = pd.read_csv(path)
    last_run = df["run_date"].iloc[-1]
    run = df[df["run_date"] == last_run]
    print(f"run_date={last_run}")
    print(f"eve_model={run['eve_model'].iloc[0]}")
    print(f"judge_model={run['judge_model'].iloc[0]}")
    print(run.relevance.value_counts(normalize=True))


def main(
    eve_model: str = DEFAULT_EVE_MODEL,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    sample_size: int = 10,
    eve_host: str = DEFAULT_EVE_HOST,
    ground_truth_path: Path = DEFAULT_GROUND_TRUTH,
    data_path: Path | None = None,
    results_path: Path = DEFAULT_RESULTS_CSV,
    metrics_only: bool = False,
) -> Path:
    """Collect Eve answers with ``eve_model`` and judge them with ``judge_model``.

    Eve itself is whatever model the running Compose ``eve`` service (or host
    ``pnpm dev``) was started with (``OPENAI_MODEL_DEV``). Pass ``eve_model``
    to label the data and results for that run. Restart Eve with a different
    ``OPENAI_MODEL_DEV`` to generate answers from another model.
    """
    if metrics_only:
        print_last_run_metrics(results_path)
        return results_path

    if data_path is None:
        slug = eve_model.replace(".", "_").replace("/", "_").replace("-", "_")
        data_path = Path(f"evaluation/agent_evaluation_data_{slug}.csv")

    if data_path.exists():
        print(f"using existing Eve answers at {data_path}")
        eve_responses = load_eve_answers(data_path)
    else:
        df_ground_truth = pd.read_csv(ground_truth_path)
        ground_truth = df_ground_truth.to_dict(orient="records")
        ground_truth_sample = ground_truth[:sample_size]

        print(f"collecting Eve answers (eve_model={eve_model})...")
        store = collect_eve_answers(
            cast(list[GroundTruthQuery], ground_truth_sample),
            eve_host,
        )
        save_eve_answers(store, data_path, eve_model)
        print(f"saved {len(store)} answers to {data_path}")
        eve_responses = pd.DataFrame(store)
    print(f"judging with {judge_model}...")
    evaluations = judge_eve_responses(eve_responses, judge_model)
    df_eval = build_eval_df(evaluations)
    print(df_eval.relevance.value_counts(normalize=True))

    saved = save_results(df_eval, eve_model, judge_model, results_path)
    print(
        f"saved results to {saved} (eve_model={eve_model}, judge_model={judge_model})"
    )
    return saved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple Eve LLM-as-judge eval.")
    parser.add_argument("--eve-model", default=DEFAULT_EVE_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--sample-size", type=int, default=10)
    parser.add_argument("--eve-host", default=DEFAULT_EVE_HOST)
    parser.add_argument("--ground-truth-path", type=Path, default=DEFAULT_GROUND_TRUTH)
    parser.add_argument("--data-path", type=Path, default=None)
    parser.add_argument("--results-path", type=Path, default=DEFAULT_RESULTS_CSV)
    parser.add_argument(
        "--metrics-only",
        action="store_true",
        help="Print the last eval run's metrics and exit.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(
        eve_model=args.eve_model,
        judge_model=args.judge_model,
        sample_size=args.sample_size,
        eve_host=args.eve_host,
        ground_truth_path=args.ground_truth_path,
        data_path=args.data_path,
        results_path=args.results_path,
        metrics_only=args.metrics_only,
    )
