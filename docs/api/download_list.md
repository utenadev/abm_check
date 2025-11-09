# DownloadList API Reference

ダウンロードURL一覧生成モジュール

## クラス

### `DownloadListGenerator`

エピソードのダウンロードURL一覧を生成するクラス。

#### コンストラクタ

```python
DownloadListGenerator(output_dir: str = "output")
```

**パラメータ:**
- `output_dir`: 出力ディレクトリ（デフォルト: "output"）

**例:**
```python
from abm_check.infrastructure.download_list import DownloadListGenerator

# デフォルトディレクトリ（output/）
generator = DownloadListGenerator()

# カスタムディレクトリ
generator = DownloadListGenerator(output_dir="downloads")
```

#### メソッド

##### `generate_download_list(program: Program, new_episodes: List[Episode], premium_to_free: List[Episode], output_file: str = "download_urls.txt") -> Path`

ダウンロードURL一覧を生成します。

**パラメータ:**
- `program`: Programオブジェクト
- `new_episodes`: 新規エピソードのリスト
- `premium_to_free`: プレミアム→無料エピソードのリスト
- `output_file`: 出力ファイル名（デフォルト: "download_urls.txt"）

**戻り値:** 生成したファイルのPath

**例:**
```python
from abm_check.infrastructure.download_list import DownloadListGenerator
from abm_check.infrastructure.updater import ProgramUpdater

updater = ProgramUpdater()
generator = DownloadListGenerator()

# 番組を更新
new_episodes, premium_to_free = updater.update_program("26-249")

# ダウンロードリストを生成
if new_episodes or premium_to_free:
    program = updater.storage.find_program("26-249")
    file_path = generator.generate_download_list(
        program,
        new_episodes,
        premium_to_free
    )
    print(f"Download list saved to: {file_path}")
```

## 出力フォーマット

### ファイル構造

```
# 番組タイトル - New Episodes
# Episode 1: エピソードタイトル1
https://abema.tv/video/episode/26-249_s1_p1

# Episode 2: エピソードタイトル2
https://abema.tv/video/episode/26-249_s1_p2

# 番組タイトル - Premium to Free
https://abema.tv/video/episode/26-249_s1_p3
https://abema.tv/video/episode/26-249_s1_p4
```

### セクション

**1. 新規エピソード (New Episodes):**
- コメント行: `# Episode {話数}: {タイトル}`
- URL行: エピソードのURL

**2. プレミアム→無料 (Premium to Free):**
- URLのみ（コメントなし）

### ファイル配置

```
output/
└── download_urls.txt  (デフォルト)
```

または

```
output/
└── download_urls_26-249.txt  (カスタムファイル名)
```

## 使用例

### 基本的な使用

```python
from abm_check.infrastructure.download_list import DownloadListGenerator
from abm_check.infrastructure.updater import ProgramUpdater

updater = ProgramUpdater()
generator = DownloadListGenerator()

# 番組を更新
new_eps, p2f_eps = updater.update_program("26-249")

if new_eps or p2f_eps:
    program = updater.storage.find_program("26-249")
    
    # ダウンロードリスト生成
    file_path = generator.generate_download_list(
        program,
        new_eps,
        p2f_eps
    )
    
    print(f"Generated: {file_path}")
    print(f"New episodes: {len(new_eps)}")
    print(f"Premium to free: {len(p2f_eps)}")
```

### カスタムファイル名での保存

```python
from datetime import datetime

generator = DownloadListGenerator()

# 日付付きファイル名
output_file = f"downloads_{datetime.now():%Y%m%d_%H%M%S}.txt"

file_path = generator.generate_download_list(
    program,
    new_episodes,
    premium_to_free,
    output_file=output_file
)
```

### 番組ごとに個別ファイル生成

```python
generator = DownloadListGenerator()
updater = ProgramUpdater()

results = updater.update_all_programs()

for program_id, (new_eps, p2f_eps) in results.items():
    if new_eps or p2f_eps:
        program = updater.storage.find_program(program_id)
        
        # 番組IDをファイル名に含める
        output_file = f"downloads_{program_id}.txt"
        
        file_path = generator.generate_download_list(
            program,
            new_eps,
            p2f_eps,
            output_file=output_file
        )
        
        print(f"{program.title}: {file_path}")
```

### 生成されたファイルの読み込み

```python
from pathlib import Path

# ダウンロードリスト生成
file_path = generator.generate_download_list(
    program,
    new_episodes,
    premium_to_free
)

# ファイルを読み込み
content = Path(file_path).read_text(encoding="utf-8")
print(content)

# URLのみを抽出
urls = [
    line for line in content.split("\n")
    if line.startswith("http")
]

print(f"Total URLs: {len(urls)}")
for url in urls:
    print(url)
```

### yt-dlpと連携

```python
import subprocess

# ダウンロードリスト生成
file_path = generator.generate_download_list(
    program,
    new_episodes,
    premium_to_free
)

# yt-dlpでダウンロード
subprocess.run([
    "yt-dlp",
    "-a", str(file_path),  # バッチファイルモード
    "-o", "downloads/%(title)s.%(ext)s"
])
```

### カスタムフォーマット

独自のフォーマットでURL一覧を生成:

```python
from pathlib import Path

def generate_custom_format(program, new_episodes, premium_to_free):
    """カスタムフォーマットでURL一覧を生成"""
    lines = []
    
    # ヘッダー
    lines.append(f"# {program.title}")
    lines.append(f"# Program ID: {program.id}")
    lines.append(f"# Generated: {datetime.now()}")
    lines.append("")
    
    # 新規エピソード
    if new_episodes:
        lines.append("## New Episodes")
        for ep in sorted(new_episodes, key=lambda x: x.number):
            lines.append(f"# {ep.number:02d}. {ep.title} ({ep.duration // 60}min)")
            lines.append(ep.get_episode_url())
            lines.append("")
    
    # プレミアム→無料
    if premium_to_free:
        lines.append("## Premium to Free")
        for ep in sorted(premium_to_free, key=lambda x: x.number):
            lines.append(f"{ep.get_episode_url()}  # Episode {ep.number}")
        lines.append("")
    
    # ファイルに保存
    output_path = Path("output") / f"custom_{program.id}.txt"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    
    return output_path
```

### JSON形式での出力

```python
import json
from pathlib import Path

def generate_json_format(program, new_episodes, premium_to_free):
    """JSON形式でエピソード情報を出力"""
    data = {
        "program": {
            "id": program.id,
            "title": program.title,
            "url": program.url
        },
        "new_episodes": [
            {
                "number": ep.number,
                "title": ep.title,
                "url": ep.get_episode_url(),
                "duration": ep.duration
            }
            for ep in new_episodes
        ],
        "premium_to_free": [
            {
                "number": ep.number,
                "title": ep.title,
                "url": ep.get_episode_url()
            }
            for ep in premium_to_free
        ]
    }
    
    output_path = Path("output") / f"{program.id}_downloads.json"
    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    return output_path
```

### 統計情報の追加

```python
def generate_with_stats(program, new_episodes, premium_to_free):
    """統計情報付きでダウンロードリストを生成"""
    lines = []
    
    # ヘッダー
    lines.append(f"# {program.title}")
    lines.append(f"# Generated: {datetime.now()}")
    lines.append("")
    
    # 統計情報
    lines.append("# Statistics")
    lines.append(f"# Total episodes: {program.total_episodes}")
    lines.append(f"# New episodes: {len(new_episodes)}")
    lines.append(f"# Premium to free: {len(premium_to_free)}")
    
    total_duration = sum(ep.duration for ep in new_episodes + premium_to_free)
    lines.append(f"# Total duration: {total_duration // 60} minutes")
    lines.append("")
    
    # エピソードURL
    lines.append("# Download URLs")
    for ep in new_episodes:
        lines.append(f"# Episode {ep.number}: {ep.title}")
        lines.append(ep.get_episode_url())
    
    for ep in premium_to_free:
        lines.append(ep.get_episode_url())
    
    output_path = Path("output") / "download_urls_with_stats.txt"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    
    return output_path
```

### エピソードのフィルタリング

特定の条件でエピソードをフィルタリング:

```python
generator = DownloadListGenerator()

# 番組を更新
new_episodes, premium_to_free = updater.update_program("26-249")

# 特定の話数範囲のみを含める（例: 1-10話）
filtered_new = [ep for ep in new_episodes if 1 <= ep.number <= 10]

# 長時間エピソードのみ（例: 20分以上）
filtered_new = [ep for ep in new_episodes if ep.duration >= 1200]

# フィルタリング後のリストで生成
file_path = generator.generate_download_list(
    program,
    filtered_new,
    premium_to_free
)
```

### 複数番組を1つのファイルにまとめる

```python
from pathlib import Path

def generate_combined_list(programs_data):
    """複数番組のURLを1つのファイルにまとめる"""
    lines = []
    
    for program, new_eps, p2f_eps in programs_data:
        if new_eps or p2f_eps:
            lines.append(f"\n# ===== {program.title} =====")
            
            if new_eps:
                lines.append("# New Episodes")
                for ep in new_eps:
                    lines.append(f"# Episode {ep.number}: {ep.title}")
                    lines.append(ep.get_episode_url())
            
            if p2f_eps:
                lines.append("# Premium to Free")
                for ep in p2f_eps:
                    lines.append(ep.get_episode_url())
    
    output_path = Path("output") / "all_downloads.txt"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    
    return output_path

# 使用例
updater = ProgramUpdater()
results = updater.update_all_programs()

programs_data = []
for program_id, (new_eps, p2f_eps) in results.items():
    if new_eps or p2f_eps:
        program = updater.storage.find_program(program_id)
        programs_data.append((program, new_eps, p2f_eps))

combined_file = generate_combined_list(programs_data)
print(f"Combined list: {combined_file}")
```

## パフォーマンス考慮事項

### ファイルサイズ

- 1エピソード: 約100-150バイト
- 100エピソード: 約10-15KB
- 非常に軽量

### 生成速度

- ほぼ瞬時（I/O時間のみ）
- メモリ使用量も最小限

### 推奨事項

1. **ファイル管理**
   - 古いダウンロードリストを定期的に削除
   - 日付付きファイル名で履歴管理

2. **エンコーディング**
   - 常にUTF-8で保存
   - コメント行に日本語を使用可能

3. **自動化**
   - 更新後に自動生成
   - yt-dlpとの連携スクリプト作成

## 出力例

実際の出力例:

```txt
# 瑠璃の宝石 - New Episodes
# Episode 13: 第13話 新たな冒険
https://abema.tv/video/episode/26-249_s2_p1

# Episode 14: 第14話 危機一髪
https://abema.tv/video/episode/26-249_s2_p2

# 瑠璃の宝石 - Premium to Free
https://abema.tv/video/episode/26-249_s1_p11
https://abema.tv/video/episode/26-249_s1_p12
```

この形式は`yt-dlp -a`オプションでそのまま使用できます:

```bash
yt-dlp -a output/download_urls.txt -o "downloads/%(title)s.%(ext)s"
```
