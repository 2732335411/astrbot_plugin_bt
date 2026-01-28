"""AstrBot command registration for BT Panel."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .client import (
    BtPanelClient,
    BtPanelConfig,
    BtPanelError,
    format_site_list,
    format_system_status,
)


def _load_config(config: Optional[Dict[str, Any]]) -> BtPanelConfig:
    if not config:
        raise BtPanelError("Missing plugin configuration")
    try:
        return BtPanelConfig(
            base_url=str(config["base_url"]),
            api_key=str(config["api_key"]),
            timeout_seconds=int(config.get("timeout_seconds", 10)),
            verify_tls=bool(config.get("verify_tls", True)),
            token_mode=str(config.get("token_mode", "time+md5key")),
        )
    except KeyError as exc:
        raise BtPanelError(f"Missing config key: {exc}") from exc


def _handle_command(client: BtPanelClient, command: str) -> str:
    if command == "bt status":
        response = client.get_system_status()
        return format_system_status(response)
    if command == "bt sites":
        response = client.list_sites()
        return format_site_list(response)
    if command == "bt restart panel":
        response = client.restart_panel()
        return f"面板重启结果: {response.message()}"
    if command == "bt help":
        return (
            "可用命令:\n"
            "- bt status\n"
            "- bt sites\n"
            "- bt restart panel\n"
            "- bt help"
        )
    return "未知命令，请使用 bt help 查看支持的命令。"


def register(bot: Any, config: Optional[Dict[str, Any]] = None) -> None:
    """Register commands with AstrBot.

    The bot is expected to provide a `register_command` method accepting
    `(command: str, handler: Callable[[], str])`.
    """

    panel_config = _load_config(config or {})
    client = BtPanelClient(panel_config)

    def make_handler(command: str) -> Callable[[], str]:
        def handler() -> str:
            try:
                return _handle_command(client, command)
            except BtPanelError as exc:
                return f"BT Panel 请求失败: {exc}"

        return handler

    if not hasattr(bot, "register_command"):
        raise BtPanelError("Bot does not support register_command")

    for command in ("bt status", "bt sites", "bt restart panel", "bt help"):
        bot.register_command(command, make_handler(command))
