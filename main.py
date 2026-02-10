import json
import os
import sys
import random
from datetime import datetime
from collectors.base_collector import GenericEconomicCollector
from discoverer import SourceDiscoverer

def main():
    print(f"--- Quota-Aware Process Started at {datetime.now().isoformat()} ---")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    registry_path = os.path.join(base_dir, "collectors", "registry.json")
    status_path = os.path.join(base_dir, "data", "status.json")

    # 1. レジストリの読み込み
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            sources = json.load(f)
    else:
        sources = [
            {"id": "imf", "country": "INT", "org": "IMF", "url": "https://www.imf.org/en/publications/search", "category": "Global"},
            {"id": "jp_mof", "country": "JPN", "org": "MOF", "url": "https://www.mof.go.jp/budget/index.html", "category": "Budget"}
        ]

    # 【省エネ戦略】1回の実行で処理するソースを最大3件に絞る（ランダムに選ぶことで全ソースを順次カバー）
    MAX_SOURCES_PER_RUN = 3
    if len(sources) > MAX_SOURCES_PER_RUN:
        selected_sources = random.sample(sources, MAX_SOURCES_PER_RUN)
        print(f"[*] Quota Mode: Processing {MAX_SOURCES_PER_RUN} out of {len(sources)} sources.")
    else:
        selected_sources = sources

    total_new_docs = 0
    quota_exhausted = False

    # 2. 収集実行
    for src in selected_sources:
        if quota_exhausted: break
        print(f"[*] Processing {src['org']}...")
        collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
        try:
            found_count = collector.fetch_latest_documents()
            total_new_docs += found_count
        except Exception as e:
            if "429" in str(e):
                print("[!] API Quota Reached. Stopping collection.")
                quota_exhausted = True
            else:
                print(f"  Error: {e}")

    # 3. AIによる新規ソース探索（ソースが少ない時、または20%の確率で実行）
    if not quota_exhausted and (len(sources) < 10 or random.random() < 0.2):
        print("\n--- Expansion Phase (Occasional) ---")
        try:
            discoverer = SourceDiscoverer()
            new_sources = discoverer.search_new_sources(sources)
            if new_sources:
                sources.extend(new_sources)
                with open(registry_path, "w", encoding="utf-8") as f:
                    json.dump(sources, f, indent=4, ensure_ascii=False)
                print(f"[+] AI discovered {len(new_sources)} new sources.")
        except Exception as e:
            print(f"Discovery error: {e}")

    # 4. インデックス更新（これはAPIを使わないので必ず実行）
    print("\n--- Finalizing Index ---")
    indexer = GenericEconomicCollector("SYSTEM", "INDEXER")
    indexer.generate_master_index()
    
    # 5. ステータス保存
    status_log = {
        "last_run": datetime.now().isoformat(),
        "docs_collected_this_run": total_new_docs,
        "total_sources": len(sources),
        "quota_hit": quota_exhausted
    }
    os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status_log, f, indent=4)

    print(f"--- Process Finished. ---")

if __name__ == "__main__":
    main()
