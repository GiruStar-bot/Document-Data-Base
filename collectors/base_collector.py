import json
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

class BaseCollector(ABC):
    """
    全てのスクレイパーの親クラス。
    """
    def __init__(self, region: str, country_code: str):
        self.region = region
        self.country_code = country_code
        self.base_data_path = Path("data/regions") / region

    @abstractmethod
    def fetch(self) -> list:
        """データを取得し、辞書のリストを返す"""
        pass

    def normalize(self, raw_data: dict) -> dict:
        """共通フォーマットに整形"""
        return {
            "title": raw_data.get("title", "No Title"),
            "url": raw_data.get("url", ""),
            "date": raw_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "summary": raw_data.get("summary", ""),
            "status_level": raw_data.get("status_level", "Notice"),
            "collected_at": datetime.now().isoformat()
        }

    def save_data(self, new_items: list):
        """JSONファイルに保存（重複排除）"""
        file_path = self.base_data_path / f"{self.country_code}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        existing_data = []
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except:
                existing_data = []

        existing_urls = {item["url"] for item in existing_data}
        added_count = 0
        for item in new_items:
            normalized = self.normalize(item)
            if normalized["url"] not in existing_urls:
                existing_data.append(normalized)
                added_count += 1

        existing_data.sort(key=lambda x: x["date"], reverse=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
        return added_count
