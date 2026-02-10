from collectors.economic_collectors import IMFCollector, JapanMOFCollector, USFedCollector

def main():
    print("--- Economic Document Collection Started ---")
    
    # 実行するクローラーのリストに USFedCollector を追加
    collectors = [
        IMFCollector(),
        JapanMOFCollector(),
        USFedCollector()  # ← ここを追加！
    ]
    
    # 各クローラーを実行
    for collector in collectors:
        print(f"Processing: {collector.organization_name}...")
        try:
            collector.fetch_latest_documents()
        except Exception as e:
            print(f"Error in {collector.organization_name}: {e}")
        
    # 最後に全てのデータを集約して master_index.json を作成
    print("Updating master index...")
    # どのコレクターを使っても generate_master_index は全データをスキャンします
    IMFCollector().generate_master_index()
    
    print("--- All processes completed successfully ---")

if __name__ == "__main__":
    main()
