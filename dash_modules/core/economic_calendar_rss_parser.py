"""
Economic Calendar RSS Parser - Extension pour récupérer les événements économiques
Spécialisé dans l'extraction d'événements économiques depuis les flux RSS
"""

import requests
import feedparser
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
import re
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class EconomicCalendarRSSParser:
    """Parser spécialisé pour les calendriers économiques RSS"""
    
    def __init__(self, timeout: int = 15, retries: int = 3):
        """
        Initialise le parser de calendrier économique
        
        Args:
            timeout: Timeout pour les requêtes HTTP
            retries: Nombre de tentatives en cas d'échec
        """
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 THEBOT/1.0'
        })
        
        # Sources RSS pour calendriers économiques
        self.economic_rss_sources = [
            {
                'name': 'Yahoo Finance Economics',
                'url': 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^DJI,^GSPC,^IXIC&region=US&lang=en-US',
                'type': 'yahoo_finance',
                'priority': 1
            },
            {
                'name': 'MarketWatch Real-time',
                'url': 'https://feeds.marketwatch.com/marketwatch/realtimeheadlines/',
                'type': 'marketwatch',
                'priority': 2
            },
            {
                'name': 'Investing.com General News',
                'url': 'https://www.investing.com/rss/news.rss',
                'type': 'investing_news',
                'priority': 3
            },
            {
                'name': 'Federal Reserve News',
                'url': 'https://www.federalreserve.gov/feeds/press_all.xml',
                'type': 'fed_news',
                'priority': 1
            },
            {
                'name': 'ECB Press Releases',
                'url': 'https://www.ecb.europa.eu/rss/press.html',
                'type': 'ecb_news',
                'priority': 1
            }
        ]
        
        # Mapping des impacts par mots-clés (amélioré pour news générales)
        self.impact_keywords = {
            'critical': [
                'non-farm payroll', 'nfp', 'employment report', 'jobs report',
                'fed rate', 'federal reserve', 'fomc', 'interest rate decision',
                'ecb rate', 'european central bank', 'boe rate', 'bank of england',
                'gdp report', 'gross domestic product', 'gdp growth',
                'cpi inflation', 'consumer price index', 'inflation report',
                'unemployment rate', 'jobless claims'
            ],
            'high': [
                'retail sales', 'consumer spending', 'ism manufacturing', 'ism services',
                'pmi', 'purchasing managers index', 'core cpi', 'core inflation',
                'pce', 'personal consumption expenditures', 'housing starts',
                'durable goods', 'factory orders', 'trade balance', 'current account'
            ],
            'medium': [
                'housing data', 'existing home sales', 'new home sales',
                'consumer confidence', 'business sentiment', 'consumer sentiment',
                'industrial production', 'capacity utilization', 'building permits',
                'pending home sales', 'wholesale inventories'
            ],
            'low': [
                'leading indicators', 'philadelphia fed', 'empire state',
                'kansas city fed', 'chicago pmi', 'construction spending',
                'consumer credit', 'import price index', 'export price index'
            ]
        }
        
        # Pays et devises
        self.country_mapping = {
            'united states': 'US', 'usa': 'US', 'us': 'US',
            'eurozone': 'EU', 'euro area': 'EU', 'eu': 'EU',
            'united kingdom': 'UK', 'britain': 'UK', 'uk': 'UK',
            'japan': 'JP', 'jp': 'JP',
            'canada': 'CA', 'ca': 'CA',
            'australia': 'AU', 'au': 'AU',
            'switzerland': 'CH', 'ch': 'CH',
            'china': 'CN', 'cn': 'CN'
        }
    
    def get_economic_events(self, days_ahead: int = 7, max_events: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les événements économiques des prochains jours
        
        Args:
            days_ahead: Nombre de jours à l'avance
            max_events: Maximum d'événements à retourner
            
        Returns:
            Liste d'événements économiques normalisés
        """
        all_events = []
        
        for source in self.economic_rss_sources:
            try:
                events = self._parse_economic_rss(source, days_ahead)
                all_events.extend(events)
                logger.info(f"✅ {len(events)} événements économiques récupérés depuis {source['name']}")
                
                # Petit délai entre les sources
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"⚠️ Échec RSS {source['name']}: {e}")
                continue
        
        # Dédoublonnage et tri par date
        unique_events = self._deduplicate_events(all_events)
        unique_events.sort(key=lambda x: x.get('event_date', datetime.now()))
        
        logger.info(f"✅ {len(unique_events)} événements économiques uniques récupérés")
        return unique_events[:max_events]
    
    def _parse_economic_rss(self, source: Dict, days_ahead: int) -> List[Dict[str, Any]]:
        """Parse un flux RSS spécifique de calendrier économique"""
        
        try:
            # Récupération du contenu RSS
            response = self.session.get(source['url'], timeout=self.timeout)
            response.raise_for_status()
            
            # Parse du flux RSS
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning(f"⚠️ Aucune entrée dans le flux RSS {source['name']}")
                return []
            
            events = []
            target_date = datetime.now() + timedelta(days=days_ahead)
            
            for entry in feed.entries:
                try:
                    # Extraction des données de base
                    event = self._extract_event_data(entry, source)
                    
                    # Filtrer seulement les vraies nouvelles économiques
                    if self._is_economic_event(event):
                        # Pour les actualités récentes, on les garde toutes (moins de filtrage par date)
                        event_date = event.get('event_date')
                        if not event_date:
                            events.append(event)
                        else:
                            # Gérer les comparaisons de dates avec/sans timezone
                            try:
                                # Assurer que les deux dates ont la même timezone
                                now = datetime.now()
                                if event_date.tzinfo is not None and now.tzinfo is None:
                                    now = now.replace(tzinfo=timezone.utc)
                                elif event_date.tzinfo is None and now.tzinfo is not None:
                                    event_date = event_date.replace(tzinfo=timezone.utc)
                                
                                if event_date >= now - timedelta(days=2):
                                    events.append(event)
                            except:
                                # En cas d'erreur, on garde l'événement
                                events.append(event)
                        
                except Exception as e:
                    logger.debug(f"Échec parsing entrée RSS: {e}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing RSS {source['name']}: {e}")
            return []
    
    def _extract_event_data(self, entry: Any, source: Dict) -> Dict[str, Any]:
        """Extrait et normalise les données d'un événement économique"""
        
        # Données de base
        title = entry.get('title', '').strip()
        description = entry.get('summary', entry.get('description', '')).strip()
        
        # Nettoyage HTML
        if description:
            soup = BeautifulSoup(description, 'html.parser')
            description = soup.get_text().strip()
        
        # Extraction de la date
        event_date = self._extract_event_date(entry)
        
        # Détection du pays
        country = self._detect_country(title, description)
        
        # Détection de l'impact
        impact = self._detect_impact(title, description)
        
        # Extraction d'autres données
        event_data = {
            'id': f"{source['type']}_{hash(title + str(event_date))}",
            'title': title,
            'description': description[:500] if description else title,
            'country': country,
            'impact': impact,
            'event_date': event_date,
            'event_time': event_date.strftime('%H:%M') if event_date else 'TBD',
            'source': source['name'],
            'source_url': entry.get('link', source['url']),
            'category': self._categorize_event(title, description),
            'currency': self._get_currency_from_country(country),
            'previous_value': None,  # Sera extrait si disponible
            'forecast_value': None,  # Sera extrait si disponible
            'actual_value': None,    # Sera mis à jour après publication
            'is_released': self._safe_datetime_compare(event_date),
            'scraped_at': datetime.now()
        }
        
        # Extraction des valeurs numériques si disponibles
        self._extract_numerical_values(event_data, description)
        
        return event_data
    
    def _extract_event_date(self, entry: Any) -> Optional[datetime]:
        """Extrait la date de l'événement depuis l'entrée RSS"""
        
        # Essayer plusieurs champs de date
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6], tzinfo=timezone.utc)
                except:
                    continue
        
        # Extraction depuis le titre ou description
        title_desc = f"{entry.get('title', '')} {entry.get('summary', '')}"
        
        # Patterns de date courantes
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # DD/MM/YYYY ou MM/DD/YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY/MM/DD
            r'(today|tomorrow|yesterday)',      # Mots-clés temporels
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, title_desc.lower())
            if match:
                try:
                    date_str = match.group(1)
                    if date_str == 'today':
                        return datetime.now()
                    elif date_str == 'tomorrow':
                        return datetime.now() + timedelta(days=1)
                    elif date_str == 'yesterday':
                        return datetime.now() - timedelta(days=1)
                    else:
                        # Tentative de parsing de date
                        for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except:
                                continue
                except:
                    continue
        
        # Par défaut, utiliser la date actuelle
        return datetime.now()
    
    def _detect_country(self, title: str, description: str) -> str:
        """Détecte le pays de l'événement économique"""
        
        text = f"{title} {description}".lower()
        
        for country_name, code in self.country_mapping.items():
            if country_name in text:
                return code
        
        # Détection par devise
        if any(currency in text for currency in ['usd', 'dollar', 'fed', 'fomc']):
            return 'US'
        elif any(currency in text for currency in ['eur', 'euro', 'ecb']):
            return 'EU'
        elif any(currency in text for currency in ['gbp', 'pound', 'boe']):
            return 'UK'
        elif any(currency in text for currency in ['jpy', 'yen', 'boj']):
            return 'JP'
        
        return 'US'  # Par défaut
    
    def _detect_impact(self, title: str, description: str) -> str:
        """Détecte le niveau d'impact de l'événement"""
        
        text = f"{title} {description}".lower()
        
        for impact_level, keywords in self.impact_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return impact_level
        
        return 'medium'  # Par défaut
    
    def _categorize_event(self, title: str, description: str) -> str:
        """Catégorise l'événement économique"""
        
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['employment', 'unemployment', 'jobs', 'payroll', 'jobless']):
            return 'employment'
        elif any(word in text for word in ['rate', 'fed', 'ecb', 'boe', 'monetary', 'policy']):
            return 'monetary_policy'
        elif any(word in text for word in ['inflation', 'cpi', 'pce', 'price']):
            return 'inflation'
        elif any(word in text for word in ['gdp', 'growth', 'economic', 'activity']):
            return 'economic_activity'
        elif any(word in text for word in ['retail', 'sales', 'consumer', 'spending']):
            return 'consumption'
        else:
            return 'other'
    
    def _get_currency_from_country(self, country: str) -> str:
        """Retourne la devise principale du pays"""
        
        currency_map = {
            'US': 'USD', 'EU': 'EUR', 'UK': 'GBP', 'JP': 'JPY',
            'CA': 'CAD', 'AU': 'AUD', 'CH': 'CHF', 'CN': 'CNY'
        }
        
        return currency_map.get(country, 'USD')
    
    def _safe_datetime_compare(self, event_date: Optional[datetime]) -> bool:
        """Compare des dates avec gestion sécurisée des timezones"""
        if not event_date:
            return False
        
        try:
            now = datetime.now()
            
            # Assurer que les deux dates ont la même timezone
            if event_date.tzinfo is not None and now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
            elif event_date.tzinfo is None and now.tzinfo is not None:
                event_date = event_date.replace(tzinfo=timezone.utc)
            
            return event_date < now
        except:
            # En cas d'erreur, considérer comme non publié
            return False

    def _extract_numerical_values(self, event_data: Dict, description: str):
        """Extrait les valeurs numériques (prévu, précédent, actuel)"""
        
        # Patterns pour extraire les valeurs
        patterns = {
            'previous': r'previous:?\s*([+-]?\d+\.?\d*[%]?)',
            'forecast': r'forecast:?\s*([+-]?\d+\.?\d*[%]?)',
            'expected': r'expected:?\s*([+-]?\d+\.?\d*[%]?)',
            'actual': r'actual:?\s*([+-]?\d+\.?\d*[%]?)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, description.lower())
            if match:
                value = match.group(1)
                if field == 'previous':
                    event_data['previous_value'] = value
                elif field in ['forecast', 'expected']:
                    event_data['forecast_value'] = value
                elif field == 'actual':
                    event_data['actual_value'] = value
    
    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """Supprime les événements en double"""
        
        seen = set()
        unique_events = []
        
        for event in events:
            # Clé unique basée sur titre + date + pays
            key = f"{event['title']}_{event.get('event_date', '')}_{event['country']}"
            
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def _is_economic_event(self, event: Dict) -> bool:
        """Détermine si un article est un vrai événement économique (version permissive)"""
        
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()
        text = f"{title} {description}"
        
        # Mots-clés économiques principaux (plus permissif)
        economic_keywords = [
            'fed', 'federal reserve', 'ecb', 'european central bank', 'boe', 'bank of england',
            'inflation', 'cpi', 'pce', 'gdp', 'employment', 'unemployment', 'jobs',
            'retail sales', 'housing', 'manufacturing', 'pmi', 'ism',
            'rate', 'monetary', 'policy', 'economy', 'economic',
            'market', 'stocks', 'trading', 'financial', 'finance'
        ]
        
        # Vérifier présence de mots-clés économiques
        has_economic = any(keyword in text for keyword in economic_keywords)
        
        # Mots-clés d'exclusion (réduite)
        exclude_keywords = [
            'crypto', 'bitcoin', 'ethereum'  # Seulement crypto pour éviter duplication
        ]
        
        has_exclude = any(keyword in text for keyword in exclude_keywords)
        
        return has_economic and not has_exclude

# Instance globale
economic_calendar_parser = EconomicCalendarRSSParser()