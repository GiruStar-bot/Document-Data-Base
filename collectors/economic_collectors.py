import requests
# インポート元を正しいファイル名に修正
from collectors.base_collector import EconomicDocumentCollector

class IMFCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("INT", "IMF")

    def fetch_latest_documents(self):
        real_docs = [
            {
                "id": "imf_weo_2024_oct",
                "title": "World Economic Outlook, October 2024",
                "date": "2024-10-22",
                "category": "Global Economy",
                "url": "https://www.imf.org/-/media/Files/Publications/WEO/2024/October/English/text.ashx"
            }
        ]
        for doc in real_docs:
            self.save_metadata(doc["id"], doc)

class JapanMOFCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("JPN", "MOF")

    def fetch_latest_documents(self):
        real_docs = [
            {
                "id": "jpn_mof_budget_r7",
                "title": "令和7年度予算案の概要",
                "date": "2024-12-24",
                "category": "Budget",
                "url": "https://www.mof.go.jp/budget/budger_workflow/budget/fy2025/seian/01.pdf"
            }
        ]
        for doc in real_docs:
            self.save_metadata(doc["id"], doc)
