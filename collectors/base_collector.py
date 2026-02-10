import os
import json
import requests
import time
from datetime import datetime

class GenericEconomicCollector:
    """
    世界各国の経済文書を収集し、インデックスを生成するクラス。
    """
    def __init__(self, country_code, organization_name, target_url=""):
        self.country_code = country_code
        self.organization_name = organization_name
        self.target_url = target_url
        
        # APIキー取得
        self.api_key = os.getenv("GEMINI_API_KEY", "") 
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # 基準ディレクトリ：このファイル(collectors/base_collector.py)の2つ上の階層がルート
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.root_dir, "data")
        self.save_dir = os.path.join(self.data_dir, country_code, organization_name)
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)

    def fetch_latest_documents(self):
        """AIを使用して文書を抽出"""
        if not self.target_url or not self.api_key:
            return 0

        print(f"    [AI] Analyzing {self.organization_name}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(self.target_url, headers=headers, timeout=15)
            html = res.text[:5000]
        except: return 0

        payload = {
            "contents": [{"parts": [{"text": f"Extract 2 PDF links as JSON array from HTML. URL: {self.target_url}\nHTML: {html}"}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        count = 0
        try:
            r = requests.post(self.api_url, json=payload, timeout=30)
            if r.status_code == 200:
                docs = json.loads(r.json()['candidates'][0]['content']['parts'][0]['text'])
                for doc in docs:
                    safe_title = "".join(x for x in doc.get('title', 'doc') if x.isalnum())[:20]
                    doc_id = f"{safe_title}_{int(time.time())}"
                    self.save_metadata(doc_id, doc)
                    count += 1
        except Exception as e:
            print(f"      Error: {e}")
        return count

    def save_metadata(self, doc_id, metadata):
        """メタデータを個別のJSONとして保存"""
        metadata.update({
            "country": self.country_code,
            "organization": self.organization_name,
            "collected_at": datetime.now().isoformat(),
            "doc_id": doc_id
        })
        path = os.path.join(self.save_dir, f"{doc_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    @staticmethod
    def generate_master_index():
        """
        data/ フォルダ内の全JSONを集約します。
        絶対パスを使用して、確実にルートの data フォルダをスキャンします。
        """
        # ルートディレクトリを取得 (base_collector.py から見て2つ上)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(root_dir, "data")
        all_data = []
        
        print(f"  [Index] Scanning absolute path: {data_dir}")
        
        if not os.path.exists(data_dir):
            print(f"  [Error] Data directory NOT FOUND at {data_dir}")
            return

        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".json") and file not in ["master_index.json", "status.json"]:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            d = json.load(f)
                            if isinstance(d, dict):
                                all_data.append(d)
                    except Exception as e:
                        print(f"  [Skip] Failed to load {file}: {e}")

        # 日付で降順ソート
        all_data.sort(key=lambda x: str(x.get("date", "0000-00-00")), reverse=True)

        # インデックスの保存
        index_path = os.path.join(data_dir, "master_index.json")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        print(f"  [Success] master_index.json updated. Total items: {len(all_data)}")
        print(f"  [Path] Saved to: {index_path}")
