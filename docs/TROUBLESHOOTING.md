# Troubleshooting Guide

abm_checkの使用中に発生する可能性のある問題と解決策をまとめています。

## 目次

- [インストール関連](#インストール関連)
- [yt-dlp関連](#yt-dlp関連)
- [番組情報取得関連](#番組情報取得関連)
- [データ保存関連](#データ保存関連)
- [CLI動作関連](#cli動作関連)
- [設定ファイル関連](#設定ファイル関連)
- [その他](#その他)

## インストール関連

### pip install でエラーが発生する

**症状:**
```
ERROR: Could not find a version that satisfies the requirement abm_check
```

**原因:** Python バージョンが古い

**解決策:**
```bash
# Pythonバージョンを確認
python --version

# Python 3.8以上が必要
# アップグレードするか、pyenvなどで新しいバージョンをインストール
```

### 依存パッケージのインストールエラー

**症状:**
```
ERROR: Failed building wheel for pyyaml
```

**原因:** C拡張のビルドに必要なツールが不足

**解決策:**

**Windows:**
```bash
# Microsoft C++ Build Tools をインストール
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**macOS:**
```bash
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-dev build-essential
```

## yt-dlp関連

### yt-dlp が見つからない

**症状:**
```
ModuleNotFoundError: No module named 'yt_dlp'
```

**原因:** yt-dlpがインストールされていない

**解決策:**
```bash
pip install yt-dlp

# またはシステム全体にインストール
pip install --user yt-dlp
```

### yt-dlp のバージョンが古い

**症状:**
- 番組情報が正しく取得できない
- `availability` フィールドが取得できない

**原因:** yt-dlpのバージョンが古く、ABEMAの最新仕様に対応していない

**解決策:**
```bash
# yt-dlpを最新版にアップデート
pip install --upgrade yt-dlp

# バージョン確認
yt-dlp --version
```

### yt-dlp の取得が遅い・タイムアウトする

**症状:**
- 番組情報取得に異常に時間がかかる
- ネットワークタイムアウトエラーが発生

**原因:** ネットワーク環境、ABEMAサーバーの負荷

**解決策:**
```bash
# リトライオプションを追加（将来のバージョンで対応予定）
# 現在は時間をおいて再実行

# または、abm_check.yaml で設定を調整
ytdlp:
  socket_timeout: 30  # タイムアウト時間を延長
```

## 番組情報取得関連

### 番組が見つからない

**症状:**
```
Error: Program not found: 26-249
```

**原因:**
1. 番組IDが間違っている
2. 番組が配信終了している
3. ABEMAの仕様変更

**解決策:**
```bash
# 番組URLをブラウザで確認
# 正しい番組IDを使用

# 例: https://abema.tv/video/title/26-249
# → 番組ID: 26-249

# 番組が配信終了している場合は取得不可
```

### プレミアム限定エピソードが正しく判定されない

**症状:**
- 本来プレミアム限定のはずが、DL可能と表示される
- または逆のパターン

**原因:**
1. yt-dlpのバージョンが古い
2. ABEMAの仕様変更

**解決策:**
```bash
# yt-dlpを最新版にアップデート
pip install --upgrade yt-dlp

# それでも改善しない場合、Issueを報告
# https://github.com/your-org/abm_check/issues
```

### 複数シーズンが検出されない

**症状:**
- シーズン2以降のエピソードが取得されない

**原因:**
1. シーズン1が12話未満（デフォルト閾値）
2. ABEMAの URL パターンが変更された

**解決策:**
```bash
# abm_check.yaml で閾値を調整
season_detection:
  threshold: 6  # 6話以上でシーズン検出

# または、手動で全シーズンを確認
# ABEMAのWebサイトでシーズン数を確認
```

### 特別エピソード（PV等）が通常エピソードとして扱われる

**症状:**
- PVが「第100話」として表示される

**原因:** エピソード番号が100未満

**解決策:**
- これは仕様です
- abm_checkは エピソード番号 >= 100 を特別エピソードとして分類
- ABEMAが100未満の番号を割り当てている場合、通常エピソードとして扱われます

## データ保存関連

### programs.yaml が壊れた

**症状:**
```
Error: Invalid YAML format
yaml.scanner.ScannerError: ...
```

**原因:** YAMLファイルの手動編集でシンタックスエラー

**解決策:**
```bash
# バックアップがあれば復元
cp programs.yaml.backup programs.yaml

# バックアップがない場合、再度番組を追加
abm_check add <番組ID>

# 今後のため、定期的にバックアップを作成
cp programs.yaml programs.yaml.backup
```

### ファイル書き込み権限エラー

**症状:**
```
PermissionError: [Errno 13] Permission denied: 'programs.yaml'
```

**原因:** ファイルが読み取り専用、または別プロセスで開かれている

**解決策:**
```bash
# ファイル権限を確認
ls -l programs.yaml

# 読み取り専用を解除 (Unix/Linux)
chmod u+w programs.yaml

# Windows: エクスプローラーでプロパティ → 読み取り専用のチェックを外す

# ファイルが開かれている場合は閉じる
```

### 出力ディレクトリが作成されない

**症状:**
- `output/` ディレクトリが作成されない
- ファイルが見つからないエラー

**原因:** ディレクトリ作成権限がない

**解決策:**
```bash
# 手動でディレクトリを作成
mkdir -p output

# または、別の場所を指定
abm_check add 26-249  # outputディレクトリに保存

# 権限を確認
ls -ld .
```

## CLI動作関連

### コマンドが見つからない

**症状:**
```
bash: abm_check: command not found
```

**原因:**
1. パスが通っていない
2. 開発モードでインストールしていない

**解決策:**
```bash
# 開発モードでインストール
pip install -e .

# または、直接実行
python -m abm_check <command>

# パスを確認
which abm_check
echo $PATH
```

### 詳細ログが表示されない

**症状:**
- `-v` オプションをつけても詳細が出ない

**原因:** ロガーの設定問題

**解決策:**
```bash
# 現在のバージョンでは未実装の可能性
# 代わりに標準出力を確認

# デバッグ用に Python から直接実行
python -c "
from abm_check.infrastructure.fetcher import AbemaFetcher
fetcher = AbemaFetcher()
program = fetcher.fetch_program_info('26-249')
print(program)
"
```

### 更新時に変更が検出されない

**症状:**
```
abm_check update 26-249
# 新規エピソードがあるはずなのに検出されない
```

**原因:**
1. 既に最新のデータを保持している
2. エピソードがプレミアム限定

**解決策:**
```bash
# データを確認
abm_check view 26-249

# 強制的に再取得
abm_check add 26-249  # 既存データを上書き

# ABEMAのWebサイトで実際のエピソード状況を確認
```

## 設定ファイル関連

### abm_check.yaml が読み込まれない

**症状:**
- 設定ファイルを作成したが、デフォルト値が使われる

**原因:**
1. ファイル名が間違っている
2. YAMLの文法エラー
3. ファイルの配置場所が間違っている

**解決策:**
```bash
# ファイル名を確認（正確に abm_check.yaml）
ls -la abm_check.yaml

# YAMLの文法チェック
python -c "import yaml; yaml.safe_load(open('abm_check.yaml'))"

# カレントディレクトリに配置されているか確認
pwd
ls abm_check.yaml

# サンプルファイルをコピー
cp abm_check.yaml.example abm_check.yaml
```

### 設定値が反映されない

**症状:**
- threshold を変更したが、12話で検出される

**原因:** 設定ファイルの構造が間違っている

**解決策:**
```yaml
# 正しい構造
season_detection:
  threshold: 15
  max_seasons: 10

# 間違い（トップレベルに書いている）
threshold: 15  # これは無視される
```

## その他

### メモリ使用量が多い

**症状:**
- 複数番組を更新すると、メモリ使用量が増加する

**原因:** エピソード情報を全てメモリに保持

**解決策:**
```bash
# 一度に大量の番組を更新しない
# 番組を分けて更新

abm_check update 26-249
abm_check update 26-156
# ... 個別に実行
```

### Python 3.13 で動作しない

**症状:**
```
SyntaxError: ...
```

**原因:** Python 3.13は まだ正式サポート対象外

**解決策:**
```bash
# Python 3.8 〜 3.12 を使用
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```

### Windows で文字化けする

**症状:**
- 日本語が正しく表示されない
- `����` のような文字列になる

**原因:** コンソールのエンコーディング設定

**解決策:**
```bash
# PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# コマンドプロンプト
chcp 65001

# 環境変数を設定
set PYTHONIOENCODING=utf-8
```

## サポート

上記で解決しない場合:

1. **GitHub Issues**: バグ報告・機能リクエスト
   - https://github.com/your-org/abm_check/issues

2. **GitHub Discussions**: 一般的な質問
   - https://github.com/your-org/abm_check/discussions

3. **デバッグ情報の提供**:
   ```bash
   # 以下の情報を提供してください
   python --version
   pip list | grep -E "(yt-dlp|pyyaml|click)"
   abm_check version
   
   # エラーの完全なスタックトレース
   ```

---

最終更新: 2025-11-09
