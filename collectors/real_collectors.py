import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from collectors.base_collector import BaseCollector

class JapanEgovCollector(BaseCollector):
    """日本のe-Gov（パブリックコメント）RSSから取得"""
    def __init__(self):
        super().__init__("asia", "jp")
        self.rss_url = "https://public-comment.e-gov.go.jp/servlet/PcmSearch?format=rss&target=0"

    def fetch(self) -> list:
        items = []
        try:
            response = requests.get(self.rss_url, timeout=20)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                
                items.append({
                    "title": title,
                    "url": link,
                    "date": self._parse_date(pub_date),
                    "summary": f"日本政府 e-Gov パブリックコメント募集: {title}",
                    "status_level": "Notice"
                })
        except Exception as e:
            print(f"Error fetching Japan e-Gov: {e}")
        return items

    def _parse_date(self, date_str):
        try:
            # Mon, 10 Feb 2026 12:00:00 +0900 -> YYYY-MM-DD
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return dt.strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')

class USFederalRegisterCollector(BaseCollector):
    """米国連邦官報 (Federal Register) APIから取得"""
    def __init__(self):
        super().__init__("americas", "us")
        self.api_url = "https://www.federalregister.gov/api/v1/documents.json"

    def fetch(self) -> list:
        items = []
        params = {"per_page": 5, "order": "newest", "conditions[type][]": ["RULE", "PROPOSED_RULE"]}
        try:
            response = requests.get(self.api_url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            for doc in data.get("results", []):
                items.append({
                    "title": doc.get("title"),
                    "url": doc.get("html_url"),
                    "date": doc.get("publication_date"),
                    "summary": doc.get("abstract") or "No abstract available.",
                    "status_level": "Warning" if doc.get("type") == "RULE" else "Notice"
                })
        except Exception as e:
            print(f"Error fetching US Federal Register: {e}")
        return items

class UKGovCollector(BaseCollector):
    """イギリス政府 (GOV.UK) アナウンスメントRSSから取得"""
    def __init__(self):
        super().__init__("europe", "uk")
        self.rss_url = "https://www.gov.uk/government/announcements.atom"

    def fetch(self) -> list:
        items = []
        try:
            response = requests.get(self.rss_url, timeout=20)
            response.raise_for_status()
            # Atom形式のパース
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall("ns:entry", namespace):
                title = entry.find("ns:title", namespace).text
                link = entry.find("ns:link", namespace).attrib['href']
                updated = entry.find("ns:updated", namespace).text # 2026-02-10T12:00:00Z
                
                items.append({
                    "title": title,
                    "url": link,
                    "date": updated[:10],
                    "summary": f"UK Government Official Announcement: {title}",
                    "status_level": "Info"
                })
        except Exception as e:
            print(f"Error fetching UK Gov: {e}")
        return items

class UNNewsCollector(BaseCollector):
    """国際連合 (UN News) の主要ヘッドラインRSSから取得"""
    def __init__(self):
        super().__init__("global", "un") # 便宜上regionをglobalに
        self.rss_url = "https://news.un.org/feed/subscribe/en/news/all/rss.xml"

    def fetch(self) -> list:
        items = []
        try:
            response = requests.get(self.rss_url, timeout=20)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                title = item.find("title").text
                link = item.find("link").text
                pub_date = item.find("pubDate").text
                
                items.append({
                    "title": title,
                    "url": link,
                    "date": self._parse_date(pub_date),
                    "summary": f"United Nations Global Update: {title}",
                    "status_level": "Notice"
                })
        except Exception as e:
            print(f"Error fetching UN News: {e}")
        return items

    def _parse_date(self, date_str):
        try:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return dt.strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')
