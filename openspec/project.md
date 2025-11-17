# Project Context

## Purpose
abm_checkはABEMA.tvの番組情報を取得・管理するPython製CLIツールです。yt-dlpを使用してABEMAの番組情報を自動取得し、YAML形式でデータベース化、Markdown形式で可読性の高い番組情報を生成します。cron等での自動実行に最適化されています。

### 主な機能
- ABEMA番組の全エピソード情報を自動取得
- 複数シーズンの自動検出（シーズン1が12話以上の場合）
- YAML形式でのデータ永続化（programs.yaml）
- Markdown形式での見やすい番組情報生成（各番組フォルダ内のprogram.md）
- 番組更新時の差分検出（新規エピソード、プレミアム→無料変更）
- ダウンロード対象エピソードのURL一覧生成
- プレミアム限定エピソードの正確な判定

## Tech Stack
- Python 3.9+
- yt-dlp（ABEMA情報取得）
- PyYAML（データ永続化）
- Click（CLIフレームワーク）
- python-dateutil（日付操作）

## Project Conventions

### Code Style
- Black（line-length = 100）を使用したコードフォーマット
- Ruffによる静的解析
- MyPyによる型チェック
- クリーンアーキテクチャを採用（ドメイン・アプリケーション・インフラ・プレゼンテーション層の分離）

### Architecture Patterns
- クリーンアーキテクチャを採用
- ドメイン・アプリケーション・インフラ・プレゼンテーション層の分離
- テスト容易性と保守性を考慮

### Testing Strategy
- pytestを使用したテストスイート
- ドメインモデルと主要ロジックのユニットテスト
- インフラ層のモックテスト
- CLIコマンドの統合テスト

### Git Workflow
- Git Flowに似たブランチ戦略（main、develop、feature、release、hotfix）
- Conventional Commitsに準拠したコミットメッセージ
- PRベースでのマージとコードレビュー

## Domain Context
### 主要なデータモデル
- Program（番組）: id, title, description, url, thumbnail_url, total_episodes, latest_episode_number, episodes, fetched_at, updated_at
- Episode（エピソード）: id, number, title, description, duration, thumbnail_url, is_downloadable, is_premium_only, download_url, formats, upload_date

### 重要な内部機能
- 複数シーズン検出ロジック（シーズン1が12話以上の場合、シーズン2以降の探索）
- プレミアム判定ロジック（yt-dlpの`availability`フィールドにより判定）
- 差分検出ロジック（新規エピソード、プレミアム→無料変更）

## Important Constraints
- yt-dlpが事前にインストールされている必要あり
- ABEMAのサイト構造変更に影響される可能性あり
- 複数シーズンの自動検出は経験則に基づく（12話以上で次のシーズンを探索）
- プレミアム判定はyt-dlpのavailabilityフィールドに依存

## External Dependencies
- yt-dlp: ABEMA番組情報の取得
- PyYAML: YAML形式でのデータ永続化
- Click: CLIコマンドの実装
- python-dateutil: 日付操作
- pytest: テストスイート
