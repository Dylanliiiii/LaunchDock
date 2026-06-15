# LaunchDock

LaunchDock 是一个本地轻量级“启动坞”，用于管理学习、工作或个人项目中的常用网页链接，并支持一键打开某个项目所需的全部默认链接。

## 主要功能

- 创建、重命名、删除项目。
- 创建项目时可以先不添加链接，之后再补充。
- 为每个项目添加多个链接。
- 编辑链接名称、URL 和是否默认启动。
- 删除链接、调整链接顺序。
- 一键打开当前项目的默认启动网页链接或本地文件路径。
- 支持创建或选择自定义启动坞文件夹。
- 所有项目以独立文件夹保存在启动坞中，方便备份和迁移。
- 首次使用时不会自动创建默认路径，需要用户先创建启动坞，再创建启动项目。

## 界面风格

当前界面基于 PySide6 + QFluentWidgets，采用深色 Windows 11 / WinUI 风格：

- 左侧为垂直导航栏，包含图标和文字。
- 右侧为设置页式主区域。
- 标题栏显示为 `LaunchDock`。
- 启动项目以卡片形式排列。
- 项目卡片内展示启动项，每个启动项右侧有启用开关、编辑图标和删除图标。
- 项目卡片支持折叠和展开启动项。
- 顶部提供“管理项目”入口，可勾选多个启动项目，并支持全选、取消全选、反选和批量删除。
- 每个项目卡片提供“管理启动项”入口，可勾选该项目内多个启动项，并支持全选、取消全选、反选和批量删除。
- 右上角提供“新建”按钮。
- 青色用于强调色，例如主要按钮和启用状态。

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 运行方式

```bash
python main.py
```

## Windows 打包

首次打包前需要安装 PyInstaller：

```bash
python -m pip install pyinstaller
```

打包当前版本的国际版：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1 -Version v1.1.0 -UpdateChannel global
```

打包产物会生成到 `dist/v1.1.0/LaunchDock-v1.1.0-windows-global.zip`。脚本会从 `assets/icon.png` 临时派生 `build/launchdock.ico`，不会覆盖或修改原始图标文件，也不会包含用户本机的启动坞数据。

如果需要生成国内用户使用的版本，可以在打包时写入国内更新仓库地址。程序会优先通过 Git tag 检查新版本，不依赖 GitHub Release API：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1 -Version v1.1.0 -UpdateChannel china -UpdateRepoUrl https://cnb.cool/DylanLIIIII/LaunchDock.git -ReleasePageUrl https://cnb.cool/DylanLIIIII/LaunchDock/-/releases
```

国内版打包产物会生成到 `dist/v1.1.0/LaunchDock-v1.1.0-windows-china.zip`。国际版默认使用 GitHub 仓库作为更新源；国内版建议将同一份发布仓库同步到 CNB 等国内可访问平台。

如需生成 Windows 安装包，需要先安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)，然后运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-installer.ps1 -Version 1.1.0 -UpdateChannel global
powershell -ExecutionPolicy Bypass -File scripts\build-installer.ps1 -Version 1.1.0 -UpdateChannel china -UpdateRepoUrl https://cnb.cool/DylanLIIIII/LaunchDock.git -ReleasePageUrl https://cnb.cool/DylanLIIIII/LaunchDock/-/releases
```

安装包适合在 GitHub Release 中提供给普通用户直接安装，可以创建开始菜单、桌面快捷方式和卸载入口。安装包文件名同样会区分渠道，例如 `LaunchDock-v1.1.0-windows-global-setup.exe` 和 `LaunchDock-v1.1.0-windows-china-setup.exe`。

## 发布 Release

发布前先确认：

- `launchdock/__init__.py` 中的 `__version__` 已更新。
- `development-log.md` 顶部已经添加 `## Version x.x.x - 时间` 正式发布记录。
- 已运行基础验证：`python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py` 和 `python -m unittest discover -s tests`。
- 已使用 `scripts\build-windows.ps1 -UpdateChannel global` 生成国际版 Windows 压缩包。
- 已使用 `scripts\build-windows.ps1 -UpdateChannel china` 和国内更新仓库地址生成国内版 Windows 压缩包，并确认对应 Git tag 已同步到国内镜像仓库。
- 如发布安装版，已使用 `scripts\build-installer.ps1` 生成 Windows 安装包。
- GitHub Actions 中已配置 `GIT_PASSWORD` secret，作为 CNB token 使用；GitHub Release 发布或编辑后，`Sync CNB Release` 工作流会尝试自动创建/更新 CNB Release 并同步附件。

GitHub Release 标题建议使用 `LaunchDock v1.0.0`。Release 正文应从上一个 `Version` 发布记录之后到本次发布记录之间提炼重点，保持简短；小型格式、文案和布局调整可以概括为“界面细节优化”。

如果 CNB Release 同步失败，可以在 GitHub Actions 中手动运行 `Sync CNB Release`，输入需要同步的 tag（例如 `v1.1.2`）重试。该流程只从 GitHub Secrets 读取 CNB token，不能把 token 写入仓库文件或日志。

Release 资产建议同时上传国际版和国内版，并在正文中说明：

```text
下载说明：

- 国际版：`LaunchDock-v版本号-windows-global.zip`，更新源为 GitHub，适合能稳定访问 GitHub 的用户。
- 国内版：`LaunchDock-v版本号-windows-china.zip`，更新源为 CNB 国内镜像，适合中国大陆网络环境。

如果你在国内且没有 VPN，建议下载国内版，以便后续能够正常自动检查更新。
```

`v1.0.0` 首次发布正文建议：

```text
首次正式发布 LaunchDock。

- 支持创建启动坞，并在本地保存多个启动项目。
- 支持为项目添加、编辑、删除启动项，并一键打开启用的网页链接或本地文件。
- 支持项目和启动项管理模式，可批量选择和删除。
- 提供深色 Fluent 风格界面、关于页、版本检查入口和基础多语言界面。
```

## 应用图标

应用图标文件为 `assets/icon.png`。当前运行时会将它设置为窗口图标；后续打包为桌面软件时，也应继续使用该文件作为软件图标源。图标源推荐使用带透明通道的 PNG；如果源图缺少透明通道，程序运行时会尝试基于角落背景色临时剔除纯色背景，但不会修改原始图标文件。

## 启动坞结构

首次运行时，程序不会自动创建默认路径。用户需要先在窗口中点击“创建 / 选择启动坞”，选择一个本地文件夹作为启动坞。启动坞用于保存启动项目的存储位置；没有启动坞时，不能创建启动项目。

启动坞结构示例：

```text
用户选择的启动坞文件夹/
  launchdock.json
  projects/
    pytorch/
      project.json
```

程序自身配置保存在用户主目录的 `.launchdock/config.json` 中，用于记住启动坞路径。开源仓库内不会写死任何开发者本机路径。

## 开发说明

- 项目协作规则见 `AGENTS.md`。
- 项目专属 Skill 见 `.agents/skills/launchdock-project/SKILL.md`。
- 每次生成或修改代码后，需要同步更新 `development-log.md`。
