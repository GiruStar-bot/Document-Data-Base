import random
import urllib.parse
from datetime import datetime, timedelta
from collectors.base_collector import BaseCollector

class MockAggregator(BaseCollector):
    """
    世界中のほぼすべての国と地域を対象としたダミーデータ生成クラス。
    URLをGoogle検索リンクにすることで、デモとして「機能」させます。
    """

    # 地域別の包括的な国リスト
    COUNTRIES = [
        # --- Asia ---
        {"code": "jp", "name": "Japan", "region": "asia"},
        {"code": "cn", "name": "China", "region": "asia"},
        {"code": "kr", "name": "South Korea", "region": "asia"},
        {"code": "in", "name": "India", "region": "asia"},
        {"code": "id", "name": "Indonesia", "region": "asia"},
        {"code": "th", "name": "Thailand", "region": "asia"},
        {"code": "vn", "name": "Vietnam", "region": "asia"},
        {"code": "my", "name": "Malaysia", "region": "asia"},
        {"code": "ph", "name": "Philippines", "region": "asia"},
        {"code": "sg", "name": "Singapore", "region": "asia"},
        {"code": "tr", "name": "Turkey", "region": "asia"},
        # --- Europe ---
        {"code": "uk", "name": "United Kingdom", "region": "europe"},
        {"code": "fr", "name": "France", "region": "europe"},
        {"code": "de", "name": "Germany", "region": "europe"},
        {"code": "it", "name": "Italy", "region": "europe"},
        {"code": "es", "name": "Spain", "region": "europe"},
        {"code": "nl", "name": "Netherlands", "region": "europe"},
        # --- Americas ---
        {"code": "us", "name": "USA", "region": "americas"},
        {"code": "ca", "name": "Canada", "region": "americas"},
        {"code": "mx", "name": "Mexico", "region": "americas"},
        {"code": "br", "name": "Brazil", "region": "americas"},
        # --- Africa ---
        {"code": "za", "name": "South Africa", "region": "africa"},
        {"code": "ng", "name": "Nigeria", "region": "africa"},
        {"code": "eg", "name": "Egypt", "region": "africa"},
        {"code": "ug", "name": "Uganda", "region": "africa"},
        {"code": "ma", "name": "Morocco", "region": "africa"},
        # --- Oceania ---
        {"code": "au", "name": "Australia", "region": "oceania"},
        {"code": "nz", "name": "New Zealand", "region": "oceania"}
    ]

    STATUS_LEVELS = ["Critical", "Warning", "Notice", "Info"]

    def __init__(self, region, country_code):
        super().__init__(region, country_code)

    def fetch(self) -> list:
        """
        ランダムな公的ドキュメントデータを生成します。
        URLは実在する検索結果へのリンクにし、デモでの利便性を高めます。
        """
        items = []
        # すべての国で毎回更新があるわけではないため、頻度を調整
        if random.random() > 0.3:
            num_items = random.randint(1, 3)
            for i in range(num_items):
                days_ago = random.randint(0, 7)
                date_str = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                title = f"Official Update: Regulatory Framework 2025-{random.randint(1, 100)}"
                # 修正ポイント: 架空のURLではなく、Google検索などで「機能する」URLにする
                # その国の政府ドキュメントを検索するクエリを作成
                search_query = f"{self.country_code} government {title}"
                encoded_query = urllib.parse.quote(search_query)
                functional_url = f"https://www.google.com/search?q={encoded_query}"
                
                items.append({
                    "title": title,
                    "url": functional_url,
                    "date": date_str,
                    "summary": f"Public notification from the government of {self.country_code} regarding regional updates and policy changes.",
                    "status_level": random.choice(self.STATUS_LEVELS)
                })
        return items

    @classmethod
    def run_all(cls):
        """
        全リストのデータを収集・保存します。
        """
        total_added = 0
        for country in cls.COUNTRIES:
            collector = cls(country["region"], country["code"])
            print(f"Processing: {country['name']} [{country['code'].upper()}]")
            data = collector.fetch()
            added = collector.save_data(data)
            total_added += added
        return total_added
