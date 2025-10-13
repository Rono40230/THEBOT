"""
Cache Manager Intelligent - Phase 2 THEBOT
Système de cache adaptatif pour optimiser les performances des APIs
"""

import hashlib
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class IntelligentCache:
    """
    Cache intelligent avec TTL adaptatif selon la volatilité des données
    """

    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._lock = threading.RLock()
        self._access_stats: Dict[str, Dict] = {}

        # Configuration TTL par type de donnée
        self.ttl_config = {
            # Données crypto (volatiles)
            "crypto_ohlcv": 300,  # 5 minutes
            "crypto_prices": 180,  # 3 minutes
            "crypto_news": 600,  # 10 minutes
            # Données forex (moyennement volatiles)
            "forex_ohlcv": 600,  # 10 minutes
            "forex_rates": 300,  # 5 minutes
            # Données stocks (moins volatiles)
            "stocks_ohlcv": 900,  # 15 minutes
            "stocks_news": 1800,  # 30 minutes
            # News RSS (peu volatiles)
            "rss_news": 900,  # 15 minutes
            "economic_news": 1800,  # 30 minutes
            # Métadonnées (très stables)
            "symbols_list": 3600,  # 1 heure
            "exchange_info": 7200,  # 2 heures
        }

    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Génère une clé de cache unique"""
        # Créer signature à partir des paramètres
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}_{params_hash}"

    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """Récupère une valeur du cache si elle existe et est valide"""
        key = self._generate_key(prefix, **kwargs)

        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # Vérifier expiration
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                if key in self._access_stats:
                    del self._access_stats[key]
                return None

            # Mettre à jour les stats d'accès
            self._update_access_stats(key)

            logger.debug(f"📋 Cache hit: {key}")
            return entry["data"]

    def set(self, prefix: str, data: Any, **kwargs) -> None:
        """Met en cache une valeur avec TTL adaptatif"""
        key = self._generate_key(prefix, **kwargs)

        # Déterminer TTL selon le type de donnée
        ttl = self._get_adaptive_ttl(prefix, data)
        expires_at = time.time() + ttl

        with self._lock:
            self._cache[key] = {
                "data": data,
                "created_at": time.time(),
                "expires_at": expires_at,
                "prefix": prefix,
                "ttl": ttl,
            }

            # Initialiser stats d'accès
            self._access_stats[key] = {
                "hits": 0,
                "last_access": time.time(),
                "created": time.time(),
            }

        logger.debug(f"💾 Cache set: {key} (TTL: {ttl}s)")

    def _get_adaptive_ttl(self, prefix: str, data: Any) -> int:
        """Calcule TTL adaptatif selon le type et la volatilité des données"""
        base_ttl = self.ttl_config.get(prefix, 600)  # Défaut 10min

        # Ajustement selon la taille des données (plus de données = cache plus long)
        if isinstance(data, (list, dict)):
            size_multiplier = min(1.5, 1 + len(str(data)) / 100000)
            base_ttl = int(base_ttl * size_multiplier)

        # Ajustement selon l'heure (marché fermé = cache plus long)
        now = datetime.now()
        if now.weekday() >= 5:  # Weekend
            base_ttl *= 2
        elif now.hour < 9 or now.hour > 17:  # Hors heures de marché
            base_ttl = int(base_ttl * 1.5)

        return min(base_ttl, 7200)  # Max 2 heures

    def _update_access_stats(self, key: str) -> None:
        """Met à jour les statistiques d'accès"""
        if key in self._access_stats:
            self._access_stats[key]["hits"] += 1
            self._access_stats[key]["last_access"] = time.time()

    def invalidate(self, pattern: str = None) -> int:
        """Invalide les entrées du cache"""
        with self._lock:
            if pattern is None:
                # Tout vider
                count = len(self._cache)
                self._cache.clear()
                self._access_stats.clear()
                logger.info(f"🗑️ Cache complètement vidé ({count} entrées)")
                return count

            # Vider selon le motif
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                if key in self._access_stats:
                    del self._access_stats[key]

            logger.info(
                f"🗑️ Cache invalidé: {len(keys_to_remove)} entrées avec motif '{pattern}'"
            )
            return len(keys_to_remove)

    def cleanup_expired(self) -> int:
        """Nettoie les entrées expirées"""
        current_time = time.time()

        with self._lock:
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if current_time > entry["expires_at"]
            ]

            for key in expired_keys:
                del self._cache[key]
                if key in self._access_stats:
                    del self._access_stats[key]

        if expired_keys:
            logger.debug(
                f"🧹 Nettoyage cache: {len(expired_keys)} entrées expirées supprimées"
            )

        return len(expired_keys)

    def get_stats(self) -> Dict:
        """Retourne les statistiques du cache"""
        with self._lock:
            total_entries = len(self._cache)
            total_hits = sum(stats["hits"] for stats in self._access_stats.values())

            # Calculer taille approximative
            total_size = sum(len(str(entry["data"])) for entry in self._cache.values())

            # Analyser par préfixe
            prefix_stats = {}
            for key, entry in self._cache.items():
                prefix = entry["prefix"]
                if prefix not in prefix_stats:
                    prefix_stats[prefix] = {"count": 0, "hits": 0}
                prefix_stats[prefix]["count"] += 1
                if key in self._access_stats:
                    prefix_stats[prefix]["hits"] += self._access_stats[key]["hits"]

            return {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "total_size_bytes": total_size,
                "prefix_breakdown": prefix_stats,
                "avg_hits_per_entry": total_hits / max(total_entries, 1),
            }


def cached_api_call(cache_prefix: str, cache_instance: IntelligentCache = None):
    """
    Décorateur pour mettre en cache les appels API
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Utiliser cache global si non spécifié
            cache = cache_instance or global_cache

            # Essayer de récupérer du cache
            cached_result = cache.get(cache_prefix, args=args, kwargs=kwargs)
            if cached_result is not None:
                return cached_result

            # Exécuter la fonction et cacher le résultat
            try:
                result = func(*args, **kwargs)
                if result is not None:  # Ne pas cacher les résultats vides
                    cache.set(cache_prefix, result, args=args, kwargs=kwargs)
                return result
            except Exception as e:
                logger.error(f"❌ Erreur dans appel API {func.__name__}: {e}")
                raise

        return wrapper

    return decorator


# Instance globale du cache
global_cache = IntelligentCache()


def get_global_cache() -> IntelligentCache:
    """Retourne l'instance globale du cache"""
    return global_cache
