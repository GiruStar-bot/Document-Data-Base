import os
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# インポートパスの解決（ModuleNotFoundError対策）
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from collectors.base_collector import BaseCollector

class JapanEgovCollector(BaseCollector):
    """日本のe-GovパブリックコメントRSSから取得"""
    def __init__(self):
        super().__init__("asia", "jp")
        self.rss_url = "https://public-comment.e-gov.go.jp/servlet/PcmSearch?format=rss&target=0"

    def fetch(self) -> list:
        items = []
        try:
            response = requests.get(self.rss_url, timeout=20)
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                title = item.find("title").text
                link = item.find("link").text
                items.append({
                    "title": title,
                    "url": link,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "summary": f"日本 e-Gov: {title}",
                    "status_level": "Notice"
                })
        except Exception as e:
            print(f"JP Fetch Error: {e}")
        return items

class USFederalRegisterCollector(BaseCollector):
    """米国連邦官報 APIから取得"""
    def __init__(self):
        super().__init__("americas", "us")
        self.api_url = "https://www.federalregister.gov/api/v1/documents.json"

    def fetch(self) -> list:
        items = []
        try:
            response = requests.get(self.api_url, params={"per_page": 5}, timeout=20)
            for doc in response.json().get("results", []):
                items.append({
                    "title": doc.get("title"),
                    "url": doc.get("html_url"),
                    "date": doc.get("publication_date"),
                    "summary": doc.get("abstract"),
                    "status_level": "Warning"
                })
        except Exception as e:
            print(f"US Fetch Error: {e}")
        return items
