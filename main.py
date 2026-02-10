import json
import os
from pathlib import Path
from collectors.sources.real_collectors import JapanEgovCollector, USFederalRegisterCollector
from collectors.sources.pdf_analyzer import PDFAnalyzer

def process_pdfs_and_update_index():
    """
    data/pdfs フォルダ内のPDFをスキャンし、AIで分析してインデックスを更新する。
    """
    print("--- AI Document Analysis Started ---")
    
    # APIキーはGitHub ActionsのSecretsから取得することを想定
    api_key = os.environ.get("GEMINI_API_KEY", "")
    analyzer = PDFAnalyzer(api_key)
    
    pdf_dir = Path("data/pdfs")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    analysis_results = {}
    
    # 1. 既存のPDFをスキャン
    for pdf_path in pdf_dir.glob("*.pdf"):
        print(f"Analyzing {pdf_path.name}...")
        analysis = analyzer.analyze_pdf(pdf_path)
        analysis_results[pdf_path.name] = analysis

    # 2. グローバルインデックスの生成（AI分析結果を統合）
    generate_global_index(analysis_results)

def generate_global_index(ai_metadata):
    regions_path = Path("data/regions")
    global_index = []

    # 既存のJSONデータを読み込む
    for country_file in regions_path.rglob("*.json"):
        try:
            with open(country_file, "r", encoding="utf-8") as f:
                docs = json.load(f)
                for doc in docs:
                    # PDFファイル名との紐付け（URLの末尾などを利用）
                    filename = doc['url'].split('/')[-1] + ".pdf"
                    if filename in ai_metadata:
                        doc.update(ai_metadata[filename])
                        doc["has_pdf"] = True
                        doc["pdf_path"] = f"data/pdfs/{filename}"
                    else:
                        doc["has_pdf"] = False
                    
                    doc["country_code"] = country_file.stem
                    doc["region"] = country_file.parent.name
                    global_index.append(doc)
        except Exception as e:
            print(f"Error reading {country_file}: {e}")

    global_index.sort(key=lambda x: x["date"], reverse=True)

    output_path = Path("data/current")
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "global-index.json", "w", encoding="utf-8") as f:
        json.dump(global_index, f, ensure_ascii=False, indent=2)

def main():
    # 1. 実データ取得
    collectors = [JapanEgovCollector(), USFederalRegisterCollector()]
    for c in collectors:
        data = c.fetch()
        c.save_data(data)
    
    # 2. PDF分析とインデックス統合
    process_pdfs_and_update_index()
    print("--- All processes complete ---")

if __name__ == "__main__":
    main()
