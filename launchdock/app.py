from __future__ import annotations

import json
import sys
import webbrowser
from threading import Thread
from pathlib import Path
from urllib.error import HTTPError, URLError

from PySide6.QtCore import QObject, QTimer, Qt, Signal
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
    TitleLabel,
    TransparentPushButton,
    TransparentToolButton,
    setTheme,
    setThemeColor,
)

from .icons import app_icon
from .i18n import load_user_settings, language_options, save_user_setting, theme_from_setting, theme_options, tr
from .models import Link, Project
from .storage import DockStorage, StorageError, save_dock_path
from .targets import is_valid_target, looks_like_url, open_target
from .updates import GITHUB_REPO_URL, fetch_latest_release, release_page_url
from . import __version__

ACCENT_COLOR = "#00c8d7"
NAVIGATION_EXPAND_MIN_WIDTH = 176
NAVIGATION_EXPAND_MAX_WIDTH = 280
NAVIGATION_TEXT_EXTRA_WIDTH = 118


class UpdateSignals(QObject):
    checked = Signal(dict)
    failed = Signal(dict)


def is_checked_state(state: object) -> bool:
    return state == Qt.CheckState.Checked or state == Qt.CheckState.Checked.value


def set_switch_checked_without_animation(switch: SwitchButton, checked: bool) -> None:
    switch.setChecked(checked)
    switch.indicator.slideAni.stop()
    switch.indicator.setSliderX(25 if checked else 5)



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
        launch_button = TransparentToolButton(FluentIcon.PLAY_SOLID, row)
        launch_button.clicked.connect(lambda _=False, l=link: self.app_window.launch_link(l))
        switch = SwitchButton(row)
        switch.setOnText("")
        switch.setOffText("")
        set_switch_checked_without_animation(switch, link.default_open)
        switch.checkedChanged.connect(lambda checked, p=project, l=link: self.app_window.toggle_link(p, l, checked))

        layout.addWidget(launch_button)
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
        self.update_title.setText(self.app_window.text("checking_update_title"))
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
        self.auto_update_switch = SwitchButton(self)
        self.theme_key_by_text: dict[str, str] = {}
        self.language_key_by_text: dict[str, str] = {}

        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        self.auto_update_switch.checkedChanged.connect(self.on_auto_update_changed)

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
        layout.addWidget(
            self.setting_card(
                icon=FluentIcon.SYNC,
                title=self.app_window.text("auto_check_updates"),
                description=self.app_window.text("auto_check_updates_desc"),
                control=self.auto_update_switch,
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
        self.auto_update_switch.blockSignals(True)
        self.theme_combo.clear()
        self.language_combo.clear()
        self.theme_combo.addItems(list(theme_items.values()))
        self.language_combo.addItems(list(language_items.values()))
        self.theme_combo.setCurrentText(theme_items[settings["theme"]])
        self.language_combo.setCurrentText(language_items[settings["language"]])
        set_switch_checked_without_animation(self.auto_update_switch, bool(settings["auto_check_updates"]))
        self.theme_combo.blockSignals(False)
        self.language_combo.blockSignals(False)
        self.auto_update_switch.blockSignals(False)

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

    def on_auto_update_changed(self, checked: bool) -> None:
        self.app_window.update_auto_check_updates_setting(checked)


class LaunchDockApp(FluentWindow):
    def __init__(self) -> None:
        super().__init__()
        self.user_settings = load_user_settings()
        setTheme(theme_from_setting(str(self.user_settings["theme"])))
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
        QTimer.singleShot(0, lambda: self.navigationInterface.expand(False))
        if self.should_auto_check_updates():
            QTimer.singleShot(1200, lambda: self.check_for_updates(manual=False))

    def has_launch_dock(self) -> bool:
        return self.storage.dock_path is not None

    def text(self, key: str, **kwargs: object) -> str:
        return tr(str(self.user_settings["language"]), key, **kwargs)

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

    def update_auto_check_updates_setting(self, checked: bool) -> None:
        self.user_settings["auto_check_updates"] = checked
        try:
            save_user_setting("auto_check_updates", checked)
        except StorageError as exc:
            self.show_warning(self.text("settings_save_failed"), self.text("auto_update_save_failed", error=exc))

    def should_auto_check_updates(self) -> bool:
        return bool(self.user_settings.get("auto_check_updates", True))

    def open_github(self) -> None:
        webbrowser.open_new_tab(GITHUB_REPO_URL)

    def copy_download_link(self) -> None:
        QApplication.clipboard().setText(release_page_url())
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
        self.about_interface.set_checking()

        def worker() -> None:
            try:
                result = fetch_latest_release()
                result["manual"] = manual
                self.update_signals.checked.emit(result)
            except (HTTPError, URLError, OSError, json.JSONDecodeError, ValueError) as exc:
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
        release_url = str(result.get("html_url") or release_page_url())
        if str(result.get("source") or "") == "git":
            body = self.text("git_update_notes")
        else:
            body = str(result.get("body") or "").strip() or self.text("empty_release_notes")
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
        self.about_interface.set_update_result(self.text("update_check_failed_title"), message)
        if manual:
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
        self.collapsed_project_ids.update(valid_project_ids)
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
        self.collapsed_project_ids.add(project.id)
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

    def launch_link(self, link: Link) -> None:
        if not link.url.strip() or not is_valid_target(link.url):
            self.show_warning(self.text("invalid_targets_title"), self.text("invalid_targets_desc", names=link.name))
            return
        open_target(link.url)
        InfoBar.success(self.text("launch_done_title"), self.text("launch_done_desc", count=1), position=InfoBarPosition.TOP_RIGHT, parent=self)

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


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    icon = app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    window = LaunchDockApp()
    window.show()
    sys.exit(app.exec())
