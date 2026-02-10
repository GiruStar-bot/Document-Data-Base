import os
import json
import requests
from datetime import datetime
from abc import ABC, abstractmethod

class EconomicDocumentCollector(ABC):
    """
    世界各国の経済文書を収集するための基底クラス。
    新しい国や組織を追加する場合は、このクラスを継承します。
    """
    def __init__(self, country_code, organization_name):
        self.country_code = country_code
        self.organization_name = organization_name
        self.base_data_path = f"data/{country_code}/{organization_name}"
        os.makedirs(self.base_data_path, exist_ok=True)

    @abstractmethod
    def fetch_latest_documents(self):
        """
        最新の文書リストを取得するメソッド。各サブクラスで実装。
        """
        pass

    def save_metadata(self, doc_id, metadata):
        """
        文書のメタデータをJSONとして保存。
        """
        metadata.update({
            "collected_at": datetime.now().isoformat(),
            "country": self.country_code,
            "organization": self.organization_name
        })
        file_path = os.path.join(self.base_data_path, f"{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print(f"Saved: {metadata['title']}")

    def generate_master_index(self):
        """
        収集した全データのインデックスを更新。フロントエンドが読み込む用。
        """
        all_data = []
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith(".json") and file != "master_index.json":
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        all_data.append(json.load(f))
        
        with open("data/master_index.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
