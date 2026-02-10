import requests
from base_collector import EconomicDocumentCollector

class IMFCollector(EconomicDocumentCollector):
    """
    IMF Collector with real-world URL examples.
    """
    def __init__(self):
        super().__init__("INT", "IMF")

    def fetch_latest_documents(self):
        # In a real scenario, you would use BeautifulSoup to scrape these.
        # Here we provide actual valid URLs to the documents.
        real_docs = [
            {
                "id": "imf_weo_2024_oct",
                "title": "World Economic Outlook, October 2024: Steady but Slow",
                "date": "2024-10-22",
                "category": "Global Economy",
                "url": "https://www.imf.org/-/media/Files/Publications/WEO/2024/October/English/text.ashx"
            },
            {
                "id": "imf_gfs_2024_oct",
                "title": "Global Financial Stability Report, October 2024",
                "date": "2024-10-22",
                "category": "Financial Stability",
                "url": "https://www.imf.org/-/media/Files/Publications/GFSR/2024/October/English/text.ashx"
            }
        ]
        for doc in real_docs:
            self.save_metadata(doc["id"], doc)

class JapanMOFCollector(EconomicDocumentCollector):
    """
    Japan Ministry of Finance Collector.
    """
    def __init__(self):
        super().__init__("JPN", "MOF")

    def fetch_latest_documents(self):
        real_docs = [
            {
                "id": "jpn_mof_budget_r7",
                "title": "令和7年度予算フレームワーク",
                "date": "2024-12-24",
                "category": "Budget",
                "url": "https://www.mof.go.jp/budget/budger_workflow/budget/fy2025/seian/01.pdf"
            }
        ]
        for doc in real_docs:
            self.save_metadata(doc["id"], doc)
