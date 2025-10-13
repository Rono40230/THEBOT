"""
API Specialization Manager - Phase 2 THEBOT
Gestion spécialisée des providers par type de marché pour optimiser les performances
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .intelligent_cache import cached_api_call, get_global_cache

logger = logging.getLogger(__name__)


class SpecializedAPIManager:
    """
    Gestionnaire spécialisé des APIs par marché pour optimiser les requêtes
    """

    def __init__(self):
        self.cache = get_global_cache()

        # Configuration de spécialisation par marché
        self.specialization_config = {
            "crypto": {
                "primary": "binance",  # Données OHLCV principales
                "secondary": "coin_gecko",  # Backup + métadonnées
                "news": "rss",  # News via RSS
                "fallback_order": ["binance", "coin_gecko", "twelve_data"],
            },
            "forex": {
                "primary": "twelve_data",  # Données forex spécialisées
                "secondary": "coin_gecko",  # Backup pour major pairs
                "news": "rss",
                "fallback_order": ["twelve_data", "coin_gecko"],
            },
            "stocks": {
                "primary": "twelve_data",  # Yahoo Finance non encore intégré
                "secondary": "coin_gecko",  # Backup limité
                "news": "rss",
                "fallback_order": ["twelve_data"],
            },
            "indices": {
                "primary": "twelve_data",
                "secondary": None,
                "news": "rss",
                "fallback_order": ["twelve_data"],
            },
        }

        # Providers disponibles (sera initialisé par real_data_manager)
        self.providers = {}

    def set_providers(self, providers: Dict):
        """Configure les providers disponibles"""
        self.providers = providers
        logger.info(f"📊 Providers configurés: {list(providers.keys())}")

    def get_optimal_provider(self, symbol: str, data_type: str = "ohlcv") -> str:
        """
        Détermine le provider optimal pour un symbole donné
        """
        # Validation basique du symbole
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError(f"Symbole invalide: {symbol}")

        symbol = symbol.upper().strip()

        market_type = self._detect_market_type(symbol)
        config = self.specialization_config.get(market_type, {})

        if data_type == "news":
            return config.get("news", "rss")

        # Pour les données OHLCV/prix
        primary = config.get("primary")
        if primary and primary in self.providers:
            return primary

        # Fallback vers providers secondaires
        for provider_name in config.get("fallback_order", []):
            if provider_name in self.providers:
                logger.warning(f"🔄 Fallback vers {provider_name} pour {symbol}")
                return provider_name

        # Dernière option: premier provider disponible
        if self.providers:
            fallback = list(self.providers.keys())[0]
            logger.warning(f"⚠️ Utilisation fallback {fallback} pour {symbol}")
            return fallback

        raise ValueError(f"Aucun provider disponible pour {symbol}")

    def _detect_market_type(self, symbol: str) -> str:
        """
        Détecte le type de marché d'un symbole
        """
        symbol_upper = symbol.upper()

        # Crypto patterns
        crypto_patterns = [
            "BTC",
            "ETH",
            "ADA",
            "XRP",
            "DOT",
            "LINK",
            "UNI",
            "DOGE",
            "SHIB",
            "USDT",
            "USDC",
            "BUSD",
            "DAI",
            "MATIC",
            "SOL",
            "AVAX",
            "LUNA",
            "ATOM",
            "FTT",
            "NEAR",
            "ALGO",
            "VET",
            "ICP",
            "THETA",
            "FIL",
        ]

        for pattern in crypto_patterns:
            if pattern in symbol_upper:
                return "crypto"

        # Forex patterns (currency pairs)
        if len(symbol) >= 6 and "/" in symbol:
            return "forex"
        if len(symbol) == 6 and symbol.isalpha():  # EURUSD format
            return "forex"

        # Indices patterns
        indices_patterns = ["SPY", "QQQ", "DIA", "SPX", "NDX", "DJI", "VIX"]
        if any(idx in symbol_upper for idx in indices_patterns):
            return "indices"

        # Défaut: stocks
        return "stocks"

    @cached_api_call("specialized_ohlcv")
    def get_optimized_data(
        self, symbol: str, timeframe: str = "1h", limit: int = 100
    ) -> Optional[List[Dict]]:
        """
        Récupère des données OHLCV en utilisant le provider optimal
        """
        try:
            provider_name = self.get_optimal_provider(symbol, "ohlcv")
            provider = self.providers.get(provider_name)

            if not provider:
                logger.error(
                    f"❌ Provider {provider_name} non disponible pour {symbol}"
                )
                return None

            logger.info(f"📊 Utilisation {provider_name} pour {symbol} ({timeframe})")

            # Appel spécialisé selon le provider
            if provider_name == "binance":
                return self._get_binance_data(provider, symbol, timeframe, limit)
            elif provider_name == "coin_gecko":
                return self._get_coingecko_data(provider, symbol, timeframe, limit)
            elif provider_name == "twelve_data":
                return self._get_twelve_data(provider, symbol, timeframe, limit)
            else:
                logger.warning(
                    f"⚠️ Provider {provider_name} non spécialisé pour {symbol}"
                )
                return None

        except Exception as e:
            logger.error(f"❌ Erreur données optimisées {symbol}: {e}")
            return None

    def _get_binance_data(
        self, provider, symbol: str, timeframe: str, limit: int
    ) -> Optional[List[Dict]]:
        """Récupération données Binance optimisée"""
        try:
            # Convertir symbole au format Binance si nécessaire
            binance_symbol = symbol.replace("/", "").upper()
            if not binance_symbol.endswith("USDT") and "USD" not in binance_symbol:
                binance_symbol += "USDT"

            # Conversion timeframe Binance
            tf_mapping = {
                "1m": "1m",
                "5m": "5m",
                "15m": "15m",
                "30m": "30m",
                "1h": "1h",
                "4h": "4h",
                "1d": "1d",
                "1w": "1w",
            }
            binance_tf = tf_mapping.get(timeframe, "1h")

            if hasattr(provider, "get_ohlcv_data"):
                return provider.get_ohlcv_data(binance_symbol, binance_tf, limit)
            elif hasattr(provider, "get_historical_data"):
                return provider.get_historical_data(binance_symbol, binance_tf, limit)
            else:
                logger.warning(f"⚠️ Méthode OHLCV non trouvée sur provider Binance")
                return None

        except Exception as e:
            logger.error(f"❌ Erreur Binance {symbol}: {e}")
            return None

    def _get_coingecko_data(
        self, provider, symbol: str, timeframe: str, limit: int
    ) -> Optional[List[Dict]]:
        """Récupération données CoinGecko optimisée"""
        try:
            # Mapping symbole vers ID CoinGecko
            symbol_to_id = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "ADA": "cardano",
                "XRP": "ripple",
                "DOT": "polkadot",
                "LINK": "chainlink",
                "UNI": "uniswap",
                "DOGE": "dogecoin",
                "MATIC": "polygon",
            }

            base_symbol = (
                symbol.split("/")[0].upper() if "/" in symbol else symbol.upper()
            )
            gecko_id = symbol_to_id.get(base_symbol, base_symbol.lower())

            if hasattr(provider, "get_ohlcv_data"):
                return provider.get_ohlcv_data(gecko_id, timeframe, limit)
            elif hasattr(provider, "get_historical_data"):
                return provider.get_historical_data(gecko_id, timeframe, limit)
            else:
                logger.warning(f"⚠️ Méthode OHLCV non trouvée sur provider CoinGecko")
                return None

        except Exception as e:
            logger.error(f"❌ Erreur CoinGecko {symbol}: {e}")
            return None

    def _get_twelve_data(
        self, provider, symbol: str, timeframe: str, limit: int
    ) -> Optional[List[Dict]]:
        """Récupération données Twelve Data optimisée"""
        try:
            if hasattr(provider, "get_ohlcv_data"):
                return provider.get_ohlcv_data(symbol, timeframe, limit)
            elif hasattr(provider, "get_historical_data"):
                return provider.get_historical_data(symbol, timeframe, limit)
            else:
                logger.warning(f"⚠️ Méthode OHLCV non trouvée sur provider Twelve Data")
                return None

        except Exception as e:
            logger.error(f"❌ Erreur Twelve Data {symbol}: {e}")
            return None

    @cached_api_call("specialized_news")
    def get_optimized_news(
        self, categories: List[str] = None, limit: int = 20
    ) -> List[Dict]:
        """
        Récupère des news optimisées selon les catégories
        """
        try:
            all_news = []

            # RSS News (principale source)
            if "rss_news_manager" in self.providers:
                rss_manager = self.providers["rss_news_manager"]
                rss_news = rss_manager.get_news(categories=categories, limit=limit // 2)
                all_news.extend(rss_news)
                logger.info(f"📰 RSS: {len(rss_news)} articles")

            # API News complémentaires
            remaining_limit = limit - len(all_news)
            if remaining_limit > 0:
                # Binance pour crypto
                if (
                    categories
                    and "crypto" in categories
                    and "binance" in self.providers
                ):
                    try:
                        binance_news = self.providers["binance"].get_news(
                            limit=remaining_limit // 2
                        )
                        if binance_news:
                            all_news.extend(binance_news)
                            logger.info(f"📰 Binance: {len(binance_news)} articles")
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur news Binance: {e}")

                # CoinGecko pour métadonnées crypto
                if (
                    categories
                    and "crypto" in categories
                    and "coin_gecko" in self.providers
                ):
                    try:
                        gecko_updates = self.providers["coin_gecko"].get_market_updates(
                            limit=remaining_limit // 2
                        )
                        if gecko_updates:
                            all_news.extend(gecko_updates)
                            logger.info(f"📰 CoinGecko: {len(gecko_updates)} updates")
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur updates CoinGecko: {e}")

            # Dédupliquer et limiter
            unique_news = self._deduplicate_news(all_news)
            return unique_news[:limit]

        except Exception as e:
            logger.error(f"❌ Erreur news optimisées: {e}")
            return []

    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """Supprime les doublons dans les news"""
        seen_titles = set()
        unique_news = []

        for article in news_list:
            title = article.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(article)

        return unique_news

    def get_performance_stats(self) -> Dict:
        """Retourne les statistiques de performance"""
        cache_stats = self.cache.get_stats()

        return {
            "specialization_config": self.specialization_config,
            "active_providers": list(self.providers.keys()),
            "cache_performance": cache_stats,
            "timestamp": datetime.now().isoformat(),
        }


# Instance globale
specialized_api_manager = SpecializedAPIManager()
