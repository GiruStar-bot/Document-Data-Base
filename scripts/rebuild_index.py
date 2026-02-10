import os
import json
from datetime import datetime

def rebuild_index():
    """
    クラスや外部ライブラリに依存せず、dataフォルダ内の全JSONをスキャンして
    master_index.json を再構築する独立スクリプト。
    """
    print("--- Index Rebuild Started ---")
    
    # 実行場所に関わらずリポジトリのルートにあるdataフォルダを探す
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    index_path = os.path.join(data_dir, "master_index.json")
    
    print(f"Target Directory: {data_dir}")
    
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} does not exist.")
        return

    all_items = []
    
    # 再帰的に全ファイルを走査
    for root, _, files in os.walk(data_dir):
        for file in files:
            # 自身とステータスファイルは除外
            if file.endswith(".json") and file not in ["master_index.json", "status.json"]:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = json.load(f)
                        if isinstance(content, dict):
                            # 最低限必要なフィールドを保証
                            if "title" in content:
                                all_items.append(content)
                except Exception as e:
                    print(f"Skipping {file}: {e}")

    # 日付でソート（日付がないものは一番下に）
    all_items.sort(key=lambda x: str(x.get("date", "0000-00-00")), reverse=True)

    # 書き出し
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(all_items, f, ensure_ascii=False, indent=4)
        print(f"--- [Success] master_index.json updated with {len(all_items)} items ---")
    except Exception as e:
        print(f"Critical Error saving index: {e}")

if __name__ == "__main__":
    rebuild_index()
