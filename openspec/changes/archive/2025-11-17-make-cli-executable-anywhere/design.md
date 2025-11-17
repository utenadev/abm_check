# Design

## Architecture

### Current State
現在、abm_checkは`pyproject.toml`の`[project.scripts]`セクションで`abm_check = "abm_check.cli.main:cli"`として定義されており、`pip install -e .`により、`abm_check`コマンドが利用可能になるはずである。

しかし、ユーザーがこのコマンドを任意のディレクトリから実行できるようにするには、以下が重要である：
1. インストール時にスクリプトがPATHに正しく追加されること
2. ユーザーがインストールを正しく行うこと

### Proposed Architecture
明確なインストール手順と、動作確認手順を提供することで、ユーザーがどこからでも実行できるようにする。

#### Components Affected
1. `pyproject.toml` - スクリプト定義の確認
2. `README.md` - インストール手順の更新
3. 新しい検証手順の追加

## Trade-offs and Considerations

### Positive Impacts
- ユーザーの利便性向上
- システム全体でのCLI利用性の向上

### Potential Issues
- ユーザー環境の違い（PATH設定など）
- インストール方法の違いによる影響（pip vs condaなど）
- 複数のPython環境がある場合の対応

### Error Handling
- インストール後にコマンドが実行可能でない場合のトラブルシューティング手順

## Validation
- 各OSでのインストール確認
- コマンドが任意のディレクトリから実行できることの確認
- README更新後のユーザーアクセプタンステスト