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
            print("  [Discovery] Error: GEMINI_API_KEY is not set.")
            return []

        existing_orgs = [s['org'] for s in existing_sources]
        existing_urls = [s['url'] for s in existing_sources]
        
        system_instruction = """あなたは世界中の公的経済データの所在を特定するエキスパートです。
必ず指定されたJSON形式の配列のみを回答してください。説明文は一切不要です。"""
        
        # AIに対して「既存リスト以外」を強く意識させ、かつ検索ワードを具体化します
        prompt = f"""
        世界中には190以上の国と数多くの国際機関があります。
        現在、以下の組織はすでに収集済みです: {', '.join(existing_orgs)}。
        
        これら以外の国（特に南米、中央アジア、中東、アフリカ、太平洋諸国）で、
        最新の経済報告書や統計PDFを公開している「財務省」または「中央銀行」の公式URLを【10件】新しく特定してください。
        
        以下の条件を厳守してください：
        1. 既にリストにあるURL ({', '.join(existing_urls[:5])}...) は絶対に含めない。
        2. 文書（Publications/Reports）が直接掲載されているページのURLを指定する。
        3. 以下のJSON配列形式で出力する。
        
        [
            {{"id": "unique_id", "country": "ISO3", "org": "略称", "url": "URL", "category": "Economic"}}
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
                print(f"  [AI Discovery] Searching for 10 new sources (Attempt {i+1})...")
                response = requests.post(self.api_url, json=payload, timeout=50)
                
                if response.status_code == 200:
                    result = response.json()
                    raw_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    try:
                        new_sources = json.loads(raw_text)
                    except json.JSONDecodeError:
                        print("    [Error] AI returned invalid JSON. Retrying...")
                        continue

                    # フィルタリング
                    unique_new_sources = []
                    for ns in new_sources:
                        if ns['url'] not in existing_urls:
                            unique_new_sources.append(ns)
                    
                    print(f"    [Success] AI suggested {len(new_sources)} sources, {len(unique_new_sources)} are new.")
                    return unique_new_sources
                
                print(f"    [Error] API Status: {response.status_code}")
                time.sleep(2**i)
            except Exception as e:
                print(f"    [Exception] {e}")
                time.sleep(2**i)
        
        return []
