# API Reference

abm_checkの内部APIリファレンスです。各モジュールの詳細な使用方法を説明します。

## モジュール一覧

- [Config](config.md) - 設定管理
- [Models](models.md) - ドメインモデル
- [Exceptions](exceptions.md) - カスタム例外
- [Fetcher](fetcher.md) - 番組情報取得
- [Storage](storage.md) - データ永続化
- [Markdown](markdown.md) - Markdown生成
- [Updater](updater.md) - 更新・差分検出
- [DownloadList](download_list.md) - ダウンロードURL一覧生成

## クイックスタート

### 番組情報を取得

```python
from abm_check.infrastructure.fetcher import AbemaFetcher

fetcher = AbemaFetcher()
program = fetcher.fetch_program_info("26-249")

print(f"Title: {program.title}")
print(f"Total Episodes: {program.total_episodes}")
```

### YAMLに保存

```python
from abm_check.infrastructure.storage import ProgramStorage

storage = ProgramStorage()
storage.save_program(program)
```

### Markdownを生成

```python
from abm_check.infrastructure.markdown import MarkdownGenerator

generator = MarkdownGenerator()
md_content = generator.generate_program_md(program)
print(md_content)
```

## アーキテクチャ

abm_checkはクリーンアーキテクチャを採用しています:

```
┌─────────────────────────────────────┐
│      Presentation Layer (CLI)       │
│         cli/main.py                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Infrastructure Layer           │
│  - fetcher.py (yt-dlp integration)  │
│  - storage.py (YAML persistence)    │
│  - markdown.py (Markdown generation)│
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Domain Layer                 │
│  - models.py (Business Models)       │
│  - exceptions.py (Domain Exceptions) │
└──────────────────────────────────────┘
```

### レイヤーの依存関係

- **Presentation → Infrastructure → Domain**
- 上位レイヤーは下位レイヤーに依存
- 下位レイヤーは上位レイヤーを知らない

## 使用例

詳細な使用例は各モジュールのドキュメントを参照してください。
