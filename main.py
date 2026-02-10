import json
import os
import sys
import random
from datetime import datetime
from collectors.economic_collectors import STABLE_COLLECTORS
from collectors.base_collector import GenericEconomicCollector
from discoverer import SourceDiscoverer

def main():
    print(f"--- Process Start: {datetime.now().isoformat()} ---")
    
    total_new_docs = 0

    # 1. 安定ソース（API不使用）の実行
    print("\n--- Phase 1: Stable Sources ---")
    for collector_class in STABLE_COLLECTORS:
        try:
            instance = collector_class()
            print(f"[*] {instance.organization_name}...")
            total_new_docs += instance.fetch_latest_documents()
        except Exception as e:
            print(f"  Error in {collector_class.__name__}: {e}")

    # 2. AIソース（API使用）の実行
    print("\n--- Phase 2: Generic AI Sources ---")
    registry_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collectors", "registry.json")
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            generic_sources = json.load(f)
        
        # 1回のリクエストを2件に絞る
        selected = random.sample(generic_sources, min(len(generic_sources), 2))
        for src in selected:
            print(f"[*] AI Analysis: {src['org']}...")
            try:
                collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
                total_new_docs += collector.fetch_latest_documents()
            except Exception as e:
                print(f"  AI Error: {e}")

    # 3. master_index.json の更新（何があっても最後に実行）
    print("\n--- Phase 3: Rebuilding Index ---")
    try:
        GenericEconomicCollector.generate_master_index()
    except Exception as e:
        print(f"Critical error during indexing: {e}")
    
    # GitHub Actions の変更トリガー用
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    status_path = os.path.join(data_dir, "status.json")
    os.makedirs(data_dir, exist_ok=True)
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump({
            "last_run": datetime.now().isoformat(),
            "docs_found": total_new_docs
        }, f, indent=4)
    
    print(f"--- Process Finished. Docs Found: {total_new_docs} ---")

if __name__ == "__main__":
    main()
