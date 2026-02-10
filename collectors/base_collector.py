import json
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

class BaseCollector(ABC):
    """
    全てのスクレイパーの親となる基底クラス。
    各国のデータソースに合わせて継承して使用します。
    """
    
    def __init__(self, region: str, country_code: str):
        self.region = region
        self.country_code = country_code
        self.base_data_path = Path("data/regions") / region

    @abstractmethod
    def fetch(self) -> list:
        """
        データを取得する抽象メソッド。
        各サブクラスで実装が必要です。
        """
        pass

    def normalize(self, raw_data: dict) -> dict:
        """
        取得したデータを共通フォーマットに変換します。
        """
        return {
            "title": raw_data.get("title", "No Title"),
            "url": raw_data.get("url", ""),
            "date": raw_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "summary": raw_data.get("summary", ""),
            "status_level": raw_data.get("status_level", "Notice"), # Critical, Warning, Notice
            "collected_at": datetime.now().isoformat()
        }

    def save_data(self, new_items: list):
        """
        既存のJSONファイルを読み込み、重複を排除して新しいデータを追記保存します。
        """
        file_path = self.base_data_path / f"{self.country_code}.json"
        
        # フォルダの作成
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        existing_data = []
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing_data = []

        # 重複排除用のURLリスト
        existing_urls = {item["url"] for item in existing_data}
        
        # 正規化と新規データの抽出
        added_count = 0
        for item in new_items:
            normalized = self.normalize(item)
            if normalized["url"] not in existing_urls:
                existing_data.append(normalized)
                existing_urls.add(normalized["url"])
                added_count += 1

        # 日付順にソート（新しい順）
        existing_data.sort(key=lambda x: x["date"], reverse=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
        return added_count
