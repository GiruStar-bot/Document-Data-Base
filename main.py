import json
import os
import sys
import random
from datetime import datetime
# 専用クローラーと汎用クローラーをインポート
from collectors.economic_collectors import STABLE_COLLECTORS
from collectors.base_collector import GenericEconomicCollector
from discoverer import SourceDiscoverer

def main():
    print(f"--- Hybrid Collection Process Started at {datetime.now().isoformat()} ---")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    registry_path = os.path.join(base_dir, "collectors", "registry.json")
    status_path = os.path.join(base_dir, "data", "status.json")

    total_new_docs = 0

    # === フェーズ1: 安定ソース（専用クローラー）の実行 ===
    # これらはGemini APIを消費せずに実行される
    print("\n--- Phase 1: Processing Stable Sources (Non-AI) ---")
    for collector_class in STABLE_COLLECTORS:
        try:
            instance = collector_class()
            print(f"[*] Processing {instance.organization_name}...")
            count = instance.fetch_latest_documents()
            total_new_docs += count
        except Exception as e:
            print(f"  Error in stable source {collector_class.__name__}: {e}")

    # === フェーズ2: AIソース（レジストリ内の汎用クローラー）の実行 ===
    print("\n--- Phase 2: Processing Generic Sources (AI-Assisted) ---")
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            generic_sources = json.load(f)
    else:
        generic_sources = []

    # API節約のため、1回の実行でAI解析を行うソースは最大2件に絞る
    MAX_AI_TASKS = 2
    if len(generic_sources) > MAX_AI_TASKS:
        selected_generic = random.sample(generic_sources, MAX_AI_TASKS)
        print(f"[*] AI Mode: Processing {MAX_AI_TASKS} out of {len(generic_sources)} generic sources.")
    else:
        selected_generic = generic_sources

    quota_exhausted = False
    for src in selected_generic:
        if quota_exhausted: break
        print(f"[*] AI analyzing {src['org']}...")
        collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
        try:
            count = collector.fetch_latest_documents()
            total_new_docs += count
        except Exception as e:
            if "429" in str(e):
                print("[!] Gemini API Quota Reached. Skipping remaining AI tasks.")
                quota_exhausted = True
            else:
                print(f"  AI Error: {e}")

    # === フェーズ3: AIによる新規ソース探索（低頻度実行） ===
    if not quota_exhausted and random.random() < 0.1: # 10%の確率で実行
        print("\n--- Phase 3: AI Discovery (Occasional) ---")
        try:
            discoverer = SourceDiscoverer()
            new_sources = discoverer.search_new_sources(generic_sources)
            if new_sources:
                generic_sources.extend(new_sources)
                with open(registry_path, "w", encoding="utf-8") as f:
                    json.dump(generic_sources, f, indent=4, ensure_ascii=False)
                print(f"[+] AI discovered {len(new_sources)} new sources.")
        except Exception as e:
            print(f"Discovery error: {e}")

    # === フェーズ4: インデックス更新 ===
    print("\n--- Finalizing Index ---")
    GenericEconomicCollector("SYSTEM", "INDEXER").generate_master_index()
    
    # ステータス保存
    status_log = {
        "last_run": datetime.now().isoformat(),
        "docs_collected": total_new_docs,
        "generic_sources_count": len(generic_sources),
        "quota_exhausted": quota_exhausted
    }
    os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status_log, f, indent=4)

    print(f"--- Process Finished. New docs: {total_new_docs} ---")

if __name__ == "__main__":
    main()
