import json
import os
from collectors.base_collector import GenericEconomicCollector
from discoverer import SourceDiscoverer

def main():
    print("--- Autonomous Collection Start ---")
    
    # レジストリの読み込み
    registry_path = "collectors/registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            sources = json.load(f)
    else:
        sources = []

    # 1. 既存ソースからの収集
    for src in sources:
        print(f"Processing {src['org']}...")
        collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
        try:
            # ここでAIまたはスクレイピング実行
            collector.fetch_latest_documents()
        except Exception as e:
            print(f"Error in {src['org']}: {e}")

    # 2. AIによる新規ソース探索 (任意)
    try:
        discoverer = SourceDiscoverer()
        new_sources = discoverer.search_new_sources(sources)
        if new_sources:
            sources.extend(new_sources)
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(sources, f, indent=4, ensure_ascii=False)
            print(f"Added {len(new_sources)} new sources.")
    except Exception as e:
        print(f"Discovery error: {e}")

    # 3. master_index.json の更新 (ここが重要！)
    print("--- Rebuilding Master Index ---")
    # インデックス更新専用のインスタンスを作成して実行
    indexer = GenericEconomicCollector("SYSTEM", "INDEXER")
    indexer.generate_master_index()
    
    print("--- All processes finished ---")

if __name__ == "__main__":
    main()
