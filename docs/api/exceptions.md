# Exceptions API Reference

カスタム例外クラス

## 例外階層

```
Exception
└── AbmCheckError (基底例外)
    ├── ProgramNotFoundError
    ├── InvalidProgramIdError
    ├── SeasonDetectionError
    ├── FetchError
    ├── YtdlpError
    └── StorageError
```

## 例外クラス

### `AbmCheckError`

abm_checkの全てのカスタム例外の基底クラス。

```python
class AbmCheckError(Exception):
    """Base exception for abm_check."""
```

**使用例:**
```python
try:
    # abm_checkの処理
    pass
except AbmCheckError as e:
    # すべてのabm_check例外をキャッチ
    print(f"Error: {e}")
```

---

### `ProgramNotFoundError`

番組が見つからない場合にスローされる例外。

```python
class ProgramNotFoundError(AbmCheckError):
    """Program not found."""
    
    def __init__(self, program_id: str):
        self.program_id = program_id
        super().__init__(f"Program not found: {program_id}")
```

**属性:**
- `program_id: str` - 見つからなかった番組ID

**例:**
```python
from abm_check.domain.exceptions import ProgramNotFoundError

try:
    program = storage.find_program("999-999")
    if program is None:
        raise ProgramNotFoundError("999-999")
except ProgramNotFoundError as e:
    print(f"Program ID: {e.program_id}")
    print(f"Error: {e}")
```

---

### `InvalidProgramIdError`

無効な番組IDが指定された場合にスローされる例外。

```python
class InvalidProgramIdError(AbmCheckError):
    """Invalid program ID format."""
    
    def __init__(self, program_id: str, reason: str = ""):
        self.program_id = program_id
        self.reason = reason
```

**属性:**
- `program_id: str` - 無効な番組ID
- `reason: str` - 理由（オプション）

**例:**
```python
from abm_check.domain.exceptions import InvalidProgramIdError

def validate_program_id(program_id: str):
    if not program_id.count("-") == 1:
        raise InvalidProgramIdError(
            program_id,
            "Program ID must contain exactly one hyphen"
        )

try:
    validate_program_id("invalid_id")
except InvalidProgramIdError as e:
    print(f"Invalid ID: {e.program_id}")
    print(f"Reason: {e.reason}")
```

---

### `SeasonDetectionError`

シーズン検出に失敗した場合にスローされる例外。

```python
class SeasonDetectionError(AbmCheckError):
    """Season detection failed."""
    
    def __init__(self, program_id: str, season: int, reason: str = ""):
        self.program_id = program_id
        self.season = season
        self.reason = reason
```

**属性:**
- `program_id: str` - 番組ID
- `season: int` - 検出に失敗したシーズン番号
- `reason: str` - 理由（オプション）

**例:**
```python
from abm_check.domain.exceptions import SeasonDetectionError

try:
    # シーズン2の取得を試行
    season_info = fetch_season(program_id, season=2)
    if not season_info:
        raise SeasonDetectionError(
            program_id,
            season=2,
            reason="No episodes found"
        )
except SeasonDetectionError as e:
    print(f"Failed to detect season {e.season} for {e.program_id}")
    print(f"Reason: {e.reason}")
```

---

### `FetchError`

番組情報の取得に失敗した場合にスローされる例外。

```python
class FetchError(AbmCheckError):
    """Failed to fetch program information."""
    
    def __init__(self, program_id: str, reason: str):
        self.program_id = program_id
        self.reason = reason
```

**属性:**
- `program_id: str` - 番組ID
- `reason: str` - エラーの理由

**例:**
```python
from abm_check.domain.exceptions import FetchError

try:
    program = fetcher.fetch_program_info("26-249")
except FetchError as e:
    print(f"Failed to fetch {e.program_id}: {e.reason}")
```

---

### `YtdlpError`

yt-dlpの実行でエラーが発生した場合にスローされる例外。

```python
class YtdlpError(AbmCheckError):
    """yt-dlp error occurred."""
```

**例:**
```python
from abm_check.domain.exceptions import YtdlpError

try:
    info = ydl.extract_info(url, download=False)
except Exception as e:
    raise YtdlpError(f"Failed to extract info from {url}: {str(e)}")
```

---

### `StorageError`

データの保存・読み込みに失敗した場合にスローされる例外。

```python
class StorageError(AbmCheckError):
    """Storage operation failed."""
    
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
```

**属性:**
- `operation: str` - 失敗した操作（例: "save_program", "load_programs"）
- `reason: str` - エラーの理由

**例:**
```python
from abm_check.domain.exceptions import StorageError

try:
    with open(file_path, 'w') as f:
        yaml.safe_dump(data, f)
except Exception as e:
    raise StorageError("save_program", str(e))
```

## 使用例

### 例外の階層的なキャッチ

```python
from abm_check.domain.exceptions import (
    AbmCheckError,
    ProgramNotFoundError,
    FetchError
)

try:
    program = fetcher.fetch_program_info("26-249")
except ProgramNotFoundError:
    print("番組が見つかりません")
except FetchError as e:
    print(f"取得エラー: {e.reason}")
except AbmCheckError as e:
    print(f"その他のエラー: {e}")
```

### エラー情報の詳細な取得

```python
from abm_check.domain.exceptions import FetchError

try:
    program = fetcher.fetch_program_info(program_id)
except FetchError as e:
    # エラー詳細をログに記録
    logger.error(
        f"Fetch failed",
        extra={
            "program_id": e.program_id,
            "reason": e.reason,
            "error_type": type(e).__name__
        }
    )
```

### カスタムエラーハンドリング

```python
from abm_check.domain.exceptions import (
    InvalidProgramIdError,
    ProgramNotFoundError,
    StorageError
)

def safe_add_program(program_id: str):
    """例外を適切に処理して番組を追加"""
    try:
        # 番組ID検証
        if not validate_program_id(program_id):
            raise InvalidProgramIdError(program_id, "Invalid format")
        
        # 番組取得
        program = fetcher.fetch_program_info(program_id)
        
        # 保存
        storage.save_program(program)
        
        return True
        
    except InvalidProgramIdError as e:
        print(f"無効な番組ID: {e.program_id} ({e.reason})")
        return False
        
    except ProgramNotFoundError as e:
        print(f"番組が見つかりません: {e.program_id}")
        return False
        
    except StorageError as e:
        print(f"保存エラー ({e.operation}): {e.reason}")
        return False
```

### リトライロジック

```python
from abm_check.domain.exceptions import YtdlpError
import time

def fetch_with_retry(program_id: str, max_retries: int = 3):
    """リトライ機能付きで番組情報を取得"""
    for attempt in range(max_retries):
        try:
            return fetcher.fetch_program_info(program_id)
        except YtdlpError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # exponential backoff
                print(f"Retry in {wait_time}s... ({attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
```
