#!/usr/bin/env python3
"""Shared data structures for iran-war-tracker."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SearchResult:
    title: str
    content: str
    url: str = ""
    published_date: str = ""
    published_at: str = ""
    source: str = ""
    timestamp_verified: bool = False
    within_lookback: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NewsBundle:
    topic: str
    query: str
    provider: str
    answer: str = ""
    results: list[SearchResult] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["results"] = [item.to_dict() for item in self.results]
        return data


@dataclass
class AssetSnapshot:
    name: str
    symbol: str
    price: str = ""
    change_pct: str = ""
    source: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReportContext:
    generated_at: str
    framework: dict[str, Any]
    news: dict[str, NewsBundle]
    telegraph: list[dict[str, Any]]
    assets: dict[str, AssetSnapshot]
    meta: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "framework": self.framework,
            "news": {key: bundle.to_dict() for key, bundle in self.news.items()},
            "telegraph": self.telegraph,
            "assets": {key: asset.to_dict() for key, asset in self.assets.items()},
            "meta": self.meta,
        }
