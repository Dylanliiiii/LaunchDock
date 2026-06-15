<div align="center">
  <h1 align="center">
    <img src="assets/icon.png" width="180" alt="LaunchDock logo" />
    <br />
    LaunchDock
  </h1>

  <p>
    A lightweight local launch dock for organizing project links, local files, and folders, then opening everything you need with one click.
    <br />
    一个本地轻量级启动坞，用于一键进入学习、工作或个人项目状态。
  </p>

  <p><i>Local-first, user-selected storage, no cloud account required.</i></p>
</div>

<div align="center">

![platform](https://img.shields.io/badge/platform-Windows-blue)
[![GitHub release](https://img.shields.io/github/v/release/Dylanliiiii/LaunchDock)](https://github.com/Dylanliiiii/LaunchDock/releases)
[![downloads](https://img.shields.io/github/downloads/Dylanliiiii/LaunchDock/total)](https://github.com/Dylanliiiii/LaunchDock/releases)
![python](https://img.shields.io/badge/Python-3.x-3776AB)
![UI](https://img.shields.io/badge/UI-PySide6%20%2B%20QFluentWidgets-00c8d7)

</div>

### [中文说明](README.md) | English Readme | [日本語 Readme](README_ja.md)

---

## Quick Start

1. Open [GitHub Releases](https://github.com/Dylanliiiii/LaunchDock/releases) and download the latest version.
2. If you are in mainland China and cannot access GitHub reliably, download `LaunchDock-vVERSION-windows-china-setup.exe`.
3. If GitHub access is stable for you, download `LaunchDock-vVERSION-windows-global-setup.exe`.
4. After installation, create or select a local dock folder on first launch.

Portable zip packages are also provided:

- `LaunchDock-vVERSION-windows-global.zip`
- `LaunchDock-vVERSION-windows-china.zip`

## What LaunchDock Does

- Create multiple study, work, or personal project modules.
- Save web links, local files, and folder paths for each project.
- Choose which items are opened by default.
- Launch all enabled items in a project with one click.
- Add, edit, delete, and batch-manage projects and launch items.
- Keep user data in a local dock folder selected by the user.
- Support both GitHub update sources and China-friendly CNB update sources.

## Download Channels

- GitHub Releases: [https://github.com/Dylanliiiii/LaunchDock/releases](https://github.com/Dylanliiiii/LaunchDock/releases)
- CNB Releases: [https://cnb.cool/DylanLIIIII/LaunchDock/-/releases](https://cnb.cool/DylanLIIIII/LaunchDock/-/releases)

The global package is intended for users who can access GitHub reliably. The China package uses a domestic update source and is recommended for mainland China users without a VPN.

## Local Data Structure

LaunchDock does not store user project data inside the application directory. Users select a local folder as the dock root:

```text
Selected dock folder/
  launchdock.json
  projects/
    pytorch/
      project.json
    linear-algebra/
      project.json
```

- `launchdock.json` stores global settings such as project order, recent project, and window settings.
- `projects/` stores all project modules.
- Each project has its own folder.
- Each project stores its links in `project.json`.

## Run from Source

A Python virtual environment is recommended:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m launchdock.app
```

## Build Windows Packages

Build the Windows package:

```powershell
.\scripts\build-windows.ps1
```

The build script derives temporary package icons from `assets/icon.png` and does not overwrite the original source icon.

Example for the China package:

```powershell
.\scripts\build-windows.ps1 `
  -UpdateChannel china `
  -UpdateRepoUrl "domestic mirror repository url" `
  -ReleasePageUrl "domestic download page url"
```

Build the installer with Inno Setup 6:

```powershell
.\scripts\build-installer.ps1
```

Release artifacts are stored under `dist/vVERSION/`.

## Release Notes

Each official release should provide:

- Global zip: `LaunchDock-vVERSION-windows-global.zip`
- China zip: `LaunchDock-vVERSION-windows-china.zip`
- Global installer: `LaunchDock-vVERSION-windows-global-setup.exe`
- China installer: `LaunchDock-vVERSION-windows-china-setup.exe`

The release body should note that the global package uses GitHub as the update source, while the China package uses CNB or another domestic mirror.

## Development Notes

- UI layer: `launchdock/app.py`
- Business models: `launchdock/models.py`
- Local storage: `launchdock/storage.py`
- Collaboration rules: `AGENTS.md`
- Update `development-log.md` whenever code or documentation changes.

## License

This project is licensed under the AGPL-3.0 license.
