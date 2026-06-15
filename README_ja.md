<div align="center">
  <h1 align="center">
    <img src="assets/icon.png" width="180" alt="LaunchDock logo" />
    <br />
    LaunchDock
  </h1>

  <p>
    学習、仕事、個人プロジェクトで使うリンクやローカルファイルを整理し、ワンクリックで作業状態に入るための軽量ローカルランチャーです。
    <br />
    A lightweight local launch dock for opening project links and files with one click.
  </p>

  <p><i>ローカル保存、ユーザー選択の保存先、クラウドアカウント不要。</i></p>
</div>

<div align="center">

![platform](https://img.shields.io/badge/platform-Windows-blue)
[![GitHub release](https://img.shields.io/github/v/release/Dylanliiiii/LaunchDock)](https://github.com/Dylanliiiii/LaunchDock/releases)
[![downloads](https://img.shields.io/github/downloads/Dylanliiiii/LaunchDock/total)](https://github.com/Dylanliiiii/LaunchDock/releases)
![python](https://img.shields.io/badge/Python-3.x-3776AB)
![UI](https://img.shields.io/badge/UI-PySide6%20%2B%20QFluentWidgets-00c8d7)

</div>

### [中文说明](README.md) | [English Readme](README_en.md) | 日本語 Readme

---

## クイックスタート

1. [GitHub Releases](https://github.com/Dylanliiiii/LaunchDock/releases) から最新版をダウンロードします。
2. 中国大陆で GitHub に安定して接続できない場合は、`LaunchDock-vVERSION-windows-china-setup.exe` をおすすめします。
3. GitHub に問題なく接続できる場合は、`LaunchDock-vVERSION-windows-global-setup.exe` を使用してください。
4. インストール後、初回起動時にローカルの「起動ドック」フォルダーを作成または選択します。

ポータブル zip 版も提供しています。

- `LaunchDock-vVERSION-windows-global.zip`
- `LaunchDock-vVERSION-windows-china.zip`

## LaunchDock の主な機能

- 学習、仕事、個人用など複数のプロジェクトを作成できます。
- 各プロジェクトに Web リンク、ローカルファイル、フォルダーのパスを保存できます。
- デフォルトで開く項目を切り替えられます。
- プロジェクト内の有効な項目をワンクリックで開けます。
- プロジェクトと起動項目の追加、編集、削除、まとめて管理に対応しています。
- ユーザーが選んだローカルフォルダーにデータを保存します。
- GitHub 更新元と、中国向けの CNB 更新元に対応しています。

## ダウンロード

- GitHub Releases: [https://github.com/Dylanliiiii/LaunchDock/releases](https://github.com/Dylanliiiii/LaunchDock/releases)
- CNB Releases: [https://cnb.cool/DylanLIIIII/LaunchDock/-/releases](https://cnb.cool/DylanLIIIII/LaunchDock/-/releases)

グローバル版は GitHub に安定して接続できるユーザー向けです。中国版は国内ミラーの更新元を使用するため、中国大陆で VPN なしに使う場合に適しています。

## ローカルデータ構成

LaunchDock はユーザーのプロジェクトデータをアプリ本体のフォルダーに保存しません。ユーザーが選んだフォルダーを起動ドックのルートとして使用します。

```text
選択した起動ドックフォルダー/
  launchdock.json
  projects/
    pytorch/
      project.json
    linear-algebra/
      project.json
```

- `launchdock.json` はプロジェクト順、最近使ったプロジェクト、ウィンドウ設定などを保存します。
- `projects/` はすべてのプロジェクトを保存します。
- 各プロジェクトは個別のフォルダーを持ちます。
- 各プロジェクトのリンク情報は `project.json` に保存されます。

## ソースから実行

Python の仮想環境を使うことをおすすめします。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m launchdock.app
```

## Windows パッケージ作成

Windows パッケージを作成します。

```powershell
.\scripts\build-windows.ps1
```

このスクリプトは `assets/icon.png` から一時的なパッケージ用アイコンを生成し、元のアイコンファイルは上書きしません。

中国版の例：

```powershell
.\scripts\build-windows.ps1 `
  -UpdateChannel china `
  -UpdateRepoUrl "国内ミラーリポジトリ URL" `
  -ReleasePageUrl "国内ダウンロードページ URL"
```

Inno Setup 6 でインストーラーを作成します。

```powershell
.\scripts\build-installer.ps1
```

正式リリースの成果物は `dist/vVERSION/` に保存されます。

## リリース時の内容

正式リリースでは、次のファイルを提供します。

- グローバル zip: `LaunchDock-vVERSION-windows-global.zip`
- 中国版 zip: `LaunchDock-vVERSION-windows-china.zip`
- グローバルインストーラー: `LaunchDock-vVERSION-windows-global-setup.exe`
- 中国版インストーラー: `LaunchDock-vVERSION-windows-china-setup.exe`

リリース本文には、グローバル版は GitHub を更新元に使い、中国版は CNB などの国内ミラーを使うことを明記します。

## 開発メモ

- UI 層: `launchdock/app.py`
- ビジネスモデル: `launchdock/models.py`
- ローカル保存: `launchdock/storage.py`
- 協作ルール: `AGENTS.md`
- コードまたはドキュメントを変更した場合は、`development-log.md` を更新します。

## License

このプロジェクトは AGPL-3.0 license の下で公開されています。
