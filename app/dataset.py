from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


def _safe_lower(s: Optional[str]) -> str:
    return (s or "").strip().lower()


class DatasetStore:
    """
    Loads a small JSON dataset into memory.
    - Primary lookup: transaction_id
    - Secondary lookup: email -> most recent transaction_time
    """

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.by_txid: Dict[str, Dict[str, Any]] = {}
        self.email_index: Dict[str, List[str]] = {}

    def load(self) -> None:
        self.by_txid = {}
        self.email_index = {}

        if not os.path.exists(self.dataset_path):
            return

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            rows = json.load(f)

        for row in rows:
            txid = row.get("transaction", {}).get("transaction_id")
            if not txid:
                continue
            self.by_txid[txid] = row

            email = _safe_lower(row.get("customer", {}).get("email"))
            if email:
                self.email_index.setdefault(email, []).append(txid)

    def find(self, transaction_id: str, email: str) -> Optional[Dict[str, Any]]:
        if transaction_id in self.by_txid:
            return self.by_txid[transaction_id]

        e = _safe_lower(email)
        txids = self.email_index.get(e, [])
        if not txids:
            return None

        def parse_time(row: Dict[str, Any]) -> float:
            t = row.get("transaction", {}).get("transaction_time")
            try:
                # Accept Z timestamps
                return datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() if t else 0.0
            except Exception:
                return 0.0

        rows = [self.by_txid[txid] for txid in txids if txid in self.by_txid]
        rows.sort(key=parse_time, reverse=True)
        return rows[0] if rows else None
