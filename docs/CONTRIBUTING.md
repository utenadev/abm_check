# Contributing to abm_check

abm_checkプロジェクトへの貢献ありがとうございます！このドキュメントでは、開発環境のセットアップから、コード規約、プルリクエストの作成方法まで説明します。

## 目次

- [開発環境のセットアップ](#開発環境のセットアップ)
- [プロジェクト構成](#プロジェクト構成)
- [コーディング規約](#コーディング規約)
- [テストの実行](#テストの実行)
- [コミットメッセージ](#コミットメッセージ)
- [プルリクエスト](#プルリクエスト)
- [Issue報告](#issue報告)

## 開発環境のセットアップ

### 前提条件

- Python 3.8以上
- Git
- yt-dlp

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/abm_check.git
cd abm_check
```

### 2. 仮想環境の作成と有効化

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
# 開発依存関係を含めてインストール
pip install -e ".[dev]"
```

開発依存関係には以下が含まれます:
- pytest: テストフレームワーク
- pytest-cov: カバレッジ計測
- pytest-mock: モックテスト
- ruff: Linter/Formatter
- mypy: 型チェック

### 4. 動作確認

```bash
# CLIが動作することを確認
abm_check version

# テストを実行
pytest tests/unit/ -v

# カバレッジ付きでテストを実行
pytest tests/unit/ --cov=abm_check --cov-report=html
```

## プロジェクト構成

abm_checkはクリーンアーキテクチャを採用しています:

```
abm_check/
├── abm_check/
│   ├── __init__.py
│   ├── __main__.py          # CLIエントリーポイント
│   ├── config.py            # 設定管理
│   ├── domain/              # ドメイン層（ビジネスロジック）
│   │   ├── models.py        # データモデル
│   │   └── exceptions.py    # カスタム例外
│   ├── infrastructure/      # インフラ層（外部システム連携）
│   │   ├── fetcher.py       # yt-dlpによる情報取得
│   │   ├── storage.py       # YAMLストレージ
│   │   ├── markdown.py      # Markdown生成
│   │   ├── updater.py       # 更新・差分検出
│   │   └── download_list.py # ダウンロードURL生成
│   └── cli/                 # プレゼンテーション層
│       └── main.py          # CLIコマンド実装
├── tests/
│   ├── unit/                # ユニットテスト
│   │   ├── test_models.py
│   │   ├── test_fetcher.py
│   │   ├── test_storage.py
│   │   ├── test_markdown.py
│   │   ├── test_config.py
│   │   └── test_exceptions.py
│   ├── integration/         # 統合テスト（今後追加予定）
│   └── e2e/                 # E2Eテスト（今後追加予定）
├── docs/                    # ドキュメント
├── pyproject.toml           # プロジェクト設定
└── README.md
```

### レイヤーの責務

1. **Domain層** (`domain/`)
   - ビジネスロジックとドメインモデル
   - 外部依存なし（純粋なPythonコード）
   - `Program`, `Episode`, `VideoFormat`などのモデル定義

2. **Infrastructure層** (`infrastructure/`)
   - 外部システムとの連携（yt-dlp, ファイルシステム）
   - Domain層のモデルを使用
   - 技術的な詳細を隠蔽

3. **Presentation層** (`cli/`)
   - ユーザーインターフェース（CLI）
   - InfrastructureとDomain層を使用
   - Clickフレームワークによるコマンド実装

## コーディング規約

### Python スタイルガイド

- PEP 8に準拠
- ruffによる自動フォーマット・Lintを使用
- 型ヒントを積極的に使用（Python 3.8+）

```python
# Good
def fetch_program_info(self, program_id: str) -> Program:
    """Fetch program information from ABEMA."""
    ...

# Bad (型ヒントなし)
def fetch_program_info(self, program_id):
    ...
```

### コメントとドキュメント

- すべてのpublicメソッドにdocstringを記述
- 複雑なロジックには説明コメントを追加
- docstringはGoogle形式を推奨

```python
def save_program(self, program: Program) -> None:
    """
    Save program to YAML file.
    
    Args:
        program: Program to save
        
    Raises:
        StorageError: If save fails
    """
    ...
```

### 命名規則

- クラス: `PascalCase`
- 関数・変数: `snake_case`
- 定数: `UPPER_SNAKE_CASE`
- プライベートメソッド: `_leading_underscore`

### インポート順序

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルアプリケーション

```python
import os
from pathlib import Path
from typing import List, Optional

import click
import yaml

from abm_check.domain.models import Program, Episode
from abm_check.domain.exceptions import FetchError
```

## テストの実行

### 全テストを実行

```bash
pytest tests/unit/ -v
```

### 特定のテストファイルを実行

```bash
pytest tests/unit/test_fetcher.py -v
```

### 特定のテストケースを実行

```bash
pytest tests/unit/test_fetcher.py::TestAbemaFetcher::test_fetch_program_info -v
```

### カバレッジレポート生成

```bash
# HTML形式のカバレッジレポート生成
pytest tests/unit/ --cov=abm_check --cov-report=html

# ターミナルにカバレッジ表示
pytest tests/unit/ --cov=abm_check --cov-report=term
```

### テスト作成ガイドライン

1. **ユニットテストは必須**
   - 新しい機能を追加する場合、対応するテストを必ず追加
   - カバレッジは80%以上を目標

2. **テストの命名規則**
   ```python
   def test_<メソッド名>_<条件>_<期待結果>():
       """Test <何をテストするか>."""
   ```

3. **Arrange-Act-Assert パターン**
   ```python
   def test_save_program_new():
       """Test saving a new program."""
       # Arrange: テストデータの準備
       storage = ProgramStorage("test.yaml")
       program = Program(...)
       
       # Act: テスト対象の実行
       storage.save_program(program)
       
       # Assert: 結果の検証
       programs = storage.load_programs()
       assert len(programs) == 1
       assert programs[0].id == program.id
   ```

4. **モックの使用**
   - 外部依存（yt-dlp, ファイルシステム）はモック化
   - `unittest.mock`または`pytest-mock`を使用

5. **Parametrized Tests**
   - 複数の入力パターンがある場合は`pytest.mark.parametrize`を使用
   ```python
   @pytest.mark.parametrize("program_id,expected", [
       ("26-249", "26-249"),
       ("189-85", "189-85"),
   ])
   def test_program_ids(program_id: str, expected: str):
       assert program_id == expected
   ```

## コミットメッセージ

### フォーマット

```
<type>: <subject>

<body>

<footer>
```

### Type

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更
- `style`: コードフォーマット（機能変更なし）
- `refactor`: リファクタリング
- `test`: テストの追加・修正
- `chore`: ビルドプロセス、補助ツールの変更

### 例

```
feat: Add multi-season detection for programs with 12+ episodes

- Automatically detect and fetch season 2, 3, etc. when season 1 has 12+ episodes
- Add configuration option for season threshold
- Add tests for multi-season detection logic

Closes #123
```

## プルリクエスト

### プルリクエスト作成前のチェックリスト

- [ ] すべてのテストが通る (`pytest tests/unit/ -v`)
- [ ] カバレッジが低下していない
- [ ] コードスタイルが統一されている (`ruff check .`)
- [ ] 型チェックが通る (`mypy abm_check`)
- [ ] 新機能の場合、ドキュメントを更新
- [ ] 変更内容に対応するテストを追加

### プルリクエストテンプレート

```markdown
## 概要
この変更の目的を簡潔に説明

## 変更内容
- 変更点1
- 変更点2

## テスト
- 追加したテストケース
- 手動テスト結果

## チェックリスト
- [ ] テストが通る
- [ ] カバレッジが低下していない
- [ ] ドキュメントを更新

## 関連Issue
Closes #123
```

### レビュープロセス

1. プルリクエストを作成
2. レビュアーが指定される
3. レビューコメントに対応
4. 承認後、mainブランチにマージ

## Issue報告

### バグ報告

```markdown
## バグの概要
簡潔な説明

## 再現手順
1. 手順1
2. 手順2

## 期待する動作
何が起こるべきか

## 実際の動作
何が起こったか

## 環境
- OS: Windows 11 / macOS 14 / Ubuntu 22.04
- Python: 3.11.5
- abm_check: 0.1.0
```

### 機能リクエスト

```markdown
## 機能の概要
簡潔な説明

## 背景・課題
なぜこの機能が必要か

## 提案する解決策
どのように実装するか

## 代替案
他に考えられるアプローチ
```

## 質問・サポート

- GitHub Discussions: 一般的な質問
- GitHub Issues: バグ報告、機能リクエスト

---

貢献いただきありがとうございます！
