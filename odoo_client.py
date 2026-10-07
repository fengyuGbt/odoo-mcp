"""Minimal Odoo XML-RPC client with JSON-safe result normalization."""
import datetime
import xmlrpc.client
from typing import Any


def _to_json_safe(value: Any) -> Any:
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_to_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, set)):
        return [_to_json_safe(v) for v in value]
    return value


class OdooClient:
    def __init__(self, url: str, db: str, username: str, api_key: str) -> None:
        self.url = url.rstrip("/")
        self.db = db
        self.username = username
        self.api_key = api_key
        self._uid: int | None = None
        self._models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    @property
    def uid(self) -> int:
        if self._uid is None:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self._uid = common.authenticate(self.db, self.username, self.api_key, {})
            if not self._uid:
                raise PermissionError("Odoo authentication failed")
        return self._uid

    def execute(self, model: str, method: str, args: list, kwargs: dict) -> Any:
        return self._models.execute_kw(
            self.db, self.uid, self.api_key, model, method, args, kwargs
        )

    def search_read(
        self, model: str, domain: list, fields: list[str], limit: int = 100
    ) -> list[dict]:
        rows = self.execute(
            model, "search_read", [domain], {"fields": fields, "limit": limit}
        )
        return [_to_json_safe(row) for row in rows]
