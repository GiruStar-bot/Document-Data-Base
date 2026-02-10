import json
from pathlib import Path
from collectors.sources.mock_aggregator import MockAggregator

def generate_global_index():
    """
    全地域のデータを集約し、フロントエンド用の global-index.json を作成します。
    """
    print("Generating global index...")
    regions_path = Path("data/regions")
    global_index = []

    if not regions_path.exists():
        print("No data found in data/regions/")
        return

    # 各地域のディレクトリを走査
    for region_dir in regions_path.iterdir():
        if region_dir.is_dir():
            for country_file in region_dir.glob("*.json"):
                country_code = country_file.stem
                try:
                    with open(country_file, "r", encoding="utf-8") as f:
                        docs = json.load(f)
                        # 各ドキュメントに国・地域情報を付与してインデックスに追加
                        for doc in docs:
                            doc_entry = doc.copy()
                            doc_entry["country_code"] = country_code
                            doc_entry["region"] = region_dir.name
                            global_index.append(doc_entry)
                except Exception as e:
                    print(f"Error reading {country_file}: {e}")

    # 最新順にソート
    global_index.sort(key=lambda x: x["date"], reverse=True)

    # 保存
    output_path = Path("data/current")
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "global-index.json", "w", encoding="utf-8") as f:
        json.dump(global_index, f, ensure_ascii=False, indent=2)
    
    print(f"Global index updated with {len(global_index)} entries.")

def main():
    """
    メイン実行フロー
    """
    print("--- Public Document Collection System Started ---")
    
    # 1. データの収集 (モック収集機を実行)
    total_new = MockAggregator.run_all()
    print(f"Collection complete. Total new documents added: {total_new}")

    # 2. インデックスの生成
    generate_global_index()

    print("--- All tasks completed successfully ---")

if __name__ == "__main__":
    main()
