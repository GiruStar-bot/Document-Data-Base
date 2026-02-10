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
        self.api_key = os.getenv("GEMINI_API_KEY", "") 
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.save_dir = os.path.join(self.data_dir, country_code, organization_name)
        os.makedirs(self.save_dir, exist_ok=True)

    def fetch_latest_documents(self):
        if not self.target_url or not self.api_key:
            return 0

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(self.target_url, headers=headers, timeout=15)
            html = res.text[:4000] # 文字数をさらに絞ってトークン節約
        except: return 0

        # プロンプトを短くしてトークン節約
        payload = {
            "contents": [{"parts": [{"text": f"Extract 2 PDF links as JSON array from HTML. URL: {self.target_url}\nHTML: {html}"}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        try:
            r = requests.post(self.api_url, json=payload, timeout=30)
            if r.status_code == 429:
                raise Exception("429: API Quota Exhausted")
            
            if r.status_code == 200:
                docs = json.loads(r.json()['candidates'][0]['content']['parts'][0]['text'])
                count = 0
                for doc in docs:
                    doc_id = f"doc_{int(time.time())}_{count}"
                    self.save_metadata(doc_id, doc)
                    count += 1
                return count
        except Exception as e:
            if "429" in str(e): raise e # 429はmainに伝播させる
            print(f"      Error: {e}")
        return 0

    def save_metadata(self, doc_id, metadata):
        metadata.update({"country": self.country_code, "organization": self.organization_name, "collected_at": datetime.now().isoformat()})
        path = os.path.join(self.save_dir, f"{doc_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def generate_master_index(self):
        all_data = []
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".json") and file not in ["master_index.json", "status.json"]:
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            d = json.load(f)
                            if isinstance(d, dict): all_data.append(d)
                    except: continue
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)
        with open(os.path.join(self.data_dir, "master_index.json"), "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
