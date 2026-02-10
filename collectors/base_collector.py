import os
import json
from datetime import datetime
from abc import ABC, abstractmethod

class GenericEconomicCollector:
    """
    世界各国の経済文書を収集し、インデックスを生成する汎用クラス。
    """
    def __init__(self, country_code, organization_name, target_url=""):
        self.country_code = country_code
        self.organization_name = organization_name
        self.target_url = target_url
        # 実行ディレクトリからの相対パスを保証
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_path, "data")
        self.save_dir = os.path.join(self.data_dir, country_code, organization_name)
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)

    def save_metadata(self, doc_id, metadata):
        """個別のJSONファイルを保存"""
        metadata.update({
            "collected_at": datetime.now().isoformat(),
            "country": self.country_code,
            "organization": self.organization_name,
            "doc_id": doc_id
        })
        file_path = os.path.join(self.save_dir, f"{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print(f"    [Saved] {metadata.get('title')}")

    def generate_master_index(self):
        """
        data/ フォルダ内の全JSONをスキャンして master_index.json を再構築します。
        """
        all_data = []
        print(f"  [Index] Scanning directory: {self.data_dir}")
        
        if not os.path.exists(self.data_dir):
            print("  [Error] Data directory does not exist.")
            return

        for root, _, files in os.walk(self.data_dir):
            for file in files:
                # master_index.json 自体は読み込まない
                if file.endswith(".json") and file != "master_index.json":
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                all_data.append(data)
                    except Exception as e:
                        print(f"  [Error] Failed to load {file}: {e}")

        # 日付順にソート（最新が上）
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)

        # インデックスの書き出し
        index_path = os.path.join(self.data_dir, "master_index.json")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        print(f"  [Success] Master index updated with {len(all_data)} items at {index_path}")

    @abstractmethod
    def fetch_latest_documents(self):
        pass
