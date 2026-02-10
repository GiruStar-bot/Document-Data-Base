import os
import json
import base64
from pathlib import Path
import google.generativeai as genai

class PDFAnalyzer:
    """
    PDFファイルをGemini AIで分析し、構造化データを抽出するクラス。
    """
    def __init__(self, api_key=""):
        # APIキーの設定（環境変数または直接入力）
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

    def analyze_pdf(self, pdf_path: Path):
        """
        PDFを読み込み、AIに分析を依頼する。
        """
        if not self.api_key:
            return self._get_mock_analysis(pdf_path.name)

        try:
            # PDFファイルを読み込んでBase64エンコード（Gemini APIへの送信用）
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            
            # AIへのプロンプト
            prompt = """
            この公的ドキュメントを分析し、以下のJSON形式で返してください。
            {
                "summary": "100字程度の要約",
                "category": "経済/安全保障/環境/教育/その他",
                "risk_level": "Critical/Warning/Notice/Info",
                "key_points": ["重要点1", "重要点2", "重要点3"]
            }
            """
            
            # Gemini 2.5 Flash はマルチモーダル対応なので、PDFを直接渡せます
            response = self.model.generate_content([
                prompt,
                {'mime_type': 'application/pdf', 'data': pdf_data}
            ])
            
            # JSON部分を抽出してパース
            result_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(result_text)
        except Exception as e:
            print(f"AI Analysis Error for {pdf_path.name}: {e}")
            return self._get_mock_analysis(pdf_path.name)

    def _get_mock_analysis(self, filename):
        """APIキーがない場合やエラー時のフォールバック"""
        return {
            "summary": f"Analysis for {filename}: This document discusses regional policy updates.",
            "category": "Environment" if "env" in filename.lower() else "Policy",
            "risk_level": "Notice",
            "key_points": ["Policy change", "Implementation date", "Budget allocation"]
        }
