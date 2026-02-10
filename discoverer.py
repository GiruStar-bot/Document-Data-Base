import json
import requests
import time

class SourceDiscoverer:
    """
    Gemini APIを使用して、インターネットから新しい経済文書のソース（公式サイト）を探索するクラス。
    """
    def __init__(self):
        self.api_key = "" # 実行環境から自動提供されます
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def _call_gemini(self, prompt, system_instruction):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "country": {"type": "STRING"},
                            "org": {"type": "STRING"},
                            "url": {"type": "STRING"},
                            "category": {"type": "STRING"}
                        },
                        "required": ["id", "country", "org", "url", "category"]
                    }
                }
            }
        }

        for i in range(5):
            try:
                response = requests.post(self.url, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(text)
                time.sleep(2**i) # 指数バックオフ: 1s, 2s, 4s, 8s, 16s
            except Exception:
                time.sleep(2**i)
        return []

    def search_new_sources(self, existing_sources):
        existing_orgs = [s['org'] for s in existing_sources]
        system_instruction = "あなたは世界中の公的経済文書（官報、予算書、中央銀行レポート）を収集する専門家です。指定された形式のJSON配列のみを返してください。"
        
        prompt = f"""
        現在、以下の組織を追跡しています: {', '.join(existing_orgs)}。
        これら以外の、まだ登録されていない国の「財務省(Ministry of Finance)」または「中央銀行(Central Bank)」の
        公式な「経済報告書（Reports/Publications）ページ」のURLを3つ新しく見つけてください。
        特にアジア、アフリカ、ヨーロッパの国を優先してください。
        """

        print("  [AI] Searching the web for new economic sources...")
        new_sources = self._call_gemini(prompt, system_instruction)
        
        # 重複チェック
        unique_new_sources = []
        for ns in new_sources:
            if ns['url'] not in [s['url'] for s in existing_sources]:
                unique_new_sources.append(ns)
        
        return unique_new_sources
