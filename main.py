import json
import os
from collectors.base_collector import GenericEconomicCollector
from discoverer import SourceDiscoverer

def load_registry():
    registry_path = "collectors/registry.json"
    if not os.path.exists(registry_path):
        # 初期データ
        initial_data = [
            {"id": "imf", "country": "INT", "org": "IMF", "url": "https://www.imf.org/en/publications/search", "category": "Global"},
            {"id": "jp_mof", "country": "JPN", "org": "MOF", "url": "https://www.mof.go.jp/budget/index.html", "category": "Budget"},
            {"id": "us_fed", "country": "USA", "org": "FED", "url": "https://www.federalreserve.gov/monetarypolicy/beigebook.htm", "category": "Monetary"}
        ]
        os.makedirs("collectors", exist_ok=True)
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4)
        return initial_data
    
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("--- Starting Autonomous Document Collection ---")
    
    # 1. 登録済みソースの実行
    sources = load_registry()
    print(f"Loaded {len(sources)} sources from registry.")
    
    for src in sources:
        print(f"-> Processing {src['org']} ({src['country']})...")
        collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
        try:
            # AIを活用した汎用スクレイピング実行
            collector.fetch_latest_documents()
        except Exception as e:
            print(f"Error processing {src['org']}: {e}")

    # 2. 自動拡張フェーズ: 未知のソースをAIで探索
    print("\n--- Expansion Phase: Discovering New Sources ---")
    discoverer = SourceDiscoverer()
    new_sources = discoverer.search_new_sources(existing_sources=sources)
    
    if new_sources:
        print(f"Found {len(new_sources)} new potential sources!")
        # レジストリを更新
        sources.extend(new_sources)
        with open("collectors/registry.json", "w", encoding="utf-8") as f:
            json.dump(sources, f, indent=4, ensure_ascii=False)
    else:
        print("No new sources discovered in this cycle.")

    # 3. インデックス更新
    print("\n--- Finalizing: Updating master index ---")
    GenericEconomicCollector("INT", "SYSTEM", "").generate_master_index()
    
    print("--- Cycle Finished ---")

if __name__ == "__main__":
    main()
