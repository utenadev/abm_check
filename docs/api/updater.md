# Updater API Reference

番組更新・差分検出モジュール

## クラス

### `ProgramUpdater`

番組の更新と差分検出を行うクラス。

#### コンストラクタ

```python
ProgramUpdater(fetcher=None, storage=None)
```

**パラメータ:**
- `fetcher`: AbemaFetcherインスタンス（省略時は新規作成）
- `storage`: ProgramStorageインスタンス（省略時は新規作成）

**例:**
```python
from abm_check.infrastructure.updater import ProgramUpdater

# デフォルト設定で初期化
updater = ProgramUpdater()

# カスタムインスタンスを指定
from abm_check.infrastructure.fetcher import AbemaFetcher
from abm_check.infrastructure.storage import ProgramStorage

fetcher = AbemaFetcher()
storage = ProgramStorage()
updater = ProgramUpdater(fetcher, storage)
```

#### メソッド

##### `update_program(program_id: str) -> Tuple[List[Episode], List[Episode]]`

番組を更新し、差分を検出します。

**パラメータ:**
- `program_id`: 更新する番組ID

**戻り値:** `(新規エピソード, プレミアム→無料エピソード)` のタプル

**例外:**
- `ProgramNotFoundError`: 番組が見つからない
- `FetchError`: 取得に失敗

**例:**
```python
from abm_check.infrastructure.updater import ProgramUpdater

updater = ProgramUpdater()

try:
    new_episodes, premium_to_free = updater.update_program("26-249")
    
    print(f"New episodes: {len(new_episodes)}")
    for ep in new_episodes:
        print(f"  - Episode {ep.number}: {ep.title}")
    
    print(f"Premium to free: {len(premium_to_free)}")
    for ep in premium_to_free:
        print(f"  - Episode {ep.number}: {ep.title}")
        
except Exception as e:
    print(f"Update failed: {e}")
```

##### `update_all_programs() -> Dict[str, Tuple[List[Episode], List[Episode]]]`

すべての番組を更新します。

**戻り値:** `{番組ID: (新規エピソード, プレミアム→無料エピソード)}` の辞書

**例:**
```python
updater = ProgramUpdater()

results = updater.update_all_programs()

for program_id, (new_eps, p2f_eps) in results.items():
    if new_eps or p2f_eps:
        print(f"\n{program_id}:")
        if new_eps:
            print(f"  New: {len(new_eps)}")
        if p2f_eps:
            print(f"  Premium to Free: {len(p2f_eps)}")
```

## 差分検出ロジック

### 1. 新規エピソード検出

前回取得時に存在しなかった、ダウンロード可能なエピソードを検出します。

```python
for new_ep in new_program.episodes:
    old_ep = old_episodes_dict.get(new_ep.id)
    
    # 前回取得時に存在しなかった
    if old_ep is None:
        # かつダウンロード可能
        if new_ep.is_downloadable:
            new_episodes.append(new_ep)
```

**条件:**
- 前回のデータに存在しない
- ダウンロード可能 (`is_downloadable == True`)

### 2. プレミアム→無料変更検出

前回プレミアム限定だったエピソードが無料になった場合を検出します。

```python
for new_ep in new_program.episodes:
    old_ep = old_episodes_dict.get(new_ep.id)
    
    # 前回取得時に存在した
    if old_ep is not None:
        # 前回: プレミアム限定、今回: ダウンロード可能
        if old_ep.is_premium_only and new_ep.is_downloadable:
            premium_to_free.append(new_ep)
```

**条件:**
- 前回のデータに存在する
- 前回: `is_premium_only == True`
- 今回: `is_downloadable == True`

## 使用例

### 基本的な更新

```python
from abm_check.infrastructure.updater import ProgramUpdater

updater = ProgramUpdater()

# 1つの番組を更新
new_episodes, premium_to_free = updater.update_program("26-249")

if new_episodes:
    print("新規エピソードが見つかりました:")
    for ep in new_episodes:
        print(f"  - 第{ep.number}話: {ep.title}")
        print(f"    URL: {ep.get_episode_url()}")

if premium_to_free:
    print("\nプレミアム→無料に変更:")
    for ep in premium_to_free:
        print(f"  - 第{ep.number}話: {ep.title}")
```

### 全番組の更新

```python
updater = ProgramUpdater()

print("全番組を更新中...")
results = updater.update_all_programs()

# 変更があった番組のみを表示
for program_id, (new_eps, p2f_eps) in results.items():
    if new_eps or p2f_eps:
        # 番組情報を取得
        storage = updater.storage
        program = storage.find_program(program_id)
        
        print(f"\n{program.title} ({program_id}):")
        
        if new_eps:
            print(f"  新規: {len(new_eps)}話")
            for ep in new_eps:
                print(f"    - 第{ep.number}話: {ep.title}")
        
        if p2f_eps:
            print(f"  無料化: {len(p2f_eps)}話")
            for ep in p2f_eps:
                print(f"    - 第{ep.number}話: {ep.title}")
```

### 更新とダウンロードURL出力の組み合わせ

```python
from abm_check.infrastructure.updater import ProgramUpdater
from abm_check.infrastructure.download_list import DownloadListGenerator

updater = ProgramUpdater()
dl_generator = DownloadListGenerator()

# 番組を更新
new_episodes, premium_to_free = updater.update_program("26-249")

# ダウンロードURLを生成
if new_episodes or premium_to_free:
    storage = updater.storage
    program = storage.find_program("26-249")
    
    file_path = dl_generator.generate_download_list(
        program,
        new_episodes,
        premium_to_free,
        output_file="download_urls_26-249.txt"
    )
    
    print(f"Download list saved to: {file_path}")
```

### スケジュール実行（cron等）

```python
#!/usr/bin/env python3
"""
定期実行用スクリプト
cron: 0 */6 * * * /path/to/update_all.py
"""
from abm_check.infrastructure.updater import ProgramUpdater
from abm_check.infrastructure.download_list import DownloadListGenerator
from datetime import datetime

def main():
    updater = ProgramUpdater()
    dl_generator = DownloadListGenerator()
    
    print(f"[{datetime.now()}] Starting update...")
    
    results = updater.update_all_programs()
    
    # 変更があった番組のみ処理
    for program_id, (new_eps, p2f_eps) in results.items():
        if new_eps or p2f_eps:
            program = updater.storage.find_program(program_id)
            
            # ダウンロードリスト生成
            output_file = f"downloads_{program_id}_{datetime.now():%Y%m%d}.txt"
            dl_generator.generate_download_list(
                program,
                new_eps,
                p2f_eps,
                output_file=output_file
            )
            
            print(f"[{program.title}] New: {len(new_eps)}, P2F: {len(p2f_eps)}")
    
    print(f"[{datetime.now()}] Update completed")

if __name__ == "__main__":
    main()
```

### エラーハンドリング付き更新

```python
from abm_check.infrastructure.updater import ProgramUpdater
from abm_check.domain.exceptions import ProgramNotFoundError, FetchError

updater = ProgramUpdater()
program_ids = ["26-249", "26-156", "189-85"]

for program_id in program_ids:
    try:
        new_episodes, premium_to_free = updater.update_program(program_id)
        print(f"✓ {program_id}: New={len(new_episodes)}, P2F={len(premium_to_free)}")
        
    except ProgramNotFoundError:
        print(f"✗ {program_id}: Not found in storage")
        
    except FetchError as e:
        print(f"✗ {program_id}: Fetch failed - {e.reason}")
        
    except Exception as e:
        print(f"✗ {program_id}: Unexpected error - {e}")
```

### 変更履歴の記録

```python
from abm_check.infrastructure.updater import ProgramUpdater
from datetime import datetime
import json

updater = ProgramUpdater()

# 更新実行
results = updater.update_all_programs()

# 変更履歴をJSON形式で保存
history = {
    "timestamp": datetime.now().isoformat(),
    "programs": {}
}

for program_id, (new_eps, p2f_eps) in results.items():
    if new_eps or p2f_eps:
        history["programs"][program_id] = {
            "new_episodes": [
                {"number": ep.number, "title": ep.title}
                for ep in new_eps
            ],
            "premium_to_free": [
                {"number": ep.number, "title": ep.title}
                for ep in p2f_eps
            ]
        }

# 履歴ファイルに追記
with open("update_history.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(history, ensure_ascii=False) + "\n")
```

### 通知機能の統合

```python
from abm_check.infrastructure.updater import ProgramUpdater
import smtplib
from email.message import EmailMessage

def send_notification(program_title, new_count, p2f_count):
    """メール通知を送信"""
    msg = EmailMessage()
    msg["Subject"] = f"[abm_check] {program_title} に更新があります"
    msg["From"] = "noreply@example.com"
    msg["To"] = "user@example.com"
    
    body = f"""
    番組: {program_title}
    
    新規エピソード: {new_count}話
    プレミアム→無料: {p2f_count}話
    """
    msg.set_content(body)
    
    with smtplib.SMTP("localhost") as s:
        s.send_message(msg)

updater = ProgramUpdater()
results = updater.update_all_programs()

for program_id, (new_eps, p2f_eps) in results.items():
    if new_eps or p2f_eps:
        program = updater.storage.find_program(program_id)
        send_notification(program.title, len(new_eps), len(p2f_eps))
```

## パフォーマンス考慮事項

### 更新時間

- 1番組: 約5-10秒
- 10番組: 約50-100秒
- ネットワークI/Oがボトルネック

### メモリ使用量

- 1番組あたり: 約1-5MB
- 100番組: 約100-500MB

### 推奨事項

1. **バッチ処理**
   - 一度に大量の番組を更新しない
   - 優先度の高い番組から更新

2. **エラーハンドリング**
   - ネットワークエラーに対応
   - 一部の失敗で全体を止めない

3. **スリープの挿入**
   - サーバー負荷を考慮
   - 連続更新時は間隔を空ける

```python
import time

updater = ProgramUpdater()
storage = updater.storage
program_ids = storage.get_all_program_ids()

for i, program_id in enumerate(program_ids):
    try:
        updater.update_program(program_id)
        print(f"Updated {i+1}/{len(program_ids)}: {program_id}")
        
        # 5秒待機
        if i < len(program_ids) - 1:
            time.sleep(5)
            
    except Exception as e:
        print(f"Failed {program_id}: {e}")
```

## 差分検出の詳細

### 検出されるケース

**新規エピソード:**
- ✅ 新しく追加されたエピソード（DL可能）
- ❌ 新しく追加されたエピソード（プレミアム限定）

**プレミアム→無料:**
- ✅ プレミアム限定 → 無料（DL可能）
- ❌ プレミアム限定 → プレミアム限定（変更なし）
- ❌ 無料 → プレミアム限定（逆方向の変更は検出しない）

### 検出されないケース

- エピソードの削除（ABEMAでは稀）
- タイトルや説明文の変更
- サムネイルの変更
- 動画フォーマットの変更

これらの変更は番組データに反映されますが、差分として報告されません。
