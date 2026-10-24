"""Suggest extra CV skills with an LLM on RunPod. Owner: Member 3.

The keyword matcher in cv.py stays the main reader. This module asks a model (Qwen3-8B on a
RunPod serverless vLLM endpoint) for skills the keywords missed, then checks every answer:

  - the skill id must exist in data/skills.json, so the model cannot invent skills;
  - the quote must appear word for word in the redacted CV text, so it cannot invent evidence;
  - skills the keyword matcher already returned are skipped, so there are no duplicates.

What survives is returned as level "possible" with source "ai": the UI shows it unticked and
the person decides. The model only ever sees the redacted text (no emails or phone numbers).
Nothing is stored or logged, and errors never include the CV text.

Settings (Replit Secrets, or .env locally): RUNPOD_API_KEY, RUNPOD_ENDPOINT_ID, and optionally
RUNPOD_MODEL for the label shown to users. Without the first two the feature reports "off".
"""
import json
import logging
import os
import re
import time

import httpx

from .cv import match_cv, redact

MODEL_CHARS = 12_000             # CV characters sent to the model; fits an 8192-token context
MAX_TOKENS = 800                 # length of the model's reply
TIMEOUT = 90                     # seconds in total, enough for a cold start with a cached model
POLL = 2                         # seconds between status checks while the job is queued
API = "https://api.runpod.ai/v2/{endpoint}"
NOTE = "suggested by AI; the quote was checked against your CV"

log = logging.getLogger(__name__)

SYSTEM = (
    "You read CVs and pick skills from a fixed list. Pick a skill only if the CV shows the person "
    "has already used it. Do not pick skills they only want to learn, are learning, or say they "
    "lack. For each pick, copy one short quote (3 to 12 words) exactly as written in the CV. "
    "Use only ids from the list. Reply with JSON only, no other text: "
    '{"skills": [{"id": "skill_id", "quote": "exact words from the CV"}]}'
)


class AIUnavailable(Exception):
    """The model could not be reached or gave no usable reply."""


def enabled() -> bool:
    return bool(os.environ.get("RUNPOD_API_KEY") and os.environ.get("RUNPOD_ENDPOINT_ID"))


def model_name() -> str:
    return os.environ.get("RUNPOD_MODEL", "Qwen/Qwen3-8B")


def build_messages(clean: str, skills: list[dict]) -> list[dict]:
    listing = "\n".join(f"{s['id']}: {s['name']}" for s in skills)
    user = (f"Skill list (id: name):\n{listing}\n\n"
            f'CV:\n"""\n{clean[:MODEL_CHARS]}\n"""\n\n/no_think')  # /no_think: skip Qwen3's reasoning
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def _output_text(output) -> str:
    """Pull the reply text out of the worker-vllm output (its own format or the OpenAI one)."""
    if isinstance(output, list):
        output = output[0] if output else None
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        choices = output.get("choices") or []
        if choices:
            c = choices[0]
            if "tokens" in c:
                return "".join(c["tokens"])
            if "message" in c:
                return c["message"].get("content") or ""
            return c.get("text") or ""
    raise AIUnavailable("unexpected reply format")


def call_model(messages: list[dict]) -> str:
    """Send one chat request to the RunPod endpoint and wait for the reply text."""
    base = API.format(endpoint=os.environ["RUNPOD_ENDPOINT_ID"])
    headers = {"Authorization": f"Bearer {os.environ['RUNPOD_API_KEY']}"}
    body = {"input": {"messages": messages,
                      "sampling_params": {"temperature": 0, "max_tokens": MAX_TOKENS}}}
    deadline = time.monotonic() + TIMEOUT
    try:
        # submit with /run and poll /status with short requests: a held-open /runsync can
        # outlast the HTTP timeout while a cold worker starts
        with httpx.Client(timeout=15) as client:
            r = client.post(f"{base}/run", json=body, headers=headers)
            r.raise_for_status()
            job = r.json()
            while job.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
                if time.monotonic() > deadline:
                    client.post(f"{base}/cancel/{job['id']}", headers=headers)
                    raise AIUnavailable("timed out waiting for a worker")
                time.sleep(POLL)
                r = client.get(f"{base}/status/{job['id']}", headers=headers)
                r.raise_for_status()
                job = r.json()
    except httpx.HTTPError as e:
        raise AIUnavailable(type(e).__name__) from None
    if job.get("status") != "COMPLETED":
        raise AIUnavailable(f"job {job.get('status')}")
    return _output_text(job.get("output"))


def parse_reply(text: str) -> list[dict]:
    """The model's picks as a list of {"id", "quote"}; anything unreadable is dropped."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        return []
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return []
    picks = data.get("skills") if isinstance(data, dict) else None
    return [p for p in picks if isinstance(p, dict)] if isinstance(picks, list) else []


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def verify(picks: list[dict], clean: str, skills: list[dict], skip: set[str]) -> list[dict]:
    """Keep picks with a real skill id and a quote that is literally in the CV."""
    by_id = {s["id"]: s for s in skills}
    hay = _norm(clean)
    out, seen = [], set(skip)
    for p in picks:
        sid, quote = p.get("id"), p.get("quote")
        if not isinstance(sid, str) or sid not in by_id or sid in seen or not isinstance(quote, str):
            continue
        q = _norm(quote).strip(" .,;:\"'…")
        if len(q) < 3 or q not in hay:
            continue
        seen.add(sid)
        out.append({
            "skill": sid, "name": by_id[sid]["name"], "level": "possible", "source": "ai",
            "term": None, "evidence": " ".join(quote.split()).strip(" \"'"), "note": NOTE,
        })
    out.sort(key=lambda r: r["name"])
    return out


def suggest(text: str, skills: list[dict], call=None) -> dict:
    """Extra "possible" skills from the model, after the checks above.

    status is "ok", "off" (no RunPod settings) or "error" (model unreachable or slow); in the
    last two cases possible is empty and the keyword results are unaffected.
    """
    result = {"status": "off", "model": model_name(), "possible": []}
    if not enabled():
        return result
    clean, _ = redact(text)
    keywords = match_cv(text, skills)
    skip = {r["skill"] for r in keywords["found"] + keywords["possible"]}
    try:
        picks = parse_reply((call or call_model)(build_messages(clean, skills)))
    except AIUnavailable as e:
        log.warning("CV AI unavailable: %s", e)          # never log the CV text
        return {**result, "status": "error"}
    return {**result, "status": "ok", "possible": verify(picks, clean, skills, skip),
            "suggested": len(picks)}
