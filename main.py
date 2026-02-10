from collectors.economic_collectors import IMFCollector, JapanMOFCollector

def main():
    print("--- Economic Document Collection Started ---")
    
    # クローラーのリスト
    collectors = [
        IMFCollector(),
        JapanMOFCollector()
        # ここに米国FRB、欧州ECBなどを順次追加
    ]
    
    # 実行
    for collector in collectors:
        print(f"Processing: {collector.organization_name}...")
        collector.fetch_latest_documents()
        
    # インデックス更新
    print("Updating master index...")
    IMFCollector().generate_master_index() # どのインスタンスから呼んでも全データを集約します
    
    print("--- Done ---")

if __name__ == "__main__":
    main()
