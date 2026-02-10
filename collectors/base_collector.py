import os
import json
import requests
import time
from datetime import datetime

class GenericEconomicCollector:
    """
    世界各国の経済文書を収集し、インデックスを生成する具象クラス。
    抽象クラスを解除し、直接インスタンス化できるようにしました。
    """
    def __init__(self, country_code, organization_name, target_url=""):
        self.country_code = country_code
        self.organization_name = organization_name
        self.target_url = target_url
        self.api_key = "" # Runtime provides this
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # 実行パスの解決
        self.base_path = os.getcwd()
        self.data_dir = os.path.join(self.base_path, "data")
        self.save_dir = os.path.join(self.data_dir, country_code, organization_name)
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)

    def fetch_latest_documents(self):
        """
        AIを使用して文書を抽出します。
        """
        if not self.target_url:
            return

        print(f"  [AI] Parsing target: {self.target_url}")
        
        try:
            # 1. ページ取得
            response = requests.get(self.target_url, timeout=15)
            html_snippet = response.text[:5000]
        except Exception as e:
            print(f"    Fetch error: {e}")
            return

        # 2. Geminiによる解析
        system_prompt = "あなたは経済レポートのURLを抽出するエンジニアです。JSON配列のみを返してください。"
        user_query = f"URL: {self.target_url}\nHTML Snippet: {html_snippet}\nこの中から最新のPDFまたはレポートのURLを2つ抽出してJSONで返してください。properties: [title, date, url, category]"

        payload = {
            "contents": [{"parts": [{"text": user_query}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "title": {"type": "STRING"},
                            "date": {"type": "STRING"},
                            "url": {"type": "STRING"},
                            "category": {"type": "STRING"}
                        },
                        "required": ["title", "date", "url"]
                    }
                }
            }
        }

        # リトライ処理
        for i in range(5):
            try:
                api_res = requests.post(self.api_url, json=payload)
                if api_res.status_code == 200:
                    docs = json.loads(api_res.json()['candidates'][0]['content']['parts'][0]['text'])
                    for doc in docs:
                        doc_id = f"{self.organization_name.lower()}_{int(time.time())}_{docs.index(doc)}"
                        self.save_metadata(doc_id, doc)
                    return
                time.sleep(2**i)
            except:
                time.sleep(2**i)

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
        data/ フォルダ内の全JSONを集約します。
        """
        all_data = []
        print(f"  [Index] Scanning data directory...")
        
        if not os.path.exists(self.data_dir):
            print(f"  [Warning] Directory not found: {self.data_dir}")
            return

        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".json") and file != "master_index.json":
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                all_data.append(data)
                    except:
                        continue

        # 日付でソート
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)

        index_path = os.path.join(self.data_dir, "master_index.json")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        print(f"  [Success] Master index updated with {len(all_data)} items.")
