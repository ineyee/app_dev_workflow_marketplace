#!/usr/bin/env python3
"""Send the Nearstream review submission notification to a WeCom robot."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_WECOM_WEBHOOK = (
    "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=02aa9754-7a61-429c-a8f8-bb18e5222568"
)
WECOM_WEBHOOK = os.environ.get("WECOM_WEBHOOK", DEFAULT_WECOM_WEBHOOK)
DEFAULT_MENTIONED_MOBILES: tuple[str, ...] = (
    "18868112221",
    "15796578657",
    "15558097426"
)
MENTIONED_MOBILES = tuple(
    mobile.strip()
    for mobile in os.environ.get(
        "WECOM_MENTIONED_MOBILES", ",".join(DEFAULT_MENTIONED_MOBILES)
    ).split(",")
    if mobile.strip()
)
DEFAULT_TIMEOUT_SECONDS = 15
REVIEW_NOTIFICATION_LIMIT = (999, 999, 999)


class NotificationError(RuntimeError):
    """Raised when a WeCom notification cannot be delivered or is rejected."""


def _parse_version(version: str) -> tuple[int, ...]:
    value = version.strip()
    parts = value.split(".")
    if not value or not parts or any(not part.isdigit() for part in parts):
        raise NotificationError(f"Invalid version: {version!r}")
    return tuple(int(part) for part in parts)


def should_notify_review(version: str) -> bool:
    """Return whether a review submission notification is allowed for version."""

    parsed = _parse_version(version)
    width = max(len(parsed), len(REVIEW_NOTIFICATION_LIMIT))
    normalized = parsed + (0,) * (width - len(parsed))
    limit = REVIEW_NOTIFICATION_LIMIT + (0,) * (width - len(REVIEW_NOTIFICATION_LIMIT))
    return normalized < limit


def build_review_submitted_message(version: str) -> str:
    """Build the exact text requested for the review submission notice."""

    version = version.strip()
    _parse_version(version)
    return f"【iOS 端】+【Android 端】已提审，提审版本号：{version}"


def build_review_submitted_payload(
    version: str,
    mentioned_mobiles: Iterable[str] = MENTIONED_MOBILES,
) -> dict:
    if not should_notify_review(version):
        raise NotificationError(
            f"Skipped WeCom notification for version {version.strip()!r}: "
            "version must be lower than 999.999.999"
        )
    mobiles = tuple(mobile.strip() for mobile in mentioned_mobiles if mobile.strip())
    return {
        "msgtype": "text",
        "text": {
            "content": build_review_submitted_message(version),
            "mentioned_mobile_list": list(mobiles),
        },
    }


def send_payload(
    payload: dict,
    webhook: str = WECOM_WEBHOOK,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict:
    webhook = webhook.strip()
    if not webhook:
        raise NotificationError(
            "WeCom webhook is not configured; edit WECOM_WEBHOOK or set the "
            "WECOM_WEBHOOK environment variable"
        )
    request = Request(
        webhook,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as error:
        raise NotificationError(f"WeCom HTTP error {error.code}") from error
    except URLError as error:
        raise NotificationError(f"WeCom network error: {error.reason}") from error
    try:
        result = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise NotificationError("WeCom returned invalid JSON") from error
    if result.get("errcode") != 0:
        raise NotificationError(
            f"WeCom rejected notification: {result.get('errmsg', 'unknown error')}"
        )
    return result


def push_review_submitted(
    version: str,
    mentioned_mobiles: Iterable[str] = MENTIONED_MOBILES,
    webhook: str = WECOM_WEBHOOK,
) -> dict:
    return send_payload(
        build_review_submitted_payload(version, mentioned_mobiles), webhook=webhook
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send Nearstream WeCom notifications")
    subparsers = parser.add_subparsers(dest="method", required=True)
    review = subparsers.add_parser(
        "review-submitted", help="notify the review submission version"
    )
    review.add_argument("--version", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.method == "review-submitted" and not should_notify_review(args.version):
        print(
            "notify_wecom: skipped review-submitted for version "
            f"{args.version.strip()} (threshold: 999.999.999)"
        )
        return 0
    try:
        push_review_submitted(version=args.version)
    except NotificationError as error:
        print(f"notify_wecom: {error}", file=sys.stderr)
        return 1
    print(f"notify_wecom: sent {args.method}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
