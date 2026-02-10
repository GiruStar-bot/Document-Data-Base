import json
import os
import requests
import time

class SourceDiscoverer:
    """
    Gemini APIを使用して、インターネットから新しい経済文書のソース（公式サイト）を探索するクラス。
    """
    def __init__(self):
        # 環境変数からAPIキーを取得
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def search_new_sources(self, existing_sources):
        if not self.api_key:
            print("  [Discovery] Skip: GEMINI_API_KEY is not set.")
            return []

        existing_orgs = [s['org'] for s in existing_sources]
        
        # 探索のためのプロンプト
        prompt = f"""
        Find 3 official websites (Ministry of Finance or Central Bank) of countries NOT in this list: {', '.join(existing_orgs)}.
        Focus on emerging economies in Africa, SE Asia, or South America.
        Return ONLY a JSON array of objects with keys: id, country (ISO3), org, url (direct link to publications/reports page), category.
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        # 5回リトライ（指数バックオフ）
        for i in range(5):
            try:
                print(f"  [AI Discovery] Searching for new sources (Attempt {i+1})...")
                response = requests.post(self.api_url, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    new_sources = json.loads(text)
                    
                    # URLの重複チェック
                    unique_sources = [ns for ns in new_sources if ns['url'] not in [s['url'] for s in existing_sources]]
                    return unique_sources
                
                print(f"    API Error: {response.status_code}")
                time.sleep(2**i)
            except Exception as e:
                print(f"    Exception: {e}")
                time.sleep(2**i)
        
        return []
