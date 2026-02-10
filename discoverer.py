import json
import os
import requests
import time

class SourceDiscoverer:
    """
    Gemini APIを使用して、インターネットから新しい経済文書のソース（公式サイト）を探索するクラス。
    """
    def __init__(self):
        # 環境変数からAPIキーを取得。Secretに設定されていればここに入ります。
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def search_new_sources(self, existing_sources):
        if not self.api_key:
            print("  [Discovery] Skip: GEMINI_API_KEY is not set in environment.")
            return []

        existing_orgs = [s['org'] for s in existing_sources]
        
        system_instruction = "あなたは経済機関の公式サイトを探索する専門家です。必ず指定されたJSON配列形式で回答してください。"
        
        # 探索数を3つから10件以上に増やし、より広範な地域を指定します
        prompt = f"""
        現在以下の組織を収集済みです: {', '.join(existing_orgs)}。
        これら以外の、まだ登録されていない世界各国の財務省（Ministry of Finance）や中央銀行（Central Bank）の、
        最新の経済レポートや公的文書が掲載されている公式URLを「10件」新しく見つけてください。
        
        対象地域: アフリカ、中東、東南アジア、中南米、東欧を重点的に。
        
        回答は以下の形式のJSON配列のみにしてください:
        [
            {{"id": "unique_id", "country": "ISO3", "org": "略称", "url": "レポートページのURL", "category": "Economic"}}
        ]
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        for i in range(5):
            try:
                print(f"  [AI Discovery] Searching web for more sources (Attempt {i+1})...")
                response = requests.post(self.api_url, json=payload, timeout=40)
                if response.status_code == 200:
                    result = response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    new_sources = json.loads(text)
                    # 重複を除外して返す
                    filtered_sources = [ns for ns in new_sources if ns['url'] not in [s['url'] for s in existing_sources]]
                    print(f"  [AI Discovery] Found {len(filtered_sources)} new unique sources.")
                    return filtered_sources
                
                print(f"    API Error: {response.status_code}")
                time.sleep(2**i)
            except Exception as e:
                print(f"    Exception during discovery: {e}")
                time.sleep(2**i)
        
        return []
