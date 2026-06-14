from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from .models import Project, now_text

APP_CONFIG_DIR = Path.home() / ".launchdock"
APP_CONFIG_FILE = APP_CONFIG_DIR / "config.json"
GLOBAL_FILE = "launchdock.json"
PROJECTS_DIR = "projects"
PROJECT_FILE = "project.json"


class StorageError(Exception):
    """启动坞读写失败。"""


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise StorageError(f"JSON 文件格式异常：{path}") from exc
    except OSError as exc:
        raise StorageError(f"无法读取文件：{path}") from exc


def write_json(path: Path, data: Any) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temp_path.replace(path)
    except OSError as exc:
        raise StorageError(f"无法写入文件：{path}") from exc


def load_app_config() -> dict[str, Any]:
    return read_json(APP_CONFIG_FILE, {})


def save_app_config(config: dict[str, Any]) -> None:
    write_json(APP_CONFIG_FILE, config)


def get_saved_dock_path() -> Path | None:
    config = load_app_config()
    value = config.get("dock_path")
    if value:
        return Path(str(value)).expanduser()
    return None


def save_dock_path(path: Path) -> None:
    config = load_app_config()
    config["dock_path"] = str(path.expanduser())
    save_app_config(config)


def slugify_name(name: str) -> str:
    text = name.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", text)
    text = re.sub(r"-+", "-", text).strip("-. ")
    return text or "project"


class DockStorage:
    def __init__(self, dock_path: Path | None = None) -> None:
        self.missing_dock_path: Path | None = None
        if dock_path is not None:
            self.dock_path = dock_path.expanduser()
            return

        saved_path = get_saved_dock_path()
        if saved_path is None:
            self.dock_path = None
            return

        expanded_path = saved_path.expanduser()
        if not expanded_path.exists():
            self.dock_path = None
            self.missing_dock_path = expanded_path
            return

        self.dock_path = expanded_path

    def require_dock_path(self) -> Path:
        if self.dock_path is None:
            raise StorageError("请先创建启动坞，选择一个用于保存启动项目的本地文件夹。")
        return self.dock_path

    @property
    def global_path(self) -> Path:
        return self.require_dock_path() / GLOBAL_FILE

    @property
    def projects_path(self) -> Path:
        return self.require_dock_path() / PROJECTS_DIR

    def initialize(self) -> None:
        self.projects_path.mkdir(parents=True, exist_ok=True)
        if not self.global_path.exists():
            write_json(
                self.global_path,
                {
                    "version": 1,
                    "created_at": now_text(),
                    "updated_at": now_text(),
                    "project_order": [],
                    "recent_project_id": None,
                },
            )

    def load_global(self) -> dict[str, Any]:
        self.initialize()
        data = read_json(self.global_path, {})
        if not isinstance(data, dict):
            raise StorageError("全局配置文件格式异常。")
        data.setdefault("version", 1)
        data.setdefault("project_order", [])
        data.setdefault("recent_project_id", None)
        return data

    def save_global(self, data: dict[str, Any]) -> None:
        data["updated_at"] = now_text()
        write_json(self.global_path, data)

    def project_file(self, folder_name: str) -> Path:
        return self.projects_path / folder_name / PROJECT_FILE

    def list_projects(self) -> list[Project]:
        self.initialize()
        projects: list[Project] = []
        if not self.projects_path.exists():
            return projects
        for folder in self.projects_path.iterdir():
            if not folder.is_dir():
                continue
            project_path = folder / PROJECT_FILE
            if not project_path.exists():
                continue
            data = read_json(project_path, {})
            if not isinstance(data, dict):
                continue
            projects.append(Project.from_dict(data, fallback_folder_name=folder.name))
        order = self.load_global().get("project_order", [])
        order_map = {project_id: index for index, project_id in enumerate(order)}
        projects.sort(key=lambda project: (order_map.get(project.id, 999999), project.name.casefold()))
        return projects

    def make_unique_folder_name(self, name: str, current_folder_name: str | None = None) -> str:
        base = slugify_name(name)
        candidate = base
        index = 2
        while candidate != current_folder_name and (self.projects_path / candidate).exists():
            candidate = f"{base}-{index}"
            index += 1
        return candidate

    def create_project(self, name: str) -> Project:
        self.initialize()
        folder_name = self.make_unique_folder_name(name)
        project = Project.create(name=name, folder_name=folder_name)
        self.save_project(project)
        global_data = self.load_global()
        project_order = list(global_data.get("project_order", []))
        project_order.append(project.id)
        global_data["project_order"] = project_order
        global_data["recent_project_id"] = project.id
        self.save_global(global_data)
        return project

    def save_project(self, project: Project) -> None:
        self.initialize()
        project.touch()
        write_json(self.project_file(project.folder_name), project.to_dict())

    def rename_project(self, project: Project, name: str) -> Project:
        self.initialize()
        new_name = name.strip()
        if not new_name:
            raise StorageError("项目名称不能为空。")

        old_folder_name = project.folder_name
        new_folder_name = self.make_unique_folder_name(new_name, current_folder_name=old_folder_name)
        old_dir = self.projects_path / old_folder_name
        new_dir = self.projects_path / new_folder_name

        if not old_dir.exists():
            raise StorageError(f"项目文件夹不存在：{old_dir}")

        if new_folder_name != old_folder_name:
            try:
                old_dir.rename(new_dir)
            except OSError as exc:
                raise StorageError(f"无法重命名项目文件夹：{old_dir} -> {new_dir}") from exc

        project.name = new_name
        project.folder_name = new_folder_name
        self.save_project(project)
        return project

    def delete_project(self, project: Project) -> None:
        project_dir = self.projects_path / project.folder_name
        if project_dir.exists():
            shutil.rmtree(project_dir)
        global_data = self.load_global()
        global_data["project_order"] = [
            project_id for project_id in global_data.get("project_order", []) if project_id != project.id
        ]
        if global_data.get("recent_project_id") == project.id:
            global_data["recent_project_id"] = None
        self.save_global(global_data)

    def set_recent_project(self, project_id: str | None) -> None:
        global_data = self.load_global()
        global_data["recent_project_id"] = project_id
        self.save_global(global_data)
