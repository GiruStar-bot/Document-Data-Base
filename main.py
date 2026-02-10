import os
import sys
from datetime import datetime

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.economic_collectors import STABLE_COLLECTORS
from scripts.rebuild_index import rebuild_index

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
            total += count
        except Exception as e:
            print(f"  [!] Failed: {e}")

    # Phase 2: AI-Assisted Discovery (Optional logic can go here)
    # For now, focus on stable growth.

    # Phase 3: Indexing
    print("\n[Phase 3] Rebuilding Master Index...")
    try:
        rebuild_index()
    except Exception as e:
        print(f"  [!] Indexing Error: {e}")

    print(f"\n=== Process Completed. New items found: {total} ===")

if __name__ == "__main__":
    main()
