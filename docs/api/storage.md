# Storage API Reference

データ永続化モジュール（YAML）

## クラス

### `ProgramStorage`

YAML形式で番組データを管理するクラス。

#### コンストラクタ

```python
ProgramStorage(data_file: str = None, config=None)
```

**パラメータ:**
- `data_file`: YAMLファイルのパス（省略時は設定ファイルの値を使用）
- `config`: Configインスタンス（省略時はデフォルト設定）

**例:**
```python
from abm_check.infrastructure.storage import ProgramStorage

# デフォルト設定（programs.yaml）
storage = ProgramStorage()

# カスタムファイルを指定
storage = ProgramStorage("custom_programs.yaml")

# カスタム設定で初期化
from abm_check.config import Config
config = Config("custom.yaml")
storage = ProgramStorage(config=config)
```

#### メソッド

##### `save_program(program: Program) -> None`

番組をYAMLファイルに保存します。既存の番組は上書きされます。

**パラメータ:**
- `program`: 保存するProgramオブジェクト

**例外:**
- `StorageError`: 保存に失敗

**例:**
```python
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.infrastructure.fetcher import AbemaFetcher

fetcher = AbemaFetcher()
storage = ProgramStorage()

program = fetcher.fetch_program_info("26-249")
storage.save_program(program)
```

##### `load_programs() -> List[Program]`

すべての番組をYAMLファイルから読み込みます。

**戻り値:** Programオブジェクトのリスト

**例外:**
- `StorageError`: 読み込みに失敗

**例:**
```python
storage = ProgramStorage()
programs = storage.load_programs()

for program in programs:
    print(f"{program.id}: {program.title}")
```

##### `find_program(program_id: str) -> Optional[Program]`

番組IDで番組を検索します。

**パラメータ:**
- `program_id`: 番組ID

**戻り値:** Programオブジェクト（見つからない場合はNone）

**例:**
```python
storage = ProgramStorage()
program = storage.find_program("26-249")

if program:
    print(f"Found: {program.title}")
else:
    print("Not found")
```

##### `delete_program(program_id: str) -> None`

番組を削除します。

**パラメータ:**
- `program_id`: 削除する番組ID

**例外:**
- `ProgramNotFoundError`: 番組が見つからない
- `StorageError`: 削除に失敗

**例:**
```python
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.domain.exceptions import ProgramNotFoundError

storage = ProgramStorage()

try:
    storage.delete_program("26-249")
    print("Deleted successfully")
except ProgramNotFoundError:
    print("Program not found")
```

##### `get_all_program_ids() -> List[str]`

すべての番組IDを取得します。

**戻り値:** 番組IDのリスト

**例:**
```python
storage = ProgramStorage()
program_ids = storage.get_all_program_ids()

print(f"Total programs: {len(program_ids)}")
for program_id in program_ids:
    print(f"  - {program_id}")
```

## データ形式

### YAML構造

```yaml
programs:
  - id: "26-249"
    title: "番組タイトル"
    description: "番組説明"
    url: "https://abema.tv/video/title/26-249"
    thumbnailUrl: "https://example.com/thumb.png"
    totalEpisodes: 24
    latestEpisodeNumber: 12
    fetchedAt: "2025-01-08T12:00:00"
    updatedAt: "2025-01-08T15:30:00"
    episodes:
      - id: "26-249_s1_p1"
        number: 1
        title: "第1話"
        description: "エピソード説明"
        duration: 1420
        thumbnailUrl: "https://example.com/ep1.jpg"
        isDownloadable: true
        isPremiumOnly: false
        downloadUrl: "https://abema.tv/video/episode/26-249_s1_p1"
        uploadDate: "20230122"
        formats:
          - formatId: "1080p"
            resolution: "1920x1080"
            tbr: 2500.0
            url: "https://example.com/stream"
lastUpdated: "2025-01-08T15:30:00"
```

### フィールド説明

**Program:**
- `id`: 番組ID
- `title`: 番組タイトル
- `description`: 番組説明
- `url`: 番組URL
- `thumbnailUrl`: サムネイルURL
- `totalEpisodes`: 総エピソード数
- `latestEpisodeNumber`: 最新話番号（通常エピソードのみ）
- `fetchedAt`: 初回取得日時（ISO 8601形式）
- `updatedAt`: 最終更新日時（ISO 8601形式）
- `episodes`: エピソードリスト

**Episode:**
- `id`: エピソードID
- `number`: エピソード番号
- `title`: エピソードタイトル
- `description`: 説明
- `duration`: 長さ（秒）
- `thumbnailUrl`: サムネイルURL
- `isDownloadable`: ダウンロード可能か
- `isPremiumOnly`: プレミアム限定か
- `downloadUrl`: ダウンロードURL（nullable）
- `uploadDate`: アップロード日（YYYYMMDD形式、nullable）
- `formats`: VideoFormatリスト（オプション）

**VideoFormat:**
- `formatId`: フォーマットID
- `resolution`: 解像度
- `tbr`: ビットレート
- `url`: ストリームURL

## 使用例

### 基本的な保存と読み込み

```python
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.infrastructure.fetcher import AbemaFetcher

fetcher = AbemaFetcher()
storage = ProgramStorage()

# 番組を取得して保存
program = fetcher.fetch_program_info("26-249")
storage.save_program(program)

# すべての番組を読み込み
programs = storage.load_programs()
print(f"Total: {len(programs)} programs")
```

### 番組の検索と更新

```python
storage = ProgramStorage()

# 既存番組を検索
program = storage.find_program("26-249")

if program:
    # 番組情報を更新
    fetcher = AbemaFetcher()
    updated_program = fetcher.fetch_program_info(program.id)
    storage.save_program(updated_program)
    print(f"Updated: {updated_program.title}")
else:
    print("Program not found")
```

### 番組一覧の表示

```python
storage = ProgramStorage()
programs = storage.load_programs()

# 更新日時でソート
sorted_programs = sorted(
    programs,
    key=lambda p: p.updated_at,
    reverse=True
)

for i, program in enumerate(sorted_programs, 1):
    print(f"{i}. {program.id} - {program.title}")
    print(f"   Episodes: {program.total_episodes}")
    print(f"   Updated: {program.updated_at}")
```

### 条件検索

```python
storage = ProgramStorage()
programs = storage.load_programs()

# ダウンロード可能なエピソードがある番組を検索
programs_with_downloadable = [
    p for p in programs
    if any(ep.is_downloadable for ep in p.episodes)
]

print(f"Programs with downloadable episodes: {len(programs_with_downloadable)}")
```

### バックアップの作成

```python
from pathlib import Path
from shutil import copy2
from datetime import datetime

storage = ProgramStorage()

# バックアップファイル名を生成
backup_name = f"programs_backup_{datetime.now():%Y%m%d_%H%M%S}.yaml"
backup_path = Path("backups") / backup_name

# バックアップディレクトリを作成
backup_path.parent.mkdir(exist_ok=True)

# ファイルをコピー
copy2(storage.data_file, backup_path)
print(f"Backup created: {backup_path}")
```

### データのマイグレーション

```python
from abm_check.infrastructure.storage import ProgramStorage

# 旧ストレージから読み込み
old_storage = ProgramStorage("old_programs.yaml")
programs = old_storage.load_programs()

# 新ストレージに保存
new_storage = ProgramStorage("new_programs.yaml")
for program in programs:
    new_storage.save_program(program)

print(f"Migrated {len(programs)} programs")
```

### エラーハンドリング

```python
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.domain.exceptions import StorageError, ProgramNotFoundError

storage = ProgramStorage()

try:
    # 番組を保存
    storage.save_program(program)
    
except StorageError as e:
    print(f"Save failed ({e.operation}): {e.reason}")
    # バックアップから復元など

try:
    # 番組を削除
    storage.delete_program("26-249")
    
except ProgramNotFoundError as e:
    print(f"Program not found: {e.program_id}")
    
except StorageError as e:
    print(f"Delete failed: {e.reason}")
```

### VideoFormatの保存と読み込み

```python
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.infrastructure.fetcher import AbemaFetcher

fetcher = AbemaFetcher()
storage = ProgramStorage()

# VideoFormat情報を含む番組を取得
program = fetcher.fetch_program_info("26-249")

# 保存（VideoFormatも一緒に保存される）
storage.save_program(program)

# 読み込み
loaded_program = storage.find_program("26-249")

# VideoFormat情報を確認
for ep in loaded_program.episodes:
    if ep.formats:
        print(f"Episode {ep.number}: {len(ep.formats)} formats")
        for fmt in ep.formats:
            print(f"  - {fmt.resolution} ({fmt.tbr} kbps)")
```

### 統計情報の取得

```python
storage = ProgramStorage()
programs = storage.load_programs()

# 統計情報を計算
total_episodes = sum(p.total_episodes for p in programs)
total_downloadable = sum(
    sum(1 for ep in p.episodes if ep.is_downloadable)
    for p in programs
)
total_premium = sum(
    sum(1 for ep in p.episodes if ep.is_premium_only)
    for p in programs
)

print(f"Total Programs: {len(programs)}")
print(f"Total Episodes: {total_episodes}")
print(f"Downloadable: {total_downloadable}")
print(f"Premium Only: {total_premium}")
```

## パフォーマンス考慮事項

### ファイルサイズ

- 1番組（24エピソード）: 約5-10KB
- VideoFormat含む: 約10-20KB
- 100番組: 約1-2MB

### 読み込み速度

- 100番組: < 1秒
- 1000番組: 約1-3秒
- YAML解析がボトルネック

### 推奨事項

1. **定期的なバックアップ**
   - 手動編集前にバックアップを作成
   - 日次バックアップの自動化を検討

2. **ファイルロック**
   - 複数プロセスから同時に書き込まない
   - 必要に応じてロック機構を実装

3. **データ検証**
   - 読み込み後にデータの整合性を確認
   - 破損したデータに対する処理を実装
