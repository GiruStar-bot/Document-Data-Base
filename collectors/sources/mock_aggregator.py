import random
from datetime import datetime, timedelta
from collectors.base_collector import BaseCollector

class MockAggregator(BaseCollector):
    """
    世界中のほぼすべての国と地域を対象としたダミーデータ生成クラス。
    ISO 3166-1 に基づく国リストを保持します。
    """

    # 地域別の包括的な国リスト (主要な国と地域を網羅)
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
        {"code": "pk", "name": "Pakistan", "region": "asia"},
        {"code": "bd", "name": "Bangladesh", "region": "asia"},
        {"code": "ir", "name": "Iran", "region": "asia"},
        {"code": "iq", "name": "Iraq", "region": "asia"},
        {"code": "sa", "name": "Saudi Arabia", "region": "asia"},
        {"code": "ae", "name": "UAE", "region": "asia"},
        {"code": "il", "name": "Israel", "region": "asia"},
        {"code": "tr", "name": "Turkey", "region": "asia"},
        {"code": "tw", "name": "Taiwan", "region": "asia"},
        {"code": "hk", "name": "Hong Kong", "region": "asia"},

        # --- Europe ---
        {"code": "uk", "name": "United Kingdom", "region": "europe"},
        {"code": "fr", "name": "France", "region": "europe"},
        {"code": "de", "name": "Germany", "region": "europe"},
        {"code": "it", "name": "Italy", "region": "europe"},
        {"code": "es", "name": "Spain", "region": "europe"},
        {"code": "nl", "name": "Netherlands", "region": "europe"},
        {"code": "be", "name": "Belgium", "region": "europe"},
        {"code": "ch", "name": "Switzerland", "region": "europe"},
        {"code": "at", "name": "Austria", "region": "europe"},
        {"code": "se", "name": "Sweden", "region": "europe"},
        {"code": "no", "name": "Norway", "region": "europe"},
        {"code": "fi", "name": "Finland", "region": "europe"},
        {"code": "dk", "name": "Denmark", "region": "europe"},
        {"code": "pl", "name": "Poland", "region": "europe"},
        {"code": "ru", "name": "Russia", "region": "europe"},
        {"code": "ua", "name": "Ukraine", "region": "europe"},
        {"code": "gr", "name": "Greece", "region": "europe"},
        {"code": "pt", "name": "Portugal", "region": "europe"},
        {"code": "cz", "name": "Czech Republic", "region": "europe"},
        {"code": "ie", "name": "Ireland", "region": "europe"},

        # --- Americas ---
        {"code": "us", "name": "USA", "region": "americas"},
        {"code": "ca", "name": "Canada", "region": "americas"},
        {"code": "mx", "name": "Mexico", "region": "americas"},
        {"code": "br", "name": "Brazil", "region": "americas"},
        {"code": "ar", "name": "Argentina", "region": "americas"},
        {"code": "cl", "name": "Chile", "region": "americas"},
        {"code": "co", "name": "Colombia", "region": "americas"},
        {"code": "pe", "name": "Peru", "region": "americas"},
        {"code": "ve", "name": "Venezuela", "region": "americas"},
        {"code": "cu", "name": "Cuba", "region": "americas"},

        # --- Africa ---
        {"code": "za", "name": "South Africa", "region": "africa"},
        {"code": "ng", "name": "Nigeria", "region": "africa"},
        {"code": "eg", "name": "Egypt", "region": "africa"},
        {"code": "ke", "name": "Kenya", "region": "africa"},
        {"code": "et", "name": "Ethiopia", "region": "africa"},
        {"code": "gh", "name": "Ghana", "region": "africa"},
        {"code": "ma", "name": "Morocco", "region": "africa"},
        {"code": "dz", "name": "Algeria", "region": "africa"},
        {"code": "tz", "name": "Tanzania", "region": "africa"},
        {"code": "ug", "name": "Uganda", "region": "africa"},

        # --- Oceania ---
        {"code": "au", "name": "Australia", "region": "oceania"},
        {"code": "nz", "name": "New Zealand", "region": "oceania"},
        {"code": "fj", "name": "Fiji", "region": "oceania"},
        {"code": "pg", "name": "Papua New Guinea", "region": "oceania"}
    ]

    STATUS_LEVELS = ["Critical", "Warning", "Notice", "Info"]

    def __init__(self, region, country_code):
        super().__init__(region, country_code)

    def fetch(self) -> list:
        """
        ランダムな公的ドキュメントデータを生成します。
        国によってはデータが発生しない(0件)ケースもシミュレートします。
        """
        items = []
        # すべての国で毎回更新があるわけではないため、頻度を調整
        if random.random() > 0.3:
            num_items = random.randint(1, 3)
            for i in range(num_items):
                days_ago = random.randint(0, 7)
                date_str = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                items.append({
                    "title": f"Official Update: Regulatory Framework {random.randint(2024, 2026)}-{random.randint(1, 50)}",
                    "url": f"https://gov.{self.country_code}/announcements/{random.randint(10000, 99999)}",
                    "date": date_str,
                    "summary": f"Public notification from the government of {self.country_code} regarding regional updates.",
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
