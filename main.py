import json
import os
import sys
from collectors.base_collector import GenericEconomicCollector
from discoverer import SourceDiscoverer

def main():
    print("--- Autonomous Collection Start ---")
    
    # 実行パスを調整 (モジュール読み込みのため)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # レジストリの読み込み
    registry_path = "collectors/registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            sources = json.load(f)
    else:
        # デフォルトソース
        sources = [
            {"id": "imf", "country": "INT", "org": "IMF", "url": "https://www.imf.org/en/publications/search", "category": "Global"},
            {"id": "jp_mof", "country": "JPN", "org": "MOF", "url": "https://www.mof.go.jp/budget/index.html", "category": "Budget"}
        ]

    # 1. 既存ソースからの収集
    for src in sources:
        print(f"Processing {src['org']}...")
        collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
        try:
            collector.fetch_latest_documents()
        except Exception as e:
            print(f"  Error processing {src['org']}: {e}")

    # 2. AIによる新規ソース探索
    print("\n--- Expansion Phase ---")
    try:
        discoverer = SourceDiscoverer()
        new_sources = discoverer.search_new_sources(sources)
        if new_sources:
            sources.extend(new_sources)
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(sources, f, indent=4, ensure_ascii=False)
            print(f"Added {len(new_sources)} new sources to registry.")
    except Exception as e:
        print(f"Discovery error: {e}")

    # 3. master_index.json の更新
    print("\n--- Finalizing: Rebuilding Master Index ---")
    try:
        # GenericEconomicCollector は具象クラスになったので直接呼べます
        indexer = GenericEconomicCollector("SYSTEM", "INDEXER")
        indexer.generate_master_index()
    except Exception as e:
        print(f"Critical error during indexing: {e}")
    
    print("--- All processes finished ---")

if __name__ == "__main__":
    main()
