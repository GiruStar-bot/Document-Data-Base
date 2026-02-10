import os
import sys
from datetime import datetime

# プロジェクトルートを作業ディレクトリとして追加
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# インポートエラーを防ぐため絶対パスでインポート
try:
    from collectors.economic_collectors import STABLE_COLLECTORS
    from scripts.rebuild_index import rebuild_index
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def main():
    print(f"=== GiruStar Archive Engine: {datetime.now().isoformat()} ===")
    
    total = 0
    # Phase 1: Direct Collection (Stable Sources)
    print("\n[Phase 1] Processing Stable Sources...")
    for collector_class in STABLE_COLLECTORS:
        try:
            c = collector_class()
            print(f"[*] Running {c.organization_name} ({c.country_code})...")
            count = c.fetch_latest_documents()
            total += (count if count is not None else 0)
        except Exception as e:
            print(f"  [!] Failed {collector_class.__name__}: {e}")

    # Phase 2: Indexing
    print("\n[Phase 2] Rebuilding Master Index...")
    try:
        rebuild_index()
        print("  [Success] master_index.json updated.")
    except Exception as e:
        print(f"  [!] Indexing Error: {e}")

    print(f"\n=== Process Completed. Total items processed: {total} ===")

if __name__ == "__main__":
    main()
