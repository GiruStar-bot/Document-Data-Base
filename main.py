import os
import json
import requests
from pathlib import Path
from collectors.sources.real_collectors import JapanEgovCollector, USFederalRegisterCollector
from collectors.sources.pdf_analyzer import PDFAnalyzer

def download_file(url, target_path):
    """ファイルをリポジトリ内に保存"""
    if target_path.exists():
        return True
    try:
        r = requests.get(url, timeout=30, stream=True)
        r.raise_for_status()
        with open(target_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except:
        return False

def main():
    print("--- Start AI Document Pipeline ---")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    analyzer = PDFAnalyzer(api_key)
    
    # 1. 各国のデータ取得
    collectors = [JapanEgovCollector(), USFederalRegisterCollector()]
    pdf_dir = Path("data/pdfs")
    pdf_dir.mkdir(parents=True, exist_ok=True)

    for c in collectors:
        print(f"Collecting: {c.country_code}...")
        data = c.fetch()
        c.save_data(data)
        
        # 資料の実体(PDFなど)があればダウンロード
        for item in data:
            # URLがPDFを指している、または官報のようにPDF取得が期待される場合
            if ".pdf" in item["url"].lower() or "federalregister" in item["url"]:
                fname = f"{item['date']}_{item['country_code']}_{hash(item['url'])}.pdf"
                target = pdf_dir / fname
                if download_file(item["url"], target):
                    item["pdf_local_path"] = f"data/pdfs/{fname}"

    # 2. PDFのAI分析とグローバルインデックス統合
    regions_path = Path("data/regions")
    global_index = []
    
    for json_file in regions_path.rglob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            docs = json.load(f)
            for doc in docs:
                doc["country_code"] = json_file.stem
                doc["region"] = json_file.parent.name
                
                # PDFがあればAIで分析
                if "pdf_local_path" in doc:
                    pdf_path = Path(doc["pdf_local_path"])
                    if pdf_path.exists():
                        print(f"Analyzing PDF: {pdf_path.name}")
                        analysis = analyzer.analyze(pdf_path)
                        doc.update(analysis)
                
                global_index.append(doc)

    # 3. 最新順に保存
    global_index.sort(key=lambda x: x["date"], reverse=True)
    out_dir = Path("data/current")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "global-index.json", "w", encoding="utf-8") as f:
        json.dump(global_index, f, ensure_ascii=False, indent=2)

    print(f"Pipeline complete. Total docs: {len(global_index)}")

if __name__ == "__main__":
    main()
