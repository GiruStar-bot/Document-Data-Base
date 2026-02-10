import requests
from collectors.base_collector import EconomicDocumentCollector

class IMFCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("INT", "IMF")

    def fetch_latest_documents(self):
        real_docs = [
            {
                "id": "imf_weo_2024_oct",
                "title": "World Economic Outlook, October 2024: Steady but Slow",
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

class USFedCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("USA", "FED")

    def fetch_latest_documents(self):
        real_docs = [
            {
                "id": "usa_fed_beige_202602",
                "title": "Beige Book - February 2026",
                "date": "2026-02-05",
                "category": "Economic Conditions",
                "url": "https://www.federalreserve.gov/monetarypolicy/beigebook202602.htm"
            }
        ]
        for doc in real_docs:
            self.save_metadata(doc["id"], doc)

class ECBCollector(EconomicDocumentCollector):
    """
    欧州中央銀行 (ECB) の情報を取得
    """
    def __init__(self):
        super().__init__("EUR", "ECB")

    def fetch_latest_documents(self):
        # ECBの経済見通しをサンプルとして追加
        real_docs = [
            {
                "id": "eur_ecb_bulletin_2025_01",
                "title": "Economic Bulletin, Issue 1, 2025",
                "date": "2025-01-30",
                "category": "Monetary Policy",
                "url": "https://www.ecb.europa.eu/pub/pdf/ecbu/eb202501.en.pdf"
            }
        ]
        for doc in real_docs:
            self.save_metadata(doc["id"], doc)
