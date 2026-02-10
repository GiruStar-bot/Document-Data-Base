import os
import json
import requests
from datetime import datetime
from abc import ABC, abstractmethod

class GenericEconomicCollector:
    """
    特定のサイト構造に依存せず、URLとAIの指示で文書を特定する汎用コレクター。
    """
    def __init__(self, country_code, organization_name, target_url):
        self.country_code = country_code
        self.organization_name = organization_name
        self.target_url = target_url
        self.base_data_path = f"data/{country_code}/{organization_name}"
        os.makedirs(self.base_data_path, exist_ok=True)

    def fetch_latest_documents(self):
        """
        AI (Gemini) を呼び出して、ターゲットURLから経済文書のリンクを抽出する（想定）。
        現在はモックデータを保存しますが、ここをAI API連携に差し替えます。
        """
        # ここに Gemini 連携 (Image Understanding or HTML Analysis) を入れることで
        # あらゆるサイトの構造変化に対応できます。
        print(f"  Fetching from {self.target_url} using AI Parsing...")
        
        # 擬似的に取得されたデータ
        sample_doc = {
            "id": f"{self.organization_name.lower()}_{datetime.now().strftime('%Y%m%d')}",
            "title": f"Recent Report from {self.organization_name}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": "Economic Policy",
            "url": self.target_url # 本来はAIが抽出したPDFリンク
        }
        self.save_metadata(sample_doc["id"], sample_doc)

    def save_metadata(self, doc_id, metadata):
        metadata.update({
            "collected_at": datetime.now().isoformat(),
            "country": self.country_code,
            "organization": self.organization_name,
            "doc_id": doc_id
        })
        file_path = os.path.join(self.base_data_path, f"{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def generate_master_index(self):
        all_data = []
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith(".json") and file != "master_index.json":
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                all_data.append(data)
                    except: pass
        
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)
        with open("data/master_index.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
