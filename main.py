import os
import sys
from datetime import datetime

# モジュール検索パスの追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.economic_collectors import STABLE_COLLECTORS
from collectors.base_collector import GenericEconomicCollector

def main():
    print(f"=== Execution Start: {datetime.now().isoformat()} ===")
    
    # フェーズ1: 安定ソースの収集
    print("\nPhase 1: Stable Collectors")
    for collector_class in STABLE_COLLECTORS:
        try:
            c = collector_class()
            print(f"[*] Running {c.organization_name}...")
            c.fetch_latest_documents()
        except Exception as e:
            print(f"[!] Failed stable collector {collector_class.__name__}: {e}")

    # フェーズ2: 目次の再構築 (独立スクリプトを呼び出す)
    print("\nPhase 2: Indexing")
    try:
        from scripts.rebuild_index import rebuild_index
        rebuild_index()
    except Exception as e:
        print(f"[!] Critical error during index phase: {e}")

    print("\n=== Execution Finished ===")

if __name__ == "__main__":
    main()
