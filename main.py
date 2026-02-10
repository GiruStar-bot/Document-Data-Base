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

    # 1. 安定ソースの実行
    print("\n--- Phase 1: Stable Sources ---")
    for collector_class in STABLE_COLLECTORS:
        try:
            instance = collector_class()
            print(f"[*] {instance.organization_name}...")
            total_new_docs += instance.fetch_latest_documents()
        except Exception as e:
            print(f"  Error: {e}")

    # 2. AIソースの実行 (Quota節約のため2件)
    print("\n--- Phase 2: Generic AI Sources ---")
    registry_path = "collectors/registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            generic_sources = json.load(f)
        
        selected = random.sample(generic_sources, min(len(generic_sources), 2))
        for src in selected:
            print(f"[*] AI: {src['org']}...")
            try:
                collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
                total_new_docs += collector.fetch_latest_documents()
            except Exception as e:
                print(f"  AI Error: {e}")

    # 3. master_index.json の更新 (静的メソッドを直接実行)
    print("\n--- Phase 3: Rebuilding Index ---")
    try:
        GenericEconomicCollector.generate_master_index()
    except Exception as e:
        print(f"Critical error during indexing: {e}")
    
    # 生存確認用ログ
    status_path = "data/status.json"
    os.makedirs("data", exist_ok=True)
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump({"last_run": datetime.now().isoformat(), "docs_found": total_new_docs}, f, indent=4)
    
    print("--- Process Finished ---")

if __name__ == "__main__":
    main()
