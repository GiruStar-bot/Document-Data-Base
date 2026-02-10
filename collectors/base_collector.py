import os
import json
import requests
from datetime import datetime
from abc import ABC, abstractmethod

class EconomicDocumentCollector(ABC):
    """
    世界各国の経済文書を収集するための基底クラス。
    """
    def __init__(self, country_code, organization_name):
        self.country_code = country_code
        self.organization_name = organization_name
        self.base_data_path = f"data/{country_code}/{organization_name}"
        os.makedirs(self.base_data_path, exist_ok=True)

    @abstractmethod
    def fetch_latest_documents(self):
        """最新文書リストを取得（各子クラスで実装）"""
        pass

    def save_metadata(self, doc_id, metadata):
        """メタデータを保存"""
        metadata.update({
            "collected_at": datetime.now().isoformat(),
            "country": self.country_code,
            "organization": self.organization_name,
            "doc_id": doc_id
        })
        
        file_path = os.path.join(self.base_data_path, f"{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print(f"Saved Metadata: {metadata.get('title', doc_id)}")

    def generate_master_index(self):
        """
        全JSONを集約して master_index.json を生成。
        リスト型のデータが混入してソートエラーが出る問題を修正。
        """
        all_data = []
        for root, dirs, files in os.walk("data"):
            for file in files:
                # master_index.json 自体は読み込まない
                if file.endswith(".json") and file != "master_index.json":
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            # データが辞書型であることを確認 (リスト型ならスキップ)
                            if isinstance(data, dict):
                                all_data.append(data)
                            else:
                                print(f"Skipping non-dict file: {file}")
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
        
        # 'date' キーを持つものだけでソート。ない場合は空文字にする
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)

        # 最終的な書き出し
        with open("data/master_index.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully updated master index with {len(all_data)} items.")
