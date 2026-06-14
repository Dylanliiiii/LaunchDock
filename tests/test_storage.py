import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from launchdock.app import is_newer_version, is_valid_target, load_user_settings, normalized_target_text, save_user_setting, tr
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
                self.assertEqual(load_user_settings(), {"theme": "dark", "language": "zh_cn"})
                save_user_setting("theme", "system")
                save_user_setting("language", "es")
                self.assertEqual(load_user_settings(), {"theme": "system", "language": "es"})

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


if __name__ == "__main__":
    unittest.main()
