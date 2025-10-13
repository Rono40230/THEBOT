"""
Configuration des sources RSS pour THEBOT
Définit toutes les sources RSS disponibles par catégorie
"""

from typing import Any, Dict, List


class RSSSourcesConfig:
    """Configuration centralisée des sources RSS"""

    def __init__(self):
        self.sources = self._initialize_sources()

    def _initialize_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialise la configuration des sources RSS"""
        return {
            "economic": [
                {
                    "name": "The Economist Business",
                    "url": "https://www.economist.com/business/rss.xml",
                    "source": "The Economist",
                    "category": "economic",
                    "update_interval": 300,
                    "max_entries": 15,
                    "active": True,
                    "description": "Actualités économiques The Economist",
                },
                {
                    "name": "BBC Business",
                    "url": "http://feeds.bbci.co.uk/news/business/rss.xml",
                    "source": "BBC",
                    "category": "economic",
                    "update_interval": 600,
                    "max_entries": 15,
                    "active": True,
                    "description": "Nouvelles économiques BBC",
                },
                {
                    "name": "Financial Times",
                    "url": "https://www.ft.com/rss/home",
                    "source": "Financial Times",
                    "category": "economic",
                    "update_interval": 600,
                    "max_entries": 10,
                    "active": False,  # Peut nécessiter abonnement
                    "description": "Nouvelles économiques FT",
                },
            ],
            "crypto": [
                {
                    "name": "CoinDesk News",
                    "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                    "source": "CoinDesk",
                    "category": "crypto",
                    "update_interval": 180,  # 3 minutes
                    "max_entries": 25,
                    "active": True,
                    "description": "Actualités crypto CoinDesk",
                },
                {
                    "name": "CryptoNews Feed",
                    "url": "https://cryptonews.com/news/feed/",
                    "source": "CryptoNews",
                    "category": "crypto",
                    "update_interval": 300,
                    "max_entries": 20,
                    "active": True,
                    "description": "Nouvelles crypto générales",
                },
                {
                    "name": "Bitcoin Magazine",
                    "url": "https://bitcoinmagazine.com/.rss/full/",
                    "source": "Bitcoin Magazine",
                    "category": "crypto",
                    "update_interval": 600,
                    "max_entries": 15,
                    "active": True,
                    "description": "Actualités Bitcoin spécialisées",
                },
                {
                    "name": "Decrypt News",
                    "url": "https://decrypt.co/feed",
                    "source": "Decrypt",
                    "category": "crypto",
                    "update_interval": 300,
                    "max_entries": 15,
                    "active": True,
                    "description": "Nouvelles crypto et blockchain",
                },
                {
                    "name": "CoinTelegraph",
                    "url": "https://cointelegraph.com/rss",
                    "source": "CoinTelegraph",
                    "category": "crypto",
                    "update_interval": 240,
                    "max_entries": 20,
                    "active": True,
                    "description": "Actualités crypto mondiales",
                },
            ],
            "market": [
                {
                    "name": "Seeking Alpha News",
                    "url": "https://seekingalpha.com/feed.xml",
                    "source": "Seeking Alpha",
                    "category": "market",
                    "update_interval": 600,
                    "max_entries": 15,
                    "active": True,
                    "description": "Analyses et nouvelles investissement",
                },
                {
                    "name": "Yahoo Finance Business",
                    "url": "https://finance.yahoo.com/news/rssindex",
                    "source": "Yahoo Finance",
                    "category": "market",
                    "update_interval": 600,
                    "max_entries": 10,
                    "active": True,
                    "description": "Nouvelles investissement Yahoo Finance",
                },
            ],
            "forex": [
                {
                    "name": "DailyFX News",
                    "url": "https://www.dailyfx.com/feeds/market-news",
                    "source": "DailyFX",
                    "category": "forex",
                    "update_interval": 600,
                    "max_entries": 15,
                    "active": False,  # À tester
                    "description": "Nouvelles et analyses forex",
                },
                {
                    "name": "Investing.com Forex",
                    "url": "https://www.investing.com/rss/news_14.rss",
                    "source": "Investing.com",
                    "category": "forex",
                    "update_interval": 600,
                    "max_entries": 10,
                    "active": True,
                    "description": "Nouvelles forex",
                },
            ],
            "general": [
                {
                    "name": "CNN Business",
                    "url": "http://rss.cnn.com/rss/money_latest.rss",
                    "source": "CNN Business",
                    "category": "general",
                    "update_interval": 600,
                    "max_entries": 15,
                    "active": True,
                    "description": "Nouvelles business CNN",
                }
            ],
        }

    def get_sources_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retourne les sources RSS d'une catégorie"""
        return self.sources.get(category, [])

    def get_active_sources(self, category: str = None) -> List[Dict[str, Any]]:
        """Retourne toutes les sources actives, optionnellement filtrées par catégorie"""
        if category:
            return [
                source
                for source in self.sources.get(category, [])
                if source.get("active", False)
            ]

        active_sources = []
        for cat_sources in self.sources.values():
            active_sources.extend(
                [source for source in cat_sources if source.get("active", False)]
            )
        return active_sources

    def get_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retourne toutes les sources configurées"""
        return self.sources

    def validate_source(self, url: str) -> bool:
        """Valide qu'une source RSS existe dans la configuration"""
        for category_sources in self.sources.values():
            if any(source["url"] == url for source in category_sources):
                return True
        return False

    def get_source_info(self, url: str) -> Dict[str, Any]:
        """Retourne les informations d'une source RSS par URL"""
        for category_sources in self.sources.values():
            for source in category_sources:
                if source["url"] == url:
                    return source
        return {}

    def update_source_status(self, url: str, active: bool) -> bool:
        """Met à jour le statut actif d'une source"""
        for category_sources in self.sources.values():
            for source in category_sources:
                if source["url"] == url:
                    source["active"] = active
                    return True
        return False

    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories disponibles"""
        return list(self.sources.keys())

    def get_source_count(self, category: str = None, active_only: bool = False) -> int:
        """Retourne le nombre de sources"""
        if category:
            sources = self.sources.get(category, [])
            if active_only:
                sources = [s for s in sources if s.get("active", False)]
            return len(sources)

        total = 0
        for cat_sources in self.sources.values():
            if active_only:
                total += len([s for s in cat_sources if s.get("active", False)])
            else:
                total += len(cat_sources)
        return total


# Instance globale
rss_sources_config = RSSSourcesConfig()
