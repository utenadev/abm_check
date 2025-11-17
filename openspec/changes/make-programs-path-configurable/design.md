# Design

## Architecture

### Current State
現在、データベースファイルのパスは`Config`クラスの`programs_file`プロパティで管理されており、デフォルト値は`programs.yaml`です。`ProgramStorage`クラスはこの設定値を使用しています。

### Proposed Architecture
CLIオプションが追加され、`ProgramStorage`クラスがCLIから渡されたファイルパスを優先して使用するように変更されます。

#### Option Precedence
1. CLI Option (`--data-file`)
2. Config File
3. Default value (`programs.yaml`)

### Components Affected
1. `abm_check/cli/main.py` - CLIオプションの追加とProgramStorageへの渡し方
2. `abm_check/infrastructure/storage.py` - ProgramStorageクラスの引数変更
3. `abm_check/config.py` - 設定値の優先順位の調整（必要に応じて）

## Trade-offs and Considerations

### Positive Impacts
- ユーザーが複数のデータベースファイルを管理できる柔軟性の向上
- 後方互換性の維持

### Potential Issues
- 既存スクリプトとの互換性の確認が必要
- ドキュメントの更新作業が伴う

### Error Handling
- 指定されたファイルパスが存在しない場合やアクセスできない場合のエラーハンドリングが必要

## Validation
- 単体テストでCLIオプションが正しく機能することを検証
- 統合テストで実際のファイル操作が正しく行われることを検証