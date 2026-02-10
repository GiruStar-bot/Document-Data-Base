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
        # data/国名/組織名 という階層で保存場所を決定
        self.base_data_path = f"data/{country_code}/{organization_name}"
        os.makedirs(self.base_data_path, exist_ok=True)

    @abstractmethod
    def fetch_latest_documents(self):
        """
        最新の文書リストを取得するメソッド。
        継承先の各クローラーで具体的なスクレイピング処理を記述します。
        """
        pass

    def save_metadata(self, doc_id, metadata):
        """
        文書のメタデータをJSONとして保存し、GitHub Pagesで利用可能にします。
        """
        # URLが未設定、または仮の「#」の場合は警告を表示
        if "url" not in metadata or metadata["url"] == "#":
            print(f"Warning: No valid URL for {metadata.get('title', doc_id)}")

        # 共通情報を追加
        metadata.update({
            "collected_at": datetime.now().isoformat(),
            "country": self.country_code,
            "organization": self.organization_name,
            "doc_id": doc_id
        })
        
        file_path = os.path.join(self.base_data_path, f"{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print(f"Saved Metadata: {metadata['title']}")

    def generate_master_index(self):
        """
        data/ フォルダ内の全てのJSONを読み込み、フロントエンド用の master_index.json を作成します。
        """
        all_data = []
        # dataディレクトリ以下の全ファイルを探索
        for root, dirs, files in os.walk("data"):
            for file in files:
                # インデックス自身を除外して読み込み
                if file.endswith(".json") and file != "master_index.json":
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            all_data.append(data)
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
        
        # 文書の日付が新しい順（降順）に並べ替え
        all_data.sort(key=lambda x: x.get("date", ""), reverse=True)

        with open("data/master_index.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"Master index updated with {len(all_data)} items.")
