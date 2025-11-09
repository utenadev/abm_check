# Fetcher API Reference

番組情報取得モジュール（yt-dlp統合）

## クラス

### `AbemaFetcher`

yt-dlpを使用してABEMA番組情報を取得するクラス。

#### コンストラクタ

```python
AbemaFetcher(config=None)
```

**パラメータ:**
- `config`: Configインスタンス（省略時はデフォルト設定）

**例:**
```python
from abm_check.infrastructure.fetcher import AbemaFetcher

# デフォルト設定で初期化
fetcher = AbemaFetcher()

# カスタム設定で初期化
from abm_check.config import Config
config = Config("custom.yaml")
fetcher = AbemaFetcher(config)
```

#### メソッド

##### `fetch_program_info(program_id: str) -> Program`

番組情報を取得します。

**パラメータ:**
- `program_id`: 番組ID（例: "26-249"）

**戻り値:** Programオブジェクト

**例外:**
- `YtdlpError`: yt-dlpでの情報取得に失敗
- `FetchError`: その他の取得エラー

**例:**
```python
from abm_check.infrastructure.fetcher import AbemaFetcher
from abm_check.domain.exceptions import FetchError

fetcher = AbemaFetcher()

try:
    program = fetcher.fetch_program_info("26-249")
    print(f"Title: {program.title}")
    print(f"Episodes: {len(program.episodes)}")
except FetchError as e:
    print(f"Error: {e}")
```

## 動作詳細

### 複数シーズン検出ロジック

`AbemaFetcher`は以下のロジックで複数シーズンを自動検出します:

1. **シーズン1の取得**
   ```
   https://abema.tv/video/title/{program_id}
   ```

2. **追加シーズンの探索**
   - シーズン1が `config.season_threshold` 話以上の場合、シーズン2以降を探索
   - デフォルトの閾値は12話
   - 最大 `config.max_seasons` まで探索（デフォルト10）

3. **シーズンURL**
   ```
   https://abema.tv/video/title/{program_id}?s={program_id}_s{season}&eg={program_id}_eg0
   ```

4. **探索終了条件**
   - エピソードが取得できなくなった場合
   - 最大シーズン数に到達した場合

**例:**
```python
# シーズン1が15話の場合
program = fetcher.fetch_program_info("26-249")
# → シーズン2, 3, ... も自動的に取得される

# 設定で閾値を変更
from abm_check.config import Config
config = Config()
config.config['season_detection']['threshold'] = 6  # 6話以上で検出
fetcher = AbemaFetcher(config)
```

### エピソード情報の変換

yt-dlpから取得した情報をEpisodeモデルに変換します:

```python
{
    "id": "26-249_s1_p1",
    "title": "第1話",
    "duration": 1420,
    "episode_number": 1,
    "availability": "public",  # or "premium_only"
    "formats": [...]
}
```

↓

```python
Episode(
    id="26-249_s1_p1",
    number=1,
    title="第1話",
    duration=1420,
    is_downloadable=True,      # availability == "public"
    is_premium_only=False,
    formats=[VideoFormat(...)]
)
```

### プレミアム判定ロジック

```python
availability = entry.get('availability', '')
is_premium = availability == 'premium_only'
has_formats = len(entry.get('formats', [])) > 0

is_downloadable = has_formats and not is_premium
```

- `availability == "public"` → 無料視聴可能
- `availability == "premium_only"` → プレミアム限定
- `formats`が空 → ダウンロード不可

## 使用例

### 基本的な使用

```python
from abm_check.infrastructure.fetcher import AbemaFetcher

fetcher = AbemaFetcher()

# 番組情報取得
program = fetcher.fetch_program_info("26-249")

print(f"Title: {program.title}")
print(f"Total Episodes: {program.total_episodes}")
print(f"Latest Episode: {program.latest_episode_number}")

# エピソード情報の表示
for ep in program.episodes:
    status = "✅" if ep.is_downloadable else "🔒"
    print(f"{status} Episode {ep.number}: {ep.title}")
```

### カスタム設定での使用

```python
from abm_check.config import Config
from abm_check.infrastructure.fetcher import AbemaFetcher

# カスタム設定を作成
config = Config()
config.config['season_detection']['threshold'] = 6
config.config['season_detection']['max_seasons'] = 5

# フェッチャーを初期化
fetcher = AbemaFetcher(config)

program = fetcher.fetch_program_info("26-249")
```

### エラーハンドリング

```python
from abm_check.infrastructure.fetcher import AbemaFetcher
from abm_check.domain.exceptions import YtdlpError, FetchError

fetcher = AbemaFetcher()

try:
    program = fetcher.fetch_program_info("26-249")
    
except YtdlpError as e:
    # yt-dlp固有のエラー
    print(f"yt-dlp error: {e}")
    # リトライや代替手段を試す
    
except FetchError as e:
    # その他の取得エラー
    print(f"Fetch error for {e.program_id}: {e.reason}")
```

### 複数番組の一括取得

```python
from abm_check.infrastructure.fetcher import AbemaFetcher
from abm_check.infrastructure.storage import ProgramStorage

fetcher = AbemaFetcher()
storage = ProgramStorage()

program_ids = ["26-249", "26-156", "189-85"]

for program_id in program_ids:
    try:
        print(f"Fetching {program_id}...")
        program = fetcher.fetch_program_info(program_id)
        storage.save_program(program)
        print(f"✓ {program.title}")
    except Exception as e:
        print(f"✗ {program_id}: {e}")
```

### VideoFormat情報の活用

```python
fetcher = AbemaFetcher()
program = fetcher.fetch_program_info("26-249")

for ep in program.episodes:
    if ep.formats:
        # 利用可能なフォーマットを表示
        print(f"\nEpisode {ep.number}: {ep.title}")
        for fmt in ep.formats:
            print(f"  - {fmt.resolution} ({fmt.tbr} kbps)")
        
        # 最高画質を取得
        best = max(ep.formats, key=lambda f: f.tbr)
        print(f"  Best: {best.resolution}")
```

### 取得情報のデバッグ

```python
import json
from abm_check.infrastructure.fetcher import AbemaFetcher

fetcher = AbemaFetcher()
program = fetcher.fetch_program_info("26-249")

# 番組情報をJSON形式で出力
program_dict = {
    "id": program.id,
    "title": program.title,
    "total_episodes": program.total_episodes,
    "episodes": [
        {
            "number": ep.number,
            "title": ep.title,
            "is_downloadable": ep.is_downloadable,
            "is_premium": ep.is_premium_only
        }
        for ep in program.episodes
    ]
}

print(json.dumps(program_dict, indent=2, ensure_ascii=False))
```

## パフォーマンス考慮事項

### 取得時間

- シーズン1のみ: 約5-10秒
- 複数シーズン（2シーズン）: 約10-20秒
- ネットワーク環境に依存

### メモリ使用量

- 1番組あたり: 約1-5MB（エピソード数に依存）
- VideoFormat情報を含む場合: やや増加

### 推奨事項

1. **一度に大量の番組を取得しない**
   - 1つずつ取得して保存
   - 必要に応じてスリープを挟む

2. **エラーハンドリングを実装**
   - ネットワークエラーに対応
   - リトライロジックを検討

3. **取得済みデータの再利用**
   - Storageを活用
   - 不要な再取得を避ける
