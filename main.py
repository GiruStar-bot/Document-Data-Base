import json
import os
import sys
from datetime import datetime
from collectors.base_collector import GenericEconomicCollector
from discoverer import SourceDiscoverer

def main():
    print(f"--- Process Started at {datetime.now().isoformat()} ---")
    
    # 実行ディレクトリを固定
    base_dir = os.path.dirname(os.path.abspath(__file__))
    registry_path = os.path.join(base_dir, "collectors", "registry.json")
    status_path = os.path.join(base_dir, "data", "status.json")

    # 0. ログの初期化（生存確認用）
    status_log = {
        "last_run": datetime.now().isoformat(),
        "new_sources_found": 0,
        "documents_collected": 0,
        "errors": []
    }

    # 1. レジストリの読み込み
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            sources = json.load(f)
    else:
        sources = [
            {"id": "imf", "country": "INT", "org": "IMF", "url": "https://www.imf.org/en/publications/search", "category": "Global"},
            {"id": "jp_mof", "country": "JPN", "org": "MOF", "url": "https://www.mof.go.jp/budget/index.html", "category": "Budget"}
        ]

    # 2. 既存ソースからの収集
    for src in sources:
        print(f"[*] Processing {src['org']}...")
        collector = GenericEconomicCollector(src['country'], src['org'], src['url'])
        try:
            found_count = collector.fetch_latest_documents()
            status_log["documents_collected"] += found_count
        except Exception as e:
            status_log["errors"].append(f"{src['org']}: {str(e)}")

    # 3. AIによる新規ソース探索（自律拡張）
    print("\n--- Expansion Phase ---")
    try:
        discoverer = SourceDiscoverer()
        new_sources = discoverer.search_new_sources(sources)
        if new_sources:
            sources.extend(new_sources)
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(sources, f, indent=4, ensure_ascii=False)
            status_log["new_sources_found"] = len(new_sources)
            print(f"[+] AI discovered {len(new_sources)} new sources.")
    except Exception as e:
        status_log["errors"].append(f"Discovery: {str(e)}")

    # 4. master_index.json の強制更新
    print("\n--- Finalizing Index ---")
    indexer = GenericEconomicCollector("SYSTEM", "INDEXER")
    indexer.generate_master_index()
    
    # 5. ステータス保存（これがGitHubへの変更トリガーになる）
    os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status_log, f, indent=4)

    print(f"--- Process Finished. Documents: {status_log['documents_collected']} ---")

if __name__ == "__main__":
    main()
