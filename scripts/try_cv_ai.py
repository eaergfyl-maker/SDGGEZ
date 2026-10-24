"""Send one invented sample CV to the RunPod model and print what survives the checks.

Usage: python -m scripts.try_cv_ai [sample_id]   (needs RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID)
Also handy as a warm-up just before a demo, so the first real request is not a cold start.
"""
import sys
import time

from backend.app import data_loader
from backend.app.scoring import cv_ai

name = sys.argv[1] if len(sys.argv) > 1 else "customer_service"
sample = next(s for s in data_loader.sample_cvs() if s["id"] == name)
start = time.monotonic()
r = cv_ai.suggest(sample["text"], data_loader.skills())
print(f"{sample['title']}: status={r['status']} model={r['model']} "
      f"suggested={r.get('suggested', 0)} kept={len(r['possible'])} in {time.monotonic() - start:.0f}s")
for x in r["possible"]:
    print(f"  {x['name']}: \"{x['evidence']}\"")
