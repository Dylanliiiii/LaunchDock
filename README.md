<div align="center">
  <h1 align="center">
    <img src="assets/icon.png" width="180" alt="LaunchDock logo" />
    <br />
    LaunchDock
  </h1>

  <p>
    一个本地轻量级启动坞，用于整理学习、工作和个人项目中的常用网页链接与本地文件，并一键进入对应工作状态。
    <br />
    A lightweight local launch dock for opening project links and files with one click.
  </p>

  <p><i>本地保存、用户自选启动坞路径、不绑定云服务。</i></p>
</div>

<div align="center">

![platform](https://img.shields.io/badge/platform-Windows-blue)
[![GitHub release](https://img.shields.io/github/v/release/Dylanliiiii/LaunchDock)](https://github.com/Dylanliiiii/LaunchDock/releases)
[![downloads](https://img.shields.io/github/downloads/Dylanliiiii/LaunchDock/total)](https://github.com/Dylanliiiii/LaunchDock/releases)
![python](https://img.shields.io/badge/Python-3.x-3776AB)
![UI](https://img.shields.io/badge/UI-PySide6%20%2B%20QFluentWidgets-00c8d7)

</div>

### 中文说明 | [English Readme](README_en.md) | [日本語 Readme](README_ja.md)

---

## 快速开始

1. 打开 [GitHub Releases](https://github.com/Dylanliiiii/LaunchDock/releases) 下载最新版。
2. 中国大陆无 VPN 用户建议下载 `LaunchDock-v版本号-windows-china-setup.exe`，更新源使用国内镜像。
3. 可正常访问 GitHub 的用户可以下载 `LaunchDock-v版本号-windows-global-setup.exe`。
4. 安装并启动后，首次使用需要创建或选择一个本地“启动坞”文件夹。

压缩包版本也会同时提供，文件名分别为：

- `LaunchDock-v版本号-windows-global.zip`
- `LaunchDock-v版本号-windows-china.zip`

## LaunchDock 可以做什么

- 创建多个学习、工作或个人项目。
- 每个项目保存多个网页链接、本地文件或文件夹路径。
- 为链接设置是否参与默认启动。
- 一键打开某个项目中已启用的全部启动项。
- 支持项目和启动项的添加、编辑、删除与批量管理。
- 支持自定义本地启动坞路径，数据保存在用户自己的文件夹中。
- 支持国际版 GitHub 更新源和国内版 CNB 更新源。

## 下载渠道

- GitHub Release：[https://github.com/Dylanliiiii/LaunchDock/releases](https://github.com/Dylanliiiii/LaunchDock/releases)
- CNB Release：[https://cnb.cool/DylanLIIIII/LaunchDock/-/releases](https://cnb.cool/DylanLIIIII/LaunchDock/-/releases)

国际版适合可以稳定访问 GitHub 的用户；国内版适合中国大陆无 VPN 用户，便于正常检查更新。

## 本地数据结构

LaunchDock 不把用户项目数据写进程序目录。用户需要选择一个本地文件夹作为启动坞根目录，推荐结构如下：

```text
用户选择的启动坞文件夹/
  launchdock.json
  projects/
    pytorch/
      project.json
    linear-algebra/
      project.json
```

- `launchdock.json` 保存全局配置，例如项目排序、最近打开项目和窗口设置。
- `projects/` 保存所有启动项目。
- 每个项目一个独立文件夹。
- 每个项目的链接数据保存在自己的 `project.json` 中。

## 项目源码结构

下面是仓库中主要目录和文件的用途，方便第一次阅读或参与开发时快速定位：

```text
LaunchDock/
  .agents/                 项目专属 Codex Skill，记录协作、开发和发布流程
  .github/workflows/       GitHub Actions 工作流，用于同步 CNB Release 等自动化流程
  assets/                  应用资源文件，目前主要保存软件图标
  build/                   打包过程生成的临时文件，不属于用户数据
  dist/                    Windows 压缩包和安装包等发布产物
  installer/               Inno Setup 安装包配置
  launchdock/              应用主代码包
  scripts/                 打包、安装包生成和 Release 同步脚本
  tests/                   自动化测试
  AGENTS.md                项目协作说明和产品/技术约定
  development-log.md       开发记录，每次代码或文档修改后都需要更新
  LaunchDock.spec          PyInstaller 打包配置
  main.py                  应用入口文件
  requirements.txt         Python 依赖列表
```

关键代码文件说明：

- `launchdock/app.py`：PySide6 + QFluentWidgets 图形界面，包含主窗口、项目卡片、启动项管理、设置页、关于页和各页面交互入口。
- `launchdock/i18n.py`：多语言文本、语言选项、主题选项和用户设置读写逻辑。
- `launchdock/updates.py`：版本比较、Git tag 解析、更新配置读取和 Release 检查逻辑。
- `launchdock/targets.py`：URL / 本地文件目标识别、校验和打开逻辑。
- `launchdock/icons.py`：应用图标加载，以及图标缺少透明通道时的临时纯色背景剔除逻辑。
- `launchdock/models.py`：项目和启动项的数据模型，定义项目名称、链接地址、是否默认启动、排序、创建时间和更新时间等结构。
- `launchdock/storage.py`：本地启动坞读写逻辑，负责 `launchdock.json`、`projects/<项目文件夹>/project.json`、项目文件夹命名、排序和持久化配置。
- `launchdock/__init__.py`：应用包基础信息，目前包含版本号。
- `main.py`：从源码运行时的轻量入口，会启动 LaunchDock 桌面应用。
- `tests/test_storage.py`：存储层、设置、启动目标和更新检查相关逻辑的单元测试。

打包与发布相关文件说明：

- `scripts/build-windows.ps1`：使用 PyInstaller 生成 Windows 绿色压缩包，并写入不同渠道的更新源配置。
- `scripts/build-installer.ps1`：调用 Inno Setup 6 生成 Windows 安装包。
- `scripts/sync-cnb-release.ps1`：在需要时同步 GitHub Release 附件到 CNB Release。
- `installer/launchdock.iss`：Inno Setup 安装包脚本模板。
- `.github/workflows/sync-cnb-release.yml`：GitHub Release 发布或编辑后同步 CNB Release 的工作流。

`build/`、`dist/` 和 `__pycache__/` 都是本地生成内容；其中 `dist/` 用于保存发布产物，`build/` 和 `__pycache__/` 通常不需要手动维护。

## 从源码运行

建议使用 Python 虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m launchdock.app
```

## Windows 打包

项目提供 Windows 打包脚本：

```powershell
.\scripts\build-windows.ps1
```

打包脚本会从 `assets/icon.png` 临时派生打包所需图标，不会覆盖原始图标源文件。

国内版打包示例：

```powershell
.\scripts\build-windows.ps1 `
  -UpdateChannel china `
  -UpdateRepoUrl "国内镜像仓库地址" `
  -ReleasePageUrl "国内下载页面地址"
```

安装包使用 Inno Setup 6：

```powershell
.\scripts\build-installer.ps1
```

正式发布产物位于 `dist/v版本号/`，不同版本会分目录保存。

## 发布说明

正式发布时需要同时提供：

- 国际版压缩包：`LaunchDock-v版本号-windows-global.zip`
- 国内版压缩包：`LaunchDock-v版本号-windows-china.zip`
- 国际版安装包：`LaunchDock-v版本号-windows-global-setup.exe`
- 国内版安装包：`LaunchDock-v版本号-windows-china-setup.exe`

Release 正文应说明国际版更新源为 GitHub，国内版更新源为 CNB 等国内镜像；中国大陆无 VPN 用户建议下载国内版。

## 开发说明

- UI 层主入口和页面组件位于 `launchdock/app.py`。
- 多语言、更新检查、启动目标处理和图标处理分别位于 `launchdock/i18n.py`、`launchdock/updates.py`、`launchdock/targets.py` 和 `launchdock/icons.py`。
- 业务模型位于 `launchdock/models.py`。
- 本地存储逻辑位于 `launchdock/storage.py`。
- 项目协作约定见 `AGENTS.md`。
- 每次修改代码或文档后，需要同步更新 `development-log.md`，并检查 README、项目协作说明和相关 Skill 是否也需要同步。

## License

本项目使用 AGPL-3.0 license。
