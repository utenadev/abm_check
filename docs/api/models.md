# Models API Reference

ドメインモデル

## クラス

### `VideoFormat`

動画フォーマット情報を表すデータクラス。

#### 属性

```python
@dataclass
class VideoFormat:
    format_id: str       # フォーマットID
    resolution: str      # 解像度 (例: "1920x1080")
    tbr: float          # ビットレート
    url: str            # ストリームURL
```

#### 例

```python
from abm_check.domain.models import VideoFormat

format = VideoFormat(
    format_id="1080p",
    resolution="1920x1080",
    tbr=2500.0,
    url="https://example.com/stream"
)
```

---

### `Episode`

エピソード情報を表すデータクラス。

#### 属性

```python
@dataclass
class Episode:
    id: str                          # エピソードID (例: "26-249_s1_p1")
    number: int                      # エピソード番号
    title: str                       # エピソードタイトル
    description: str                 # 説明
    duration: int                    # 長さ（秒）
    thumbnail_url: str               # サムネイルURL
    is_downloadable: bool            # ダウンロード可能か
    is_premium_only: bool            # プレミアム限定か
    download_url: Optional[str]      # ダウンロードURL
    formats: List[VideoFormat]       # 利用可能なフォーマット
    upload_date: Optional[str]       # アップロード日 (YYYYMMDD)
```

#### メソッド

##### `get_episode_url(program_id: str = None) -> str`

エピソードの視聴URLを生成します。

**パラメータ:**
- `program_id`: 番組ID（後方互換性のため残されているが未使用）

**戻り値:** エピソードURL

**例:**
```python
episode = Episode(
    id="26-249_s1_p1",
    number=1,
    title="第1話",
    # ... その他の属性
)

url = episode.get_episode_url()
# "https://abema.tv/video/episode/26-249_s1_p1"
```

#### 分類ルール

- **通常エピソード**: `number < 100`
- **特別エピソード（PV等）**: `number >= 100`

#### 例

```python
from abm_check.domain.models import Episode, VideoFormat

episode = Episode(
    id="26-249_s1_p1",
    number=1,
    title="第1話 はじめての鉱物採集",
    description="エピソードの説明",
    duration=1420,
    thumbnail_url="https://example.com/thumb.jpg",
    is_downloadable=True,
    is_premium_only=False,
    download_url="https://abema.tv/video/episode/26-249_s1_p1",
    formats=[
        VideoFormat(
            format_id="1080p",
            resolution="1920x1080",
            tbr=2500.0,
            url="https://example.com/stream"
        )
    ],
    upload_date="20230122"
)
```

---

### `Program`

番組情報を表すデータクラス。

#### 属性

```python
@dataclass
class Program:
    id: str                        # 番組ID (例: "26-249")
    title: str                     # 番組タイトル
    description: str               # 番組説明
    url: str                       # 番組URL
    thumbnail_url: str             # サムネイルURL
    total_episodes: int            # 総エピソード数
    latest_episode_number: int     # 最新話番号（通常エピソードのみ）
    episodes: List[Episode]        # エピソードリスト
    fetched_at: datetime           # 取得日時
    updated_at: datetime           # 更新日時
```

#### 例

```python
from datetime import datetime
from abm_check.domain.models import Program, Episode

program = Program(
    id="26-249",
    title="瑠璃の宝石",
    description="番組の説明",
    url="https://abema.tv/video/title/26-249",
    thumbnail_url="https://example.com/thumb.png",
    total_episodes=24,
    latest_episode_number=12,
    episodes=[
        Episode(...),
        Episode(...),
    ],
    fetched_at=datetime.now(),
    updated_at=datetime.now()
)
```

## 使用例

### エピソード一覧の取得

```python
from abm_check.infrastructure.storage import ProgramStorage

storage = ProgramStorage()
programs = storage.load_programs()

for program in programs:
    print(f"Title: {program.title}")
    print(f"Total Episodes: {program.total_episodes}")
    
    # 通常エピソードのみを取得
    regular_episodes = [ep for ep in program.episodes if ep.number < 100]
    print(f"Regular Episodes: {len(regular_episodes)}")
    
    # ダウンロード可能なエピソードのみを取得
    downloadable = [ep for ep in program.episodes if ep.is_downloadable]
    print(f"Downloadable: {len(downloadable)}")
```

### プレミアム限定エピソードの判定

```python
for episode in program.episodes:
    if episode.is_premium_only:
        print(f"Premium Only: {episode.title}")
    elif episode.is_downloadable:
        print(f"Free: {episode.title}")
    else:
        print(f"Unknown: {episode.title}")
```

### エピソードURLの生成

```python
for episode in program.episodes:
    if episode.is_downloadable:
        url = episode.get_episode_url()
        print(f"{episode.number:02d}: {url}")
```

### 特別エピソードと通常エピソードの分離

```python
# 通常エピソード（第1話、第2話...）
regular_episodes = [ep for ep in program.episodes if ep.number < 100]

# 特別エピソード（PV、特番など）
special_episodes = [ep for ep in program.episodes if ep.number >= 100]

print(f"Regular: {len(regular_episodes)}")
print(f"Special: {len(special_episodes)}")
```

### VideoFormatの利用

```python
for episode in program.episodes:
    if episode.formats:
        # 最高画質を取得
        best_format = max(episode.formats, key=lambda f: f.tbr)
        print(f"{episode.title}: {best_format.resolution} ({best_format.tbr} kbps)")
```
