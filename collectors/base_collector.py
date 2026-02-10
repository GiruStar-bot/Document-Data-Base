import os
import json
import requests
import time
from datetime import datetime

class GenericEconomicCollector:
    def __init__(self, country_code, organization_name, target_url=""):
        self.country_code = country_code
        self.organization_name = organization_name
        self.target_url = target_url
        
        # APIキーは環境変数から取得（GitHub Secrets対応）
        self.api_key = os.getenv("GEMINI_API_KEY", "") 
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.save_dir = os.path.join(self.data_dir, country_code, organization_name)
        os.makedirs(self.save_dir, exist_ok=True)

    def fetch_latest_documents(self):
        if not self.target_url or not self.api_key:
            print("    [Skip] Missing URL or API Key")
            return 0

        print(f"    [AI] Analyzing {self.target_url}")
        try:
            res = requests.get(self.target_url, timeout=10)
            html = res.text[:5000]
        except: return 0

        payload = {
            "contents": [{"parts": [{"text": f"Extract latest 2 economic report links from this HTML as JSON array. URL: {self.target_url}\nHTML: {html}"}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        count = 0
        for i in range(3):
            try:
                r = requests.post(self.api_url, json=payload)
                if r.status_code == 200:
                    docs = json.loads(r.json()['candidates'][0]['content']['parts'][0]['text'])
                    for doc in docs:
                        self.save_metadata(f"doc_{int(time.time())}_{count}", doc)
                        count += 1
                    break
                time.sleep(2)
            except: time.sleep(2)
        return count

    def save_metadata(self, doc_id, metadata):
        metadata.update({"country": self.country_code, "organization": self.organization_name, "date": metadata.get("date", datetime.now().strftime("%Y-%m-%d"))})
        path = os.path.join(self.save_dir, f"{doc_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def generate_master_index(self):
        all_data = []
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".json") and file != "master_index.json" and file != "status.json":
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            d = json.load(f)
                            if isinstance(d, dict): all_data.append(d)
                    except: continue
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)
        with open(os.path.join(self.data_dir, "master_index.json"), "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"  [Index] Rebuilt with {len(all_data)} items.")
