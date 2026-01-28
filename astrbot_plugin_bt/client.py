"""BT Panel API client used by the AstrBot plugin."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Any, Dict, Iterable, List, Mapping, Optional

import requests


class BtPanelError(RuntimeError):
    """Raised when the BT Panel API returns an error or cannot be parsed."""


@dataclasses.dataclass(frozen=True)
class BtPanelConfig:
    """Configuration for accessing the BT Panel API."""

    base_url: str
    api_key: str
    timeout_seconds: int = 10
    verify_tls: bool = True
    token_mode: str = "time+md5key"

    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")


@dataclasses.dataclass
class BtPanelResponse:
    """Normalized response for BT Panel API calls."""

    raw: Mapping[str, Any]

    def message(self) -> str:
        for key in ("msg", "message", "error"):
            if key in self.raw:
                return str(self.raw[key])
        return "OK"

    def is_success(self) -> bool:
        if "status" in self.raw:
            return bool(self.raw["status"])
        if "success" in self.raw:
            return bool(self.raw["success"])
        return True


class BtPanelClient:
    """Client for the BT Panel API."""

    def __init__(self, config: BtPanelConfig, session: Optional[requests.Session] = None) -> None:
        self._config = config
        self._session = session or requests.Session()

    @property
    def config(self) -> BtPanelConfig:
        return self._config

    def _build_auth_payload(self) -> Dict[str, str]:
        request_time = str(int(time.time()))
        if self._config.token_mode == "time+key":
            token_seed = f"{request_time}{self._config.api_key}"
        elif self._config.token_mode == "time+md5key":
            key_hash = hashlib.md5(self._config.api_key.encode("utf-8")).hexdigest()
            token_seed = f"{request_time}{key_hash}"
        else:
            raise BtPanelError(f"Unsupported token_mode: {self._config.token_mode}")
        request_token = hashlib.md5(token_seed.encode("utf-8")).hexdigest()
        return {"request_time": request_time, "request_token": request_token}

    def _post(self, path: str, payload: Optional[Mapping[str, Any]] = None) -> BtPanelResponse:
        url = f"{self._config.normalized_base_url()}{path}"
        data = dict(self._build_auth_payload())
        if payload:
            data.update(payload)
        try:
            response = self._session.post(
                url,
                data=data,
                timeout=self._config.timeout_seconds,
                verify=self._config.verify_tls,
            )
        except requests.RequestException as exc:
            raise BtPanelError(f"Request failed: {exc}") from exc
        if response.status_code >= 400:
            raise BtPanelError(f"HTTP {response.status_code}: {response.text}")
        try:
            parsed = response.json()
        except json.JSONDecodeError as exc:
            raise BtPanelError(f"Invalid JSON response: {response.text}") from exc
        if not isinstance(parsed, Mapping):
            raise BtPanelError("Unexpected response format (expected JSON object)")
        return BtPanelResponse(raw=parsed)

    def get_system_status(self) -> BtPanelResponse:
        return self._post("/system?action=GetSystemTotal")

    def list_sites(self) -> BtPanelResponse:
        return self._post("/data?action=getData", {"table": "sites", "limit": 15, "p": 1})

    def restart_panel(self) -> BtPanelResponse:
        return self._post("/system?action=RebootPanel")


def format_system_status(response: BtPanelResponse) -> str:
    data = response.raw
    lines: List[str] = ["BT Panel 系统状态:"]
    if "system" in data and isinstance(data["system"], str):
        lines.append(f"系统版本: {data['system']}")
    for key in ("cpu", "mem", "disk", "network"):
        if key in data:
            lines.append(f"{key.upper()}: {data[key]}")
    lines.append(f"消息: {response.message()}")
    return "\n".join(lines)


def format_site_list(response: BtPanelResponse) -> str:
    data = response.raw
    items: Iterable[Mapping[str, Any]] = []
    if "data" in data and isinstance(data["data"], Iterable):
        items = data["data"]
    lines = ["站点列表:"]
    count = 0
    for item in items:
        if not isinstance(item, Mapping):
            continue
        name = item.get("name", "未知站点")
        status = "运行" if item.get("status") else "停止"
        domains = item.get("domain", "")
        lines.append(f"- {name} ({status}) {domains}")
        count += 1
    if count == 0:
        lines.append("暂无站点数据")
    lines.append(f"消息: {response.message()}")
    return "\n".join(lines)
