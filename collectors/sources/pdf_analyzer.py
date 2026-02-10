import os
import json
import google.generativeai as genai
from pathlib import Path

class PDFAnalyzer:
    """Gemini APIを使用してPDFを分析する"""
    def __init__(self, api_key):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        else:
            self.model = None

    def analyze(self, pdf_path: Path):
        """PDFの内容をAIで要約・分類する"""
        if not self.model:
            return self._fallback_analysis()

        try:
            # PDFファイルをアップロード
            sample_file = genai.upload_file(path=pdf_path, mime_type="application/pdf")
            
            prompt = """
            この公的ドキュメントを読み、以下の項目を日本語のJSON形式で出力してください。
            - summary: 150文字以内の簡潔な要約
            - risk_level: 文脈に基づいた重要度 (Critical, Warning, Notice, Info)
            - category: 経済, 安全保障, 環境, 医療, その他のいずれか
            - insights: 注目すべきポイント3点のリスト
            JSON以外のテキストは含めないでください。
            """
            
            response = self.model.generate_content([prompt, sample_file])
            # JSON文字列を抽出
            raw_text = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(raw_text)
        except Exception as e:
            print(f"AI Analysis Error for {pdf_path.name}: {e}")
            return self._fallback_analysis()

    def _fallback_analysis(self):
        return {
            "summary": "AI分析がスキップされました（APIキー未設定またはエラー）。",
            "risk_level": "Notice",
            "category": "その他",
            "insights": ["資料は保存されています。詳細を確認してください。"]
        }
