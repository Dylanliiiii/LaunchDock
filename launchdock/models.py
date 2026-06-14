from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def now_text() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def new_id() -> str:
    return str(uuid4())


@dataclass
class Link:
    id: str
    name: str
    url: str
    default_open: bool = True
    order: int = 1

    @classmethod
    def create(cls, name: str, url: str, default_open: bool = True, order: int = 1) -> "Link":
        return cls(id=new_id(), name=name.strip(), url=url.strip(), default_open=default_open, order=order)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Link":
        return cls(
            id=str(data.get("id") or new_id()),
            name=str(data.get("name") or "未命名链接"),
            url=str(data.get("url") or ""),
            default_open=bool(data.get("default_open", True)),
            order=int(data.get("order") or 1),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "default_open": self.default_open,
            "order": self.order,
        }


@dataclass
class Project:
    id: str
    name: str
    folder_name: str
    created_at: str
    updated_at: str
    links: list[Link] = field(default_factory=list)

    @classmethod
    def create(cls, name: str, folder_name: str) -> "Project":
        timestamp = now_text()
        return cls(
            id=new_id(),
            name=name.strip(),
            folder_name=folder_name,
            created_at=timestamp,
            updated_at=timestamp,
            links=[],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any], fallback_folder_name: str) -> "Project":
        links = [Link.from_dict(item) for item in data.get("links", []) if isinstance(item, dict)]
        links.sort(key=lambda item: item.order)
        for index, link in enumerate(links, start=1):
            link.order = index
        timestamp = now_text()
        return cls(
            id=str(data.get("id") or new_id()),
            name=str(data.get("name") or "未命名项目"),
            folder_name=str(data.get("folder_name") or fallback_folder_name),
            created_at=str(data.get("created_at") or timestamp),
            updated_at=str(data.get("updated_at") or timestamp),
            links=links,
        )

    def touch(self) -> None:
        self.updated_at = now_text()

    def normalize_link_order(self) -> None:
        self.links.sort(key=lambda item: item.order)
        for index, link in enumerate(self.links, start=1):
            link.order = index

    def to_dict(self) -> dict[str, Any]:
        self.normalize_link_order()
        return {
            "id": self.id,
            "name": self.name,
            "folder_name": self.folder_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "links": [link.to_dict() for link in self.links],
        }
