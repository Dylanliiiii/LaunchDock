from __future__ import annotations

import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import __version__

UPDATE_CONFIG_FILE = "update-config.json"
GITHUB_REPO_URL = "https://github.com/Dylanliiiii/LaunchDock"
GITHUB_UPDATE_REPO_URL = "https://github.com/Dylanliiiii/LaunchDock.git"
GITHUB_RELEASES_URL = f"{GITHUB_REPO_URL}/releases"
GITHUB_LATEST_RELEASE_API = "https://api.github.com/repos/Dylanliiiii/LaunchDock/releases/latest"
DEFAULT_UPDATE_CONFIG = {
    "update_channel": "global",
    "update_repo_url": GITHUB_UPDATE_REPO_URL,
    "release_page_url": GITHUB_RELEASES_URL,
    "release_api_url": GITHUB_LATEST_RELEASE_API,
}


def version_parts(version: str) -> tuple[int, ...]:
    cleaned = version.strip().lower().lstrip("v")
    parts: list[int] = []
    for item in cleaned.replace("-", ".").split("."):
        if not item.isdigit():
            break
        parts.append(int(item))
    return tuple(parts or [0])


def is_newer_version(latest: str, current: str) -> bool:
    latest_parts = version_parts(latest)
    current_parts = version_parts(current)
    length = max(len(latest_parts), len(current_parts))
    return latest_parts + (0,) * (length - len(latest_parts)) > current_parts + (0,) * (length - len(current_parts))


def has_version_number(version: str) -> bool:
    return bool(version.strip().lower().lstrip("v")[:1].isdigit())


def latest_tag_from_git_ls_remote(output: str) -> str:
    tags: list[str] = []
    for line in output.splitlines():
        if "refs/tags/" not in line:
            continue
        tag = line.rsplit("refs/tags/", 1)[-1].strip()
        if tag.endswith("^{}"):
            tag = tag[:-3]
        if has_version_number(tag):
            tags.append(tag)
    if not tags:
        return ""
    return max(tags, key=version_parts)


def latest_tag_from_git_info_refs(content: str) -> str:
    tags: list[str] = []
    for item in content.replace("\x00", "\n").splitlines():
        if "refs/tags/" not in item:
            continue
        tag = item.rsplit("refs/tags/", 1)[-1].strip().split()[0]
        if tag.endswith("^{}"):
            tag = tag[:-3]
        if has_version_number(tag):
            tags.append(tag)
    if not tags:
        return ""
    return max(tags, key=version_parts)


def update_config_paths() -> list[Path]:
    paths = [Path(__file__).resolve().parent / UPDATE_CONFIG_FILE]
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        paths.insert(0, Path(bundle_root) / "launchdock" / UPDATE_CONFIG_FILE)
    return paths


@lru_cache(maxsize=1)
def load_update_config() -> dict[str, str]:
    config = dict(DEFAULT_UPDATE_CONFIG)
    for path in update_config_paths():
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            continue
        for key in ("update_channel", "update_repo_url", "release_page_url", "release_api_url"):
            value = data.get(key)
            if isinstance(value, str):
                config[key] = value.strip()
        break
    return config


def release_page_url() -> str:
    return load_update_config().get("release_page_url") or GITHUB_RELEASES_URL


def git_info_refs_url(repo_url: str) -> str:
    url = repo_url.strip()
    if not url:
        return ""
    if url.endswith(".git"):
        url = url[:-4]
    return f"{url.rstrip('/')}/info/refs?service=git-upload-pack"


def fetch_latest_release_from_git_http(repo_url: str, release_url: str) -> dict[str, object]:
    request = Request(git_info_refs_url(repo_url), headers={"User-Agent": "LaunchDock"})
    with urlopen(request, timeout=8) as response:
        content = response.read().decode("utf-8", errors="replace")
    tag_name = latest_tag_from_git_info_refs(content)
    if not tag_name:
        return {"status": "none"}
    return {
        "status": "ok",
        "tag_name": tag_name,
        "html_url": release_url,
        "body": "",
        "source": "git",
        "is_newer": is_newer_version(tag_name, __version__),
    }


def fetch_latest_release_from_git(repo_url: str, release_url: str) -> dict[str, object]:
    completed = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", repo_url],
        capture_output=True,
        text=True,
        timeout=8,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    tag_name = latest_tag_from_git_ls_remote(completed.stdout)
    if not tag_name:
        return {"status": "none"}
    return {
        "status": "ok",
        "tag_name": tag_name,
        "html_url": release_url,
        "body": "",
        "source": "git",
        "is_newer": is_newer_version(tag_name, __version__),
    }


def fetch_latest_release_from_api(api_url: str) -> dict[str, object]:
    request = Request(api_url, headers={"Accept": "application/vnd.github+json", "User-Agent": "LaunchDock"})
    try:
        with urlopen(request, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8-sig"))
    except HTTPError as exc:
        if exc.code == 404:
            return {"status": "none"}
        raise
    if not isinstance(data, dict):
        raise ValueError("更新信息格式不正确。")
    tag_name = str(data.get("tag_name") or "")
    html_url = str(data.get("html_url") or GITHUB_RELEASES_URL)
    body = str(data.get("body") or "").strip()
    return {
        "status": "ok",
        "tag_name": tag_name,
        "html_url": html_url,
        "body": body,
        "is_newer": is_newer_version(tag_name, __version__) if tag_name else False,
    }


def fetch_latest_release() -> dict[str, object]:
    config = load_update_config()
    release_url = config.get("release_page_url") or GITHUB_RELEASES_URL
    errors: list[str] = []

    repo_url = config.get("update_repo_url", "")
    if repo_url:
        try:
            return fetch_latest_release_from_git_http(repo_url, release_url)
        except (HTTPError, URLError, OSError, ValueError) as exc:
            errors.append(f"Git HTTP 更新源：{exc}")
        try:
            return fetch_latest_release_from_git(repo_url, release_url)
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            errors.append(f"Git 更新源：{exc}")

    api_url = config.get("release_api_url", "")
    if api_url:
        try:
            return fetch_latest_release_from_api(api_url)
        except (HTTPError, URLError, OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"Release API：{exc}")

    if errors:
        raise URLError("；".join(errors))
    return {"status": "none"}
