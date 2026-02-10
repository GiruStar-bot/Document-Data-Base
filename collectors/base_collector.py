import os
import json
import requests
import time
from datetime import datetime

class GenericEconomicCollector:
    """
    AIを使用して、任意のURLから経済文書のリンクを動的に抽出する汎用コレクター。
    """
    def __init__(self, country_code, organization_name, target_url):
        self.country_code = country_code
        self.organization_name = organization_name
        self.target_url = target_url
        self.base_data_path = f"data/{country_code}/{organization_name}"
        self.api_key = "" 
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        os.makedirs(self.base_data_path, exist_ok=True)

    def fetch_latest_documents(self):
        """
        ページのHTML構造をAIに解析させ、最新の文書リンクを取得します。
        """
        if not self.target_url: return

        print(f"  [AI] Parsing target page: {self.target_url}")
        
        try:
            # 1. ページのHTMLテキストを取得 (簡易的に最初の5000文字)
            page_response = requests.get(self.target_url, timeout=10)
            html_snippet = page_response.text[:5000]
        except Exception as e:
            print(f"    Failed to fetch HTML: {e}")
            return

        # 2. Geminiにリンクの抽出を依頼
        system_prompt = "あなたはHTMLから経済レポートのURLを抽出するスクレイピングエンジニアです。JSON形式の配列のみを返してください。"
        user_query = f"""
        以下のHTMLスニペットまたはこのURL ({self.target_url}) から、最新の経済レポート、統計、または公的文書のURLを最大2つ抽出してください。
        絶対パスのURLを返してください。
        
        HTML:
        {html_snippet}
        """

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

        for i in range(5):
            try:
                response = requests.post(self.api_url, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    docs = json.loads(result['candidates'][0]['content']['parts'][0]['text'])
                    for doc in docs:
                        doc_id = f"{self.organization_name.lower()}_{int(time.time())}"
                        self.save_metadata(doc_id, doc)
                    return
                time.sleep(2**i)
            except Exception:
                time.sleep(2**i)

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
        print(f"    [AI Found] {metadata.get('title')}")

    def generate_master_index(self):
        all_data = []
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith(".json") and file != "master_index.json":
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict): all_data.append(data)
                    except: pass
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)
        with open("data/master_index.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
