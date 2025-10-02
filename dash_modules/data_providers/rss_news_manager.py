"""
RSS News Manager - Gestionnaire principal des flux RSS
Coordonne la récupération et la normalisation des nouvelles RSS
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

from ..core.rss_parser import RSSParser
from .rss_sources_config import rss_sources_config

logger = logging.getLogger(__name__)

class RSSNewsManager:
    """Gestionnaire principal des flux RSS pour THEBOT"""
    
    def __init__(self, max_workers: int = 5):
        """
        Initialise le gestionnaire RSS
        
        Args:
            max_workers: Nombre de threads pour le parsing parallèle
        """
        self.parser = RSSParser()
        self.max_workers = max_workers
        self.cache = {}
        self.cache_ttl = {}
        self.lock = threading.RLock()
        
        # Configuration cache
        self.default_cache_duration = 300  # 5 minutes
        self.max_cache_entries = 1000
        
        logger.info(f"🚀 RSS News Manager initialized with {max_workers} workers")
    
    def get_news(self, 
                 categories: List[str] = None,
                 sources: List[str] = None,
                 limit: int = 50,
                 use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère les nouvelles RSS selon les critères spécifiés
        
        Args:
            categories: Liste des catégories à inclure (None = toutes)
            sources: Liste des sources spécifiques (None = toutes actives)
            limit: Nombre maximum d'articles à retourner
            use_cache: Utiliser le cache si disponible
            
        Returns:
            Liste d'articles normalisés triés par date
        """
        try:
            logger.info(f"📰 Getting RSS news - Categories: {categories}, Sources: {sources}, Limit: {limit}")
            
            # Déterminer les sources à utiliser
            target_sources = self._determine_target_sources(categories, sources)
            
            if not target_sources:
                logger.warning("⚠️ No RSS sources found for criteria")
                return []
            
            # Récupérer les articles de toutes les sources
            all_articles = []
            
            # Utilisation du ThreadPoolExecutor pour paralléliser
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_source = {
                    executor.submit(self._fetch_source_articles, source, use_cache): source 
                    for source in target_sources
                }
                
                for future in as_completed(future_to_source):
                    source = future_to_source[future]
                    try:
                        articles = future.result(timeout=30)
                        if articles:
                            all_articles.extend(articles)
                            logger.debug(f"✅ Got {len(articles)} articles from {source['name']}")
                    except Exception as e:
                        logger.error(f"❌ Failed to fetch from {source['name']}: {e}")
            
            # Trier par date (plus récent en premier)
            all_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
            
            # Limiter et dédupliquer
            unique_articles = self._deduplicate_articles(all_articles)
            result = unique_articles[:limit]
            
            logger.info(f"✅ Retrieved {len(result)} unique articles from {len(target_sources)} RSS sources")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting RSS news: {e}")
            return []
    
    def _determine_target_sources(self, categories: List[str], sources: List[str]) -> List[Dict[str, Any]]:
        """Détermine les sources RSS à utiliser selon les critères"""
        if sources:
            # Sources spécifiques par nom
            all_sources = []
            for category_sources in rss_sources_config.get_all_sources().values():
                all_sources.extend(category_sources)
            
            return [s for s in all_sources if s['name'] in sources and s.get('active', False)]
        
        elif categories:
            # Sources par catégories
            target_sources = []
            for category in categories:
                target_sources.extend(rss_sources_config.get_active_sources(category))
            return target_sources
        
        else:
            # Toutes les sources actives
            return rss_sources_config.get_active_sources()
    
    def _fetch_source_articles(self, source: Dict[str, Any], use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère les articles d'une source RSS spécifique
        
        Args:
            source: Configuration de la source RSS
            use_cache: Utiliser le cache si disponible
            
        Returns:
            Liste d'articles de cette source
        """
        url = source['url']
        max_entries = source.get('max_entries', 20)
        
        # Vérifier le cache
        if use_cache:
            cached_articles = self._get_from_cache(url)
            if cached_articles is not None:
                logger.debug(f"💾 Using cached articles for {source['name']}")
                return cached_articles
        
        # Parser le flux RSS
        try:
            articles = self.parser.parse_feed(url, max_entries)
            
            # Enrichir avec les métadonnées de la source
            for article in articles:
                article.update({
                    'rss_source_name': source['name'],
                    'rss_category': source['category'],
                    'rss_description': source.get('description', '')
                })
            
            # Mettre en cache
            if use_cache and articles:
                cache_duration = source.get('update_interval', self.default_cache_duration)
                self._put_in_cache(url, articles, cache_duration)
            
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching RSS source {source['name']}: {e}")
            return []
    
    def _get_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Récupère des articles du cache si valides"""
        with self.lock:
            if key in self.cache and key in self.cache_ttl:
                if datetime.now(timezone.utc) < self.cache_ttl[key]:
                    return self.cache[key]
                else:
                    # Cache expiré
                    del self.cache[key]
                    del self.cache_ttl[key]
            return None
    
    def _put_in_cache(self, key: str, articles: List[Dict[str, Any]], duration_seconds: int):
        """Met des articles en cache"""
        with self.lock:
            # Limiter la taille du cache
            if len(self.cache) >= self.max_cache_entries:
                self._cleanup_cache()
            
            self.cache[key] = articles
            self.cache_ttl[key] = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
    
    def _cleanup_cache(self):
        """Nettoie le cache des entrées expirées"""
        now = datetime.now(timezone.utc)
        expired_keys = [k for k, ttl in self.cache_ttl.items() if now >= ttl]
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_ttl:
                del self.cache_ttl[key]
        
        logger.debug(f"🧹 Cleaned {len(expired_keys)} expired cache entries")
    
    def _deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Déduplique les articles par URL et titre similaire"""
        seen_urls = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            title = article.get('title', '').lower().strip()
            
            # Vérifier URL exacte
            if url in seen_urls:
                continue
            
            # Vérifier titre similaire (éviter les doublons de contenu)
            title_key = ' '.join(sorted(title.split()[:8]))  # 8 premiers mots triés
            if title_key in seen_titles:
                continue
            
            seen_urls.add(url)
            seen_titles.add(title_key)
            unique_articles.append(article)
        
        logger.debug(f"🔄 Deduplicated {len(articles)} → {len(unique_articles)} articles")
        return unique_articles
    
    def clear_cache(self):
        """Vide complètement le cache"""
        with self.lock:
            self.cache.clear()
            self.cache_ttl.clear()
        logger.info("🧹 RSS cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        with self.lock:
            now = datetime.now(timezone.utc)
            valid_entries = sum(1 for ttl in self.cache_ttl.values() if now < ttl)
            
            return {
                'total_entries': len(self.cache),
                'valid_entries': valid_entries,
                'expired_entries': len(self.cache) - valid_entries,
                'cache_hit_ratio': getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1)
            }
    
    def test_sources(self, categories: List[str] = None) -> Dict[str, Any]:
        """
        Teste la connectivité des sources RSS
        
        Args:
            categories: Catégories à tester (None = toutes)
            
        Returns:
            Rapport de test des sources
        """
        logger.info("🧪 Testing RSS sources connectivity")
        
        if categories:
            sources_to_test = []
            for cat in categories:
                sources_to_test.extend(rss_sources_config.get_active_sources(cat))
        else:
            sources_to_test = rss_sources_config.get_active_sources()
        
        results = {
            'total_sources': len(sources_to_test),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for source in sources_to_test:
            try:
                start_time = time.time()
                is_valid = self.parser.validate_feed(source['url'])
                response_time = time.time() - start_time
                
                if is_valid:
                    results['successful'] += 1
                    status = 'OK'
                else:
                    results['failed'] += 1
                    status = 'FAILED'
                
                results['details'].append({
                    'name': source['name'],
                    'url': source['url'],
                    'category': source['category'],
                    'status': status,
                    'response_time': round(response_time, 2)
                })
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'name': source['name'],
                    'url': source['url'],
                    'category': source['category'],
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        logger.info(f"✅ RSS sources test completed: {results['successful']}/{results['total_sources']} successful")
        return results


# Instance globale
rss_news_manager = RSSNewsManager()