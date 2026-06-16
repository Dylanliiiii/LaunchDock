---
name: launchdock-release
description: 仅用于 LaunchDock 项目的更新、推送、打包和双平台发布流程。用于用户要求更新代码后推送 GitHub、发布新版本、打包 release、创建 GitHub/CNB Release、同步双端更新源、处理 PyInstaller/Inno Setup 构建产物、生成手动发布说明；当用户的“更新”“发版”“release”“打包”“push GitHub”意图不明确时，也用于判断是否必须先向用户确认。
---

# LaunchDock 更新与发布技能

## 核心原则

- 只服务当前 LaunchDock 仓库，不作为全局通用发布流程。
- 普通代码或文档更新完成后，验证通过就提交并 push 到 GitHub。
- 只有用户明确要求“release / 发版 / 发布新版本 / 打包 release / 打包安装包 / 上新版本”时，才执行完整 release 流程。
- 如果用户只说“更新一下”“更新 GitHub”“更新版本”等模糊表达，且无法判断是普通 push 还是正式 release，必须先向用户确认。
- 自动 release 仍是默认目标；如果上传或同步在同一位置卡住或失败，最多尝试两次。两次后停止自动上传，告知用户需要手动在 GitHub 和 CNB 发布，并给出可复制的版本号、标题、正文和附件清单。
- 不把 token、cookie、账号密码写入仓库、日志、Release 正文或开发记录。

## 意图判断

按以下规则处理用户请求：

- “修改代码”“修复问题”“美化 README”“更新到 GitHub”“push 一下”：实现、验证、commit、push，不升版本号，不打包，不创建 Release。
- “更新 release”“打包 release”“发布新版”“发版”“上架新版本”“生成安装包并发布”：执行完整 release 流程。
- “更新版本”：如果上下文不能明确是只改代码还是正式发版，先问用户是“只 push GitHub”还是“打包并发布 Release”。
- 用户明确说“先不用 release”：只 push，不创建 tag，不上传附件。
- 用户明确说“我已经手动 release”：不要重复上传；只检查或修复必要的仓库流程，并给出后续手动材料。

## 项目链接

- GitHub 仓库：`https://github.com/Dylanliiiii/LaunchDock`
- GitHub Releases：`https://github.com/Dylanliiiii/LaunchDock/releases`
- GitHub Actions：`https://github.com/Dylanliiiii/LaunchDock/actions`
- GitHub CNB 同步工作流：`https://github.com/Dylanliiiii/LaunchDock/actions/workflows/sync-cnb-release.yml`
- CNB 仓库：`https://cnb.cool/DylanLIIIII/LaunchDock`
- CNB Releases：`https://cnb.cool/DylanLIIIII/LaunchDock/-/releases`
- CNB tag Release 链接格式：`https://cnb.cool/DylanLIIIII/LaunchDock/-/releases/tag/v版本号`
- CNB API Base：`https://api.cnb.cool`

## 技术栈与发布依赖

- 主程序：Python。
- UI：PySide6 + QFluentWidgets。
- 打包：PyInstaller，由 `scripts/build-windows.ps1` 调用。
- 安装包：Inno Setup 6，由 `scripts/build-installer.ps1` 调用。
- 国际版更新源：GitHub Git tags，Release API 作为可选兜底。
- 国内版更新源：CNB Git tags，避免中国大陆用户必须访问 GitHub API。
- 更新配置：打包时生成 `build/update-config.json` 并写入产物。
- GitHub Release 同步 CNB：优先使用 `.github/workflows/sync-cnb-release.yml`；本地兜底脚本为 `scripts/sync-cnb-release.ps1`。

### Inno Setup 路径

`scripts/build-installer.ps1` 会按以下顺序寻找 Inno Setup Compiler：

1. PATH 中的 `ISCC.exe`。
2. `$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe`。
3. `$env:ProgramFiles\Inno Setup 6\ISCC.exe`。
4. 如果仍找不到，使用 `-InnoSetupCompiler "实际ISCC.exe路径"` 手动传入。

本机检查记录：2026-06-15 确认 `E:\Apps_Work\Inno Setup 6\ISCC.exe` 存在。该路径不是脚本默认候选路径；生成安装包时如果自动发现失败，应显式传入：

```powershell
.\scripts\build-installer.ps1 -Version 版本号 -UpdateChannel global -InnoSetupCompiler "E:\Apps_Work\Inno Setup 6\ISCC.exe"
```

## 普通更新流程

用于非 release 的代码或文档更新：

1. 读取 `AGENTS.md` 和相关 Skill。
2. 修改代码或文档。
3. 同步更新 `development-log.md`；日常更新标题使用普通时间，不写 `Version x.x.x`。
4. 如果代码结构、入口命令、模块职责、打包流程或功能行为有变化，检查并同步更新 README、`AGENTS.md`、项目专属 Skill、打包脚本说明和其他相关文档。
5. 运行与改动风险匹配的验证。
6. 检查 `git status --short` 和关键 diff。
7. `git add`、`git commit`。
8. `git push origin main`。如果遇到 safe.directory 问题，使用：

```powershell
git -c safe.directory=<仓库绝对路径> push origin main
```

普通更新不创建 tag，不构建 `dist/v版本号/`，不创建 GitHub/CNB Release。

## Release 流程

### 1. 确认版本号

按语义化版本选择：

- 修复 bug：修订号，例如 `1.1.4` -> `1.1.5`。
- 新功能：次版本号，例如 `1.1.4` -> `1.2.0`。
- 不兼容大改：主版本号，例如 `1.1.4` -> `2.0.0`。

如果不确定版本级别，先向用户确认。

### 2. 更新版本文件和开发记录

- 更新 `launchdock/__init__.py` 的 `__version__`。
- 在 `development-log.md` 顶部新增：

```markdown
## Version x.x.x - YYYY-MM-DD HH:mm:ss +08:00
```

- Release 正文从上一次 `Version` 记录之后到本次记录之间提炼重点。

### 3. 验证

至少运行：

```powershell
python -m unittest discover -s tests
python -m compileall launchdock
```

根据改动范围补充 UI、打包或手动验证。

### 4. 构建国际版和国内版

压缩包：

```powershell
.\scripts\build-windows.ps1 -Version v版本号 -UpdateChannel global
.\scripts\build-windows.ps1 -Version v版本号 -UpdateChannel china -UpdateRepoUrl "https://cnb.cool/DylanLIIIII/LaunchDock.git" -ReleasePageUrl "https://cnb.cool/DylanLIIIII/LaunchDock/-/releases"
```

安装包：

```powershell
.\scripts\build-installer.ps1 -Version 版本号 -UpdateChannel global
.\scripts\build-installer.ps1 -Version 版本号 -UpdateChannel china -UpdateRepoUrl "https://cnb.cool/DylanLIIIII/LaunchDock.git" -ReleasePageUrl "https://cnb.cool/DylanLIIIII/LaunchDock/-/releases"
```

如果找不到 Inno Setup：

```powershell
.\scripts\build-installer.ps1 -Version 版本号 -UpdateChannel global -InnoSetupCompiler "实际ISCC.exe路径"
```

### 5. 检查产物

确认 `dist/v版本号/` 至少包含：

- `LaunchDock-v版本号-windows-global.zip`
- `LaunchDock-v版本号-windows-china.zip`
- `LaunchDock-v版本号-windows-global-setup.exe`
- `LaunchDock-v版本号-windows-china-setup.exe`

检查压缩包内的 `update-config.json`：

- global 指向 `https://github.com/Dylanliiiii/LaunchDock.git` 和 GitHub Releases。
- china 指向 `https://cnb.cool/DylanLIIIII/LaunchDock.git` 和 CNB Releases。
- 不包含用户启动坞数据、本机配置文件或 token。

### 6. 提交、推送和 tag

```powershell
git status --short
git add launchdock/__init__.py development-log.md 其他修改文件
git commit -m "chore: release v版本号"
git push origin main
git tag v版本号
git push origin v版本号
```

如遇 safe.directory，给 Git 命令追加：

```powershell
-c safe.directory=<仓库绝对路径>
```

### 7. 自动创建 GitHub Release

优先使用 GitHub CLI：

```powershell
gh release create v版本号 `
  "dist/v版本号/LaunchDock-v版本号-windows-global.zip" `
  "dist/v版本号/LaunchDock-v版本号-windows-china.zip" `
  "dist/v版本号/LaunchDock-v版本号-windows-global-setup.exe" `
  "dist/v版本号/LaunchDock-v版本号-windows-china-setup.exe" `
  --title "LaunchDock v版本号" `
  --notes-file "release-notes-v版本号.md"
```

如果 `gh` 未登录，提示开发者运行 `gh auth login`。登录后继续，不要改用不明来源 token。

### 8. 同步 CNB Release

优先等待 GitHub Actions 的 `Sync CNB Release` 工作流自动同步。

如果需要本地兜底，使用 `CNB_TOKEN` 环境变量调用：

```powershell
.\scripts\sync-cnb-release.ps1 `
  -TagName "v版本号" `
  -Title "LaunchDock v版本号" `
  -BodyFile "release-notes-v版本号.md" `
  -Assets @(
    "dist/v版本号/LaunchDock-v版本号-windows-global.zip",
    "dist/v版本号/LaunchDock-v版本号-windows-china.zip",
    "dist/v版本号/LaunchDock-v版本号-windows-global-setup.exe",
    "dist/v版本号/LaunchDock-v版本号-windows-china-setup.exe"
  )
```

不要把 `CNB_TOKEN` 写入命令历史可见输出、仓库文件或日志。

## 上传失败处理

- 对同一个上传或同步动作最多尝试两次。
- 如果第二次仍卡住、超时或失败，立即停止自动上传。
- 不要反复创建重复 Release 或重复上传同名资产。
- 告诉开发者需要手动在 GitHub 和 CNB 创建或更新 Release。
- 必须给出手动发布材料，方便复制。

手动发布材料模板：

```markdown
版本号：v版本号
Release title：LaunchDock v版本号
Target：main / 提交哈希

Release 正文：
下载说明：
- 国际版：更新源为 GitHub，适合可以稳定访问 GitHub 的用户。
- 国内版：更新源为 CNB，适合中国大陆无 VPN 用户。

更新内容：
- ...
- ...

需要上传的附件：
- dist/v版本号/LaunchDock-v版本号-windows-global.zip
- dist/v版本号/LaunchDock-v版本号-windows-china.zip
- dist/v版本号/LaunchDock-v版本号-windows-global-setup.exe
- dist/v版本号/LaunchDock-v版本号-windows-china-setup.exe

GitHub Release：
https://github.com/Dylanliiiii/LaunchDock/releases/tag/v版本号

CNB Release：
https://cnb.cool/DylanLIIIII/LaunchDock/-/releases/tag/v版本号
```

## Release 正文要求

正文保持简短，优先写用户能理解的变化：

- 修复了什么问题。
- 新增了什么用户可见能力。
- 国内版和国际版下载建议。
- 如果更新检查相关逻辑有变化，明确说明国际版和国内版的更新源。

不要把内部调试日志、token、绝对本机路径、无关重构细节写进 Release 正文。

## 收尾检查

完成普通更新或 release 后：

- 确认 `git status --short` 为空，除非明确说明剩余文件。
- 确认 README、`AGENTS.md`、项目专属 Skill、打包脚本说明等相关文档没有因本次代码结构、入口命令、模块职责、打包流程或功能行为变化而过期。
- 把 commit、tag、push、Release URL 或手动发布材料告诉开发者。
- 如果本次没有运行某项验证，说明原因。
