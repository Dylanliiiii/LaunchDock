# Development Log

## Version 1.1.3 - 2026-06-15 18:41:15 +08:00

### 修改范围

- 自动检查更新设置
- 设置页开关显示修复
- Windows 打包发布

### 涉及文件

- `launchdock/__init__.py`
- `launchdock/app.py`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 将版本号更新为 `v1.1.3`，作为自动检查更新设置和开关显示问题的修订版。
- 设置页新增“自动检查更新”开关，用户可以关闭启动后的自动检查，避免每次打开软件都弹出新版本提示。
- 保留关于页“检查新版本”按钮的手动检查能力，关闭自动检查后仍可手动检测更新并弹窗提示。
- 修复“自动检查更新”开关开启时滑块颜色正确但右侧文字仍显示 `Off` 的问题。
- 自动检查更新设置会保存到本地配置，重启后继续生效。

### 验证情况

- 已运行 `python -m unittest tests.test_storage`。
- 已运行 `python -m compileall launchdock`。
- 已运行 Qt offscreen 冒烟测试，确认自动检查更新开关默认开启时显示 `On`，关闭后显示 `Off`，重新加载开启配置后仍显示 `On`。
- 已生成 `dist/v1.1.3/LaunchDock-v1.1.3-windows-global.zip` 和 `dist/v1.1.3/LaunchDock-v1.1.3-windows-china.zip`。
- 已生成 `dist/v1.1.3/LaunchDock-v1.1.3-windows-global-setup.exe` 和 `dist/v1.1.3/LaunchDock-v1.1.3-windows-china-setup.exe`。
- 已检查两个压缩包内置 `update-config.json`，均为无 BOM 的 UTF-8，且国际版指向 GitHub、国内版指向 CNB。
- 已检查两个压缩包没有包含用户本机启动坞数据。

## 2026-06-15 18:35:30 +08:00

### 修改范围

- 设置页自动检查更新开关显示
- 通用开关状态同步

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 修复设置页“自动检查更新”开关在开启状态下滑块颜色正确但右侧文字仍显示 `Off` 的问题。
- 调整开关状态同步 helper，优先调用 `SwitchButton.setChecked()`，让 QFluentWidgets 同步控件内部文本，再停止动画并设置滑块位置。
- 该修复同样适用于启动项列表中复用同一 helper 的开关初始化。

### 验证情况

- 已运行 Qt offscreen 冒烟测试，确认首次默认开启时开关文字显示为 `On`，关闭后显示为 `Off`，重新加载开启配置后仍显示 `On`。
- 已运行 `python -m unittest tests.test_storage`。
- 本次为日常修复，未更新项目版本号，也未发布 Release。

## 2026-06-15 18:27:52 +08:00

### 修改范围

- 自动检查更新设置
- 设置页界面
- 设置持久化测试

### 涉及文件

- `launchdock/app.py`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 在设置页新增“自动检查更新”开关，默认开启，关闭后应用启动时不再自动检查更新。
- 自动检查更新开关写入本地 `settings.auto_check_updates` 配置，重启后继续生效。
- 保留关于页“检查新版本”按钮的手动检查能力，关闭自动检查后手动点击仍会正常检测并在发现新版本时弹窗提示。
- 新增多语言文案，覆盖自动检查更新开关标题、说明和保存失败提示。
- 新增测试覆盖自动检查更新设置的默认值、保存值和非法配置兜底。

### 验证情况

- 已运行 `python -m unittest tests.test_storage`。
- 已运行 Qt offscreen 冒烟测试，确认设置页自动检查更新开关可以创建，默认值为开启，关闭后可写入临时配置。
- 本次为日常开发修改，未更新项目版本号，也未发布 Release。

## 2026-06-15 18:09:50 +08:00

### 修改范围

- CNB Release 自动同步
- GitHub Actions 发布流程
- 发布文档

### 涉及文件

- `.github/workflows/sync-cnb-release.yml`
- `scripts/sync-cnb-release.ps1`
- `README.md`
- `development-log.md`

### 具体内容

- 新增 `Sync CNB Release` GitHub Actions 工作流，在 GitHub Release 发布或编辑后自动下载 Release 附件，并尝试同步到 CNB Release。
- 新增 `scripts/sync-cnb-release.ps1`，用于通过 CNB Release 接口创建或更新 Release，并按文件名跳过已存在附件。
- 工作流复用已有的 `GIT_PASSWORD` secret 作为 CNB token，不在仓库中写入任何明文 token。
- 支持手动触发 `Sync CNB Release` 工作流并输入 tag，用于发布后重试 CNB Release 同步。
- README 补充 CNB Release 自动同步说明和 token 安全注意事项。

### 验证情况

- 已使用 PowerShell parser 检查 `scripts/sync-cnb-release.ps1`，语法解析通过。
- 已使用 PyYAML 解析 `.github/workflows/sync-cnb-release.yml`，YAML 语法通过。
- 未直接执行 CNB 附件上传流程；该流程需要在 GitHub Actions 中通过 `GIT_PASSWORD` secret 访问 CNB。

## Version 1.1.2 - 2026-06-15 16:51:53 +08:00

### 修改范围

- GitHub 到 CNB 同步流程
- CNB 无效流水线配置
- 修正版打包发布

### 涉及文件

- `launchdock/__init__.py`
- `.github/workflows/sync-cnb.yml`
- `.cnb.yml`
- `development-log.md`

### 具体内容

- 将版本号更新为 `v1.1.2`，作为 CNB 同步流程修正版。
- 修复 GitHub Actions 中 CNB tag 同步失败的问题：不再使用 `git push --tags` 重推全部标签，改为先读取 CNB 已存在的 tag，只推送 CNB 缺失的 tag。
- 避免 CNB 已存在的 tag 与 GitHub 本地 tag 对象不一致时触发 `already exists` 拒绝，导致整个同步 workflow 标红。
- 删除 `.cnb.yml`，避免 CNB 仓库收到同步后尝试执行 Docker 构建；LaunchDock 是 PySide6 桌面应用，不需要 CNB Docker pipeline。
- 保持国际版和国内版双渠道发布方式，继续区分 `global` 和 `china` 打包产物。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，15 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。
- 已生成 `dist/v1.1.2/LaunchDock-v1.1.2-windows-global.zip` 和 `dist/v1.1.2/LaunchDock-v1.1.2-windows-china.zip`。
- 已生成 `dist/v1.1.2/LaunchDock-v1.1.2-windows-global-setup.exe` 和 `dist/v1.1.2/LaunchDock-v1.1.2-windows-china-setup.exe`。
- 已检查两个压缩包内置 `update-config.json`，均为无 BOM 的 UTF-8，且国际版指向 GitHub、国内版指向 CNB。

## 2026-06-15 16:42:52 +08:00

### 修改范围

- GitHub 到 CNB 同步流程
- CNB 无效流水线配置

### 涉及文件

- `.github/workflows/sync-cnb.yml`
- `.cnb.yml`
- `development-log.md`

### 具体内容

- 修复 GitHub Actions 中 CNB tag 同步失败的问题：不再使用 `git push --tags` 重推全部标签，改为先读取 CNB 已存在的 tag，只推送 CNB 缺失的 tag。
- 避免 CNB 已存在的 tag 与 GitHub 本地 tag 对象不一致时触发 `already exists` 拒绝，导致整个同步 workflow 标红。
- 删除 `.cnb.yml`，避免 CNB 仓库收到同步后尝试执行 Docker 构建；LaunchDock 是 PySide6 桌面应用，不需要 CNB Docker pipeline。

### 验证情况

- 已检查失败的 GitHub Actions 日志，确认失败点为 `git push --tags` 推送已存在的 `v1.1.0` tag 被 CNB 拒绝。
- 本次为 CI 配置和镜像仓库配置修复，未运行应用测试。

## Version 1.1.1 - 2026-06-15 12:48:54 +08:00

### 修改范围

- 更新检查修复
- Windows 安装包安装路径
- 修正版打包发布

### 涉及文件

- `launchdock/__init__.py`
- `launchdock/app.py`
- `scripts/build-windows.ps1`
- `installer/launchdock.iss`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 将版本号更新为 `v1.1.1`，作为 `v1.1.0` 发布后的修正版。
- 修复 `update-config.json` 带 UTF-8 BOM 时无法解析，导致关于页显示“检查更新失败”的问题。
- 打包脚本写入更新配置时改用无 BOM 的 UTF-8，避免新包继续生成带 BOM 配置。
- 安装包配置强制显示安装路径选择页，允许用户在安装时自定义安装目录。
- 保持国际版和国内版双渠道发布方式，继续区分 `global` 和 `china` 打包产物。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，15 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。
- 已生成 `dist/v1.1.1/LaunchDock-v1.1.1-windows-global.zip` 和 `dist/v1.1.1/LaunchDock-v1.1.1-windows-china.zip`。
- 已生成 `dist/v1.1.1/LaunchDock-v1.1.1-windows-global-setup.exe` 和 `dist/v1.1.1/LaunchDock-v1.1.1-windows-china-setup.exe`。
- 已检查两个压缩包内置 `update-config.json`，均为无 BOM 的 UTF-8，且国际版与国内版更新源配置正确。

## 2026-06-15 12:34:04 +08:00

### 修改范围

- 更新配置编码兼容
- 打包配置写入方式
- 更新检查测试

### 涉及文件

- `launchdock/app.py`
- `scripts/build-windows.ps1`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 修复 `update-config.json` 带 UTF-8 BOM 时无法解析，导致关于页显示“检查更新失败”的问题。
- 读取更新配置和 Release API 响应时改用 `utf-8-sig`，兼容带 BOM 和不带 BOM 的 UTF-8 内容。
- 打包脚本写入 `build/update-config.json` 时改为无 BOM 的 UTF-8，避免后续新包继续生成带 BOM 配置。
- 新增测试覆盖带 BOM 的更新配置读取场景。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，15 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。

## Version 1.1.0 - 2026-06-15 11:40:36 +08:00

### 修改范围

- 国内镜像更新源
- GitHub 到 CNB 同步
- 启动项目交互优化
- Windows 打包产物规范
- 关于页更新检查状态

### 涉及文件

- `launchdock/__init__.py`
- `launchdock/app.py`
- `scripts/build-windows.ps1`
- `scripts/build-installer.ps1`
- `installer/launchdock.iss`
- `.github/workflows/sync-cnb.yml`
- `.cnb.yml`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 将版本号更新为 `v1.1.0`，作为包含国内镜像更新源能力的新功能版本。
- 支持在 PyInstaller 打包时写入不同更新源，国内版可通过 CNB 等国内镜像仓库检查 Git tag 获取最新版本。
- 同一版本的 Windows 压缩包和安装包文件名会区分渠道，国际版使用 `global` 后缀，国内版使用 `china` 后缀，避免 Release 资产互相覆盖或混淆。
- 安装包脚本在生成安装包前会按指定渠道重新构建程序目录，避免复用上一次打包留下的错误渠道内容。
- 新增 GitHub Actions 到 CNB 的代码和 tag 同步配置，确保国内镜像可获得发布 tag。
- 优化关于页更新检查状态，启动自动检查时显示“正在检查更新”，仅在确认无 Release 时显示暂无发布版本。
- 启动项目页面默认折叠项目卡片，并支持单条启动项单独启动。
- 打包脚本将压缩包和安装包输出到 `dist/v版本号/` 目录，便于多版本产物归档。
- README、AGENTS 和项目专属 Skill 补充双包发布说明：Release 中同时上传国际版和国内版，并提示中国大陆无 VPN 用户建议下载国内版以获得正常自动更新。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，14 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。
- 已运行国际版 Windows 打包脚本，生成 `dist/v1.1.0/LaunchDock-v1.1.0-windows-global.zip`。
- 已运行国内版 Windows 打包脚本，生成 `dist/v1.1.0/LaunchDock-v1.1.0-windows-china.zip`。
- 已检查两个压缩包内置 `update-config.json`：国际版更新通道为 `global`，更新仓库为 `https://github.com/Dylanliiiii/LaunchDock.git`；国内版更新通道为 `china`，更新仓库为 `https://cnb.cool/DylanLIIIII/LaunchDock.git`。
- 已使用 `E:\Apps_Work\Inno Setup 6\ISCC.exe` 运行国际版安装包打包脚本，生成 `dist/v1.1.0/LaunchDock-v1.1.0-windows-global-setup.exe`。
- 已使用 `E:\Apps_Work\Inno Setup 6\ISCC.exe` 运行国内版安装包打包脚本，生成 `dist/v1.1.0/LaunchDock-v1.1.0-windows-china-setup.exe`。

## 2026-06-15 06:01:54 +08:00

### 修改范围

- GitHub 到 CNB tag 同步

### 涉及文件

- `.github/workflows/sync-cnb.yml`
- `development-log.md`

### 具体内容

- 在 GitHub Actions 同步流程中新增 tag 同步步骤，使用 GitHub Secret `GIT_PASSWORD` 生成临时 Basic Auth header，将 GitHub 远端 tag 推送到 CNB 镜像仓库。
- 解决 CNB 仓库代码已同步但页面仍显示 `Tag 0` 的问题；下一次 GitHub push 后应同步已有 `v1.0.0` tag。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，14 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。
- 已确认本地存在 `v1.0.0` tag，且修改前 CNB 远端未返回任何 tag。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-15 05:39:36 +08:00

### 修改范围

- GitHub 到 CNB 同步配置
- 国内更新源地址

### 涉及文件

- `.github/workflows/sync-cnb.yml`
- `.cnb.yml`
- `scripts/build-windows.ps1`
- `README.md`
- `development-log.md`

### 具体内容

- 新增 GitHub Actions 同步配置，用于在 GitHub push 后通过 `tencentcom/git-sync` 同步仓库到 CNB。
- 新增 CNB 配置文件，保留教程中的 CNB push 流程配置。
- 将国内版打包脚本默认更新仓库和 README 示例改为当前 CNB 同步目标 `https://cnb.cool/DylanLIIIII/LaunchDock.git`。
- 检查同步配置未包含明文 token，CNB 密码通过 GitHub Secrets `GIT_PASSWORD` 引用。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，14 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。
- 已检查 GitHub Actions 配置和相关项目文件，未发现明文 token、私钥或密码。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-15 05:14:56 +08:00

### 修改范围

- 更新源配置
- 国内镜像版本检查
- 打包脚本
- 发布说明

### 涉及文件

- `launchdock/app.py`
- `scripts/build-windows.ps1`
- `scripts/build-installer.ps1`
- `tests/test_storage.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 新增随 PyInstaller 打包写入的 `update-config.json` 读取逻辑，支持不同发行渠道使用不同更新源。
- 更新检查优先通过配置的 Git 仓库 tag 获取最新版本，适合国内版指向 CNB 等国内镜像仓库；如果配置了 Release API，再作为兜底信息来源。
- 新增 Git tag 解析逻辑，能从 `git ls-remote --tags --refs` 输出中识别最新语义化版本。
- 打包脚本新增 `-UpdateChannel`、`-UpdateRepoUrl`、`-ReleasePageUrl`、`-ReleaseApiUrl` 参数，并将生成的更新配置文件打进应用包。
- 分享下载链接和发现新版本后的打开地址改为读取当前打包渠道配置的下载页面。
- README、AGENTS 和项目专属 Skill 补充国内版打包和更新源同步说明。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，14 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。
- 已运行本地函数冒烟测试，确认 Git tag 输出可解析出 `v1.10.0` 作为最新版本。
- 已运行 PowerShell 脚本块解析检查，确认 `scripts/build-windows.ps1` 和 `scripts/build-installer.ps1` 语法可解析。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-15 04:24:50 +08:00

### 修改范围

- 关于页更新检查状态

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 将关于页版本更新卡片的初始文案改为“尚未检查更新”，避免启动时误显示“没有检查到新版本”。
- 自动检查和手动检查开始时都会切换为“正在检查更新 / 正在检查是否有最新版本”状态。
- 自动检查完成后根据结果显示“暂无发布版本”“已是当前版本”“发现新版本”或“检查更新失败”，避免后台检查失败时卡片一直停留在检查中。
- 新增空 Release 正文兜底文案，避免发现新版本但发布说明为空时复用未检查占位文案。
- 同步更新简体中文、繁体中文、英文、日语、韩语和西班牙语文案。

### 验证情况

- 已运行 `python -m unittest discover -s tests`，13 个测试全部通过。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过语法检查。
- 已运行 Qt offscreen 冒烟测试，确认关于页初始显示“尚未检查更新”，检查中显示“正在检查更新”，无 Release 时才显示“暂无发布版本”。
- 本次为日常开发修改，未更新项目版本号。

## Version 1.0.0 - 2026-06-14 20:24:33 +08:00

### 修改范围

- 首次正式发布
- 版本号规则说明

### 涉及文件

- `launchdock/__init__.py`
- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 将项目版本号升级为 `v1.0.0`，作为第一次正式发布版本。
- 关于页中的版本显示改为仅展示当前版本号，不再附带开发版字样。
- 约定后续版本号更新规则：主版本号用于大改或不兼容变更，次版本号用于新功能，修订号用于 bug 修复。例如当前版本为 `1.0.0` 时，大改发布为 `2.0.0`，新功能发布为 `1.1.0`，bug 修复发布为 `1.0.1`。
- 首次正式发布说明仅保留重点内容，后续小型格式修正和局部调整继续记录在普通开发日志中。

### 验证情况

- 已更新版本常量与关于页显示文案。
- 本次为正式发布记录，未额外运行回归测试。

## 2026-06-14 20:32:43 +08:00

### 修改范围

- Windows 打包脚本
- GitHub Release 发布说明
- 项目发布约定

### 涉及文件

- `scripts/build-windows.ps1`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 新增 Windows 打包脚本，使用 PyInstaller 生成 `dist/LaunchDock-v版本号-windows.zip`。
- 打包脚本会从 `assets/icon.png` 临时派生 `build/launchdock.ico`，不覆盖原始图标源文件。
- 在 README 中补充打包步骤、Release 发布检查项和 `v1.0.0` 首次发布正文建议。
- 将 GitHub 仓库地址、版本号规则、Release 正文提炼规则和打包产物注意事项写入项目协作说明和项目专属 Skill。

### 验证情况

- 已安装 PyInstaller 并运行 `powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1 -Version v1.0.0`，成功生成 `dist/LaunchDock-v1.0.0-windows.zip`。
- 当前环境缺少 GitHub CLI，且未配置 `GITHUB_TOKEN`，暂未直接创建 GitHub Release。
- 本次为日常发布流程补充，未更新项目版本号。

## 2026-06-14 20:58:17 +08:00

### 修改范围

- Windows 安装包发布流程

### 涉及文件

- `installer/launchdock.iss`
- `scripts/build-installer.ps1`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 新增 Inno Setup 安装脚本，用于生成 Windows `setup.exe` 安装包。
- 新增 `scripts/build-installer.ps1`，在已有 PyInstaller 程序目录基础上生成 `LaunchDock-v版本号-windows-setup.exe`。
- 在 README、项目协作说明和项目专属 Skill 中补充安装包生成方式与 Release 资产约定。
- 安装包支持开始菜单快捷方式、可选桌面快捷方式、卸载入口和应用图标。

### 验证情况

- 已检查当前环境未安装 Inno Setup 编译器，暂未生成实际安装包。
- 本次为日常发布流程补充，未更新项目版本号。

## 2026-06-14 21:41:22 +08:00

### 修改范围

- Windows 安装包脚本框架校正

### 涉及文件

- `installer/launchdock.iss`
- `development-log.md`

### 具体内容

- 将手动向导生成的安装脚本恢复为仓库模板式写法，避免写死本机绝对路径。
- 安装脚本继续由 `scripts/build-installer.ps1` 注入版本号、程序目录、输出目录和图标路径。
- 修正 Inno Setup `AppId` 的 GUID 写法，避免安装脚本解析异常。

### 验证情况

- 已检查安装脚本不再包含维护者本机绝对路径。
- 本次为日常发布流程修正，未更新项目版本号。

## 2026-06-14 23:34:26 +08:00

### 修改范围

- 启动项目交互优化
- 启动目标路径兼容
- 发布产物目录规范

### 涉及文件

- `launchdock/app.py`
- `tests/test_storage.py`
- `scripts/build-windows.ps1`
- `scripts/build-installer.ps1`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 启动项目页面默认将所有项目卡片折叠展示，用户可手动展开查看启动项。
- 每条启动项右侧新增单独启动按钮，可只打开当前启动项。
- 启动目标支持成对双引号包裹的本地路径，单边双引号仍判定为无效目标。
- 软件启动后默认展开左侧导航栏。
- Windows 压缩包和安装包输出到 `dist/v版本号/` 目录，方便不同版本发布产物分开保存。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，13 个测试全部通过。
- 已运行 Qt offscreen 构造检查，确认应用可创建且已有项目默认进入折叠状态。
- 本次为日常功能优化，未更新项目版本号。

## 2026-06-14 20:03:54 +08:00

### 修改范围

- 启动项开关状态统计刷新

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 在启动项目卡片渲染时记录每个项目的启动项统计标签。
- 通过右侧开关启用或停用启动项后，保存项目数据并即时刷新当前项目的“已启用”数量。
- 保持开关操作不重建整张项目卡片，避免不必要的界面闪动。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 19:54:49 +08:00

### 修改范围

- 启动项目卡片空状态对齐

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 将空项目提示改为 12px 左侧间距，使其与上方项目名称和“0 个启动项，0 个已启用”的文字左侧对齐，而不是与下方按钮区域对齐。
- 使用 Qt offscreen 坐标检查确认三行文字在卡片内的左侧坐标一致。

### 验证情况

- 已运行 Qt offscreen 坐标检查，项目名、统计行和空项目提示在卡片内的左侧坐标均为 30。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 19:51:16 +08:00

### 修改范围

- 启动项目卡片空状态对齐

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 移除空项目提示前额外添加的 40px 缩进，使“这个项目还没有启动项”与上方项目名称和统计信息左侧对齐。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 19:49:06 +08:00

### 修改范围

- 启动项目卡片空状态对齐
- 启动坞页面说明文案

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 将空项目中的“这个项目还没有启动项”提示调整为独立说明行，后续继续微调其左侧对齐。
- 在“启动坞”页面标题下新增一行简短说明，说明启动坞用于选择或创建本地文件夹来保存启动项目和配置。
- 为新增启动坞说明补齐简体中文、繁体中文、英文、日语、韩语和西班牙语文案。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 19:42:39 +08:00

### 修改范围

- 左侧导航栏展开宽度
- 多语言导航名称
- 项目协作说明

### 涉及文件

- `launchdock/app.py`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 新增导航栏展开宽度计算逻辑，根据当前语言下最长导航名称动态设置展开宽度。
- 为导航栏设置合理宽度上下限，避免中文界面侧边栏过宽。
- 新增导航专用短名称，例如英文侧边栏使用 `Projects` 而页面标题仍保留 `Launch Projects`，西班牙语侧边栏使用 `Proyectos` 而页面标题仍保留 `Proyectos de inicio`。
- 将导航栏多语言长度适配约定同步写入 `AGENTS.md` 和项目专属 Skill。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，12 个测试全部通过。
- 已运行 Qt offscreen 多语言冒烟测试，确认简体中文、繁体中文、英文、日语、韩语、西班牙语导航展开宽度均位于设定范围内，且导航文本不会超出侧边栏。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 19:35:32 +08:00

### 修改范围

- 关于页面按钮样式

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 将“关于”页面信息卡片右侧的“检查新版本”“GitHub”“分享下载链接”从透明按钮改为 QFluentWidgets `PushButton`。
- 为三个按钮统一设置 38px 高度，使其拥有类似 OK-WW 参考样式的低对比背景框。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，12 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，确认关于页存在 3 个带背景按钮，按钮文字和高度正常。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 19:30:34 +08:00

### 修改范围

- 关于页面
- GitHub Release 更新检查
- 默认启动页面
- 测试
- 项目协作说明

### 涉及文件

- `launchdock/app.py`
- `tests/test_storage.py`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 重构“关于”页面：保留页面标题，移除原有简单介绍卡片，新增参考 OK-WW 风格的横向信息卡片。
- 信息卡片展示软件图标、`LaunchDock` 名称、当前版本号和原介绍内容。
- 新增带图标的“检查新版本”“GitHub”“分享下载链接”按钮。
- “分享下载链接”会复制 GitHub Releases 页面链接，便于后续发布版本后分享下载入口。
- 新增更新信息区域，用于显示版本跨度和新版本改动内容。
- 新增 GitHub Releases 更新检查逻辑，通过 `releases/latest` 获取最新发布版本、下载页和 release 正文。
- 手动检查会在关于页显示检查结果；启动后会延迟自动检查，只有发现新版本时才弹窗询问是否打开下载页面。
- 没有 GitHub Release 时不会误报更新，会显示暂无发布版本。
- 软件启动后默认切换到“关于”页面。
- 新增版本比较测试，避免 `0.10.0` 与 `0.2.0` 这类版本号被字符串顺序误判。
- 将关于页和更新检查约定同步写入 `AGENTS.md` 和项目专属 Skill。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，12 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，确认启动后默认页面为“关于”，并确认关于页更新标题和检查按钮可创建。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 19:03:13 +08:00

### 修改范围

- 项目专属 Agent 配置
- 测试文件可读性

### 涉及文件

- `.agents/skills/launchdock-project/agents/openai.yaml`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 修正项目专属 Agent 配置文件中的乱码中文，恢复为正常 UTF-8 中文文案。
- 修正测试文件中被错误编码显示的中文、日文测试字符串，保持测试语义不变，提升开源仓库可读性。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，11 个测试全部通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 18:39:55 +08:00

### 修改范围

- 项目重命名存储逻辑
- 项目文件夹迁移
- 测试
- 项目协作说明

### 涉及文件

- `launchdock/storage.py`
- `launchdock/app.py`
- `tests/test_storage.py`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 新增存储层 `rename_project` 方法，重命名项目时同步迁移启动坞 `projects/` 下的项目文件夹。
- 项目重命名后会同步更新 `project.json` 中的 `name` 和 `folder_name`。
- 文件夹名生成逻辑支持排除当前项目原文件夹，避免仅大小写或同名保存时误判冲突。
- 如果新项目名对应的文件夹已存在，会自动生成不冲突的文件夹名，例如 `项目-2`，避免覆盖其他项目。
- UI 层编辑项目名称时改为调用存储层重命名方法，而不是只改内存中的项目显示名称。
- 新增测试覆盖项目重命名迁移文件夹，以及重名项目自动生成唯一文件夹名。
- 将项目重命名同步文件夹的约定写入 `AGENTS.md` 和项目专属 Skill。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，11 个测试全部通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 18:28:49 +08:00

### 修改范围

- 项目名称编辑弹窗
- 启动项编辑弹窗

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 将项目名称输入框的回车键绑定到保存按钮，按回车与点击“保存”走同一条确认逻辑。
- 将启动项名称输入框和 URL / 本地路径输入框的回车键绑定到保存按钮，避免弹窗关闭但修改未保存。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，9 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，分别触发项目名称输入框和启动项 URL 输入框的 `returnPressed` 信号，确认两个对话框都返回确认状态。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 18:08:22 +08:00

### 修改范围

- 启动项列表布局
- 主界面横向滚动
- 无边框窗口缩放命中范围
- 项目协作说明

### 涉及文件

- `launchdock/app.py`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 启动项列表中不再直接显示完整 URL 或本地路径，只保留启动项名称，避免长地址撑开项目卡片并把“启动”按钮挤到可视区域外。
- 为启动项行保留 URL 工具提示，完整地址仍可通过编辑启动项查看和修改。
- 关闭启动项目主滚动区的横向滚动条，让主界面保持纵向浏览。
- 显式开启 QFluentWidgets 无边框窗口缩放能力，并将窗口边缘缩放命中宽度调整为 10px，改善右侧边缘和右上 / 右下角难以触发缩放的问题。
- 将“启动项列表不直接展示完整地址”的界面约定同步写入 `AGENTS.md` 和项目专属 Skill。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，9 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，构造超长 URL 启动项后确认界面中不再出现完整地址文本，主滚动区横向滚动条策略为关闭。
- 已在 Qt offscreen 冒烟测试中确认窗口 `_isResizeEnabled` 为 `True`，无边框缩放命中宽度为 `10px`。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 17:05:17 +08:00

### 修改范围

- 多语言翻译覆盖
- 语言下拉显示规则
- 项目协作说明

### 涉及文件

- `launchdock/app.py`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 补齐启动项目卡片、启动项管理、启动坞页面、关于页面、常用对话框和提示信息的多语言文案引用，避免在英文、日语、韩语、西班牙语等界面中继续显示简体中文。
- 调整语言下拉列表：各语言名称始终使用对应语言自身写法，例如 `English`、`日本語`、`한국어`、`Español`。
- 保留“使用系统设置”为唯一跟随当前界面语言变化的语言选项，并在语言设置保存后立即刷新设置页下拉框显示。
- 为单个启动项删除确认补充独立翻译键，避免复用项目删除标题。
- 将语言下拉显示约定同步写入 `AGENTS.md` 和项目专属 Skill，方便后续继续维护。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，9 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，确认英文界面下项目卡片计数和空项目提示为英文，并确认语言下拉显示为 `简体中文`、`繁体中文`、`English`、`日本語`、`한국어`、`Español`、`Use system setting`。
- 已在 Qt offscreen 冒烟测试中切换到日语刷新设置页，确认语言下拉里的语言名称保持原生写法，且仅最后一项变为 `システム設定を使用`。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 15:37:17 +08:00

### 修改范围

- 设置页面图标
- 语言设置生效逻辑
- 语言切换提示
- 测试

### 涉及文件

- `launchdock/app.py`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 调整设置页“应用主题”和“语言”卡片左侧图标，固定图标尺寸为 28px，让设置项前的图标明确可见。
- 新增轻量级界面文案翻译表，覆盖导航、启动项目页标题、设置页标题、设置项标题与说明、语言重启提示等核心界面文案。
- 应用启动时会根据已保存语言读取核心界面文案；选择“使用系统设置”时会根据系统语言粗略映射到支持的语言。
- 修改语言设置后会保存到本地配置，并提示用户“语言将在重启后生效”，避免用户误以为当前界面会立即完整切换。
- 新增测试，确认语言文案函数能根据语言设置返回对应核心文案。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，9 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，确认英文设置下设置页标题显示为 `LaunchDock Settings`，并确认设置卡片图标控件宽度为 28px。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 15:28:09 +08:00

### 修改范围

- 设置页面
- 应用主题设置
- 语言选择设置
- 设置持久化
- 测试

### 涉及文件

- `launchdock/app.py`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 在左侧底部导航的“关于”下方新增“设置”入口。
- 新增 `LaunchDock设置` 页面，页面标题不使用“软件设置”。
- 新增“应用主题”设置，支持选择“浅色”“深色”“跟随系统”，并在选择后立即应用到 QFluentWidgets 主题。
- 新增“语言”设置，支持选择“简体中文”“繁体中文”“英文”“日语”“韩语”“西班牙语”“使用系统设置”。
- 将主题和语言设置保存到本地应用配置文件中的 `settings` 字段，重新启动后可以读取上次选择。
- 新增设置读写测试，覆盖默认设置和保存后的设置读取。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，8 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，确认设置页可以创建，主题和语言下拉框可以切换，并能写入临时配置文件。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 15:21:02 +08:00

### 修改范围

- 关于页面文案
- 版本号展示策略

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 移除关于页面中 `LaunchDock v0.1.5` 的版本号展示。
- 关于页面标题改为仅显示 `LaunchDock`，避免在尚未正式打包或发布版本时给用户造成已有发布版本的误解。
- 保留 `launchdock/__init__.py` 中的 `__version__` 不变，遵守日常开发不随意变更版本号的规则；后续正式打包或发布时再统一决定版本号与展示方式。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，7 个测试全部通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 15:04:57 +08:00

### 修改范围

- 启动坞路径加载逻辑
- 启动坞缺失状态提示
- 存储层测试

### 涉及文件

- `launchdock/storage.py`
- `launchdock/app.py`
- `tests/test_storage.py`
- `development-log.md`

### 具体内容

- 调整 `DockStorage` 初始化逻辑：如果已保存的启动坞路径不存在，不再把它作为可用启动坞，也不自动重新创建该文件夹。
- 新增 `missing_dock_path` 状态，用于记录上次保存但当前已经不存在的启动坞路径。
- 主界面和“启动坞”页面在路径缺失时显示明确中文提示，说明该文件夹可能已被移动、删除或重命名，并引导用户重新选择或创建启动坞。
- 选择启动坞时，如果上次路径缺失且其父目录仍存在，文件夹选择窗口默认从父目录开始，方便用户找回或重选。
- 新增测试，确认已保存的启动坞路径缺失时不会被自动重新创建。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，7 个测试全部通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 10:10:00 +08:00

### 修改范围

- 项目协作说明
- 项目专属 Skill
- 开发记录文件

### 涉及文件

- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `.agents/skills/launchdock-project/agents/openai.yaml`
- `development-log.md`

### 具体内容

- 将项目协作说明整理为中文，并明确后续文档、注释、界面文案默认使用中文。
- 明确后续新增文件和目录使用简洁、合适的英文名称，文件内容继续使用中文。
- 将项目专属 Skill 路径改为仓库相对路径，避免开源后依赖维护者本机路径。
- 创建项目专属 Skill，用于维护 LaunchDock 的项目模块、链接启动、本地数据坞和中文文档规则。
- 明确 LaunchDock 创建项目时既可以立即添加链接，也可以先创建空项目，之后再补充内容。
- 明确数据坞为用户自定义本地大文件夹，所有小项目保存在其下的独立项目文件夹中。
- 补充开源协作约束：仓库内说明、配置和示例不能写死任何开发者本机绝对路径。
- 新增本开发记录文件，用于后续记录每次生成或修改代码时的具体工作。

### 验证情况

- 已读取并检查 `AGENTS.md` 和项目专属 `SKILL.md` 的主要内容。
- 曾尝试运行 skill 验证脚本，但当前 Python 环境缺少 `yaml` 模块，验证脚本无法启动。
- 本次未生成应用代码，因此未运行应用级测试。

## 2026-06-14 10:39:34 +08:00

### 修改范围

- 项目协作说明
- 项目专属 Skill
- 开发记录格式

### 涉及文件

- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 从 `AGENTS.md` 中移除“当前阶段约束”段落。
- 明确后续开发记录需要同时包含日期和具体时间，方便判断更新顺序。
- 明确后续涉及代码生成或代码修改时，需要同步记录开发日志。
- 同步更新项目专属 Skill，要求修改代码后更新 `development-log.md` 并写清日期与具体时间。
- 将已有开发记录标题升级为包含日期、时间和时区的格式。

### 验证情况

- 已读取并检查 `AGENTS.md`、项目专属 `SKILL.md` 和 `development-log.md`。
- 本次只修改文档和项目规则，未生成应用代码，因此未运行应用级测试。

## 2026-06-14 10:41:14 +08:00

### 修改范围

- 项目协作说明
- 项目专属 Skill
- 开发记录

### 涉及文件

- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 在 `AGENTS.md` 中新增规则：后续如果新增、修改、删除或移动任何 Skill，必须同步更新 `AGENTS.md` 中的项目专属 Skill 说明。
- 在项目专属 Skill 中同步加入 Skill 变更时更新 `AGENTS.md` 的要求。
- 在项目专属 Skill 的检查清单中加入 Skill 变更同步检查项。

### 验证情况

- 已读取并检查 `AGENTS.md`、项目专属 `SKILL.md` 和 `development-log.md` 的相关段落。
- 本次只修改文档和项目规则，未生成应用代码，因此未运行应用级测试。

## 2026-06-14 10:46:32 +08:00

### 修改范围

- 应用入口
- 数据模型
- 本地数据坞存储
- Tkinter 图形界面
- 项目说明
- 测试

### 涉及文件

- `main.py`
- `launchdock/__init__.py`
- `launchdock/models.py`
- `launchdock/storage.py`
- `launchdock/app.py`
- `tests/test_storage.py`
- `README.md`
- `.gitignore`
- `development-log.md`

### 具体内容

- 新增 `main.py` 作为 LaunchDock 应用入口。
- 新增 `launchdock` 包，拆分为模型、存储和 GUI 模块。
- 实现项目和链接数据模型，包含 `id`、名称、URL、默认启动、排序、创建时间和更新时间。
- 实现本地数据坞存储层：支持 `launchdock.json`、`projects/<project>/project.json`、项目文件夹重名处理、项目排序和最近项目记录。
- 创建项目支持空项目，也支持创建后立即添加第一个链接。
- 实现 Tkinter 桌面界面：项目列表、链接表、选择数据坞、新建项目、重命名、删除、添加链接、编辑链接、删除链接、上移、下移和一键启动。
- 一键启动会按排序打开默认启动链接，并对空链接或明显异常 URL 做中文提示。
- 新增 `README.md`，说明运行方式、主要功能和数据坞结构。
- 新增 `.gitignore`，避免提交 Python 缓存、构建产物和本地默认数据坞。
- 新增存储层单元测试，覆盖创建空项目、保存链接、删除项目和全局项目排序。
- 修正存储层行为：使用临时数据坞时不再自动写入用户主目录配置；只有用户在界面主动选择数据坞时才尝试保存路径。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，4 个测试全部通过。
- 未自动启动 GUI 主循环，避免在当前会话中打开交互窗口；可通过 `python main.py` 手动运行。

## 2026-06-14 11:30:48 +08:00

### 修改范围

- 界面风格
- 主界面交互
- 启动目标类型
- 项目文档
- 测试

### 涉及文件

- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `launchdock/__init__.py`
- `launchdock/app.py`
- `tests/test_storage.py`
- `README.md`
- `development-log.md`

### 具体内容

- 根据参考图和新要求，将主界面从“左侧项目列表 + 右侧表格”重构为深色 WinUI 风格布局。
- 新界面采用左侧垂直导航栏，包含图标和文字。
- 右侧主区域改为设置页式布局，右上角提供“新建”按钮。
- 启动项目以卡片形式显示，每个项目卡片包含项目标题、启动项数量、编辑按钮、删除按钮、添加启动项按钮和启动按钮。
- 每条启动项以横向卡片行显示，左侧有图标、名称和说明地址，右侧有启用开关、编辑图标、删除图标和上下移动按钮。
- 使用深色低对比度背景、接近 Segoe UI 的字体和青色强调色。
- 启动目标从纯网页 URL 扩展为网页链接或本地文件路径；网页用浏览器打开，本地文件或文件夹交给系统默认程序打开。
- 更新 `AGENTS.md` 和项目专属 Skill，固化新的界面风格、卡片交互和本地文件启动要求。
- 更新 `README.md`，说明新界面风格和本地文件路径启动能力。
- 新增测试，覆盖 URL、本地存在文件和缺失文件的启动目标校验。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 未自动启动 GUI 主循环，避免在当前会话中打开交互窗口；可通过 `python main.py` 手动运行查看界面。

## 2026-06-14 11:56:55 +08:00

### 修改范围

- UI 技术栈迁移
- QFluentWidgets 界面重写
- 项目文档
- 依赖管理
- 验证

### 涉及文件

- `launchdock/app.py`
- `launchdock/__init__.py`
- `requirements.txt`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 根据 `UI迁移框架说明书-QFluentWidgets.md`，将 UI 层从 Tkinter 迁移到 PySide6 + QFluentWidgets。
- 保持 `launchdock/models.py` 和 `launchdock/storage.py` 不变，只重写 UI 层 `launchdock/app.py`。
- 使用 `FluentWindow` 构建主窗口，提供“启动项目”“数据坞”“关于”三个导航入口。
- 使用 `CardWidget`、`SmoothScrollArea`、`SwitchButton`、`PrimaryPushButton`、`TransparentToolButton` 等 QFluentWidgets 组件重建项目卡片和启动项卡片。
- 使用 `Dialog + LineEdit + CheckBox` 实现项目名称和启动项编辑对话框，替代 Tkinter 弹窗。
- 使用 `InfoBar` 和 `MessageBox` 统一提示、警告和确认删除体验。
- 设置深色主题和青色强调色，贴近 Windows 11 / Fluent Design 桌面应用观感。
- 新增 `requirements.txt`，记录 `PySide6` 和 `PySide6-Fluent-Widgets` 依赖。
- 更新 `README.md`、`AGENTS.md` 和项目专属 Skill，明确当前 UI 技术栈为 PySide6 + QFluentWidgets，不再使用 Tkinter 主界面。
- 参考 `ok-oldking/ok-script` 的公开仓库信息，其依赖包含 PySide6 / QFluentWidgets 技术栈，并将其作为 Qt/Fluent 桌面应用架构参考。

### 验证情况

- 已安装 `PySide6` 和 `PySide6-Fluent-Widgets`。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt 冒烟测试：在 `QT_QPA_PLATFORM=offscreen` 下创建 `LaunchDockApp` 窗口实例，成功输出 `LaunchDockApp LaunchDock 启动坞`。
- 未进入 GUI 主循环；可通过 `python main.py` 手动启动应用。

## 2026-06-14 12:11:02 +08:00

### 修改范围

- 开发记录规则
- 项目协作说明
- 项目专属 Skill

### 涉及文件

- `development-log.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`

### 具体内容

- 将所有已有开发日志条目的标题中的版本号去除，只保留日期、时间和时区。
- 删除各条目"具体内容"中"更新版本号为 `X.Y.Z`"类描述。
- 修正早期条目中关于"记录 Version"的描述，改为"记录开发日志"或"记录日期与具体时间"。
- 在 `AGENTS.md` 中新增规则：版本号仅在正式完成一轮开发、重新打包或上线更新时才记录到开发日志；日常开发和测试不改变版本号，也不改变 `__version__`。
- 在项目专属 Skill 中同步加入版本号规则：日常开发不记录版本号，仅记录日期和时间；检查清单中加入"日常开发不应变更版本号"检查项。

### 验证情况

- 已读取并检查 `development-log.md`、`AGENTS.md` 和项目专属 `SKILL.md` 的相关段落。
- 本次只修改文档和开发规则，未生成应用代码，因此未运行应用级测试。

## 2026-06-14 12:23:27 +08:00

### 修改范围

- 启动项目界面交互
- 项目管理模式
- 项目文档
- 验证

### 涉及文件

- `launchdock/app.py`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `README.md`
- `development-log.md`

### 具体内容

- 去除项目卡片右上角重复的“添加”图标，保留项目卡片底部“添加启动项”按钮。
- 去除每条启动项右侧的上移、下移箭头。
- 为项目卡片增加折叠按钮，点击可展开或收起该项目下的所有启动项。
- 增加管理模式：顶部“管理”按钮进入批量操作状态。
- 管理模式下可勾选启动项目，支持“全选”和“删除所选”。
- 管理模式下隐藏“新建”按钮，点击“完成”退出管理模式。
- 调整启动项目页滚动区域背景为透明，避免项目卡片后方出现突兀的大块黑色矩形背景。
- 更新 `AGENTS.md`、项目专属 Skill 和 `README.md`，同步记录折叠、批量删除、去除重复按钮和去除无效排序箭头等要求。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt 冒烟测试：在 `QT_QPA_PLATFORM=offscreen` 下创建 `LaunchDockApp` 窗口实例，成功输出 `LaunchDockApp LaunchDock 启动坞`。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 12:34:54 +08:00

### 修改范围

- 应用图标
- 项目文档
- 验证

### 涉及文件

- `assets/icon.webp`
- `launchdock/app.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 接入 `assets/icon.webp` 作为 LaunchDock 软件图标源。
- 在应用启动时通过 `QApplication.setWindowIcon()` 设置全局窗口图标。
- 在主窗口初始化时通过 `setWindowIcon()` 设置窗口图标。
- 新增 `app_icon()` 辅助函数，统一从仓库相对路径加载 `assets/icon.webp`。
- 更新 `README.md`，说明当前运行和后续打包都应使用 `assets/icon.webp` 作为软件图标源。
- 更新 `AGENTS.md` 和项目专属 Skill，固化软件图标源文件和后续打包图标约定。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt 冒烟测试：在 `QT_QPA_PLATFORM=offscreen` 下创建 `LaunchDockApp` 窗口实例，成功输出 `LaunchDockApp LaunchDock 启动坞 False`，其中 `False` 表示 `app_icon().isNull()` 为假，图标已成功加载。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 12:52:09 +08:00

### 修改范围

- 应用图标
- 窗口标题
- 启动项目管理
- 单项目启动项管理
- 项目文档
- 项目专属 Skill

### 涉及文件

- `assets/icon.png`
- `launchdock/app.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 将软件图标源更新为 `assets/icon.png`，并继续通过仓库相对路径加载窗口图标，方便后续开源和打包。
- 将应用窗口标题改为 `LaunchDock`，去除标题栏中的“启动坞”后缀。
- 修正启动项目管理模式的勾选控件创建方式，避免进入管理后项目内容区域显示为空。
- 保留顶部“管理项目”功能，用于勾选多个启动项目、全选并批量删除。
- 新增每个项目卡片内的“管理启动项”功能，用于勾选该项目内多个启动项、全选启动项并批量删除。
- 在进入项目管理和启动项管理时清理互斥管理状态，避免两种管理模式同时生效。
- 更新 `README.md`、`AGENTS.md` 和项目专属 Skill，记录 `assets/icon.png`、英文标题栏和两层管理功能要求。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试：成功输出 `LaunchDockApp LaunchDock False`，其中 `LaunchDock` 表示窗口标题已去除中文后缀，`False` 表示 `app_icon().isNull()` 为假，图标已成功加载。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 13:01:29 +08:00

### 修改范围

- 启动项目管理
- 单项目启动项管理
- 运行时报错修复

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 修复 QFluentWidgets `CheckBox` 没有 `checkedChanged` 信号导致点击“管理启动项”时报错的问题。
- 将项目管理和启动项管理中的勾选状态监听改为 `checkStateChanged`。
- 新增 `is_checked_state()` 辅助函数，将 Qt 勾选状态统一转换为布尔值，供批量选择逻辑使用。
- 保持 `SwitchButton.checkedChanged` 不变，因为启动项启用开关使用的是独立控件信号。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试，直接刷新项目卡片、进入“管理启动项”、再进入“管理项目”，成功输出 `LaunchDockApp LaunchDock 1`。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 13:29:29 +08:00

### 修改范围

- 启动项目管理
- 单项目启动项管理
- 选择交互优化
- 项目文档
- 项目专属 Skill

### 涉及文件

- `launchdock/app.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 为顶部“管理项目”模式新增“取消全选”和“反选”功能。
- 为单个项目卡片内“管理启动项”模式新增“取消全选”和“反选”功能。
- 修复管理模式刷新界面时 `SwitchButton.setChecked()` 触发 `checkedChanged`，导致已启用启动项开关视觉跳动的问题。
- 在初始化启动项开关状态时临时屏蔽信号，只保留用户主动点击开关时触发保存。
- 更新 `README.md`、`AGENTS.md` 和项目专属 Skill，记录两层管理都应支持全选、取消全选、反选和批量删除。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试：刷新项目卡片、执行项目管理的全选/取消全选/反选、执行启动项管理的全选/取消全选/反选，成功输出 `LaunchDockApp LaunchDock 0 2`，其中 `0` 表示批量选择过程中没有误触发启动项开关逻辑。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 13:33:53 +08:00

### 修改范围

- 启动项开关显示
- 管理模式选择交互
- 视觉跳动修复

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 修复管理模式中点击全选、取消全选或反选时，启动项启用开关仍出现视觉跳动的问题。
- 新增 `set_switch_checked_without_animation()` 辅助函数，用于在刷新界面时无动画设置 `SwitchButton` 初始状态。
- 初始化启动项开关时直接设置内部滑块最终位置，避免控件从默认关闭状态滑动到启用状态。
- 保留用户手动点击启动项开关时的正常动画和保存逻辑。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试：刷新项目卡片并执行“管理启动项”的全选操作后，所有 `SwitchButton` 动画状态均为停止，输出 `LaunchDockApp 8 [True, True, True, True, True, True, True, True] ...`。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 13:45:24 +08:00

### 修改范围

- 删除确认弹窗
- 批量删除项目
- 同名空项目删除验证

### 涉及文件

- `launchdock/app.py`
- `development-log.md`

### 具体内容

- 将删除确认从 QFluentWidgets `MessageBox` 改为 Qt 原生 `QMessageBox.question` 形式的稳定确认流程。
- 新增 `confirm_action()` 方法，统一处理删除项目、批量删除项目、删除启动项和批量删除启动项的确认。
- 删除确认按钮改为中文“确定 / 取消”，默认按钮为“取消”，避免误删。
- 修复批量删除两个同名空项目时，确认弹窗点击后无响应且程序无法退出的问题。
- 保持删除前必须确认的用户数据保护规则不变。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 已运行 Qt offscreen 冒烟测试：创建两个同名空项目，自动确认批量删除后输出 `0 [] False False`，确认两个项目记录和对应项目文件夹均已删除。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 14:05:19 +08:00

### 修改范围

- 删除确认弹窗
- 应用图标加载
- 图标透明通道处理
- 项目文档
- 项目专属 Skill

### 涉及文件

- `assets/icon.png`
- `launchdock/app.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 去除删除确认弹窗中的 Qt 默认黄色警示图标，避免与当前 Windows / Fluent 风格不匹配。
- 删除确认弹窗继续保留窗口标题栏的软件图标和“确定 / 取消”确认逻辑。
- 为应用图标加载新增透明通道检测；如果图标源已经有 alpha 通道，则保留原透明效果。
- 新增运行时纯色背景剔除逻辑：当图标源缺少透明通道时，基于四角背景色临时生成透明背景图标，不覆盖原始图标源文件。
- 将当前随机命名的图标文件规范为 `assets/icon.png`，保持代码、文档和后续打包路径一致。
- 更新 `README.md`、`AGENTS.md` 和项目专属 Skill，记录图标透明通道与运行时背景剔除规则。

### 验证情况

- 已检查 `assets/icon.png`，当前图标为 `RGBA`，透明通道有效，alpha 范围为 `0` 到 `255`。
- 已运行 Qt offscreen 冒烟测试，确认 `assets/icon.png` 存在且 `app_icon().isNull()` 为 `False`。
- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，5 个测试全部通过。
- 本次为日常开发修改，未更新项目版本号。

## 2026-06-14 14:25:26 +08:00

### 修改范围

- 启动坞命名
- 首次启动逻辑
- 启动项目创建前提
- 项目文档
- 项目专属 Skill
- 测试

### 涉及文件

- `launchdock/storage.py`
- `launchdock/app.py`
- `tests/test_storage.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/launchdock-project/SKILL.md`
- `development-log.md`

### 具体内容

- 将用户可见的“数据坞”统一改为“启动坞”。
- 移除首次使用时自动回退到用户主目录 `LaunchDockData` 的逻辑。
- 没有保存启动坞路径时，`DockStorage.dock_path` 保持为 `None`，不会自动创建本地目录。
- 主界面在没有启动坞时显示引导卡片，提示用户先创建启动坞，并说明启动坞用于保存启动项目的存储位置。
- 没有创建或选择启动坞前，隐藏“新建”和“管理项目”入口，并阻止创建启动项目。
- “启动坞”页面改为“创建 / 选择启动坞”，未创建时显示说明文字，不再显示默认地址。
- 新增存储层测试，覆盖未配置启动坞时创建项目会提示用户先选择启动坞。
- 更新 `README.md`、`AGENTS.md` 和项目专属 Skill，记录首次使用为空、先创建启动坞再创建启动项目的前提逻辑。

### 验证情况

- 已运行 `python -m py_compile main.py launchdock\__init__.py launchdock\models.py launchdock\storage.py launchdock\app.py tests\test_storage.py`，通过。
- 已运行 `python -m unittest discover -s tests`，6 个测试全部通过。
- 已运行 Qt offscreen 首次启动模拟：使用临时用户目录启动应用，成功输出 `None 0 False`，确认无启动坞路径、无项目、未处于已创建启动坞状态。
- 本次为日常开发修改，未更新项目版本号。
