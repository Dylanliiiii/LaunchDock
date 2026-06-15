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

- UI 层集中在 `launchdock/app.py`。
- 业务模型位于 `launchdock/models.py`。
- 本地存储逻辑位于 `launchdock/storage.py`。
- 项目协作约定见 `AGENTS.md`。
- 每次修改代码或文档后，需要同步更新 `development-log.md`。

## License

本项目使用 AGPL-3.0 license。
