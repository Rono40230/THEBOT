from .logger import logger
"""
RSS Parser - Parser générique pour flux RSS
Gère l'extraction et la normalisation des données RSS de différentes sources
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
import feedparser

logger = logging.getLogger(__name__)


class AsyncRSSParser:
    """Parser générique pour flux RSS avec gestion d'erreurs et normalisation - Version Async"""

    def __init__(self, timeout: int = 10, retries: int = 3):
        """
        Initialise le parser RSS async

        Args:
            timeout: Timeout pour les requêtes HTTP
            retries: Nombre de tentatives en cas d'échec
        """
        self.timeout = timeout
        self.retries = retries
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Context manager entry - initialise la session aiohttp"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ferme la session aiohttp"""
        await self._close_session()

    async def _ensure_session(self) -> None:
        """S'assure qu'une session aiohttp est disponible"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
            )
            logger.debug("📡 Session aiohttp initialisée pour RSS parser")

    async def _close_session(self) -> None:
        """Ferme la session aiohttp"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("📡 Session aiohttp fermée pour RSS parser")

    def parse_feed(self, url: str, max_entries: int = 50) -> List[Dict[str, Any]]:
        """
        Parse un flux RSS et retourne les articles normalisés

        Args:
            url: URL du flux RSS
            max_entries: Nombre maximum d'articles à récupérer

        Returns:
            Liste d'articles normalisés
        """
        try:
            logger.info(f"📡 Parsing RSS feed: {url}")

            # Récupération du contenu RSS avec retry
            content = self._fetch_rss_content(url)
            if not content:
                return []

            # Parse avec feedparser
            feed = feedparser.parse(content)

            if feed.bozo and hasattr(feed, "bozo_exception"):
                logger.warning(f"⚠️ RSS parse warning for {url}: {feed.bozo_exception}")

            # Extraction des métadonnées du feed
            feed_info = self._extract_feed_info(feed, url)

            # Normalisation des articles
            articles = []
            entries = feed.entries[:max_entries] if feed.entries else []

            for entry in entries:
                try:
                    article = self._normalize_entry(entry, feed_info)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"❌ Error normalizing entry: {e}")
                    continue

            logger.info(f"✅ Parsed {len(articles)} articles from {url}")
            return articles

        except Exception as e:
            logger.error(f"❌ Failed to parse RSS feed {url}: {e}")
            return []

    async def parse_feed_async(self, url: str, max_entries: int = 50) -> List[Dict[str, Any]]:
        """
        Parse un flux RSS et retourne les articles normalisés - Version Async

        Args:
            url: URL du flux RSS
            max_entries: Nombre maximum d'articles à récupérer

        Returns:
            Liste d'articles normalisés
        """
        try:
            logger.info(f"📡 Parsing RSS feed async: {url}")

            # Récupération du contenu RSS avec retry
            content = await self._fetch_rss_content_async(url)
            if not content:
                return []

            # Parse avec feedparser
            feed = feedparser.parse(content)

            if feed.bozo and hasattr(feed, "bozo_exception"):
                logger.warning(f"⚠️ RSS parse warning for {url}: {feed.bozo_exception}")

            # Extraction des métadonnées du feed
            feed_info = self._extract_feed_info(feed, url)

            # Normalisation des articles
            articles = []
            entries = feed.entries[:max_entries] if feed.entries else []

            for entry in entries:
                try:
                    article = self._normalize_entry(entry, feed_info)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"❌ Error normalizing entry: {e}")
                    continue

            logger.info(f"✅ Parsed {len(articles)} articles from {url}")
            return articles

        except Exception as e:
            logger.error(f"❌ Failed to parse RSS feed {url}: {e}")
            return []

    def _fetch_rss_content(self, url: str) -> Optional[str]:
        """Récupère le contenu RSS avec gestion des retries"""
        for attempt in range(self.retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.content

            except requests.RequestException as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retries - 1:
                    time.sleep(2**attempt)  # Backoff exponentiel
                else:
                    logger.error(f"❌ All attempts failed for {url}")
                    return None

    async def _fetch_rss_content_async(self, url: str) -> Optional[bytes]:
        """Récupère le contenu RSS avec gestion des retries - Version Async"""
        for attempt in range(self.retries):
            try:
                await self._ensure_session()
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    return await response.read()

            except aiohttp.ClientError as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retries - 1:
                    await asyncio.sleep(2**attempt)  # Backoff exponentiel
                else:
                    logger.error(f"❌ All attempts failed for {url}")
                    return None

    def _extract_feed_info(self, feed: Any, url: str) -> Dict[str, str]:
        """Extrait les métadonnées du feed"""
        return {
            "feed_title": getattr(feed.feed, "title", "Unknown Feed"),
            "feed_url": url,
            "feed_description": getattr(feed.feed, "description", ""),
            "feed_language": getattr(feed.feed, "language", "en"),
            "feed_source": self._extract_source_name(url),
        }

    def _extract_source_name(self, url: str) -> str:
        """Extrait le nom de la source depuis l'URL"""
        try:
            domain = urlparse(url).netloc.lower()
            if "yahoo" in domain:
                return "Yahoo Finance"
            elif "reuters" in domain:
                return "Reuters"
            elif "bloomberg" in domain:
                return "Bloomberg"
            elif "coindesk" in domain:
                return "CoinDesk"
            elif "cryptobriefing" in domain:
                return "CryptoBriefing"
            elif "marketwatch" in domain:
                return "MarketWatch"
            elif "wsj" in domain:
                return "Wall Street Journal"
            else:
                return domain.replace("www.", "").title()
        except:
            return "RSS Feed"

    def _normalize_entry(
        self, entry: Any, feed_info: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Normalise un article RSS au format THEBOT standard

        Returns:
            Article normalisé ou None si invalide
        """
        try:
            # Titre (requis)
            title = getattr(entry, "title", "").strip()
            if not title:
                return None

            # URL (requise)
            url = getattr(entry, "link", "").strip()
            if not url:
                return None

            # Date de publication
            published_date = self._parse_date(entry)

            # Résumé/Description
            summary = self._extract_summary(entry)

            # Catégories/Tags
            categories = self._extract_categories(entry)

            # Article normalisé
            article = {
                "title": title,
                "url": url,
                "summary": summary,
                "published_date": published_date,
                "source": feed_info["feed_source"],
                "provider": "rss",
                "category": self._determine_category(
                    title, summary, categories, feed_info
                ),
                "tags": categories,
                "feed_title": feed_info["feed_title"],
                "language": feed_info.get("feed_language", "en"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            return article

        except Exception as e:
            logger.error(f"❌ Error normalizing entry: {e}")
            return None

    def _parse_date(self, entry: Any) -> str:
        """Parse la date de publication"""
        try:
            # Essayer published_parsed en premier
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()

            # Fallback sur updated_parsed
            if hasattr(entry, "updated_parsed") and entry.updated_parsed:
                dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()

            # Fallback sur chaîne de date
            for date_field in ["published", "updated"]:
                if hasattr(entry, date_field):
                    date_str = getattr(entry, date_field)
                    if date_str:
                        # Utiliser feedparser pour parser la date
                        parsed = feedparser._parse_date(date_str)
                        if parsed:
                            dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                            return dt.isoformat()

            # Fallback sur maintenant
            return datetime.now(timezone.utc).isoformat()

        except Exception:
            return datetime.now(timezone.utc).isoformat()

    def _extract_summary(self, entry: Any) -> str:
        """Extrait le résumé de l'article"""
        # Essayer summary en premier
        if hasattr(entry, "summary") and entry.summary:
            return self._clean_html(entry.summary)

        # Fallback sur description
        if hasattr(entry, "description") and entry.description:
            return self._clean_html(entry.description)

        # Fallback sur content
        if hasattr(entry, "content") and entry.content:
            if isinstance(entry.content, list) and entry.content:
                return self._clean_html(entry.content[0].get("value", ""))

        return ""

    def _extract_categories(self, entry: Any) -> List[str]:
        """Extrait les catégories/tags de l'article"""
        categories = []

        # Tags depuis le champ tags
        if hasattr(entry, "tags") and entry.tags:
            for tag in entry.tags:
                if hasattr(tag, "term") and tag.term:
                    categories.append(tag.term.lower())

        # Catégories depuis category
        if hasattr(entry, "category") and entry.category:
            categories.append(entry.category.lower())

        return list(set(categories))  # Dédupliquer

    def _determine_category(
        self, title: str, summary: str, tags: List[str], feed_info: Dict[str, str]
    ) -> str:
        """Détermine la catégorie principale de l'article"""
        content = f"{title} {summary}".lower()

        # Catégories crypto
        crypto_keywords = [
            "bitcoin",
            "ethereum",
            "crypto",
            "blockchain",
            "defi",
            "nft",
            "altcoin",
        ]
        if any(keyword in content for keyword in crypto_keywords) or any(
            keyword in tags for keyword in crypto_keywords
        ):
            return "crypto"

        # Catégories économiques
        economic_keywords = [
            "economy",
            "inflation",
            "gdp",
            "federal reserve",
            "interest rate",
            "unemployment",
        ]
        if any(keyword in content for keyword in economic_keywords):
            return "economic"

        # Catégories marchés
        market_keywords = [
            "stock",
            "market",
            "trading",
            "investment",
            "portfolio",
            "earnings",
        ]
        if any(keyword in content for keyword in market_keywords):
            return "market"

        # Catégories forex
        forex_keywords = ["forex", "currency", "dollar", "euro", "exchange rate"]
        if any(keyword in content for keyword in forex_keywords):
            return "forex"

        # Basé sur la source
        source = feed_info["feed_source"].lower()
        if "coin" in source or "crypto" in source:
            return "crypto"

        return "general"

    def _clean_html(self, text: str) -> str:
        """Nettoie le HTML des descriptions"""
        import re

        # Supprimer les tags HTML
        text = re.sub(r"<[^>]+>", "", text)
        # Décoder les entités HTML
        import html

        text = html.unescape(text)
        # Nettoyer les espaces
        text = " ".join(text.split())
        return text.strip()

    def validate_feed(self, url: str) -> bool:
        """Valide qu'un flux RSS est accessible et valide"""
        try:
            content = self._fetch_rss_content(url)
            if not content:
                return False

            feed = feedparser.parse(content)
            return not feed.bozo or len(feed.entries) > 0

        except Exception:
            return False


# Instance globale - Version Async
async def get_rss_parser() -> AsyncRSSParser:
    """Factory function pour obtenir une instance AsyncRSSParser"""
    return AsyncRSSParser()

# Classe legacy pour compatibilité - À migrer vers AsyncRSSParser
class RSSParser:
    """
    ⚠️ DEPRECATED: Utilisez AsyncRSSParser à la place

    Version synchrone conservée pour compatibilité temporaire.
    Sera supprimée dans une future version.
    """

    def __init__(self, timeout: int = 10, retries: int = 3):
        import warnings
        warnings.warn(
            "RSSParser is deprecated. Use AsyncRSSParser instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.timeout = timeout
        self.retries = retries

    def parse_feed(self, url: str, max_entries: int = 50) -> List[Dict[str, Any]]:
        """⚠️ DEPRECATED: Utilisez AsyncRSSParser.parse_feed_async()"""
        raise NotImplementedError("Use AsyncRSSParser for async operations")
