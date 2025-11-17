# abm_check

ABEMA番組情報管理ツール - yt-dlpを使ってABEMAの番組情報を取得・管理するCLIツール

## 概要

`abm_check`は、ABEMA.tvの番組情報を自動取得し、YAML形式でデータベース化、Markdown形式で可読性の高い番組情報を生成するPython製CLIツールです。

### 主な機能

- 📺 ABEMA番組の全エピソード情報を自動取得
- 🔍 複数シーズンの自動検出（シーズン1が12話以上の場合、シーズン2以降も探索）
- 💾 YAML形式でのデータ永続化
- 📝 Markdown形式での見やすい番組情報生成
- 🆕 番組更新時の差分検出（新規エピソード、プレミアム→無料変更）
- 📋 ダウンロード対象エピソードのURL一覧生成
- 🔒 プレミアム限定エピソードの正確な判定
- ⏰ cron等での自動実行に最適

## 必要要件

- Python 3.8以上
- yt-dlp（インストール済み前提）

## インストール

### 開発モードでのインストール（推奨）

プロジェクトディレクトリで以下のコマンドを実行し、開発モードでインストールします:

```bash
cd abm_check
pip install -e .
```

これにより、`abm_check`コマンドがシステムのPATHに追加され、任意のディレクトリから実行できるようになります。

### 使用方法

インストール後は、任意のディレクトリから以下のように実行できます:

```bash
abm_check version
abm_check list
abm_check update
```

### 代替方法（プロジェクトディレクトリ限定）

プロジェクトディレクトリから直接実行する方法:

```bash
python -m abm_check <command>
```

## 使い方

### 番組を追加

番組IDまたはURLを指定して番組情報を取得:

```bash
# 番組IDで追加
abm_check add 26-156

# URLで追加
abm_check add https://abema.tv/video/title/26-156
```

実行すると:
- `programs.yaml` - 番組データベース（YAML形式）
- `{番組ID}/program.md` - 番組詳細情報（Markdown形式）

が生成されます。

### 番組一覧を表示

登録済みの番組一覧を表示:

```bash
abm_check list
```

出力例:
```
1 26-156 その着せ替え人形は恋をする
2 26-253 最後にひとつだけお願いしてもよろしいでしょうか
```

### 番組詳細を表示

番組ID、または `list` コマンドで表示されるシーケンス番号を指定して詳細情報を表示:

```bash
# 番組IDで表示
abm_check view 26-156

# シーケンス番号で表示 (listコマンドの出力例を参照)
abm_check view 1
```

Markdown形式の番組情報が表示されます。

### 番組情報を更新

既存番組の情報を更新し、新規エピソードやDL可否変更を検出:

```bash
# 特定の番組を更新
abm_check update 26-156

# 全番組を更新
abm_check update

# 出力ファイル名を指定
abm_check update 26-156 -o new_episodes.txt
```

更新時に検出される変更:
- **新規エピソード**: 前回取得時に存在しなかったDL可能なエピソード
- **プレミアム→無料**: 前回プレミアム限定だったが無料になったエピソード

検出された変更は`download_urls.txt`（デフォルト）に出力されます。

### バージョン情報

```bash
abm_check version
```

## インストール確認

インストールが正しく完了したか確認するには、任意のディレクトリで以下のコマンドを実行します:

```bash
abm_check version
```

正常にインストールされていれば、バージョン情報が表示されます。

もし "command not found" や "abm_check は、内部コマンドまたは外部コマンドとして認識されていません" といったエラーが発生する場合、以下の手順を確認してください:

1. `pip install -e .` がプロジェクトディレクトリで正しく実行されたか
2. ターミナル/コマンドプロンプトを再起動して、PATHの変更を反映したか
3. PythonのスクリプトディレクトリがシステムのPATHに追加されているか

## 技術的な仕組み

### アーキテクチャ

クリーンアーキテクチャを採用:

```
abm_check/
├── domain/          # ドメイン層（ビジネスロジック）
│   ├── models.py    # データモデル（Program, Episode, VideoFormat）
│   └── exceptions.py # カスタム例外
├── infrastructure/  # インフラ層（外部システム連携）
│   ├── fetcher.py   # yt-dlpを使った番組情報取得
│   ├── storage.py   # YAMLデータベース管理
│   ├── markdown.py  # Markdown生成
│   ├── updater.py   # 番組更新・差分検出
│   └── download_list.py # DL URL一覧生成
└── cli/             # プレゼンテーション層
    └── main.py      # CLIコマンド実装
```

### 複数シーズン検出ロジック

ABEMAの番組は複数シーズンが存在する場合があります。`abm_check`は以下のロジックで自動検出します:

1. **シーズン1の取得**
   ```
   https://abema.tv/video/title/{番組ID}
   ```
   デフォルトURLでシーズン1のエピソード情報を取得

2. **シーズン2以降の探索**
   - シーズン1が **12話以上** の場合、追加シーズンが存在する可能性を考慮
   - シーズン2, 3, 4...と順番に以下のURLパターンで試行:
     ```
     https://abema.tv/video/title/{番組ID}?s={番組ID}_s{シーズン番号}&eg={番組ID}_eg0
     ```
   - エピソードが取得できなくなった時点で探索終了

3. **全エピソードの統合**
   - 全シーズンのエピソードを1つの番組データとして統合
   - 通し番号は各シーズンで継続（シーズン2の第1話は通し番号13話）

例: `26-156`（その着せ替え人形は恋をする）
- シーズン1: 12話（エピソード1-12）
- シーズン2: 12話（エピソード13-24）
- → 合計24話として取得・管理

### プレミアム判定ロジック

yt-dlpが返す`availability`フィールドを使用:

```python
availability = entry.get('availability', '')
is_premium = availability == 'premium_only'
is_downloadable = has_formats and not is_premium
```

- `availability == 'public'` → 無料視聴可能（DL可能）
- `availability == 'premium_only'` → プレミアム限定（DL不可）

### 差分検出ロジック

番組更新時、以下の2種類の変更を検出します:

#### 1. 新規エピソード検出

```python
for new_ep in new_program.episodes:
    old_ep = old_episodes.get(new_ep.id)
    
    if old_ep is None:  # 前回取得時に存在しなかった
        if new_ep.is_downloadable:  # かつDL可能
            new_episodes_list.append(new_ep)
```

#### 2. プレミアム→無料変更検出

```python
for new_ep in new_program.episodes:
    old_ep = old_episodes.get(new_ep.id)
    
    if old_ep is not None:  # 前回取得時に存在した
        if old_ep.is_premium_only and new_ep.is_downloadable:
            # プレミアムから無料に変更
            premium_to_free_list.append(new_ep)
```

### エピソード分類ロジック

エピソード番号に基づいて自動分類:

- **通常エピソード**: エピソード番号 < 100
- **特別エピソード（PV等）**: エピソード番号 >= 100

この分類により、最新話番号の算出時に特別エピソードを除外し、正確な放送進行状況を把握できます。

### エピソードURL生成

エピソードIDから視聴URLを生成:

```python
def get_episode_url(self, program_id: str) -> str:
    """Generate episode URL from episode ID."""
    return f"https://abema.tv/video/episode/{self.id}"
```

例:
- Episode ID: `26-156_s1_p6`
- URL: `https://abema.tv/video/episode/26-156_s1_p6`

### ダウンロードURL一覧フォーマット

```txt
# {番組タイトル} - New Episodes
# Episode {話数}: {エピソードタイトル}
https://abema.tv/video/episode/{エピソードID}

# {番組タイトル} - Premium to Free
https://abema.tv/video/episode/{エピソードID}
```

新規エピソードには話数とタイトルをコメントで付与し、プレミアム→無料変更はURLのみを出力します。

## データ構造

### programs.yaml

```yaml
programs:
  - id: "26-156"
    title: "その着せ替え人形は恋をする"
    description: "番組説明..."
    url: "https://abema.tv/video/title/26-156"
    thumbnailUrl: "https://..."
    totalEpisodes: 24
    latestEpisodeNumber: 12
    fetchedAt: "2025-01-08T12:00:00"
    updatedAt: "2025-01-08T15:30:00"
    episodes:
      - id: "26-156_s1_p1"
        number: 1
        title: "#1 タイトル"
        description: "エピソード説明"
        duration: 1420
        thumbnailUrl: "https://..."
        isDownloadable: true
        isPremiumOnly: false
        downloadUrl: "https://..."
        uploadDate: "20230122"
lastUpdated: "2025-01-08T15:30:00"
```

### {番組ID}/program.md

Markdown形式で番組情報を見やすく整形:

```markdown
# 番組タイトル

## 基本情報

- 番組ID: 26-156
- 総エピソード数: 24話
- 最新話: 12話
- 最終更新: 2025-01-08 15:30:00

## 番組説明

番組の説明文...

## エピソード一覧

- 通常エピソード: 12話
- DL可能: 10話
- プレミアム限定: 2話
- 特別エピソード (PV等): 0話

### 通常エピソード

| DL可否 | 話数 | タイトル |
|--------|------|----------|
| ✅ | 1 | #1 タイトル |
| 🔒 | 2 | #2 タイトル |
...

### 特別エピソード (PV等)

| DL可否 | 話数 | タイトル |
|--------|------|----------|
| ✅ | 500 | PVタイトル |
```

## 共通オプション

- `--verbose` / `-v`: 詳細ログ出力
- `--quiet` / `-q`: エラーのみ出力
- `--data-file`: データベースファイルのパス (デフォルト: programs.yaml)

```bash
abm_check add 26-156 -v
abm_check update -q
abm_check list --data-file custom_programs.yaml
```

cron等での自動実行に適した簡潔なログ出力を採用しています。

## ライセンス

MIT License

## 作者

abm_check development team
