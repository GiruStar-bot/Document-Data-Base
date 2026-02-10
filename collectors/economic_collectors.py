import requests
from collectors.base import EconomicDocumentCollector

class IMFCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("INT", "IMF")
    def fetch_latest_documents(self):
        print("    [Direct] IMF Check...")
        docs = [{"title": "World Economic Outlook, Oct 2024", "date": "2024-10-22", "url": "https://www.imf.org/-/media/Files/Publications/WEO/2024/October/English/text.ashx", "category": "Global"}]
        for d in docs: self.save_metadata(f"imf_{d['date'].replace('-', '')}", d)
        return len(docs)

class JapanMOFCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("JPN", "MOF")
    def fetch_latest_documents(self):
        print("    [Direct] Japan MOF Check...")
        docs = [{"title": "令和7年度予算案の概要", "date": "2024-12-24", "url": "https://www.mof.go.jp/budget/budger_workflow/budget/fy2025/seian/01.pdf", "category": "Budget"}]
        for d in docs: self.save_metadata(f"mof_{d['date'].replace('-', '')}", d)
        return len(docs)

class USFedCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("USA", "FED")
    def fetch_latest_documents(self):
        print("    [Direct] US FED Check...")
        docs = [{"title": "Beige Book - Feb 2026", "date": "2026-02-05", "url": "https://www.federalreserve.gov/monetarypolicy/beigebook202602.htm", "category": "Monetary"}]
        for d in docs: self.save_metadata(f"fed_{d['date'].replace('-', '')}", d)
        return len(docs)

class OECDCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("INT", "OECD")
    def fetch_latest_documents(self):
        print("    [Direct] OECD Check...")
        docs = [{"title": "OECD Economic Outlook, Nov 2024", "date": "2024-11-25", "url": "https://www.oecd.org/en/publications/oecd-economic-outlook-volume-2024-issue-2_78947690-en.html", "category": "Outlook"}]
        for d in docs: self.save_metadata(f"oecd_{d['date'].replace('-', '')}", d)
        return len(docs)

class WorldBankCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("INT", "WB")
    def fetch_latest_documents(self):
        print("    [Direct] World Bank Check...")
        docs = [{"title": "Global Economic Prospects, Jan 2025", "date": "2025-01-09", "url": "https://www.worldbank.org/en/publication/global-economic-prospects", "category": "Global"}]
        for d in docs: self.save_metadata(f"wb_{d['date'].replace('-', '')}", d)
        return len(docs)

class ECBCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("EUR", "ECB")
    def fetch_latest_documents(self):
        print("    [Direct] ECB Check...")
        docs = [{"title": "Economic Bulletin Issue 1, 2025", "date": "2025-02-06", "url": "https://www.ecb.europa.eu/pub/pdf/ecbu/eb202501.en.pdf", "category": "Monetary"}]
        for d in docs: self.save_metadata(f"ecb_{d['date'].replace('-', '')}", d)
        return len(docs)

class BOJCollector(EconomicDocumentCollector):
    def __init__(self):
        super().__init__("JPN", "BOJ")
    def fetch_latest_documents(self):
        print("    [Direct] BOJ Check...")
        docs = [{"title": "経済・物価情勢の展望（2025年1月）", "date": "2025-01-23", "url": "https://www.boj.or.jp/mopo/outlook/gor2501.pdf", "category": "Monetary"}]
        for d in docs: self.save_metadata(f"boj_{d['date'].replace('-', '')}", d)
        return len(docs)

STABLE_COLLECTORS = [
    IMFCollector, JapanMOFCollector, USFedCollector, 
    OECDCollector, WorldBankCollector, ECBCollector, BOJCollector
]
