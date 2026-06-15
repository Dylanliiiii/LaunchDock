import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from launchdock.app import (
    fetch_latest_release_from_git_http,
    git_info_refs_url,
    is_newer_version,
    is_valid_target,
    latest_tag_from_git_info_refs,
    latest_tag_from_git_ls_remote,
    load_update_config,
    load_user_settings,
    normalized_target_text,
    save_user_setting,
    tr,
)
from launchdock.models import Link
from launchdock.storage import DockStorage, StorageError, save_dock_path


class DockStorageTest(unittest.TestCase):
    def test_storage_without_launch_dock_requires_user_choice(self) -> None:
        storage = DockStorage()
        storage.dock_path = None

        with self.assertRaises(StorageError):
            storage.create_project("未配置启动坞")

    def test_missing_saved_launch_dock_path_is_not_recreated(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config" / "config.json"
            missing_path = Path(temp_dir) / "deleted-dock"

            with patch("launchdock.storage.APP_CONFIG_FILE", config_file):
                save_dock_path(missing_path)
                storage = DockStorage()

            self.assertIsNone(storage.dock_path)
            self.assertEqual(storage.missing_dock_path, missing_path)
            self.assertFalse(missing_path.exists())

    def test_user_settings_have_defaults_and_can_be_saved(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config" / "config.json"

            with patch("launchdock.storage.APP_CONFIG_FILE", config_file):
                self.assertEqual(
                    load_user_settings(),
                    {"theme": "dark", "language": "zh_cn", "auto_check_updates": True},
                )
                save_user_setting("theme", "system")
                save_user_setting("language", "es")
                save_user_setting("auto_check_updates", False)
                self.assertEqual(
                    load_user_settings(),
                    {"theme": "system", "language": "es", "auto_check_updates": False},
                )

    def test_invalid_auto_update_setting_falls_back_to_enabled(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config" / "config.json"

            with patch("launchdock.storage.APP_CONFIG_FILE", config_file):
                config_file.parent.mkdir(parents=True, exist_ok=True)
                config_file.write_text(
                    json.dumps({"settings": {"auto_check_updates": "no"}}),
                    encoding="utf-8",
                )

                self.assertTrue(load_user_settings()["auto_check_updates"])

    def test_language_setting_changes_core_text(self) -> None:
        self.assertEqual(tr("en", "settings_title"), "LaunchDock Settings")
        self.assertEqual(tr("ja", "language_restart_title"), "言語は再起動後に反映されます")

    def test_create_empty_project(self) -> None:
        with TemporaryDirectory() as temp_dir:
            storage = DockStorage(Path(temp_dir))
            project = storage.create_project("PyTorch 学习")

            self.assertEqual(project.name, "PyTorch 学习")
            self.assertEqual(project.links, [])
            self.assertTrue((Path(temp_dir) / "projects" / project.folder_name / "project.json").exists())

    def test_save_project_link(self) -> None:
        with TemporaryDirectory() as temp_dir:
            storage = DockStorage(Path(temp_dir))
            project = storage.create_project("英语阅读")
            project.links.append(Link.create("Notion 笔记", "https://notion.so/example", True, 1))
            storage.save_project(project)

            loaded = storage.list_projects()[0]
            self.assertEqual(loaded.links[0].name, "Notion 笔记")
            self.assertTrue(loaded.links[0].default_open)

    def test_rename_project_moves_folder(self) -> None:
        with TemporaryDirectory() as temp_dir:
            storage = DockStorage(Path(temp_dir))
            project = storage.create_project("旧项目")
            old_folder = project.folder_name

            storage.rename_project(project, "新项目")
            loaded = storage.list_projects()[0]

            self.assertEqual(loaded.name, "新项目")
            self.assertEqual(loaded.folder_name, "新项目")
            self.assertFalse((Path(temp_dir) / "projects" / old_folder).exists())
            self.assertTrue((Path(temp_dir) / "projects" / "新项目" / "project.json").exists())

    def test_rename_project_uses_unique_folder_name(self) -> None:
        with TemporaryDirectory() as temp_dir:
            storage = DockStorage(Path(temp_dir))
            first = storage.create_project("项目")
            second = storage.create_project("其他项目")

            storage.rename_project(second, "项目")
            projects = {project.id: project for project in storage.list_projects()}

            self.assertEqual(projects[first.id].folder_name, "项目")
            self.assertEqual(projects[second.id].name, "项目")
            self.assertEqual(projects[second.id].folder_name, "项目-2")
            self.assertTrue((Path(temp_dir) / "projects" / "项目-2" / "project.json").exists())

    def test_delete_project(self) -> None:
        with TemporaryDirectory() as temp_dir:
            storage = DockStorage(Path(temp_dir))
            project = storage.create_project("临时项目")
            storage.delete_project(project)

            self.assertEqual(storage.list_projects(), [])
            self.assertFalse((Path(temp_dir) / "projects" / project.folder_name).exists())

    def test_global_file_records_project_order(self) -> None:
        with TemporaryDirectory() as temp_dir:
            storage = DockStorage(Path(temp_dir))
            first = storage.create_project("A")
            second = storage.create_project("B")

            with (Path(temp_dir) / "launchdock.json").open("r", encoding="utf-8") as file:
                data = json.load(file)

            self.assertEqual(data["project_order"], [first.id, second.id])

    def test_valid_targets_accept_url_and_existing_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "note.txt"
            file_path.write_text("hello", encoding="utf-8")

            self.assertTrue(is_valid_target("https://example.com"))
            self.assertTrue(is_valid_target(str(file_path)))
            self.assertTrue(is_valid_target(f'"{file_path}"'))
            self.assertFalse(is_valid_target(str(Path(temp_dir) / "missing.txt")))
            self.assertFalse(is_valid_target(f'"{file_path}'))
            self.assertFalse(is_valid_target(f'{file_path}"'))

    def test_normalized_target_text_handles_quotes(self) -> None:
        self.assertEqual(normalized_target_text('"C:/Program Files/file.txt"'), "C:/Program Files/file.txt")
        self.assertIsNone(normalized_target_text('"C:/Program Files/file.txt'))
        self.assertIsNone(normalized_target_text('C:/Program Files/file.txt"'))

    def test_version_compare(self) -> None:
        self.assertTrue(is_newer_version("v0.2.0", "0.1.5"))
        self.assertTrue(is_newer_version("0.10.0", "0.2.0"))
        self.assertFalse(is_newer_version("v0.1.5", "0.1.5"))
        self.assertFalse(is_newer_version("v0.1.4", "0.1.5"))

    def test_latest_tag_from_git_ls_remote(self) -> None:
        output = "\n".join(
            [
                "aaa\trefs/tags/v1.0.0",
                "bbb\trefs/tags/v1.10.0",
                "ccc\trefs/tags/v1.2.0",
                "ddd\trefs/tags/not-a-version",
            ]
        )

        self.assertEqual(latest_tag_from_git_ls_remote(output), "v1.10.0")

    def test_latest_tag_from_git_info_refs(self) -> None:
        content = "\n".join(
            [
                "001e# service=git-upload-pack",
                "abc refs/tags/v1.0.0",
                "def refs/tags/v1.10.0",
                "ghi refs/tags/v1.2.0^{}",
                "jkl refs/tags/not-a-version",
            ]
        )

        self.assertEqual(latest_tag_from_git_info_refs(content), "v1.10.0")

    def test_git_info_refs_url_removes_git_suffix(self) -> None:
        self.assertEqual(
            git_info_refs_url("https://cnb.cool/DylanLIIIII/LaunchDock.git"),
            "https://cnb.cool/DylanLIIIII/LaunchDock/info/refs?service=git-upload-pack",
        )

    def test_fetch_latest_release_from_git_http(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self) -> bytes:
                return b"abc refs/tags/v1.0.0\ndef refs/tags/v9.9.9\n"

        with patch("launchdock.app.urlopen", return_value=FakeResponse()):
            result = fetch_latest_release_from_git_http("https://example.com/repo.git", "https://example.com/releases")

        self.assertEqual(result["tag_name"], "v9.9.9")
        self.assertEqual(result["source"], "git")
        self.assertTrue(result["is_newer"])

    def test_load_update_config_accepts_utf8_bom(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "update-config.json"
            config_file.write_text('{"update_channel": "china"}', encoding="utf-8-sig")

            load_update_config.cache_clear()
            with patch("launchdock.app.update_config_paths", return_value=[config_file]):
                self.assertEqual(load_update_config()["update_channel"], "china")
            load_update_config.cache_clear()


if __name__ == "__main__":
    unittest.main()
