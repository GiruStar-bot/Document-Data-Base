import os
import json
import requests
import time
from datetime import datetime

class GenericEconomicCollector:
    """
    AIを使用して、任意のURLから経済文書のリンクを動的に抽出する汎用コレクター。
    """
    def __init__(self, country_code, organization_name, target_url=""):
        self.country_code = country_code
        self.organization_name = organization_name
        self.target_url = target_url
        self.api_key = os.getenv("GEMINI_API_KEY", "") 
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # パス設定
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.save_dir = os.path.join(self.data_dir, country_code, organization_name)
        os.makedirs(self.save_dir, exist_ok=True)

    def fetch_latest_documents(self):
        if not self.target_url or not self.api_key:
            return 0

        print(f"    [AI Engine] Analyzing: {self.organization_name} ({self.target_url})")
        
        try:
            # ユーザーエージェントを設定して拒否を防ぐ
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            res = requests.get(self.target_url, headers=headers, timeout=15)
            # 構造を把握するために冒頭のHTMLを抽出
            html_snippet = res.text[:7000] 
        except Exception as e:
            print(f"      Fetch Failed: {e}")
            return 0

        prompt = f"""
        Analyze this HTML from {self.target_url} and find the 2 most recent links to economic reports or PDF documents.
        Return ONLY a JSON array. Each object needs: title, date (YYYY-MM-DD), url (absolute link), category.
        HTML Snippet:
        {html_snippet}
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        count = 0
        for i in range(5):
            try:
                r = requests.post(self.api_url, json=payload, timeout=30)
                if r.status_code == 200:
                    text = r.json()['candidates'][0]['content']['parts'][0]['text']
                    docs = json.loads(text)
                    for doc in docs:
                        # 重複保存を避けるためのID生成
                        safe_title = "".join(filter(str.isalnum, doc.get('title', 'doc')))[:20]
                        doc_id = f"{safe_title}_{int(time.time())}"
                        self.save_metadata(doc_id, doc)
                        count += 1
                    break
                time.sleep(2**i)
            except:
                time.sleep(2**i)
        return count

    def save_metadata(self, doc_id, metadata):
        metadata.update({
            "country": self.country_code,
            "organization": self.organization_name,
            "collected_at": datetime.now().isoformat()
        })
        path = os.path.join(self.save_dir, f"{doc_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def generate_master_index(self):
        all_data = []
        # dataディレクトリ以下の全JSONを走査
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".json") and file not in ["master_index.json", "status.json"]:
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            d = json.load(f)
                            if isinstance(d, dict):
                                all_data.append(d)
                    except:
                        continue
        
        # 日付の新しい順にソート
        all_data.sort(key=lambda x: str(x.get("date", "")), reverse=True)
        
        with open(os.path.join(self.data_dir, "master_index.json"), "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"  [Index] Rebuilt index with {len(all_data)} documents.")
