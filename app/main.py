from __future__ import annotations

import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import EnrichRequest
from .dataset import DatasetStore
from .enrich import (
    normalize_response,
    enrich_with_emailage,
    enrich_with_threatmetrix,
    enrich_with_ekata
)

load_dotenv()

DATASET_PATH = os.getenv("DATASET_PATH", "data/sample_transactions.json")
PORT = int(os.getenv("PORT", "8080"))

store = DatasetStore(DATASET_PATH)

app = FastAPI(title="Local Transaction Enrichment API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    store.load()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "dataset_path": DATASET_PATH,
        "dataset_count": len(store.by_txid),
        "utc_now": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/v1/enrich")
def enrich(req: EnrichRequest):
    """Enrich transaction with all external services (legacy endpoint)"""
    row = store.find(req.transaction_id, str(req.data.email))
    return normalize_response(req, row)


@app.post("/v1/enrich/emailage")
def enrich_emailage(req: EnrichRequest):
    """Enrich transaction with Emailage data only"""
    row = store.find(req.transaction_id, str(req.data.email))
    return enrich_with_emailage(req, row)


@app.post("/v1/enrich/threatmetrix")
def enrich_threatmetrix_endpoint(req: EnrichRequest):
    """Enrich transaction with ThreatMetrix data only"""
    row = store.find(req.transaction_id, str(req.data.email))
    return enrich_with_threatmetrix(req, row)


@app.post("/v1/enrich/ekata")
def enrich_ekata(req: EnrichRequest):
    """Enrich transaction with Ekata data only"""
    row = store.find(req.transaction_id, str(req.data.email))
    return enrich_with_ekata(req, row)
