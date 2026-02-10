from collectors.economic_collectors import IMFCollector, JapanMOFCollector, USFedCollector

def main():
    print("--- Economic Document Collection Started ---")
    
    # 実行するクローラーのリスト
    collectors = [
        IMFCollector(),
        JapanMOFCollector(),
        USFedCollector()
    ]
    
    # 各クローラーを実行してデータを生成
    for collector in collectors:
        print(f"--- Processing: {collector.organization_name} ({collector.country_code}) ---")
        try:
            collector.fetch_latest_documents()
            print(f"Successfully processed {collector.organization_name}")
        except Exception as e:
            print(f"Error in {collector.organization_name}: {e}")
        
    # 最後に全てのデータを集約して master_index.json を作成
    print("--- Finalizing: Updating master index ---")
    try:
        # IMFCollector のインスタンスを使ってインデックス作成メソッドを呼び出し
        IMFCollector().generate_master_index()
        print("Master index updated successfully.")
    except Exception as e:
        print(f"Critical error during index generation: {e}")
    
    print("--- All processes finished ---")

if __name__ == "__main__":
    main()
