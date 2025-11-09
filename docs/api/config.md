# Config API Reference

設定管理モジュール

## クラス

### `Config`

設定を管理するクラス。

#### コンストラクタ

```python
Config(config_file: Optional[str] = None)
```

**パラメータ:**
- `config_file`: 設定ファイルのパス（省略時は `abm_check.yaml` を探索）

**例:**
```python
from abm_check.config import Config

# デフォルト設定を使用
config = Config()

# カスタム設定ファイルを指定
config = Config("custom_config.yaml")
```

#### プロパティ

##### `season_threshold: int`

シーズン検出の閾値（話数）。この話数以上の場合、追加シーズンを探索します。

**デフォルト:** 12

**例:**
```python
config = Config()
print(config.season_threshold)  # 12
```

##### `max_seasons: int`

検出する最大シーズン数。

**デフォルト:** 10

##### `base_url: str`

ABEMA番組ページのベースURL。

**デフォルト:** `"https://abema.tv/video/title"`

##### `episode_base_url: str`

ABEMAエピソードページのベースURL。

**デフォルト:** `"https://abema.tv/video/episode"`

##### `season_url_pattern: str`

シーズンURLのパターン文字列。

**デフォルト:** `"https://abema.tv/video/title/{program_id}?s={program_id}_s{season}&eg={program_id}_eg0"`

##### `programs_file: str`

番組データベースファイルのパス。

**デフォルト:** `"programs.yaml"`

##### `output_dir: str`

出力ディレクトリのパス。

**デフォルト:** `"output"`

##### `ytdlp_opts: dict`

yt-dlpに渡すオプション辞書。

**デフォルト:**
```python
{
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'extract_flat': False,
}
```

#### メソッド

##### `get(key: str, default=None) -> Any`

ドット区切りのキーで設定値を取得します。

**パラメータ:**
- `key`: ドット区切りのキー（例: `"season_detection.threshold"`）
- `default`: キーが存在しない場合のデフォルト値

**戻り値:** 設定値

**例:**
```python
config = Config()
threshold = config.get("season_detection.threshold", 12)
base_url = config.get("urls.base_url")
```

## 関数

### `get_config() -> Config`

グローバルなConfigインスタンスを取得します（シングルトン）。

**戻り値:** Configインスタンス

**例:**
```python
from abm_check.config import get_config

config = get_config()
print(config.season_threshold)
```

## 設定ファイル形式

`abm_check.yaml`:

```yaml
season_detection:
  threshold: 12
  max_seasons: 10

urls:
  base_url: "https://abema.tv/video/title"
  episode_base_url: "https://abema.tv/video/episode"
  season_url_pattern: "https://abema.tv/video/title/{program_id}?s={program_id}_s{season}&eg={program_id}_eg0"

storage:
  programs_file: "programs.yaml"
  output_dir: "output"

ytdlp:
  quiet: true
  no_warnings: true
  skip_download: true
  extract_flat: false
```

## 使用例

### 設定値の参照

```python
from abm_check.config import get_config

config = get_config()

# シーズン閾値を確認
if episode_count >= config.season_threshold:
    # シーズン2以降を探索
    pass
```

### カスタム設定の使用

```python
from abm_check.config import Config

# カスタム設定ファイルを読み込み
config = Config("my_config.yaml")

# 設定値を使用
print(f"Output directory: {config.output_dir}")
```

### 設定値の部分的なオーバーライド

```yaml
# custom.yaml
season_detection:
  threshold: 6  # 6話以上でシーズン検出
```

```python
config = Config("custom.yaml")
print(config.season_threshold)  # 6
print(config.max_seasons)  # 10 (デフォルト値)
```
