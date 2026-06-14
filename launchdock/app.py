from __future__ import annotations

import os
import locale
import json
import subprocess
import sys
import webbrowser
from threading import Thread
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PySide6.QtCore import QObject, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    CaptionLabel,
    CheckBox,
    ComboBox,
    Dialog,
    FluentIcon,
    FluentWindow,
    IconWidget,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    NavigationItemPosition,
    PrimaryPushButton,
    PushButton,
    SmoothScrollArea,
    SubtitleLabel,
    SwitchButton,
    Theme,
    TitleLabel,
    TransparentPushButton,
    TransparentToolButton,
    setTheme,
    setThemeColor,
)

from .models import Link, Project
from .storage import DockStorage, StorageError, load_app_config, save_app_config, save_dock_path
from . import __version__

ACCENT_COLOR = "#00c8d7"
APP_ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
BACKGROUND_REMOVE_THRESHOLD = 34
GITHUB_REPO_URL = "https://github.com/Dylanliiiii/LaunchDock"
GITHUB_RELEASES_URL = f"{GITHUB_REPO_URL}/releases"
GITHUB_LATEST_RELEASE_API = "https://api.github.com/repos/Dylanliiiii/LaunchDock/releases/latest"
NAVIGATION_EXPAND_MIN_WIDTH = 176
NAVIGATION_EXPAND_MAX_WIDTH = 280
NAVIGATION_TEXT_EXTRA_WIDTH = 118
THEME_OPTIONS = {
    "light": "浅色",
    "dark": "深色",
    "system": "跟随系统",
}
LANGUAGE_NATIVE_NAMES = {
    "zh_cn": "简体中文",
    "zh_tw": "繁体中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
}
SUPPORTED_LANGUAGES = (*LANGUAGE_NATIVE_NAMES.keys(), "system")
TEXT = {
    "zh_cn": {
        "launch_title": "启动项目",
        "nav_launch": "启动项目",
        "nav_dock": "启动坞",
        "nav_about": "关于",
        "nav_settings": "设置",
        "launch_desc": "选择一个项目，一键打开它的网页链接和本地文件。",
        "new": "新建",
        "manage_projects": "管理项目",
        "about": "关于",
        "settings": "设置",
        "dock": "启动坞",
        "settings_title": "LaunchDock设置",
        "app_theme": "应用主题",
        "app_theme_desc": "改变应用程序的外观",
        "language": "语言",
        "language_desc": "选择你的语言",
        "language_restart_title": "语言将在重启后生效",
        "language_restart_desc": "语言设置已保存。关闭并重新打开 LaunchDock 后，界面语言会切换。",
        "settings_save_failed": "设置保存失败",
        "language_save_failed": "语言选择已临时应用，但无法保存：{error}",
        "theme_save_failed": "主题已临时应用，但无法保存：{error}",
        "system_language": "使用系统设置",
        "theme_light": "浅色",
        "theme_dark": "深色",
        "theme_system": "跟随系统",
    },
    "zh_tw": {
        "launch_title": "啟動專案",
        "nav_launch": "啟動專案",
        "nav_dock": "啟動塢",
        "nav_about": "關於",
        "nav_settings": "設定",
        "launch_desc": "選擇一個專案，一鍵開啟它的網頁連結和本機檔案。",
        "new": "新增",
        "manage_projects": "管理專案",
        "about": "關於",
        "settings": "設定",
        "dock": "啟動塢",
        "settings_title": "LaunchDock設定",
        "app_theme": "應用程式主題",
        "app_theme_desc": "變更應用程式的外觀",
        "language": "語言",
        "language_desc": "選擇你的語言",
        "language_restart_title": "語言將在重新啟動後生效",
        "language_restart_desc": "語言設定已儲存。關閉並重新開啟 LaunchDock 後，介面語言會切換。",
        "settings_save_failed": "設定儲存失敗",
        "language_save_failed": "語言選擇已暫時套用，但無法儲存：{error}",
        "theme_save_failed": "主題已暫時套用，但無法儲存：{error}",
        "system_language": "使用系統設定",
        "theme_light": "淺色",
        "theme_dark": "深色",
        "theme_system": "跟隨系統",
    },
    "en": {
        "launch_title": "Launch Projects",
        "nav_launch": "Projects",
        "nav_dock": "Dock",
        "nav_about": "About",
        "nav_settings": "Settings",
        "launch_desc": "Choose a project and open its web links and local files with one click.",
        "new": "New",
        "manage_projects": "Manage Projects",
        "about": "About",
        "settings": "Settings",
        "dock": "Dock",
        "settings_title": "LaunchDock Settings",
        "app_theme": "App Theme",
        "app_theme_desc": "Change the appearance of the app",
        "language": "Language",
        "language_desc": "Choose your language",
        "language_restart_title": "Language will change after restart",
        "language_restart_desc": "The language setting has been saved. Close and reopen LaunchDock to apply it.",
        "settings_save_failed": "Failed to Save Settings",
        "language_save_failed": "Language was selected temporarily, but could not be saved: {error}",
        "theme_save_failed": "Theme was applied temporarily, but could not be saved: {error}",
        "system_language": "Use system setting",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_system": "Use system setting",
    },
    "ja": {
        "launch_title": "起動プロジェクト",
        "nav_launch": "起動",
        "nav_dock": "ドック",
        "nav_about": "概要",
        "nav_settings": "設定",
        "launch_desc": "プロジェクトを選び、Webリンクとローカルファイルをワンクリックで開きます。",
        "new": "新規",
        "manage_projects": "プロジェクト管理",
        "about": "概要",
        "settings": "設定",
        "dock": "ドック",
        "settings_title": "LaunchDock設定",
        "app_theme": "アプリテーマ",
        "app_theme_desc": "アプリの外観を変更します",
        "language": "言語",
        "language_desc": "言語を選択します",
        "language_restart_title": "言語は再起動後に反映されます",
        "language_restart_desc": "言語設定を保存しました。LaunchDockを閉じて再度開くと反映されます。",
        "settings_save_failed": "設定の保存に失敗しました",
        "language_save_failed": "言語は一時的に選択されましたが、保存できませんでした：{error}",
        "theme_save_failed": "テーマは一時的に適用されましたが、保存できませんでした：{error}",
        "system_language": "システム設定を使用",
        "theme_light": "ライト",
        "theme_dark": "ダーク",
        "theme_system": "システム設定を使用",
    },
    "ko": {
        "launch_title": "프로젝트 실행",
        "nav_launch": "실행",
        "nav_dock": "도크",
        "nav_about": "정보",
        "nav_settings": "설정",
        "launch_desc": "프로젝트를 선택하고 웹 링크와 로컬 파일을 한 번에 엽니다.",
        "new": "새로 만들기",
        "manage_projects": "프로젝트 관리",
        "about": "정보",
        "settings": "설정",
        "dock": "도크",
        "settings_title": "LaunchDock 설정",
        "app_theme": "앱 테마",
        "app_theme_desc": "앱의 모양을 변경합니다",
        "language": "언어",
        "language_desc": "언어를 선택합니다",
        "language_restart_title": "언어는 다시 시작 후 적용됩니다",
        "language_restart_desc": "언어 설정이 저장되었습니다. LaunchDock을 닫고 다시 열면 적용됩니다.",
        "settings_save_failed": "설정 저장 실패",
        "language_save_failed": "언어 선택은 임시로 적용되었지만 저장하지 못했습니다: {error}",
        "theme_save_failed": "테마는 임시로 적용되었지만 저장하지 못했습니다: {error}",
        "system_language": "시스템 설정 사용",
        "theme_light": "라이트",
        "theme_dark": "다크",
        "theme_system": "시스템 설정 사용",
    },
    "es": {
        "launch_title": "Proyectos de inicio",
        "nav_launch": "Proyectos",
        "nav_dock": "Dock",
        "nav_about": "Acerca",
        "nav_settings": "Ajustes",
        "launch_desc": "Elige un proyecto y abre sus enlaces web y archivos locales con un clic.",
        "new": "Nuevo",
        "manage_projects": "Gestionar proyectos",
        "about": "Acerca de",
        "settings": "Configuración",
        "dock": "Dock",
        "settings_title": "Configuración de LaunchDock",
        "app_theme": "Tema de la app",
        "app_theme_desc": "Cambia la apariencia de la aplicación",
        "language": "Idioma",
        "language_desc": "Elige tu idioma",
        "language_restart_title": "El idioma cambiará al reiniciar",
        "language_restart_desc": "La configuración de idioma se ha guardado. Cierra y vuelve a abrir LaunchDock para aplicarla.",
        "settings_save_failed": "No se pudo guardar la configuración",
        "language_save_failed": "El idioma se seleccionó temporalmente, pero no se pudo guardar: {error}",
        "theme_save_failed": "El tema se aplicó temporalmente, pero no se pudo guardar: {error}",
        "system_language": "Usar configuración del sistema",
        "theme_light": "Claro",
        "theme_dark": "Oscuro",
        "theme_system": "Usar configuración del sistema",
    },
}

TEXT_EXTRA = {
    "zh_cn": {
        "select_all": "全选",
        "clear_selection": "取消全选",
        "invert_selection": "反选",
        "delete_selected": "删除所选",
        "done": "完成",
        "no_projects_title": "还没有启动项目",
        "no_projects_desc": "点击右上角“新建”，先创建一个空项目也可以。",
        "missing_dock_title": "上次使用的启动坞不存在",
        "create_dock_title": "请先创建启动坞",
        "missing_dock_desc": "上次使用的启动坞文件夹不存在，可能已被移动、删除或重命名：\n{path}\n请重新选择已有启动坞，或创建新的启动坞。",
        "create_dock_desc": "启动坞用于保存启动项目的存储位置。选择一个本地文件夹作为启动坞后，才可以创建启动项目。",
        "create_or_choose_dock": "创建 / 选择启动坞",
        "link_count": "{total} 个启动项，{enabled} 个已启用",
        "empty_project_desc": "这个项目还没有启动项。可以点击下方“添加启动项”。",
        "select_all_links": "全选启动项",
        "delete_selected_links": "删除所选启动项",
        "done_manage": "完成管理",
        "add_link": "添加启动项",
        "manage_links": "管理启动项",
        "launch": "启动",
        "dock_title": "启动坞",
        "dock_desc": "选择或创建一个本地文件夹，用来保存所有启动项目和配置。",
        "current_dock_path": "当前启动坞路径",
        "dock_structure": "启动坞结构",
        "dock_structure_desc": "launchdock.json 保存全局配置；projects/ 下每个项目拥有独立文件夹和 project.json。",
        "dock_not_created": "尚未创建启动坞。请先选择一个本地文件夹，用来保存后续创建的启动项目。",
        "about_title": "关于 LaunchDock",
        "about_desc": "一个本地启动坞，用于管理学习和工作项目中的网页链接、本地文件，并一键启动。",
        "version_label": "v{version}",
        "check_update": "检查新版本",
        "github_link": "GitHub",
        "share_download_link": "分享下载链接",
        "update_placeholder_title": "版本更新",
        "update_placeholder_desc": "当前还没有检查到新版本。发布 GitHub Release 后，这里会显示版本跨度和发布说明。",
        "checking_update": "正在检查新版本...",
        "no_release_title": "暂无发布版本",
        "no_release_desc": "GitHub 仓库还没有发布 Release。之后发布 Release 后即可检查更新。",
        "no_update_title": "已是当前版本",
        "no_update_desc": "当前版本 v{current} 已是最新发布版本。",
        "update_available_title": "发现新版本",
        "update_available_desc": "可从 v{current} 更新到 {latest}。",
        "update_changelog_title": "新版本改动内容",
        "update_check_failed_title": "检查更新失败",
        "update_check_failed_desc": "无法连接 GitHub Release，请稍后再试：{error}",
        "open_release_prompt": "是否打开下载页面？",
        "download_link_copied": "下载链接已复制",
        "download_link_copied_desc": "已复制 GitHub Releases 下载页面链接。",
        "dialog_save": "保存",
        "dialog_cancel": "取消",
        "link_default_open": "启动项目时默认打开",
        "link_name_placeholder": "例如：视频课程",
        "link_url_placeholder": "例如：https://example.com 或 C:/Notes/note.pdf",
        "name": "名称",
        "url_or_path": "URL 或本地路径",
        "delete_selected_links_title": "批量删除启动项",
        "delete_selected_links_desc": "确定要删除以下 {count} 个启动项吗？\n{names}",
        "not_selected_links_title": "未选择启动项",
        "not_selected_links_desc": "请先勾选需要删除的启动项。",
        "more_links": "...以及另外 {count} 个启动项",
        "not_selected_projects_title": "未选择项目",
        "not_selected_projects_desc": "请先勾选需要删除的启动项目。",
        "more_projects": "...以及另外 {count} 个项目",
        "delete_selected_projects_title": "批量删除",
        "delete_selected_projects_desc": "确定要删除以下 {count} 个启动项目吗？\n{names}",
        "need_dock_title": "请先创建启动坞",
        "need_dock_desc": "启动坞用于保存启动项目的存储位置。请先创建启动坞，再创建启动项目。",
        "need_dock_save_desc": "启动坞用于保存启动项目的存储位置。",
        "new_project_title": "新建启动项目",
        "project_name_prompt": "请输入启动项目名称：",
        "need_name_title": "需要名称",
        "project_name_empty": "项目名称不能为空。",
        "create_failed": "创建失败",
        "create_success": "创建成功",
        "project_created": "项目“{name}”已创建。",
        "edit_project_title": "编辑项目",
        "delete_project_title": "确认删除",
        "delete_project_desc": "确定要删除项目“{name}”吗？\n此操作会删除该项目文件夹。",
        "delete_link_title": "确认删除",
        "delete_failed": "删除失败",
        "delete_project_failed": "删除“{name}”时失败：{error}",
        "delete_success": "删除成功",
        "project_deleted": "项目“{name}”已删除。",
        "add_link_title": "添加启动项",
        "edit_link_title": "编辑启动项",
        "delete_link_desc": "确定要删除启动项“{name}”吗？",
        "save_failed": "保存失败",
        "choose_dock_title": "创建或选择 LaunchDock 启动坞文件夹",
        "config_save_failed": "配置保存失败",
        "dock_path_save_failed": "启动坞可以继续使用，但无法记住路径：{error}",
        "no_launch_targets_title": "没有可启动项",
        "no_launch_targets_desc": "这个项目还没有启用的启动项。",
        "invalid_targets_title": "启动项需要检查",
        "invalid_targets_desc": "以下启动项地址无效或文件不存在：\n{names}",
        "launch_done_title": "启动完成",
        "launch_done_desc": "已启动 {count} 个项目项。",
        "link_name_required": "请填写启动项名称。",
        "link_url_required_title": "需要地址",
        "link_url_required": "请填写 URL 或本地文件路径。",
        "confirm_ok": "确定",
        "confirm_cancel": "取消",
        "dock_error": "启动坞错误",
    },
    "zh_tw": {
        "select_all": "全選",
        "clear_selection": "取消全選",
        "invert_selection": "反選",
        "delete_selected": "刪除所選",
        "done": "完成",
        "no_projects_title": "尚無啟動專案",
        "no_projects_desc": "點擊右上角「新增」，也可以先建立空專案。",
        "missing_dock_title": "上次使用的啟動塢不存在",
        "create_dock_title": "請先建立啟動塢",
        "missing_dock_desc": "上次使用的啟動塢資料夾不存在，可能已被移動、刪除或重新命名：\n{path}\n請重新選擇已有啟動塢，或建立新的啟動塢。",
        "create_dock_desc": "啟動塢用於保存啟動專案的儲存位置。選擇一個本機資料夾作為啟動塢後，才可以建立啟動專案。",
        "create_or_choose_dock": "建立 / 選擇啟動塢",
        "link_count": "{total} 個啟動項，{enabled} 個已啟用",
        "empty_project_desc": "這個專案還沒有啟動項。可以點擊下方「新增啟動項」。",
        "select_all_links": "全選啟動項",
        "delete_selected_links": "刪除所選啟動項",
        "done_manage": "完成管理",
        "add_link": "新增啟動項",
        "manage_links": "管理啟動項",
        "launch": "啟動",
        "dock_title": "啟動塢",
        "dock_desc": "選擇或建立一個本機資料夾，用來儲存所有啟動專案和設定。",
        "current_dock_path": "目前啟動塢路徑",
        "dock_structure": "啟動塢結構",
        "dock_structure_desc": "launchdock.json 保存全域設定；projects/ 下每個專案都有獨立資料夾和 project.json。",
        "dock_not_created": "尚未建立啟動塢。請先選擇一個本機資料夾，用來保存後續建立的啟動專案。",
        "about_title": "關於 LaunchDock",
        "about_desc": "一個本機啟動塢，用於管理學習和工作專案中的網頁連結、本機檔案，並一鍵啟動。",
        "version_label": "v{version}",
        "check_update": "檢查新版本",
        "github_link": "GitHub",
        "share_download_link": "分享下載連結",
        "update_placeholder_title": "版本更新",
        "update_placeholder_desc": "目前還沒有檢查到新版本。發布 GitHub Release 後，這裡會顯示版本跨度和發布說明。",
        "checking_update": "正在檢查新版本...",
        "no_release_title": "暫無發布版本",
        "no_release_desc": "GitHub 倉庫還沒有發布 Release。之後發布 Release 後即可檢查更新。",
        "no_update_title": "已是目前版本",
        "no_update_desc": "目前版本 v{current} 已是最新發布版本。",
        "update_available_title": "發現新版本",
        "update_available_desc": "可從 v{current} 更新到 {latest}。",
        "update_changelog_title": "新版本變更內容",
        "update_check_failed_title": "檢查更新失敗",
        "update_check_failed_desc": "無法連接 GitHub Release，請稍後再試：{error}",
        "open_release_prompt": "是否開啟下載頁面？",
        "download_link_copied": "下載連結已複製",
        "download_link_copied_desc": "已複製 GitHub Releases 下載頁面連結。",
        "dialog_save": "儲存",
        "dialog_cancel": "取消",
        "link_default_open": "啟動專案時預設開啟",
        "link_name_placeholder": "例如：影片課程",
        "link_url_placeholder": "例如：https://example.com 或 C:/Notes/note.pdf",
        "name": "名稱",
        "url_or_path": "URL 或本機路徑",
        "delete_selected_links_title": "批量刪除啟動項",
        "delete_selected_links_desc": "確定要刪除以下 {count} 個啟動項嗎？\n{names}",
        "not_selected_links_title": "未選擇啟動項",
        "not_selected_links_desc": "請先勾選需要刪除的啟動項。",
        "more_links": "...以及另外 {count} 個啟動項",
        "not_selected_projects_title": "未選擇專案",
        "not_selected_projects_desc": "請先勾選需要刪除的啟動專案。",
        "more_projects": "...以及另外 {count} 個專案",
        "delete_selected_projects_title": "批量刪除",
        "delete_selected_projects_desc": "確定要刪除以下 {count} 個啟動專案嗎？\n{names}",
        "need_dock_title": "請先建立啟動塢",
        "need_dock_desc": "啟動塢用於保存啟動專案的儲存位置。請先建立啟動塢，再建立啟動專案。",
        "need_dock_save_desc": "啟動塢用於保存啟動專案的儲存位置。",
        "new_project_title": "新增啟動專案",
        "project_name_prompt": "請輸入啟動專案名稱：",
        "need_name_title": "需要名稱",
        "project_name_empty": "專案名稱不能為空。",
        "create_failed": "建立失敗",
        "create_success": "建立成功",
        "project_created": "專案「{name}」已建立。",
        "edit_project_title": "編輯專案",
        "delete_project_title": "確認刪除",
        "delete_project_desc": "確定要刪除專案「{name}」嗎？\n此操作會刪除該專案資料夾。",
        "delete_link_title": "確認刪除",
        "delete_failed": "刪除失敗",
        "delete_project_failed": "刪除「{name}」時失敗：{error}",
        "delete_success": "刪除成功",
        "project_deleted": "專案「{name}」已刪除。",
        "add_link_title": "新增啟動項",
        "edit_link_title": "編輯啟動項",
        "delete_link_desc": "確定要刪除啟動項「{name}」嗎？",
        "save_failed": "儲存失敗",
        "choose_dock_title": "建立或選擇 LaunchDock 啟動塢資料夾",
        "config_save_failed": "設定儲存失敗",
        "dock_path_save_failed": "啟動塢可以繼續使用，但無法記住路徑：{error}",
        "no_launch_targets_title": "沒有可啟動項",
        "no_launch_targets_desc": "這個專案還沒有啟用的啟動項。",
        "invalid_targets_title": "啟動項需要檢查",
        "invalid_targets_desc": "以下啟動項地址無效或檔案不存在：\n{names}",
        "launch_done_title": "啟動完成",
        "launch_done_desc": "已啟動 {count} 個專案項目。",
        "link_name_required": "請填寫啟動項名稱。",
        "link_url_required_title": "需要地址",
        "link_url_required": "請填寫 URL 或本機檔案路徑。",
        "confirm_ok": "確定",
        "confirm_cancel": "取消",
        "dock_error": "啟動塢錯誤",
    },
    "en": {
        "select_all": "Select All",
        "clear_selection": "Clear Selection",
        "invert_selection": "Invert",
        "delete_selected": "Delete Selected",
        "done": "Done",
        "no_projects_title": "No launch projects yet",
        "no_projects_desc": "Click New in the upper-right corner. You can create an empty project first.",
        "missing_dock_title": "Previous dock not found",
        "create_dock_title": "Create a dock first",
        "missing_dock_desc": "The previous dock folder does not exist. It may have been moved, deleted, or renamed:\n{path}\nChoose an existing dock again, or create a new one.",
        "create_dock_desc": "A dock stores the location for your launch projects. Choose a local folder as the dock before creating launch projects.",
        "create_or_choose_dock": "Create / Choose Dock",
        "link_count": "{total} launch items, {enabled} enabled",
        "empty_project_desc": "This project has no launch items yet. Click Add Launch Item below.",
        "select_all_links": "Select All Items",
        "delete_selected_links": "Delete Selected Items",
        "done_manage": "Done",
        "add_link": "Add Launch Item",
        "manage_links": "Manage Items",
        "launch": "Launch",
        "dock_title": "Dock",
        "dock_desc": "Choose or create a local folder to store all launch projects and settings.",
        "current_dock_path": "Current Dock Path",
        "dock_structure": "Dock Structure",
        "dock_structure_desc": "launchdock.json stores global settings; every project under projects/ has its own folder and project.json.",
        "dock_not_created": "No dock has been created yet. Choose a local folder first to store launch projects.",
        "about_title": "About LaunchDock",
        "about_desc": "A local dock for managing web links and local files in study and work projects, then launching them with one click.",
        "version_label": "v{version}",
        "check_update": "Check for Updates",
        "github_link": "GitHub",
        "share_download_link": "Share Download Link",
        "update_placeholder_title": "Version Updates",
        "update_placeholder_desc": "No new version has been detected yet. After a GitHub Release is published, version changes and release notes will appear here.",
        "checking_update": "Checking for updates...",
        "no_release_title": "No Releases Yet",
        "no_release_desc": "This GitHub repository has no Release yet. Update checks will work after a Release is published.",
        "no_update_title": "Up to Date",
        "no_update_desc": "Current version v{current} is the latest published version.",
        "update_available_title": "New Version Available",
        "update_available_desc": "Update from v{current} to {latest}.",
        "update_changelog_title": "Release Notes",
        "update_check_failed_title": "Update Check Failed",
        "update_check_failed_desc": "Could not connect to GitHub Releases. Try again later: {error}",
        "open_release_prompt": "Open the download page?",
        "download_link_copied": "Download Link Copied",
        "download_link_copied_desc": "The GitHub Releases download page link has been copied.",
        "dialog_save": "Save",
        "dialog_cancel": "Cancel",
        "link_default_open": "Open by default when launching project",
        "link_name_placeholder": "Example: Video course",
        "link_url_placeholder": "Example: https://example.com or C:/Notes/note.pdf",
        "name": "Name",
        "url_or_path": "URL or Local Path",
        "delete_selected_links_title": "Delete Launch Items",
        "delete_selected_links_desc": "Delete the following {count} launch items?\n{names}",
        "not_selected_links_title": "No Items Selected",
        "not_selected_links_desc": "Select the launch items you want to delete first.",
        "more_links": "...and {count} more launch items",
        "not_selected_projects_title": "No Projects Selected",
        "not_selected_projects_desc": "Select the launch projects you want to delete first.",
        "more_projects": "...and {count} more projects",
        "delete_selected_projects_title": "Delete Projects",
        "delete_selected_projects_desc": "Delete the following {count} launch projects?\n{names}",
        "need_dock_title": "Create a dock first",
        "need_dock_desc": "A dock stores the location for launch projects. Create a dock before creating launch projects.",
        "need_dock_save_desc": "A dock stores the location for launch projects.",
        "new_project_title": "New Launch Project",
        "project_name_prompt": "Enter a launch project name:",
        "need_name_title": "Name Required",
        "project_name_empty": "Project name cannot be empty.",
        "create_failed": "Create Failed",
        "create_success": "Created",
        "project_created": "Project \"{name}\" has been created.",
        "edit_project_title": "Edit Project",
        "delete_project_title": "Confirm Delete",
        "delete_project_desc": "Delete project \"{name}\"?\nThis will delete the project folder.",
        "delete_link_title": "Confirm Delete",
        "delete_failed": "Delete Failed",
        "delete_project_failed": "Failed to delete \"{name}\": {error}",
        "delete_success": "Deleted",
        "project_deleted": "Project \"{name}\" has been deleted.",
        "add_link_title": "Add Launch Item",
        "edit_link_title": "Edit Launch Item",
        "delete_link_desc": "Delete launch item \"{name}\"?",
        "save_failed": "Save Failed",
        "choose_dock_title": "Create or Choose LaunchDock Dock Folder",
        "config_save_failed": "Failed to Save Settings",
        "dock_path_save_failed": "The dock can still be used, but the path could not be remembered: {error}",
        "no_launch_targets_title": "No Launch Items",
        "no_launch_targets_desc": "This project has no enabled launch items.",
        "invalid_targets_title": "Check Launch Items",
        "invalid_targets_desc": "The following launch item addresses are invalid or files do not exist:\n{names}",
        "launch_done_title": "Launch Complete",
        "launch_done_desc": "Launched {count} project items.",
        "link_name_required": "Enter a launch item name.",
        "link_url_required_title": "Address Required",
        "link_url_required": "Enter a URL or local file path.",
        "confirm_ok": "OK",
        "confirm_cancel": "Cancel",
        "dock_error": "Dock Error",
    },
    "ja": {
        "select_all": "すべて選択",
        "clear_selection": "選択解除",
        "invert_selection": "反転",
        "delete_selected": "選択項目を削除",
        "done": "完了",
        "no_projects_title": "起動プロジェクトはまだありません",
        "no_projects_desc": "右上の「新規」をクリックします。空のプロジェクトから作成できます。",
        "missing_dock_title": "前回のドックが見つかりません",
        "create_dock_title": "先にドックを作成してください",
        "missing_dock_desc": "前回使用したドックフォルダーが存在しません。移動、削除、または名前変更された可能性があります：\n{path}\n既存のドックを再選択するか、新しいドックを作成してください。",
        "create_dock_desc": "ドックは起動プロジェクトの保存場所です。起動プロジェクトを作成する前に、ローカルフォルダーをドックとして選択してください。",
        "create_or_choose_dock": "ドックを作成 / 選択",
        "link_count": "{total} 件の起動項目、{enabled} 件が有効",
        "empty_project_desc": "このプロジェクトにはまだ起動項目がありません。下の「起動項目を追加」をクリックしてください。",
        "select_all_links": "起動項目をすべて選択",
        "delete_selected_links": "選択した起動項目を削除",
        "done_manage": "管理完了",
        "add_link": "起動項目を追加",
        "manage_links": "起動項目を管理",
        "launch": "起動",
        "dock_title": "ドック",
        "dock_desc": "すべての起動プロジェクトと設定を保存するローカルフォルダーを選択または作成します。",
        "current_dock_path": "現在のドックパス",
        "dock_structure": "ドック構造",
        "dock_structure_desc": "launchdock.json は全体設定を保存し、projects/ 配下の各プロジェクトは独立したフォルダーと project.json を持ちます。",
        "dock_not_created": "ドックはまだ作成されていません。今後作成する起動プロジェクトを保存するため、先にローカルフォルダーを選択してください。",
        "about_title": "LaunchDock について",
        "about_desc": "学習や仕事のプロジェクト内のWebリンクとローカルファイルを管理し、ワンクリックで起動するローカルドックです。",
        "version_label": "v{version}",
        "check_update": "新しいバージョンを確認",
        "github_link": "GitHub",
        "share_download_link": "ダウンロードリンクを共有",
        "update_placeholder_title": "バージョン更新",
        "update_placeholder_desc": "まだ新しいバージョンは検出されていません。GitHub Release を公開すると、ここにバージョン差分とリリースノートが表示されます。",
        "checking_update": "新しいバージョンを確認しています...",
        "no_release_title": "リリースはまだありません",
        "no_release_desc": "GitHub リポジトリにはまだ Release がありません。Release 公開後に更新確認が利用できます。",
        "no_update_title": "最新版です",
        "no_update_desc": "現在のバージョン v{current} は最新の公開バージョンです。",
        "update_available_title": "新しいバージョンがあります",
        "update_available_desc": "v{current} から {latest} に更新できます。",
        "update_changelog_title": "新バージョンの変更内容",
        "update_check_failed_title": "更新確認に失敗しました",
        "update_check_failed_desc": "GitHub Release に接続できません。後でもう一度お試しください：{error}",
        "open_release_prompt": "ダウンロードページを開きますか？",
        "download_link_copied": "ダウンロードリンクをコピーしました",
        "download_link_copied_desc": "GitHub Releases のダウンロードページリンクをコピーしました。",
        "dialog_save": "保存",
        "dialog_cancel": "キャンセル",
        "link_default_open": "プロジェクト起動時に既定で開く",
        "link_name_placeholder": "例：動画コース",
        "link_url_placeholder": "例：https://example.com または C:/Notes/note.pdf",
        "name": "名前",
        "url_or_path": "URL またはローカルパス",
        "delete_selected_links_title": "起動項目を一括削除",
        "delete_selected_links_desc": "以下の {count} 件の起動項目を削除しますか？\n{names}",
        "not_selected_links_title": "起動項目が選択されていません",
        "not_selected_links_desc": "削除する起動項目を先に選択してください。",
        "more_links": "...ほか {count} 件の起動項目",
        "not_selected_projects_title": "プロジェクトが選択されていません",
        "not_selected_projects_desc": "削除する起動プロジェクトを先に選択してください。",
        "more_projects": "...ほか {count} 件のプロジェクト",
        "delete_selected_projects_title": "一括削除",
        "delete_selected_projects_desc": "以下の {count} 件の起動プロジェクトを削除しますか？\n{names}",
        "need_dock_title": "先にドックを作成してください",
        "need_dock_desc": "ドックは起動プロジェクトの保存場所です。起動プロジェクトを作成する前にドックを作成してください。",
        "need_dock_save_desc": "ドックは起動プロジェクトの保存場所です。",
        "new_project_title": "新規起動プロジェクト",
        "project_name_prompt": "起動プロジェクト名を入力してください：",
        "need_name_title": "名前が必要です",
        "project_name_empty": "プロジェクト名は空にできません。",
        "create_failed": "作成に失敗しました",
        "create_success": "作成しました",
        "project_created": "プロジェクト「{name}」を作成しました。",
        "edit_project_title": "プロジェクトを編集",
        "delete_project_title": "削除の確認",
        "delete_project_desc": "プロジェクト「{name}」を削除しますか？\nこの操作はプロジェクトフォルダーを削除します。",
        "delete_link_title": "削除の確認",
        "delete_failed": "削除に失敗しました",
        "delete_project_failed": "「{name}」の削除に失敗しました：{error}",
        "delete_success": "削除しました",
        "project_deleted": "プロジェクト「{name}」を削除しました。",
        "add_link_title": "起動項目を追加",
        "edit_link_title": "起動項目を編集",
        "delete_link_desc": "起動項目「{name}」を削除しますか？",
        "save_failed": "保存に失敗しました",
        "choose_dock_title": "LaunchDock ドックフォルダーを作成または選択",
        "config_save_failed": "設定の保存に失敗しました",
        "dock_path_save_failed": "ドックは使用できますが、パスを保存できませんでした：{error}",
        "no_launch_targets_title": "起動項目がありません",
        "no_launch_targets_desc": "このプロジェクトには有効な起動項目がありません。",
        "invalid_targets_title": "起動項目を確認してください",
        "invalid_targets_desc": "以下の起動項目のアドレスが無効、またはファイルが存在しません：\n{names}",
        "launch_done_title": "起動完了",
        "launch_done_desc": "{count} 件のプロジェクト項目を起動しました。",
        "link_name_required": "起動項目名を入力してください。",
        "link_url_required_title": "アドレスが必要です",
        "link_url_required": "URL またはローカルファイルパスを入力してください。",
        "confirm_ok": "OK",
        "confirm_cancel": "キャンセル",
        "dock_error": "ドックエラー",
    },
    "ko": {
        "select_all": "전체 선택",
        "clear_selection": "전체 해제",
        "invert_selection": "반전",
        "delete_selected": "선택 삭제",
        "done": "완료",
        "no_projects_title": "실행 프로젝트가 없습니다",
        "no_projects_desc": "오른쪽 위의 새로 만들기를 클릭하세요. 빈 프로젝트부터 만들 수 있습니다.",
        "missing_dock_title": "이전 도크를 찾을 수 없습니다",
        "create_dock_title": "먼저 도크를 만드세요",
        "missing_dock_desc": "이전에 사용한 도크 폴더가 없습니다. 이동, 삭제 또는 이름이 변경되었을 수 있습니다:\n{path}\n기존 도크를 다시 선택하거나 새 도크를 만드세요.",
        "create_dock_desc": "도크는 실행 프로젝트의 저장 위치를 보관합니다. 실행 프로젝트를 만들기 전에 로컬 폴더를 도크로 선택하세요.",
        "create_or_choose_dock": "도크 만들기 / 선택",
        "link_count": "실행 항목 {total}개, 사용 {enabled}개",
        "empty_project_desc": "이 프로젝트에는 아직 실행 항목이 없습니다. 아래의 실행 항목 추가를 클릭하세요.",
        "select_all_links": "항목 전체 선택",
        "delete_selected_links": "선택 항목 삭제",
        "done_manage": "관리 완료",
        "add_link": "실행 항목 추가",
        "manage_links": "항목 관리",
        "launch": "실행",
        "dock_title": "도크",
        "dock_desc": "모든 실행 프로젝트와 설정을 저장할 로컬 폴더를 선택하거나 만듭니다.",
        "current_dock_path": "현재 도크 경로",
        "dock_structure": "도크 구조",
        "dock_structure_desc": "launchdock.json은 전역 설정을 저장하고, projects/ 아래의 각 프로젝트는 독립 폴더와 project.json을 가집니다.",
        "dock_not_created": "아직 도크가 없습니다. 이후 생성할 실행 프로젝트를 저장할 로컬 폴더를 먼저 선택하세요.",
        "about_title": "LaunchDock 정보",
        "about_desc": "학습 및 업무 프로젝트의 웹 링크와 로컬 파일을 관리하고 한 번에 실행하는 로컬 도크입니다.",
        "version_label": "v{version}",
        "check_update": "새 버전 확인",
        "github_link": "GitHub",
        "share_download_link": "다운로드 링크 공유",
        "update_placeholder_title": "버전 업데이트",
        "update_placeholder_desc": "아직 새 버전을 확인하지 못했습니다. GitHub Release를 게시하면 버전 변경과 릴리스 노트가 여기에 표시됩니다.",
        "checking_update": "새 버전을 확인하는 중...",
        "no_release_title": "아직 릴리스가 없습니다",
        "no_release_desc": "GitHub 저장소에 아직 Release가 없습니다. Release 게시 후 업데이트 확인을 사용할 수 있습니다.",
        "no_update_title": "최신 버전입니다",
        "no_update_desc": "현재 버전 v{current}은 최신 게시 버전입니다.",
        "update_available_title": "새 버전 발견",
        "update_available_desc": "v{current}에서 {latest}(으)로 업데이트할 수 있습니다.",
        "update_changelog_title": "새 버전 변경 내용",
        "update_check_failed_title": "업데이트 확인 실패",
        "update_check_failed_desc": "GitHub Release에 연결할 수 없습니다. 나중에 다시 시도하세요: {error}",
        "open_release_prompt": "다운로드 페이지를 열까요?",
        "download_link_copied": "다운로드 링크 복사됨",
        "download_link_copied_desc": "GitHub Releases 다운로드 페이지 링크를 복사했습니다.",
        "dialog_save": "저장",
        "dialog_cancel": "취소",
        "link_default_open": "프로젝트 실행 시 기본으로 열기",
        "link_name_placeholder": "예: 동영상 강의",
        "link_url_placeholder": "예: https://example.com 또는 C:/Notes/note.pdf",
        "name": "이름",
        "url_or_path": "URL 또는 로컬 경로",
        "delete_selected_links_title": "실행 항목 일괄 삭제",
        "delete_selected_links_desc": "다음 실행 항목 {count}개를 삭제할까요?\n{names}",
        "not_selected_links_title": "선택한 실행 항목 없음",
        "not_selected_links_desc": "삭제할 실행 항목을 먼저 선택하세요.",
        "more_links": "...외 실행 항목 {count}개",
        "not_selected_projects_title": "선택한 프로젝트 없음",
        "not_selected_projects_desc": "삭제할 실행 프로젝트를 먼저 선택하세요.",
        "more_projects": "...외 프로젝트 {count}개",
        "delete_selected_projects_title": "일괄 삭제",
        "delete_selected_projects_desc": "다음 실행 프로젝트 {count}개를 삭제할까요?\n{names}",
        "need_dock_title": "먼저 도크를 만드세요",
        "need_dock_desc": "도크는 실행 프로젝트의 저장 위치를 보관합니다. 실행 프로젝트를 만들기 전에 도크를 만드세요.",
        "need_dock_save_desc": "도크는 실행 프로젝트의 저장 위치를 보관합니다.",
        "new_project_title": "새 실행 프로젝트",
        "project_name_prompt": "실행 프로젝트 이름을 입력하세요:",
        "need_name_title": "이름 필요",
        "project_name_empty": "프로젝트 이름은 비워둘 수 없습니다.",
        "create_failed": "생성 실패",
        "create_success": "생성 완료",
        "project_created": "프로젝트 \"{name}\"이 생성되었습니다.",
        "edit_project_title": "프로젝트 편집",
        "delete_project_title": "삭제 확인",
        "delete_project_desc": "프로젝트 \"{name}\"을 삭제할까요?\n이 작업은 프로젝트 폴더를 삭제합니다.",
        "delete_link_title": "삭제 확인",
        "delete_failed": "삭제 실패",
        "delete_project_failed": "\"{name}\" 삭제 실패: {error}",
        "delete_success": "삭제 완료",
        "project_deleted": "프로젝트 \"{name}\"이 삭제되었습니다.",
        "add_link_title": "실행 항목 추가",
        "edit_link_title": "실행 항목 편집",
        "delete_link_desc": "실행 항목 \"{name}\"을 삭제할까요?",
        "save_failed": "저장 실패",
        "choose_dock_title": "LaunchDock 도크 폴더 만들기 또는 선택",
        "config_save_failed": "설정 저장 실패",
        "dock_path_save_failed": "도크는 계속 사용할 수 있지만 경로를 저장하지 못했습니다: {error}",
        "no_launch_targets_title": "실행 항목 없음",
        "no_launch_targets_desc": "이 프로젝트에는 사용 중인 실행 항목이 없습니다.",
        "invalid_targets_title": "실행 항목 확인 필요",
        "invalid_targets_desc": "다음 실행 항목 주소가 잘못되었거나 파일이 없습니다:\n{names}",
        "launch_done_title": "실행 완료",
        "launch_done_desc": "프로젝트 항목 {count}개를 실행했습니다.",
        "link_name_required": "실행 항목 이름을 입력하세요.",
        "link_url_required_title": "주소 필요",
        "link_url_required": "URL 또는 로컬 파일 경로를 입력하세요.",
        "confirm_ok": "확인",
        "confirm_cancel": "취소",
        "dock_error": "도크 오류",
    },
    "es": {
        "select_all": "Seleccionar todo",
        "clear_selection": "Deseleccionar todo",
        "invert_selection": "Invertir",
        "delete_selected": "Eliminar selección",
        "done": "Listo",
        "no_projects_title": "Aún no hay proyectos de inicio",
        "no_projects_desc": "Haz clic en Nuevo en la esquina superior derecha. También puedes crear primero un proyecto vacío.",
        "missing_dock_title": "No se encontró el dock anterior",
        "create_dock_title": "Crea un dock primero",
        "missing_dock_desc": "La carpeta del dock anterior no existe. Puede haberse movido, eliminado o renombrado:\n{path}\nVuelve a elegir un dock existente o crea uno nuevo.",
        "create_dock_desc": "Un dock guarda la ubicación de tus proyectos de inicio. Elige una carpeta local como dock antes de crear proyectos.",
        "create_or_choose_dock": "Crear / Elegir dock",
        "link_count": "{total} elementos de inicio, {enabled} habilitados",
        "empty_project_desc": "Este proyecto aún no tiene elementos de inicio. Haz clic en Agregar elemento de inicio abajo.",
        "select_all_links": "Seleccionar elementos",
        "delete_selected_links": "Eliminar elementos seleccionados",
        "done_manage": "Terminar",
        "add_link": "Agregar elemento de inicio",
        "manage_links": "Gestionar elementos",
        "launch": "Iniciar",
        "dock_title": "Dock",
        "dock_desc": "Elige o crea una carpeta local para guardar todos los proyectos de inicio y ajustes.",
        "current_dock_path": "Ruta actual del dock",
        "dock_structure": "Estructura del dock",
        "dock_structure_desc": "launchdock.json guarda la configuración global; cada proyecto en projects/ tiene su propia carpeta y project.json.",
        "dock_not_created": "Aún no se ha creado un dock. Elige primero una carpeta local para guardar los proyectos de inicio.",
        "about_title": "Acerca de LaunchDock",
        "about_desc": "Un dock local para gestionar enlaces web y archivos locales de estudio y trabajo, e iniciarlos con un clic.",
        "version_label": "v{version}",
        "check_update": "Buscar actualización",
        "github_link": "GitHub",
        "share_download_link": "Compartir enlace",
        "update_placeholder_title": "Actualizaciones",
        "update_placeholder_desc": "Aún no se ha detectado una nueva versión. Cuando se publique un GitHub Release, aquí aparecerán el cambio de versión y las notas.",
        "checking_update": "Buscando actualizaciones...",
        "no_release_title": "Sin versiones publicadas",
        "no_release_desc": "Este repositorio de GitHub todavía no tiene Release. La comprobación funcionará cuando se publique una.",
        "no_update_title": "Actualizado",
        "no_update_desc": "La versión actual v{current} ya es la última publicada.",
        "update_available_title": "Nueva versión disponible",
        "update_available_desc": "Puedes actualizar de v{current} a {latest}.",
        "update_changelog_title": "Cambios de la nueva versión",
        "update_check_failed_title": "No se pudo buscar actualización",
        "update_check_failed_desc": "No se pudo conectar a GitHub Releases. Inténtalo más tarde: {error}",
        "open_release_prompt": "¿Abrir la página de descarga?",
        "download_link_copied": "Enlace copiado",
        "download_link_copied_desc": "Se copió el enlace de la página de descargas de GitHub Releases.",
        "dialog_save": "Guardar",
        "dialog_cancel": "Cancelar",
        "link_default_open": "Abrir por defecto al iniciar el proyecto",
        "link_name_placeholder": "Ejemplo: curso en video",
        "link_url_placeholder": "Ejemplo: https://example.com o C:/Notes/note.pdf",
        "name": "Nombre",
        "url_or_path": "URL o ruta local",
        "delete_selected_links_title": "Eliminar elementos de inicio",
        "delete_selected_links_desc": "¿Eliminar los siguientes {count} elementos de inicio?\n{names}",
        "not_selected_links_title": "No hay elementos seleccionados",
        "not_selected_links_desc": "Selecciona primero los elementos de inicio que quieres eliminar.",
        "more_links": "...y {count} elementos de inicio más",
        "not_selected_projects_title": "No hay proyectos seleccionados",
        "not_selected_projects_desc": "Selecciona primero los proyectos de inicio que quieres eliminar.",
        "more_projects": "...y {count} proyectos más",
        "delete_selected_projects_title": "Eliminar proyectos",
        "delete_selected_projects_desc": "¿Eliminar los siguientes {count} proyectos de inicio?\n{names}",
        "need_dock_title": "Crea un dock primero",
        "need_dock_desc": "Un dock guarda la ubicación de los proyectos de inicio. Crea un dock antes de crear proyectos.",
        "need_dock_save_desc": "Un dock guarda la ubicación de los proyectos de inicio.",
        "new_project_title": "Nuevo proyecto de inicio",
        "project_name_prompt": "Introduce el nombre del proyecto de inicio:",
        "need_name_title": "Nombre requerido",
        "project_name_empty": "El nombre del proyecto no puede estar vacío.",
        "create_failed": "No se pudo crear",
        "create_success": "Creado",
        "project_created": "El proyecto \"{name}\" se ha creado.",
        "edit_project_title": "Editar proyecto",
        "delete_project_title": "Confirmar eliminación",
        "delete_project_desc": "¿Eliminar el proyecto \"{name}\"?\nEsta acción eliminará la carpeta del proyecto.",
        "delete_link_title": "Confirmar eliminación",
        "delete_failed": "No se pudo eliminar",
        "delete_project_failed": "No se pudo eliminar \"{name}\": {error}",
        "delete_success": "Eliminado",
        "project_deleted": "El proyecto \"{name}\" se ha eliminado.",
        "add_link_title": "Agregar elemento de inicio",
        "edit_link_title": "Editar elemento de inicio",
        "delete_link_desc": "¿Eliminar el elemento de inicio \"{name}\"?",
        "save_failed": "No se pudo guardar",
        "choose_dock_title": "Crear o elegir carpeta dock de LaunchDock",
        "config_save_failed": "No se pudo guardar la configuración",
        "dock_path_save_failed": "El dock se puede seguir usando, pero no se pudo recordar la ruta: {error}",
        "no_launch_targets_title": "No hay elementos de inicio",
        "no_launch_targets_desc": "Este proyecto no tiene elementos de inicio habilitados.",
        "invalid_targets_title": "Revisa los elementos de inicio",
        "invalid_targets_desc": "Las siguientes direcciones son inválidas o los archivos no existen:\n{names}",
        "launch_done_title": "Inicio completado",
        "launch_done_desc": "Se iniciaron {count} elementos del proyecto.",
        "link_name_required": "Introduce el nombre del elemento de inicio.",
        "link_url_required_title": "Dirección requerida",
        "link_url_required": "Introduce una URL o una ruta de archivo local.",
        "confirm_ok": "Aceptar",
        "confirm_cancel": "Cancelar",
        "dock_error": "Error del dock",
    },
}

for language_key, values in TEXT_EXTRA.items():
    TEXT[language_key].update(values)


def load_user_settings() -> dict[str, str]:
    config = load_app_config()
    settings = config.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    theme = str(settings.get("theme", "dark"))
    language = str(settings.get("language", "zh_cn"))
    if theme not in THEME_OPTIONS:
        theme = "dark"
    if language not in SUPPORTED_LANGUAGES:
        language = "zh_cn"
    return {"theme": theme, "language": language}


def save_user_setting(key: str, value: str) -> None:
    config = load_app_config()
    settings = config.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    settings[key] = value
    config["settings"] = settings
    save_app_config(config)


def theme_from_setting(value: str) -> Theme:
    if value == "light":
        return Theme.LIGHT
    if value == "system":
        return Theme.AUTO
    return Theme.DARK


def effective_language(language: str) -> str:
    if language != "system":
        return language if language in TEXT else "zh_cn"
    system_language = (locale.getlocale()[0] or "").lower()
    if system_language.startswith("zh_tw") or system_language.startswith("zh_hk") or system_language.startswith("zh_mo"):
        return "zh_tw"
    if system_language.startswith("zh"):
        return "zh_cn"
    if system_language.startswith("ja"):
        return "ja"
    if system_language.startswith("ko"):
        return "ko"
    if system_language.startswith("es"):
        return "es"
    if system_language.startswith("en"):
        return "en"
    return "zh_cn"


def tr(language: str, key: str, **kwargs: object) -> str:
    text = TEXT.get(effective_language(language), TEXT["zh_cn"]).get(key, TEXT["zh_cn"].get(key, key))
    return text.format(**kwargs)


def theme_options(language: str) -> dict[str, str]:
    return {
        "light": tr(language, "theme_light"),
        "dark": tr(language, "theme_dark"),
        "system": tr(language, "theme_system"),
    }


def language_options(language: str) -> dict[str, str]:
    options = dict(LANGUAGE_NATIVE_NAMES)
    options["system"] = tr(language, "system_language")
    return options


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


def fetch_latest_release() -> dict[str, object]:
    request = Request(GITHUB_LATEST_RELEASE_API, headers={"Accept": "application/vnd.github+json", "User-Agent": "LaunchDock"})
    try:
        with urlopen(request, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return {"status": "none"}
        raise
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


class UpdateSignals(QObject):
    checked = Signal(dict)
    failed = Signal(dict)


def is_checked_state(state: object) -> bool:
    return state == Qt.CheckState.Checked or state == Qt.CheckState.Checked.value


def set_switch_checked_without_animation(switch: SwitchButton, checked: bool) -> None:
    switch.indicator.slideAni.stop()
    switch.indicator.blockSignals(True)
    switch.indicator.setChecked(checked)
    switch.indicator.blockSignals(False)
    switch.indicator.setSliderX(25 if checked else 5)


def image_has_alpha(image: QImage) -> bool:
    if not image.hasAlphaChannel():
        return False
    for y in range(image.height()):
        for x in range(image.width()):
            if image.pixelColor(x, y).alpha() < 255:
                return True
    return False


def remove_solid_icon_background(image: QImage) -> QImage:
    result = image.convertToFormat(QImage.Format.Format_ARGB32)
    if image_has_alpha(result):
        return result

    corners = [
        result.pixelColor(0, 0),
        result.pixelColor(result.width() - 1, 0),
        result.pixelColor(0, result.height() - 1),
        result.pixelColor(result.width() - 1, result.height() - 1),
    ]
    background = max(corners, key=lambda color: sum(1 for item in corners if color_distance(color, item) <= 6))

    for y in range(result.height()):
        for x in range(result.width()):
            color = result.pixelColor(x, y)
            distance = color_distance(color, background)
            if distance <= BACKGROUND_REMOVE_THRESHOLD:
                color.setAlpha(0)
            elif distance <= BACKGROUND_REMOVE_THRESHOLD * 2:
                color.setAlpha(min(255, int((distance - BACKGROUND_REMOVE_THRESHOLD) / BACKGROUND_REMOVE_THRESHOLD * 255)))
            result.setPixelColor(x, y, color)
    return result


def color_distance(first: QColor, second: QColor) -> int:
    return max(abs(first.red() - second.red()), abs(first.green() - second.green()), abs(first.blue() - second.blue()))


class TextInputDialog(Dialog):
    def __init__(
        self,
        title: str,
        label: str,
        value: str = "",
        parent: QWidget | None = None,
        save_text: str = "保存",
        cancel_text: str = "取消",
    ) -> None:
        super().__init__(title, "", parent)
        self.input = LineEdit(self)
        self.input.setPlaceholderText(label)
        self.input.setText(value)
        self.textLayout.addWidget(BodyLabel(label, self))
        self.textLayout.addWidget(self.input)
        self.yesButton.setText(save_text)
        self.cancelButton.setText(cancel_text)
        self.input.returnPressed.connect(self.yesButton.click)

    def text_value(self) -> str:
        return self.input.text().strip()


class LinkDialog(Dialog):
    def __init__(self, title: str, link: Link | None = None, parent: "LaunchDockApp | None" = None) -> None:
        super().__init__(title, "", parent)
        text = parent.text if parent else lambda key, **kwargs: tr("zh_cn", key, **kwargs)
        self.name_edit = LineEdit(self)
        self.name_edit.setPlaceholderText(text("link_name_placeholder"))
        self.url_edit = LineEdit(self)
        self.url_edit.setPlaceholderText(text("link_url_placeholder"))
        self.default_check = CheckBox(text("link_default_open"), self)

        if link:
            self.name_edit.setText(link.name)
            self.url_edit.setText(link.url)
            self.default_check.setChecked(link.default_open)
        else:
            self.default_check.setChecked(True)

        self.textLayout.addWidget(BodyLabel(text("name"), self))
        self.textLayout.addWidget(self.name_edit)
        self.textLayout.addSpacing(8)
        self.textLayout.addWidget(BodyLabel(text("url_or_path"), self))
        self.textLayout.addWidget(self.url_edit)
        self.textLayout.addSpacing(8)
        self.textLayout.addWidget(self.default_check)
        self.yesButton.setText(text("dialog_save"))
        self.cancelButton.setText(text("dialog_cancel"))
        self.name_edit.returnPressed.connect(self.yesButton.click)
        self.url_edit.returnPressed.connect(self.yesButton.click)

    def values(self) -> dict[str, object]:
        return {
            "name": self.name_edit.text().strip(),
            "url": self.url_edit.text().strip(),
            "default_open": self.default_check.isChecked(),
        }


class LaunchInterface(QWidget):
    def __init__(self, app_window: "LaunchDockApp") -> None:
        super().__init__()
        self.app_window = app_window
        self.setObjectName("launchInterface")
        self.setContentsMargins(28, 24, 28, 24)
        self.setStyleSheet("#launchInterface { background: transparent; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(18)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.addWidget(TitleLabel(self.app_window.text("launch_title"), self))
        title_box.addWidget(CaptionLabel(self.app_window.text("launch_desc"), self))
        header.addLayout(title_box, 1)

        new_button = PrimaryPushButton(FluentIcon.ADD, self.app_window.text("new"), self)
        new_button.clicked.connect(self.app_window.add_project)
        self.manage_button = TransparentPushButton(FluentIcon.EDIT, self.app_window.text("manage_projects"), self)
        self.manage_button.clicked.connect(lambda: self.app_window.set_manage_mode(True))
        self.select_all_button = TransparentPushButton(FluentIcon.CHECKBOX, self.app_window.text("select_all"), self)
        self.select_all_button.clicked.connect(self.app_window.select_all_projects)
        self.clear_selection_button = TransparentPushButton(FluentIcon.CLEAR_SELECTION, self.app_window.text("clear_selection"), self)
        self.clear_selection_button.clicked.connect(self.app_window.clear_project_selection)
        self.invert_selection_button = TransparentPushButton(FluentIcon.SYNC, self.app_window.text("invert_selection"), self)
        self.invert_selection_button.clicked.connect(self.app_window.invert_project_selection)
        self.delete_selected_button = TransparentPushButton(FluentIcon.DELETE, self.app_window.text("delete_selected"), self)
        self.delete_selected_button.clicked.connect(self.app_window.delete_selected_projects)
        self.done_button = PrimaryPushButton(FluentIcon.ACCEPT, self.app_window.text("done"), self)
        self.done_button.clicked.connect(lambda: self.app_window.set_manage_mode(False))
        header.addWidget(self.manage_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(self.select_all_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(self.clear_selection_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(self.invert_selection_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(self.delete_selected_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(self.done_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(new_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.new_button = new_button
        root.addLayout(header)

        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
            "QScrollBar { background: transparent; }"
        )
        self.content = QWidget(self.scroll)
        self.content.setAttribute(Qt.WA_StyledBackground, True)
        self.content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 14, 0)
        self.content_layout.setSpacing(14)
        self.project_count_labels: dict[str, CaptionLabel] = {}
        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll, 1)

    def refresh(self, projects: list[Project]) -> None:
        has_launch_dock = self.app_window.has_launch_dock()
        self.manage_button.setVisible(has_launch_dock and not self.app_window.manage_mode)
        self.new_button.setVisible(has_launch_dock and not self.app_window.manage_mode)
        self.select_all_button.setVisible(has_launch_dock and self.app_window.manage_mode)
        self.clear_selection_button.setVisible(has_launch_dock and self.app_window.manage_mode)
        self.invert_selection_button.setVisible(has_launch_dock and self.app_window.manage_mode)
        self.delete_selected_button.setVisible(has_launch_dock and self.app_window.manage_mode)
        self.done_button.setVisible(has_launch_dock and self.app_window.manage_mode)
        clear_layout(self.content_layout)
        self.project_count_labels.clear()
        if not has_launch_dock:
            self.content_layout.addWidget(self.launch_dock_required_card(self.app_window.storage.missing_dock_path))
            self.content_layout.addStretch(1)
            return
        if not projects:
            self.content_layout.addWidget(self.empty_card())
            self.content_layout.addStretch(1)
            return
        for project in projects:
            self.content_layout.addWidget(self.project_card(project))
        self.content_layout.addStretch(1)

    def empty_card(self) -> CardWidget:
        card = CardWidget(self)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)
        layout.addWidget(IconWidget(FluentIcon.ADD, card), 0, Qt.AlignTop)
        text_box = QVBoxLayout()
        text_box.addWidget(SubtitleLabel(self.app_window.text("no_projects_title"), card))
        text_box.addWidget(BodyLabel(self.app_window.text("no_projects_desc"), card))
        layout.addLayout(text_box, 1)
        return card

    def launch_dock_required_card(self, missing_path: Path | None = None) -> CardWidget:
        card = CardWidget(self)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)
        layout.addWidget(IconWidget(FluentIcon.FOLDER_ADD, card), 0, Qt.AlignTop)
        text_box = QVBoxLayout()
        text_box.setSpacing(8)
        title = self.app_window.text("missing_dock_title") if missing_path else self.app_window.text("create_dock_title")
        text_box.addWidget(SubtitleLabel(title, card))
        if missing_path:
            message = self.app_window.text("missing_dock_desc", path=missing_path)
        else:
            message = self.app_window.text("create_dock_desc")
        text = BodyLabel(message, card)
        text.setWordWrap(True)
        text_box.addWidget(text)
        create_button = PrimaryPushButton(FluentIcon.FOLDER_ADD, self.app_window.text("create_or_choose_dock"), card)
        create_button.clicked.connect(self.app_window.choose_dock)
        text_box.addWidget(create_button, 0, Qt.AlignLeft)
        layout.addLayout(text_box, 1)
        return card

    def project_card(self, project: Project) -> CardWidget:
        card = CardWidget(self)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(12)
        if self.app_window.manage_mode:
            checkbox = CheckBox("", card)
            checkbox.setChecked(project.id in self.app_window.selected_project_ids)
            checkbox.checkStateChanged.connect(
                lambda state, p=project: self.app_window.toggle_project_selection(p, is_checked_state(state))
            )
            header.addWidget(checkbox, 0, Qt.AlignTop)
        header.addWidget(IconWidget(FluentIcon.APPLICATION, card), 0, Qt.AlignTop)

        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        title_box.addWidget(SubtitleLabel(project.name, card))
        default_count = len([link for link in project.links if link.default_open])
        count_label = CaptionLabel(self.app_window.text("link_count", total=len(project.links), enabled=default_count), card)
        self.project_count_labels[project.id] = count_label
        title_box.addWidget(count_label)
        header.addLayout(title_box, 1)

        edit_button = TransparentToolButton(FluentIcon.EDIT, card)
        edit_button.clicked.connect(lambda _=False, p=project: self.app_window.rename_project(p))
        delete_button = TransparentToolButton(FluentIcon.DELETE, card)
        delete_button.clicked.connect(lambda _=False, p=project: self.app_window.delete_project(p))
        collapse_icon = FluentIcon.CHEVRON_RIGHT if project.id in self.app_window.collapsed_project_ids else FluentIcon.CHEVRON_DOWN_MED
        collapse_button = TransparentToolButton(collapse_icon, card)
        collapse_button.clicked.connect(lambda _=False, p=project: self.app_window.toggle_project_collapse(p))
        header.addWidget(collapse_button)
        header.addWidget(edit_button)
        header.addWidget(delete_button)
        layout.addLayout(header)

        if project.id not in self.app_window.collapsed_project_ids:
            if project.links:
                for link in sorted(project.links, key=lambda item: item.order):
                    layout.addWidget(self.link_row(project, link))
            else:
                empty_row = QHBoxLayout()
                empty_row.setContentsMargins(0, 0, 0, 0)
                empty_row.addSpacing(12)
                empty_label = CaptionLabel(self.app_window.text("empty_project_desc"), card)
                empty_label.setWordWrap(True)
                empty_row.addWidget(empty_label, 1)
                layout.addLayout(empty_row)

        footer = QHBoxLayout()
        link_manage_active = self.app_window.link_manage_project_id == project.id
        if link_manage_active:
            select_all_button = TransparentPushButton(FluentIcon.CHECKBOX, self.app_window.text("select_all_links"), card)
            select_all_button.clicked.connect(lambda _=False, p=project: self.app_window.select_all_links(p))
            clear_selection_button = TransparentPushButton(FluentIcon.CLEAR_SELECTION, self.app_window.text("clear_selection"), card)
            clear_selection_button.clicked.connect(lambda _=False, p=project: self.app_window.clear_link_selection(p))
            invert_selection_button = TransparentPushButton(FluentIcon.SYNC, self.app_window.text("invert_selection"), card)
            invert_selection_button.clicked.connect(lambda _=False, p=project: self.app_window.invert_link_selection(p))
            delete_selected_button = TransparentPushButton(FluentIcon.DELETE, self.app_window.text("delete_selected_links"), card)
            delete_selected_button.clicked.connect(lambda _=False, p=project: self.app_window.delete_selected_links(p))
            done_button = PrimaryPushButton(FluentIcon.ACCEPT, self.app_window.text("done_manage"), card)
            done_button.clicked.connect(lambda _=False: self.app_window.set_link_manage_project(None))
            footer.addWidget(select_all_button)
            footer.addWidget(clear_selection_button)
            footer.addWidget(invert_selection_button)
            footer.addWidget(delete_selected_button)
            footer.addWidget(done_button)
        else:
            add_button = TransparentPushButton(FluentIcon.ADD, self.app_window.text("add_link"), card)
            add_button.clicked.connect(lambda _=False, p=project: self.app_window.add_link(p))
            manage_links_button = TransparentPushButton(FluentIcon.EDIT, self.app_window.text("manage_links"), card)
            manage_links_button.clicked.connect(lambda _=False, p=project: self.app_window.set_link_manage_project(p))
            footer.addWidget(add_button)
            footer.addWidget(manage_links_button)
        footer.addStretch(1)
        launch_button = PrimaryPushButton(FluentIcon.PLAY_SOLID, self.app_window.text("launch"), card)
        launch_button.clicked.connect(lambda _=False, p=project: self.app_window.launch_project(p))
        footer.addWidget(launch_button)
        layout.addLayout(footer)
        return card

    def link_row(self, project: Project, link: Link) -> CardWidget:
        row = CardWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon = FluentIcon.LINK if looks_like_url(link.url) else FluentIcon.DOCUMENT
        if self.app_window.link_manage_project_id == project.id:
            checkbox = CheckBox("", row)
            checkbox.setChecked(link.id in self.app_window.selected_link_ids_by_project.get(project.id, set()))
            checkbox.checkStateChanged.connect(
                lambda state, p=project, l=link: self.app_window.toggle_link_selection(p, l, is_checked_state(state))
            )
            layout.addWidget(checkbox, 0, Qt.AlignTop)
        layout.addWidget(IconWidget(icon, row), 0, Qt.AlignTop)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        name_label = BodyLabel(link.name, row)
        name_label.setWordWrap(True)
        text_box.addWidget(name_label)
        row.setToolTip(link.url)
        layout.addLayout(text_box, 1)

        edit_button = TransparentToolButton(FluentIcon.EDIT, row)
        edit_button.clicked.connect(lambda _=False, p=project, l=link: self.app_window.edit_link(p, l))
        delete_button = TransparentToolButton(FluentIcon.DELETE, row)
        delete_button.clicked.connect(lambda _=False, p=project, l=link: self.app_window.delete_link(p, l))
        switch = SwitchButton(row)
        switch.setOnText("")
        switch.setOffText("")
        set_switch_checked_without_animation(switch, link.default_open)
        switch.checkedChanged.connect(lambda checked, p=project, l=link: self.app_window.toggle_link(p, l, checked))

        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addWidget(switch)
        return row

    def refresh_project_count(self, project: Project) -> None:
        count_label = self.project_count_labels.get(project.id)
        if not count_label:
            return
        enabled_count = len([link for link in project.links if link.default_open])
        count_label.setText(self.app_window.text("link_count", total=len(project.links), enabled=enabled_count))


class DockInterface(QWidget):
    def __init__(self, app_window: "LaunchDockApp") -> None:
        super().__init__()
        self.app_window = app_window
        self.setObjectName("dockInterface")
        self.setContentsMargins(28, 24, 28, 24)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.addWidget(TitleLabel(self.app_window.text("dock_title"), self))
        dock_desc = CaptionLabel(self.app_window.text("dock_desc"), self)
        dock_desc.setWordWrap(True)
        title_box.addWidget(dock_desc)
        layout.addLayout(title_box)

        self.path_label = BodyLabel("", self)
        self.path_label.setWordWrap(True)
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)
        card_layout.addWidget(SubtitleLabel(self.app_window.text("current_dock_path"), card))
        card_layout.addWidget(self.path_label)
        choose_button = PrimaryPushButton(FluentIcon.FOLDER_ADD, self.app_window.text("create_or_choose_dock"), card)
        choose_button.clicked.connect(self.app_window.choose_dock)
        card_layout.addWidget(choose_button, 0, Qt.AlignLeft)
        layout.addWidget(card)

        structure = CardWidget(self)
        structure_layout = QVBoxLayout(structure)
        structure_layout.setContentsMargins(18, 16, 18, 16)
        structure_layout.addWidget(SubtitleLabel(self.app_window.text("dock_structure"), structure))
        text = BodyLabel(self.app_window.text("dock_structure_desc"), structure)
        text.setWordWrap(True)
        structure_layout.addWidget(text)
        layout.addWidget(structure)
        layout.addStretch(1)

    def refresh(self, dock_path: Path | None, missing_path: Path | None = None) -> None:
        if dock_path is None:
            if missing_path:
                self.path_label.setText(
                    self.app_window.text("missing_dock_desc", path=missing_path)
                )
            else:
                self.path_label.setText(self.app_window.text("dock_not_created"))
        else:
            self.path_label.setText(str(dock_path))


class AboutInterface(QWidget):
    def __init__(self, app_window: "LaunchDockApp") -> None:
        super().__init__()
        self.app_window = app_window
        self.setObjectName("aboutInterface")
        self.setContentsMargins(28, 24, 28, 24)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(TitleLabel(self.app_window.text("about_title"), self))

        card = CardWidget(self)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(16)

        icon_label = QLabel(card)
        icon = app_icon()
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(56, 56))
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_label, 0, Qt.AlignVCenter)

        info_box = QVBoxLayout()
        info_box.setSpacing(3)
        info_box.addWidget(SubtitleLabel("LaunchDock", card))
        info_box.addWidget(CaptionLabel(self.app_window.text("version_label", version=__version__), card))
        intro = BodyLabel(self.app_window.text("about_desc"), card)
        intro.setWordWrap(True)
        info_box.addWidget(intro)
        card_layout.addLayout(info_box, 1)

        check_button = PushButton(FluentIcon.SYNC, self.app_window.text("check_update"), card)
        check_button.clicked.connect(lambda: self.app_window.check_for_updates(manual=True))
        github_button = PushButton(FluentIcon.GITHUB, self.app_window.text("github_link"), card)
        github_button.clicked.connect(self.app_window.open_github)
        share_button = PushButton(FluentIcon.SHARE, self.app_window.text("share_download_link"), card)
        share_button.clicked.connect(self.app_window.copy_download_link)
        for button in (check_button, github_button, share_button):
            button.setFixedHeight(38)
        card_layout.addWidget(check_button, 0, Qt.AlignVCenter)
        card_layout.addWidget(github_button, 0, Qt.AlignVCenter)
        card_layout.addWidget(share_button, 0, Qt.AlignVCenter)
        self.check_button = check_button

        layout.addWidget(card)

        update_card = CardWidget(self)
        update_layout = QVBoxLayout(update_card)
        update_layout.setContentsMargins(18, 16, 18, 16)
        update_layout.setSpacing(10)
        self.update_title = SubtitleLabel(self.app_window.text("update_placeholder_title"), update_card)
        self.update_body = BodyLabel(self.app_window.text("update_placeholder_desc"), update_card)
        self.update_body.setWordWrap(True)
        update_layout.addWidget(self.update_title)
        update_layout.addWidget(self.update_body)
        layout.addWidget(update_card)
        layout.addStretch(1)

    def set_checking(self) -> None:
        self.check_button.setEnabled(False)
        self.update_title.setText(self.app_window.text("check_update"))
        self.update_body.setText(self.app_window.text("checking_update"))

    def set_update_result(self, title: str, body: str) -> None:
        self.check_button.setEnabled(True)
        self.update_title.setText(title)
        self.update_body.setText(body)


class SettingsInterface(QWidget):
    def __init__(self, app_window: "LaunchDockApp") -> None:
        super().__init__()
        self.app_window = app_window
        self.setObjectName("settingsInterface")
        self.setContentsMargins(28, 24, 28, 24)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(TitleLabel(self.app_window.text("settings_title"), self))

        self.theme_combo = ComboBox(self)
        self.language_combo = ComboBox(self)
        self.theme_key_by_text: dict[str, str] = {}
        self.language_key_by_text: dict[str, str] = {}

        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)

        layout.addWidget(
            self.setting_card(
                icon=FluentIcon.PALETTE,
                title=self.app_window.text("app_theme"),
                description=self.app_window.text("app_theme_desc"),
                control=self.theme_combo,
            )
        )
        layout.addWidget(
            self.setting_card(
                icon=FluentIcon.LANGUAGE,
                title=self.app_window.text("language"),
                description=self.app_window.text("language_desc"),
                control=self.language_combo,
            )
        )
        layout.addStretch(1)
        self.refresh()

    def setting_card(self, icon: FluentIcon, title: str, description: str, control: QWidget) -> CardWidget:
        card = CardWidget(self)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.setSpacing(14)
        icon_widget = IconWidget(icon, card)
        icon_widget.setFixedSize(28, 28)
        layout.addWidget(icon_widget, 0, Qt.AlignVCenter)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        text_box.addWidget(SubtitleLabel(title, card))
        text_box.addWidget(CaptionLabel(description, card))
        layout.addLayout(text_box, 1)
        layout.addWidget(control, 0, Qt.AlignRight | Qt.AlignVCenter)
        return card

    def refresh(self) -> None:
        settings = self.app_window.user_settings
        theme_items = theme_options(settings["language"])
        language_items = language_options(settings["language"])
        self.theme_key_by_text = {text: key for key, text in theme_items.items()}
        self.language_key_by_text = {text: key for key, text in language_items.items()}
        self.theme_combo.blockSignals(True)
        self.language_combo.blockSignals(True)
        self.theme_combo.clear()
        self.language_combo.clear()
        self.theme_combo.addItems(list(theme_items.values()))
        self.language_combo.addItems(list(language_items.values()))
        self.theme_combo.setCurrentText(theme_items[settings["theme"]])
        self.language_combo.setCurrentText(language_items[settings["language"]])
        self.theme_combo.blockSignals(False)
        self.language_combo.blockSignals(False)

    def on_theme_changed(self, text: str) -> None:
        theme_key = self.theme_key_by_text.get(text)
        if theme_key is None:
            return
        self.app_window.update_theme_setting(theme_key)

    def on_language_changed(self, text: str) -> None:
        language_key = self.language_key_by_text.get(text)
        if language_key is None:
            return
        self.app_window.update_language_setting(language_key)


class LaunchDockApp(FluentWindow):
    def __init__(self) -> None:
        super().__init__()
        self.user_settings = load_user_settings()
        setTheme(theme_from_setting(self.user_settings["theme"]))
        setThemeColor(ACCENT_COLOR)

        self.storage = DockStorage()
        self.projects: list[Project] = []
        self.manage_mode = False
        self.selected_project_ids: set[str] = set()
        self.collapsed_project_ids: set[str] = set()
        self.link_manage_project_id: str | None = None
        self.selected_link_ids_by_project: dict[str, set[str]] = {}
        self.update_check_running = False
        self.update_signals = UpdateSignals(self)
        self.update_signals.checked.connect(self.on_update_checked)
        self.update_signals.failed.connect(self.on_update_failed)

        self.setWindowTitle("LaunchDock")
        icon = app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self.resize(1220, 760)
        self.setMinimumSize(980, 620)
        self.setResizeEnabled(True)
        # 增加无边框窗口边缘命中范围，降低右侧边缘难以拖拽缩放的概率。
        self.BORDER_WIDTH = 10
        try:
            self.setMicaEffectEnabled(True)
        except Exception:
            pass

        self.launch_interface = LaunchInterface(self)
        self.dock_interface = DockInterface(self)
        self.about_interface = AboutInterface(self)
        self.settings_interface = SettingsInterface(self)

        self.addSubInterface(self.launch_interface, FluentIcon.PLAY_SOLID, self.text("nav_launch"), NavigationItemPosition.TOP)
        self.addSubInterface(self.dock_interface, FluentIcon.FOLDER, self.text("nav_dock"), NavigationItemPosition.TOP)
        self.addSubInterface(self.about_interface, FluentIcon.HELP, self.text("nav_about"), NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settings_interface, FluentIcon.SETTING, self.text("nav_settings"), NavigationItemPosition.BOTTOM)
        self.adjust_navigation_expand_width()

        self.load_data()
        self.switchTo(self.about_interface)
        QTimer.singleShot(1200, lambda: self.check_for_updates(manual=False))

    def has_launch_dock(self) -> bool:
        return self.storage.dock_path is not None

    def text(self, key: str, **kwargs: object) -> str:
        return tr(self.user_settings["language"], key, **kwargs)

    def adjust_navigation_expand_width(self) -> int:
        labels = [
            self.text("nav_launch"),
            self.text("nav_dock"),
            self.text("nav_about"),
            self.text("nav_settings"),
        ]
        max_text_width = max(self.fontMetrics().horizontalAdvance(label) for label in labels)
        width = max(NAVIGATION_EXPAND_MIN_WIDTH, min(max_text_width + NAVIGATION_TEXT_EXTRA_WIDTH, NAVIGATION_EXPAND_MAX_WIDTH))
        self.navigationInterface.setExpandWidth(width)
        self.navigationInterface.setMinimumExpandWidth(0)
        return width

    def update_theme_setting(self, theme_key: str) -> None:
        self.user_settings["theme"] = theme_key
        setTheme(theme_from_setting(theme_key))
        setThemeColor(ACCENT_COLOR)
        try:
            save_user_setting("theme", theme_key)
        except StorageError as exc:
            self.show_warning(self.text("settings_save_failed"), self.text("theme_save_failed", error=exc))

    def update_language_setting(self, language_key: str) -> None:
        self.user_settings["language"] = language_key
        try:
            save_user_setting("language", language_key)
        except StorageError as exc:
            self.show_warning(self.text("settings_save_failed"), self.text("language_save_failed", error=exc))
            return
        self.settings_interface.refresh()
        self.show_warning(self.text("language_restart_title"), self.text("language_restart_desc"))

    def open_github(self) -> None:
        webbrowser.open_new_tab(GITHUB_REPO_URL)

    def copy_download_link(self) -> None:
        QApplication.clipboard().setText(GITHUB_RELEASES_URL)
        InfoBar.success(
            self.text("download_link_copied"),
            self.text("download_link_copied_desc"),
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )

    def check_for_updates(self, manual: bool = False) -> None:
        if self.update_check_running:
            return
        self.update_check_running = True
        if manual:
            self.about_interface.set_checking()

        def worker() -> None:
            try:
                result = fetch_latest_release()
                result["manual"] = manual
                self.update_signals.checked.emit(result)
            except (HTTPError, URLError, OSError, json.JSONDecodeError) as exc:
                self.update_signals.failed.emit({"manual": manual, "error": str(exc)})

        Thread(target=worker, daemon=True).start()

    def on_update_checked(self, result: dict[str, object]) -> None:
        self.update_check_running = False
        manual = bool(result.get("manual"))
        status = str(result.get("status") or "")
        if status == "none":
            self.about_interface.set_update_result(self.text("no_release_title"), self.text("no_release_desc"))
            if manual:
                self.show_warning(self.text("no_release_title"), self.text("no_release_desc"))
            return

        latest = str(result.get("tag_name") or "")
        release_url = str(result.get("html_url") or GITHUB_RELEASES_URL)
        body = str(result.get("body") or "").strip() or self.text("update_placeholder_desc")
        if bool(result.get("is_newer")):
            title = self.text("update_available_desc", current=__version__, latest=latest)
            content = f"{self.text('update_changelog_title')}\n{body}"
            self.about_interface.set_update_result(title, content)
            if self.confirm_action(self.text("update_available_title"), f"{title}\n\n{self.text('open_release_prompt')}"):
                webbrowser.open_new_tab(release_url)
            return

        self.about_interface.set_update_result(
            self.text("no_update_title"),
            self.text("no_update_desc", current=__version__),
        )
        if manual:
            InfoBar.success(
                self.text("no_update_title"),
                self.text("no_update_desc", current=__version__),
                position=InfoBarPosition.TOP_RIGHT,
                parent=self,
            )

    def on_update_failed(self, result: dict[str, object]) -> None:
        self.update_check_running = False
        manual = bool(result.get("manual"))
        message = self.text("update_check_failed_desc", error=result.get("error", ""))
        if manual:
            self.about_interface.set_update_result(self.text("update_check_failed_title"), message)
            self.show_warning(self.text("update_check_failed_title"), message)

    def load_data(self) -> None:
        if not self.has_launch_dock():
            self.projects = []
            self.manage_mode = False
            self.selected_project_ids.clear()
            self.collapsed_project_ids.clear()
            self.link_manage_project_id = None
            self.selected_link_ids_by_project.clear()
            self.launch_interface.refresh(self.projects)
            self.dock_interface.refresh(None, self.storage.missing_dock_path)
            return
        try:
            self.storage.initialize()
            self.projects = self.storage.list_projects()
        except StorageError as exc:
            self.show_error(self.text("dock_error"), str(exc))
            self.projects = []
        valid_project_ids = {project.id for project in self.projects}
        self.selected_project_ids.intersection_update(valid_project_ids)
        self.collapsed_project_ids.intersection_update(valid_project_ids)
        if self.link_manage_project_id not in valid_project_ids:
            self.link_manage_project_id = None
        self.selected_link_ids_by_project = {
            project_id: link_ids
            for project_id, link_ids in self.selected_link_ids_by_project.items()
            if project_id in valid_project_ids
        }
        self.launch_interface.refresh(self.projects)
        self.dock_interface.refresh(self.storage.dock_path, self.storage.missing_dock_path)

    def set_manage_mode(self, enabled: bool) -> None:
        self.manage_mode = enabled
        if enabled:
            self.link_manage_project_id = None
            self.selected_link_ids_by_project.clear()
        if not enabled:
            self.selected_project_ids.clear()
        self.launch_interface.refresh(self.projects)

    def set_link_manage_project(self, project: Project | None) -> None:
        self.link_manage_project_id = project.id if project else None
        if project is None:
            self.selected_link_ids_by_project.clear()
        else:
            self.collapsed_project_ids.discard(project.id)
            self.manage_mode = False
            self.selected_project_ids.clear()
        self.launch_interface.refresh(self.projects)

    def toggle_link_selection(self, project: Project, link: Link, checked: bool) -> None:
        selected = self.selected_link_ids_by_project.setdefault(project.id, set())
        if checked:
            selected.add(link.id)
        else:
            selected.discard(link.id)

    def select_all_links(self, project: Project) -> None:
        self.selected_link_ids_by_project[project.id] = {link.id for link in project.links}
        self.launch_interface.refresh(self.projects)

    def clear_link_selection(self, project: Project) -> None:
        self.selected_link_ids_by_project[project.id] = set()
        self.launch_interface.refresh(self.projects)

    def invert_link_selection(self, project: Project) -> None:
        all_ids = {link.id for link in project.links}
        selected_ids = self.selected_link_ids_by_project.get(project.id, set())
        self.selected_link_ids_by_project[project.id] = all_ids - selected_ids
        self.launch_interface.refresh(self.projects)

    def delete_selected_links(self, project: Project) -> None:
        selected_ids = self.selected_link_ids_by_project.get(project.id, set())
        if not selected_ids:
            self.show_warning(self.text("not_selected_links_title"), self.text("not_selected_links_desc"))
            return
        selected_links = [link for link in project.links if link.id in selected_ids]
        names = "\n".join(f"- {link.name}" for link in selected_links[:8])
        if len(selected_links) > 8:
            names += "\n" + self.text("more_links", count=len(selected_links) - 8)
        if not self.confirm_action(
            self.text("delete_selected_links_title"),
            self.text("delete_selected_links_desc", count=len(selected_links), names=names),
        ):
            return
        project.links = [link for link in project.links if link.id not in selected_ids]
        project.normalize_link_order()
        self.selected_link_ids_by_project[project.id] = set()
        self.save_project(project)

    def toggle_project_selection(self, project: Project, checked: bool) -> None:
        if checked:
            self.selected_project_ids.add(project.id)
        else:
            self.selected_project_ids.discard(project.id)

    def select_all_projects(self) -> None:
        self.selected_project_ids = {project.id for project in self.projects}
        self.launch_interface.refresh(self.projects)

    def clear_project_selection(self) -> None:
        self.selected_project_ids.clear()
        self.launch_interface.refresh(self.projects)

    def invert_project_selection(self) -> None:
        all_ids = {project.id for project in self.projects}
        self.selected_project_ids = all_ids - self.selected_project_ids
        self.launch_interface.refresh(self.projects)

    def delete_selected_projects(self) -> None:
        selected_projects = [project for project in self.projects if project.id in self.selected_project_ids]
        if not selected_projects:
            self.show_warning(self.text("not_selected_projects_title"), self.text("not_selected_projects_desc"))
            return
        names = "\n".join(f"- {project.name}" for project in selected_projects[:8])
        if len(selected_projects) > 8:
            names += "\n" + self.text("more_projects", count=len(selected_projects) - 8)
        if not self.confirm_action(
            self.text("delete_selected_projects_title"),
            self.text("delete_selected_projects_desc", count=len(selected_projects), names=names),
        ):
            return
        for project in selected_projects:
            try:
                self.storage.delete_project(project)
            except StorageError as exc:
                self.show_error(self.text("delete_failed"), self.text("delete_project_failed", name=project.name, error=exc))
                break
        self.selected_project_ids.clear()
        self.projects = self.storage.list_projects()
        valid_project_ids = {project.id for project in self.projects}
        self.collapsed_project_ids.intersection_update(valid_project_ids)
        self.selected_link_ids_by_project = {
            project_id: link_ids
            for project_id, link_ids in self.selected_link_ids_by_project.items()
            if project_id in valid_project_ids
        }
        self.launch_interface.refresh(self.projects)

    def toggle_project_collapse(self, project: Project) -> None:
        if project.id in self.collapsed_project_ids:
            self.collapsed_project_ids.remove(project.id)
        else:
            self.collapsed_project_ids.add(project.id)
        self.launch_interface.refresh(self.projects)

    def add_project(self) -> None:
        if not self.has_launch_dock():
            self.show_warning(self.text("need_dock_title"), self.text("need_dock_desc"))
            return
        dialog = TextInputDialog(
            self.text("new_project_title"),
            self.text("project_name_prompt"),
            parent=self,
            save_text=self.text("dialog_save"),
            cancel_text=self.text("dialog_cancel"),
        )
        if not dialog.exec():
            return
        name = dialog.text_value()
        if not name:
            self.show_warning(self.text("need_name_title"), self.text("project_name_empty"))
            return
        try:
            project = self.storage.create_project(name)
        except StorageError as exc:
            self.show_error(self.text("create_failed"), str(exc))
            return
        self.projects = self.storage.list_projects()
        self.launch_interface.refresh(self.projects)
        InfoBar.success(self.text("create_success"), self.text("project_created", name=project.name), position=InfoBarPosition.TOP_RIGHT, parent=self)

    def rename_project(self, project: Project) -> None:
        dialog = TextInputDialog(
            self.text("edit_project_title"),
            self.text("project_name_prompt"),
            project.name,
            self,
            save_text=self.text("dialog_save"),
            cancel_text=self.text("dialog_cancel"),
        )
        if not dialog.exec():
            return
        name = dialog.text_value()
        if not name:
            self.show_warning(self.text("need_name_title"), self.text("project_name_empty"))
            return
        try:
            self.storage.rename_project(project, name)
            self.projects = self.storage.list_projects()
        except StorageError as exc:
            self.show_error(self.text("save_failed"), str(exc))
            return
        self.launch_interface.refresh(self.projects)
        self.dock_interface.refresh(self.storage.dock_path, self.storage.missing_dock_path)

    def delete_project(self, project: Project) -> None:
        if not self.confirm_action(self.text("delete_project_title"), self.text("delete_project_desc", name=project.name)):
            return
        try:
            self.storage.delete_project(project)
        except StorageError as exc:
            self.show_error(self.text("delete_failed"), str(exc))
            return
        self.projects = self.storage.list_projects()
        self.selected_project_ids.discard(project.id)
        self.collapsed_project_ids.discard(project.id)
        self.selected_link_ids_by_project.pop(project.id, None)
        if self.link_manage_project_id == project.id:
            self.link_manage_project_id = None
        self.launch_interface.refresh(self.projects)
        InfoBar.success(self.text("delete_success"), self.text("project_deleted", name=project.name), position=InfoBarPosition.TOP_RIGHT, parent=self)

    def add_link(self, project: Project) -> None:
        dialog = LinkDialog(self.text("add_link_title"), parent=self)
        if not dialog.exec():
            return
        values = dialog.values()
        if not self.validate_link_values(values):
            return
        project.links.append(
            Link.create(
                name=str(values["name"]),
                url=str(values["url"]),
                default_open=bool(values["default_open"]),
                order=len(project.links) + 1,
            )
        )
        self.save_project(project)

    def edit_link(self, project: Project, link: Link) -> None:
        dialog = LinkDialog(self.text("edit_link_title"), link=link, parent=self)
        if not dialog.exec():
            return
        values = dialog.values()
        if not self.validate_link_values(values):
            return
        link.name = str(values["name"])
        link.url = str(values["url"])
        link.default_open = bool(values["default_open"])
        self.save_project(project)

    def delete_link(self, project: Project, link: Link) -> None:
        if not self.confirm_action(self.text("delete_link_title"), self.text("delete_link_desc", name=link.name)):
            return
        project.links = [item for item in project.links if item.id != link.id]
        project.normalize_link_order()
        self.selected_link_ids_by_project.get(project.id, set()).discard(link.id)
        self.save_project(project)

    def toggle_link(self, project: Project, link: Link, checked: bool) -> None:
        link.default_open = checked
        self.save_project(project, refresh=False)
        self.launch_interface.refresh_project_count(project)

    def save_project(self, project: Project, refresh: bool = True) -> None:
        if not self.has_launch_dock():
            self.show_warning(self.text("need_dock_title"), self.text("need_dock_save_desc"))
            return
        try:
            self.storage.save_project(project)
            self.projects = self.storage.list_projects()
        except StorageError as exc:
            self.show_error(self.text("save_failed"), str(exc))
            return
        if refresh:
            self.launch_interface.refresh(self.projects)
        self.dock_interface.refresh(self.storage.dock_path, self.storage.missing_dock_path)

    def choose_dock(self) -> None:
        if self.storage.dock_path:
            start_path = str(self.storage.dock_path)
        elif self.storage.missing_dock_path and self.storage.missing_dock_path.parent.exists():
            start_path = str(self.storage.missing_dock_path.parent)
        else:
            start_path = str(Path.home())
        path = QFileDialog.getExistingDirectory(self, self.text("choose_dock_title"), start_path)
        if not path:
            return
        self.storage = DockStorage(Path(path))
        try:
            save_dock_path(self.storage.require_dock_path())
        except StorageError as exc:
            self.show_warning(self.text("config_save_failed"), self.text("dock_path_save_failed", error=exc))
        self.load_data()

    def launch_project(self, project: Project) -> None:
        targets = [link for link in sorted(project.links, key=lambda item: item.order) if link.default_open and link.url.strip()]
        if not targets:
            self.show_warning(self.text("no_launch_targets_title"), self.text("no_launch_targets_desc"))
            return
        invalid = [link.name for link in targets if not is_valid_target(link.url)]
        if invalid:
            self.show_warning(self.text("invalid_targets_title"), self.text("invalid_targets_desc", names="\n".join(invalid)))
            return
        for link in targets:
            open_target(link.url)
        InfoBar.success(self.text("launch_done_title"), self.text("launch_done_desc", count=len(targets)), position=InfoBarPosition.TOP_RIGHT, parent=self)

    def validate_link_values(self, values: dict[str, object]) -> bool:
        if not str(values["name"]).strip():
            self.show_warning(self.text("need_name_title"), self.text("link_name_required"))
            return False
        if not str(values["url"]).strip():
            self.show_warning(self.text("link_url_required_title"), self.text("link_url_required"))
            return False
        return True

    def confirm_action(self, title: str, content: str) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(content)
        box.setIcon(QMessageBox.Icon.NoIcon)
        icon = app_icon()
        if not icon.isNull():
            box.setWindowIcon(icon)
        box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        box.button(QMessageBox.StandardButton.Ok).setText(self.text("confirm_ok"))
        box.button(QMessageBox.StandardButton.Cancel).setText(self.text("confirm_cancel"))
        return box.exec() == QMessageBox.StandardButton.Ok

    def show_warning(self, title: str, content: str) -> None:
        InfoBar.warning(title, content, position=InfoBarPosition.TOP_RIGHT, duration=3500, parent=self)

    def show_error(self, title: str, content: str) -> None:
        InfoBar.error(title, content, position=InfoBarPosition.TOP_RIGHT, duration=5000, parent=self)


def clear_layout(layout: QVBoxLayout | QHBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget:
            widget.deleteLater()
        elif child_layout:
            clear_layout(child_layout)


def looks_like_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https", "file"} and bool(parsed.netloc or parsed.path)


def is_valid_target(value: str) -> bool:
    text = value.strip()
    if looks_like_url(text):
        return True
    return Path(text).expanduser().exists()


def open_target(value: str) -> None:
    text = value.strip()
    if looks_like_url(text):
        webbrowser.open_new_tab(text)
        return
    path = Path(text).expanduser()
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


@lru_cache(maxsize=1)
def app_icon() -> QIcon:
    if APP_ICON_PATH.exists():
        image = QImage(str(APP_ICON_PATH))
        if not image.isNull():
            return QIcon(QPixmap.fromImage(remove_solid_icon_background(image)))
    return QIcon()


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    icon = app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    window = LaunchDockApp()
    window.show()
    sys.exit(app.exec())
