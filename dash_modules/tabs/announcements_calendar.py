"""
Module Calendrier des Annonces Économiques
==========================================

Ce module fournit un calendrier interactif des annonces économiques
avec possibilité de sélectionner et suivre les événements importants.

Fonctionnalités:
- Calendrier mensuel avec événements économiques
- Sélection d'événements à suivre
- Filtrage par pays, catégorie et impact
- Vues multiples : calendrier, liste, analytics
- Statistiques et analyses des événements

"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import calendar

import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from ..data_providers import economic_events_provider
from ..data_providers import economic_events_config
from ..core.economic_calendar_rss_parser import economic_calendar_parser
# Import de la nouvelle API Finnhub
from ..data_providers.finnhub_economic_calendar import finnhub_calendar


class AnnouncementsCalendarModule:
    """Module de calendrier des annonces économiques"""
    
    def __init__(self, calculators=None):
        self.name = "Calendrier Annonces"
        self.id = "announcements-calendar"
        self.calculators = calculators or {}
        
        # Configuration des widgets (version simplifiée)
        print(f"📅 {self.name} initialisé")
        
        # Configuration simplifiée - TOUS LES ÉVÉNEMENTS par défaut
        # État actuel du calendrier
        self.current_date = datetime.now()
        self.current_impact_filter = 'all'  # 'all', 'critical', 'high', 'moderate'
        
        # Cache pour les événements
        self.events_cache = {}
        self.last_update = None
        
        # Paramètres fixes
        self.filter_period = 90
        self.realtime_sync = True
        
    def _get_initial_calendar_content(self):
        """Générer le contenu initial du calendrier au démarrage - TOUS LES ÉVÉNEMENTS"""
        try:
            # Récupérer TOUS les événements sans filtrage
            events = self.get_real_economic_events(
                days_ahead=self.filter_period,
                countries=None,  # TOUS les pays
                impacts=None     # TOUS les impacts
            )
            
            # Si pas d'événements API, utiliser fallback
            if not events:
                events = self._get_fallback_events()
                
            # Pas de filtrage par catégories - TOUS LES ÉVÉNEMENTS
            return self.generate_calendar_view(events)
            
        except Exception as e:
            # En cas d'erreur, afficher un message informatif
            return html.Div([
                dbc.Alert([
                    html.H5("⏳ Chargement du calendrier..."),
                    html.P("Le calendrier économique charge tous les événements disponibles.")
                ], color="info", className="text-center mt-4")
            ])
        
    def get_layout(self) -> html.Div:
        """Retourner le layout principal du module"""
        
        return html.Div([
            # Boutons de filtrage par impact uniquement - centrés
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("🔴 Critique", id="btn-impact-critical", 
                                 color="danger", size="sm", outline=True),
                        dbc.Button("🟠 Élevé", id="btn-impact-high", 
                                 color="warning", size="sm", outline=True),
                        dbc.Button("🟡 Modéré", id="btn-impact-moderate", 
                                 color="info", size="sm", outline=True),
                        dbc.Button("📊 Tous", id="btn-impact-all", 
                                 color="success", size="sm", active=True)
                    ], className="d-flex justify-content-center")
                ], width=12)
            ], className="mb-3"),
            
            # Navigation du calendrier (pour vue calendrier)
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("◀", id="calendar-prev-month", color="outline-primary", size="sm"),
                                ], width=2),
                                dbc.Col([
                                    html.H5(id="calendar-current-month", className="text-center mb-0")
                                ], width=8),
                                dbc.Col([
                                    dbc.Button("▶", id="calendar-next-month", color="outline-primary", size="sm"),
                                ], width=2)
                            ])
                        ]),
                        dbc.CardBody([
                            # Contenu du calendrier selon la vue - Chargé automatiquement au démarrage
                            html.Div(
                                id="calendar-content",
                                children=self._get_initial_calendar_content()
                            )
                        ])
                    ])
                ], width=12)
            ], className="mt-3"),
            
            # Modal pour afficher tous les événements d'une journée
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="day-events-title")),
                dbc.ModalBody([
                    html.Div(id="day-events-content")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Fermer", id="close-day-events", className="ms-auto", n_clicks=0)
                ])
            ], id="day-events-modal", is_open=False, size="xl"),
            
        ], className="calendar-module")
    
    def get_real_economic_events(self, days_ahead: int = 7, countries: List[str] = None, impacts: List[str] = None) -> List[Dict]:
        """Récupère les vrais événements économiques via API Finnhub"""
        
        try:
            # Utiliser le cache si récent (5 minutes)
            cache_key = f"{days_ahead}_{'-'.join(countries or [])}_{'-'.join(impacts or [])}"
            
            if (self.last_update and 
                cache_key in self.events_cache and 
                (datetime.now() - self.last_update).seconds < 300):
                return self.events_cache[cache_key]
            
            # PRIORITÉ 1: Essayer l'API Finnhub d'abord
            print(f"🏛️ Tentative API Finnhub: {days_ahead} jours, pays={countries}, impacts={impacts}")
            
            events = finnhub_calendar.get_economic_events(
                days_ahead=days_ahead,
                countries=countries,
                impacts=impacts,
                max_events=100  # Plus d'événements pour un meilleur résultat
            )
            
            print(f"✅ Finnhub: {len(events)} événements récupérés")
            
            # FALLBACK: Si Finnhub échoue ou retourne peu d'événements, utiliser RSS
            if len(events) < 5:
                print(f"🔄 Fallback RSS car Finnhub a retourné {len(events)} événements")
                
                rss_events = economic_calendar_parser.get_economic_events(
                    days_ahead=days_ahead,
                    max_events=50
                )
                
                # Filtrage RSS
                if countries and 'ALL' not in countries:
                    rss_events = [e for e in rss_events if e.get('country') in countries]
                
                if impacts:
                    rss_events = [e for e in rss_events if e.get('impact') in impacts]
                
                print(f"✅ RSS Fallback: {len(rss_events)} événements après filtrage")
                
                # Combiner Finnhub + RSS pour plus de données
                events.extend(rss_events)
                
                # Déduplication par titre
                seen_titles = set()
                unique_events = []
                for event in events:
                    title = event.get('title', '').lower()
                    if title not in seen_titles:
                        seen_titles.add(title)
                        unique_events.append(event)
                
                events = unique_events[:100]  # Limiter à 100
                print(f"📊 Total après déduplication: {len(events)} événements")
            
            # Mise en cache
            self.events_cache[cache_key] = events
            self.last_update = datetime.now()
            
            return events
            
        except Exception as e:
            print(f"❌ Erreur récupération événements: {e}")
            return self._get_fallback_events()
        except Exception as e:
            print(f"❌ Erreur récupération événements économiques: {e}")
            # Retourner quelques événements de fallback
            return self._get_fallback_events()
    
    def _get_fallback_events(self) -> List[Dict]:
        """Événements de secours en cas d'échec RSS - Version étendue avec 100+ événements"""
        
        today = datetime.now()
        events = []
        
        # 🇺🇸 ÉTATS-UNIS - Événements critiques et importants
        events.extend([
            {
                'id': 'fallback_us_1',
                'title': 'US Non-Farm Payrolls (NFP)',
                'description': 'Création d\'emplois aux États-Unis - Indicateur clé du marché du travail',
                'country': 'US',
                'impact': 'critical',
                'event_date': today + timedelta(days=1),
                'event_time': '14:30',
                'category': 'employment',
                'currency': 'USD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_us_2',
                'title': 'US Consumer Price Index (CPI)',
                'description': 'Indice des prix à la consommation américain',
                'country': 'US',
                'impact': 'critical',
                'event_date': today + timedelta(days=3),
                'event_time': '14:30',
                'category': 'inflation',
                'currency': 'USD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_us_3',
                'title': 'Federal Reserve Interest Rate Decision',
                'description': 'Décision de taux de la Fed - Impact majeur sur les marchés',
                'country': 'US',
                'impact': 'critical',
                'event_date': today + timedelta(days=5),
                'event_time': '20:00',
                'category': 'monetary_policy',
                'currency': 'USD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_us_4',
                'title': 'US GDP Quarterly Growth',
                'description': 'Croissance trimestrielle du PIB américain',
                'country': 'US',
                'impact': 'critical',
                'event_date': today + timedelta(days=7),
                'event_time': '14:30',
                'category': 'gdp_growth',
                'currency': 'USD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_us_5',
                'title': 'US Retail Sales',
                'description': 'Ventes au détail américaines - Consommation',
                'country': 'US',
                'impact': 'high',
                'event_date': today + timedelta(days=9),
                'event_time': '14:30',
                'category': 'retail',
                'currency': 'USD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_us_6',
                'title': 'US Manufacturing PMI',
                'description': 'Indice PMI manufacturier américain',
                'country': 'US',
                'impact': 'high',
                'event_date': today + timedelta(days=11),
                'event_time': '15:45',
                'category': 'industrial',
                'currency': 'USD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_us_7',
                'title': 'US Trade Balance',
                'description': 'Balance commerciale des États-Unis',
                'country': 'US',
                'impact': 'medium',
                'event_date': today + timedelta(days=13),
                'event_time': '14:30',
                'category': 'trade',
                'currency': 'USD',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇪🇺 ZONE EURO - Événements BCE et économiques
        events.extend([
            {
                'id': 'fallback_eu_1',
                'title': 'ECB Interest Rate Decision',
                'description': 'Décision de taux de la Banque Centrale Européenne',
                'country': 'EU',
                'impact': 'critical',
                'event_date': today + timedelta(days=2),
                'event_time': '14:15',
                'category': 'monetary_policy',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_eu_2',
                'title': 'Eurozone CPI Flash Estimate',
                'description': 'Estimation flash de l\'inflation en Zone Euro',
                'country': 'EU',
                'impact': 'critical',
                'event_date': today + timedelta(days=4),
                'event_time': '11:00',
                'category': 'inflation',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_eu_3',
                'title': 'Eurozone GDP Growth',
                'description': 'Croissance du PIB de la Zone Euro',
                'country': 'EU',
                'impact': 'high',
                'event_date': today + timedelta(days=6),
                'event_time': '11:00',
                'category': 'gdp_growth',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_eu_4',
                'title': 'Eurozone Manufacturing PMI',
                'description': 'PMI manufacturier de la Zone Euro',
                'country': 'EU',
                'impact': 'high',
                'event_date': today + timedelta(days=8),
                'event_time': '10:00',
                'category': 'industrial',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_eu_5',
                'title': 'EU Employment Data',
                'description': 'Données sur l\'emploi en Zone Euro',
                'country': 'EU',
                'impact': 'high',
                'event_date': today + timedelta(days=10),
                'event_time': '11:00',
                'category': 'employment',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇬🇧 ROYAUME-UNI - Événements BoE et économiques
        events.extend([
            {
                'id': 'fallback_uk_1',
                'title': 'Bank of England Rate Decision',
                'description': 'Décision de taux de la Banque d\'Angleterre',
                'country': 'UK',
                'impact': 'critical',
                'event_date': today + timedelta(days=1),
                'event_time': '12:00',
                'category': 'monetary_policy',
                'currency': 'GBP',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_uk_2',
                'title': 'UK CPI Inflation',
                'description': 'Inflation des prix à la consommation UK',
                'country': 'UK',
                'impact': 'critical',
                'event_date': today + timedelta(days=3),
                'event_time': '09:30',
                'category': 'inflation',
                'currency': 'GBP',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_uk_3',
                'title': 'UK Employment Data',
                'description': 'Données sur l\'emploi au Royaume-Uni',
                'country': 'UK',
                'impact': 'high',
                'event_date': today + timedelta(days=5),
                'event_time': '09:30',
                'category': 'employment',
                'currency': 'GBP',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_uk_4',
                'title': 'UK GDP Growth',
                'description': 'Croissance du PIB britannique',
                'country': 'UK',
                'impact': 'high',
                'event_date': today + timedelta(days=7),
                'event_time': '09:30',
                'category': 'gdp_growth',
                'currency': 'GBP',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_uk_5',
                'title': 'UK Retail Sales',
                'description': 'Ventes au détail britanniques',
                'country': 'UK',
                'impact': 'medium',
                'event_date': today + timedelta(days=9),
                'event_time': '09:30',
                'category': 'retail',
                'currency': 'GBP',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇯🇵 JAPON - Événements BoJ et économiques
        events.extend([
            {
                'id': 'fallback_jp_1',
                'title': 'Bank of Japan Rate Decision',
                'description': 'Décision de taux de la Banque du Japon',
                'country': 'JP',
                'impact': 'critical',
                'event_date': today + timedelta(days=2),
                'event_time': '04:00',
                'category': 'monetary_policy',
                'currency': 'JPY',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_jp_2',
                'title': 'Japan CPI Inflation',
                'description': 'Inflation des prix à la consommation japonaise',
                'country': 'JP',
                'impact': 'high',
                'event_date': today + timedelta(days=4),
                'event_time': '01:30',
                'category': 'inflation',
                'currency': 'JPY',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_jp_3',
                'title': 'Japan GDP Quarterly',
                'description': 'PIB trimestriel du Japon',
                'country': 'JP',
                'impact': 'high',
                'event_date': today + timedelta(days=6),
                'event_time': '01:50',
                'category': 'gdp_growth',
                'currency': 'JPY',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_jp_4',
                'title': 'Japan Manufacturing PMI',
                'description': 'PMI manufacturier japonais',
                'country': 'JP',
                'impact': 'medium',
                'event_date': today + timedelta(days=8),
                'event_time': '02:30',
                'category': 'industrial',
                'currency': 'JPY',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇨🇦 CANADA - Événements BoC et économiques
        events.extend([
            {
                'id': 'fallback_ca_1',
                'title': 'Bank of Canada Rate Decision',
                'description': 'Décision de taux de la Banque du Canada',
                'country': 'CA',
                'impact': 'critical',
                'event_date': today + timedelta(days=1),
                'event_time': '16:00',
                'category': 'monetary_policy',
                'currency': 'CAD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_ca_2',
                'title': 'Canada CPI Inflation',
                'description': 'Inflation canadienne',
                'country': 'CA',
                'impact': 'high',
                'event_date': today + timedelta(days=3),
                'event_time': '14:30',
                'category': 'inflation',
                'currency': 'CAD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_ca_3',
                'title': 'Canada Employment Data',
                'description': 'Données sur l\'emploi canadien',
                'country': 'CA',
                'impact': 'high',
                'event_date': today + timedelta(days=5),
                'event_time': '14:30',
                'category': 'employment',
                'currency': 'CAD',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇦🇺 AUSTRALIE - Événements RBA et économiques
        events.extend([
            {
                'id': 'fallback_au_1',
                'title': 'Reserve Bank of Australia Rate Decision',
                'description': 'Décision de taux de la RBA',
                'country': 'AU',
                'impact': 'critical',
                'event_date': today + timedelta(days=2),
                'event_time': '05:30',
                'category': 'monetary_policy',
                'currency': 'AUD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_au_2',
                'title': 'Australia CPI Inflation',
                'description': 'Inflation australienne',
                'country': 'AU',
                'impact': 'high',
                'event_date': today + timedelta(days=4),
                'event_time': '02:30',
                'category': 'inflation',
                'currency': 'AUD',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_au_3',
                'title': 'Australia Employment Data',
                'description': 'Données sur l\'emploi australien',
                'country': 'AU',
                'impact': 'high',
                'event_date': today + timedelta(days=6),
                'event_time': '02:30',
                'category': 'employment',
                'currency': 'AUD',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇨🇭 SUISSE - Événements SNB et économiques
        events.extend([
            {
                'id': 'fallback_ch_1',
                'title': 'Swiss National Bank Rate Decision',
                'description': 'Décision de taux de la Banque Nationale Suisse',
                'country': 'CH',
                'impact': 'critical',
                'event_date': today + timedelta(days=3),
                'event_time': '09:30',
                'category': 'monetary_policy',
                'currency': 'CHF',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_ch_2',
                'title': 'Switzerland CPI',
                'description': 'Inflation suisse',
                'country': 'CH',
                'impact': 'medium',
                'event_date': today + timedelta(days=5),
                'event_time': '08:30',
                'category': 'inflation',
                'currency': 'CHF',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇨🇳 CHINE - Événements économiques majeurs
        events.extend([
            {
                'id': 'fallback_cn_1',
                'title': 'China GDP Growth',
                'description': 'Croissance du PIB chinois',
                'country': 'CN',
                'impact': 'critical',
                'event_date': today + timedelta(days=2),
                'event_time': '04:00',
                'category': 'gdp_growth',
                'currency': 'CNY',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_cn_2',
                'title': 'China Manufacturing PMI',
                'description': 'PMI manufacturier chinois',
                'country': 'CN',
                'impact': 'high',
                'event_date': today + timedelta(days=4),
                'event_time': '03:00',
                'category': 'industrial',
                'currency': 'CNY',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_cn_3',
                'title': 'China CPI Inflation',
                'description': 'Inflation chinoise',
                'country': 'CN',
                'impact': 'high',
                'event_date': today + timedelta(days=6),
                'event_time': '03:30',
                'category': 'inflation',
                'currency': 'CNY',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_cn_4',
                'title': 'China Trade Balance',
                'description': 'Balance commerciale chinoise',
                'country': 'CN',
                'impact': 'high',
                'event_date': today + timedelta(days=8),
                'event_time': '04:00',
                'category': 'trade',
                'currency': 'CNY',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇩🇪 ALLEMAGNE - Événements économiques
        events.extend([
            {
                'id': 'fallback_de_1',
                'title': 'Germany GDP Growth',
                'description': 'Croissance du PIB allemand',
                'country': 'DE',
                'impact': 'high',
                'event_date': today + timedelta(days=1),
                'event_time': '08:00',
                'category': 'gdp_growth',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_de_2',
                'title': 'Germany CPI Inflation',
                'description': 'Inflation allemande',
                'country': 'DE',
                'impact': 'high',
                'event_date': today + timedelta(days=3),
                'event_time': '08:00',
                'category': 'inflation',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_de_3',
                'title': 'Germany Manufacturing PMI',
                'description': 'PMI manufacturier allemand',
                'country': 'DE',
                'impact': 'medium',
                'event_date': today + timedelta(days=5),
                'event_time': '09:30',
                'category': 'industrial',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇫🇷 FRANCE - Événements économiques
        events.extend([
            {
                'id': 'fallback_fr_1',
                'title': 'France GDP Growth',
                'description': 'Croissance du PIB français',
                'country': 'FR',
                'impact': 'high',
                'event_date': today + timedelta(days=2),
                'event_time': '08:45',
                'category': 'gdp_growth',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_fr_2',
                'title': 'France CPI Inflation',
                'description': 'Inflation française',
                'country': 'FR',
                'impact': 'medium',
                'event_date': today + timedelta(days=4),
                'event_time': '08:45',
                'category': 'inflation',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
        ])
        
        # 🇮🇹 ITALIE - Événements économiques
        events.extend([
            {
                'id': 'fallback_it_1',
                'title': 'Italy GDP Growth',
                'description': 'Croissance du PIB italien',
                'country': 'IT',
                'impact': 'medium',
                'event_date': today + timedelta(days=3),
                'event_time': '10:00',
                'category': 'gdp_growth',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
            {
                'id': 'fallback_it_2',
                'title': 'Italy CPI Inflation',
                'description': 'Inflation italienne',
                'country': 'IT',
                'impact': 'medium',
                'event_date': today + timedelta(days=5),
                'event_time': '10:00',
                'category': 'inflation',
                'currency': 'EUR',
                'source': 'Fallback Data'
            },
        ])
        
        # ÉVÉNEMENTS SUPPLÉMENTAIRES - Tous secteurs sur 90 jours
        additional_events = []
        
        for day_offset in range(10, 90, 3):  # Événements tous les 3 jours sur 90 jours
            event_templates = [
                {
                    'title': 'Global Energy Market Report',
                    'country': 'GLOBAL',
                    'category': 'energy',
                    'impact': 'medium'
                },
                {
                    'title': 'Crypto Market Analysis',
                    'country': 'GLOBAL',
                    'category': 'crypto',
                    'impact': 'high'
                },
                {
                    'title': 'Technology Sector PMI',
                    'country': 'US',
                    'category': 'technology',
                    'impact': 'medium'
                },
                {
                    'title': 'Healthcare Industry Index',
                    'country': 'EU',
                    'category': 'healthcare',
                    'impact': 'low'
                },
                {
                    'title': 'Financial Services PMI',
                    'country': 'UK',
                    'category': 'financial',
                    'impact': 'medium'
                },
                {
                    'title': 'Real Estate Market Index',
                    'country': 'CA',
                    'category': 'real_estate',
                    'impact': 'medium'
                },
                {
                    'title': 'Agricultural Price Index',
                    'country': 'AU',
                    'category': 'agriculture',
                    'impact': 'low'
                },
                {
                    'title': 'Environmental Policy Update',
                    'country': 'EU',
                    'category': 'environment',
                    'impact': 'low'
                }
            ]
            
            template = event_templates[day_offset % len(event_templates)]
            additional_events.append({
                'id': f'fallback_additional_{day_offset}',
                'title': template['title'],
                'description': f'Événement {template["category"]} important',
                'country': template['country'],
                'impact': template['impact'],
                'event_date': today + timedelta(days=day_offset),
                'event_time': f'{9 + (day_offset % 12):02d}:00',
                'category': template['category'],
                'currency': 'USD' if template['country'] == 'US' else 'EUR',
                'source': 'Fallback Data Extended'
            })
        
        events.extend(additional_events)
        
        return events
    
    def _filter_by_categories(self, events: List[Dict], categories: List[str]) -> List[Dict]:
        """Filtre les événements par catégories sélectionnées avec correspondance flexible"""
        if not categories:
            return events
        
        # Mapping des catégories pour une correspondance flexible
        category_mapping = {
            'monetary_policy': ['monetary_policy', 'central_bank', 'interest_rates'],
            'inflation': ['inflation', 'cpi', 'ppi', 'prices'],
            'employment': ['employment', 'jobs', 'unemployment', 'labor'],
            'gdp_growth': ['gdp_growth', 'gdp', 'growth', 'economic_growth'],
            'industrial': ['industrial', 'manufacturing', 'factory', 'production'],
            'retail': ['retail', 'sales', 'consumer', 'consumption'],
            'trade': ['trade', 'exports', 'imports', 'balance'],
            'technology': ['technology', 'tech', 'innovation'],
            'healthcare': ['healthcare', 'health', 'medical'],
            'financial': ['financial', 'banking', 'finance'],
            'energy': ['energy', 'oil', 'gas', 'electricity'],
            'crypto': ['crypto', 'cryptocurrency', 'bitcoin'],
            'agriculture': ['agriculture', 'farming', 'food'],
            'real_estate': ['real_estate', 'housing', 'property'],
            'environment': ['environment', 'climate', 'green']
        }
        
        # Debug: afficher les catégories demandées
        print(f"🔍 Filtrage par catégories: {categories}")
        print(f"📊 Événements avant filtrage: {len(events)}")
        
        # Créer une liste étendue de catégories acceptées
        extended_categories = set(categories)
        for cat in categories:
            if cat in category_mapping:
                extended_categories.update(category_mapping[cat])
        
        print(f"🔍 Catégories étendues acceptées: {sorted(extended_categories)}")
        
        filtered_events = []
        for event in events:
            event_category = event.get('category', '').lower()
            
            # Vérification de correspondance directe ou étendue
            category_match = (
                event_category in categories or 
                event_category in extended_categories or
                any(cat.lower() in event_category for cat in categories)
            )
            
            if category_match:
                filtered_events.append(event)
                print(f"✅ Événement gardé: {event['title']} (catégorie: {event_category})")
            else:
                print(f"❌ Événement filtré: {event['title']} (catégorie: {event_category})")
        
        print(f"📊 Événements après filtrage: {len(filtered_events)}")
        return filtered_events
    
    def generate_calendar_view(self, events: List[Dict], target_date: datetime = None) -> html.Div:
        """Génère la vue calendrier mensuel avec événements"""
        
        if not target_date:
            target_date = self.current_date
        
        # Début et fin du mois
        month_start = target_date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
        
        # Créer la grille du calendrier
        calendar_grid = []
        
        # En-tête des jours de la semaine
        weekdays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        header_row = dbc.Row([
            dbc.Col(html.Div(day, className="text-center fw-bold"), width=True) 
            for day in weekdays
        ], className="mb-2")
        calendar_grid.append(header_row)
        
        # Calculer le premier jour affiché (peut être du mois précédent)
        first_weekday = month_start.weekday()  # 0 = Lundi
        calendar_start = month_start - timedelta(days=first_weekday)
        
        # Générer 6 semaines de calendrier
        current_date = calendar_start
        for week in range(6):
            week_row = []
            
            for day in range(7):
                day_events = []
                for e in events:
                    if e.get('event_date'):
                        # Gérer les deux formats : datetime object ou string
                        event_date = e['event_date']
                        if isinstance(event_date, str):
                            try:
                                # Convertir string en datetime si nécessaire
                                event_date = datetime.strptime(event_date, '%Y-%m-%d')
                            except ValueError:
                                try:
                                    event_date = datetime.strptime(event_date[:10], '%Y-%m-%d')
                                except ValueError:
                                    continue
                        
                        # Comparer les dates
                        if event_date.date() == current_date.date():
                            day_events.append(e)
                
                # Style de la cellule selon le mois et les événements
                cell_class = "calendar-day-cell border p-2 text-center"
                if current_date.month != target_date.month:
                    cell_class += " text-muted calendar-day-empty"
                elif day_events:
                    cell_class += " calendar-day-with-events"
                
                # Contenu de la cellule
                cell_content = [html.Strong(str(current_date.day))]
                
                # Ajouter les indicateurs d'événements
                for event in day_events[:3]:  # Max 3 événements affichés
                    impact_color = {
                        'critical': 'danger',
                        'high': 'warning', 
                        'medium': 'info',
                        'low': 'success'
                    }.get(event.get('impact', 'medium'), 'secondary')
                    
                    # Drapeaux plus grands pour meilleure visibilité
                    country_flags = {
                        'US': '🇺🇸', 'EU': '🇪🇺', 'UK': '🇬🇧', 
                        'JP': '🇯🇵', 'CN': '🇨🇳', 'CA': '🇨🇦'
                    }
                    flag = country_flags.get(event.get('country', ''), '🌍')
                    
                    event_badge = dbc.Badge([
                        html.Span(flag, style={'fontSize': '16px', 'marginRight': '3px'}),
                        html.Span(event.get('country', '??'), style={'fontSize': '10px'})
                    ],
                        color=impact_color,
                        className="me-1 event-indicator",
                        style={'fontSize': '12px'}
                    )
                    cell_content.append(html.Br())
                    cell_content.append(event_badge)
                
                # Si plus de 3 événements
                if len(day_events) > 3:
                    cell_content.append(html.Br())
                    cell_content.append(
                        dbc.Badge(f"+{len(day_events)-3}", color="secondary", className="event-indicator")
                    )
                
                day_cell = dbc.Col(
                    html.Div(
                        cell_content, 
                        className=cell_class + (" cursor-pointer" if day_events else ""),
                        id={'type': 'calendar-day', 'date': current_date.strftime('%Y-%m-%d')},
                        n_clicks=0
                    ),
                    width=True
                )
                week_row.append(day_cell)
                current_date += timedelta(days=1)
            
            calendar_grid.append(dbc.Row(week_row, className="mb-1"))
        
        return html.Div(calendar_grid)
    
    def generate_list_view(self, events: List[Dict]) -> html.Div:
        """Génère la vue liste des événements"""
        
        if not events:
            return dbc.Alert("📅 Aucun événement économique trouvé pour les critères sélectionnés", color="info")
        
        # Grouper par date
        events_by_date = {}
        for event in events:
            event_date = event.get('event_date')
            if event_date:
                date_key = event_date.strftime('%Y-%m-%d')
                if date_key not in events_by_date:
                    events_by_date[date_key] = []
                events_by_date[date_key].append(event)
        
        # Générer la liste
        list_items = []
        
        for date_key in sorted(events_by_date.keys()):
            date_obj = datetime.strptime(date_key, '%Y-%m-%d')
            day_events = events_by_date[date_key]
            
            # En-tête de la date
            date_header = html.H6(
                f"📅 {date_obj.strftime('%A %d %B %Y')}",
                className="text-primary mt-3 mb-2"
            )
            list_items.append(date_header)
            
            # Événements du jour
            for event in day_events:
                impact_colors = {
                    'critical': 'danger',
                    'high': 'warning',
                    'medium': 'info', 
                    'low': 'success'
                }
                
                impact_color = impact_colors.get(event.get('impact', 'medium'), 'secondary')
                
                country_flags = {
                    'US': '🇺🇸', 'EU': '🇪🇺', 'UK': '🇬🇧', 
                    'JP': '🇯🇵', 'CN': '🇨🇳', 'CA': '🇨🇦'
                }
                
                flag = country_flags.get(event.get('country', ''), '🌍')
                
                event_item = dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Badge(event.get('event_time', 'TBD'), color="secondary", className="me-2"),
                                dbc.Badge(event.get('impact', 'medium').title(), color=impact_color, className="me-2"),
                                html.Span(f"{flag} {event.get('title', 'Événement économique')}", className="fw-bold")
                            ]),
                            html.Small(event.get('description', ''), className="text-muted")
                        ], width=10),
                        dbc.Col([
                            html.Small(event.get('currency', ''), className="text-muted")
                        ], width=2)
                    ])
                ], className=f"event-item-{event.get('impact', 'medium')}")
                
                list_items.append(event_item)
        
        return dbc.ListGroup(list_items)
    
    def generate_analytics_view(self, events: List[Dict]) -> html.Div:
        """Génère la vue analytics avec statistiques"""
        
        if not events:
            return dbc.Alert("📊 Aucune donnée disponible pour les analytics", color="warning")
        
        # Statistiques de base
        total_events = len(events)
        countries = list(set(e.get('country', 'Unknown') for e in events))
        impacts = list(set(e.get('impact', 'unknown') for e in events))
        
        # Répartition par impact
        impact_counts = {}
        for event in events:
            impact = event.get('impact', 'unknown')
            impact_counts[impact] = impact_counts.get(impact, 0) + 1
        
        # Répartition par pays
        country_counts = {}
        for event in events:
            country = event.get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(str(total_events), className="text-primary"),
                            html.P("Événements total", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(str(len(countries)), className="text-success"),
                            html.P("Pays concernés", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(str(impact_counts.get('critical', 0)), className="text-danger"),
                            html.P("Événements critiques", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(str(impact_counts.get('high', 0)), className="text-warning"),
                            html.P("Impact élevé", className="mb-0")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H6("📊 Répartition par Impact"),
                    dbc.ListGroup([
                        dbc.ListGroupItem(f"{impact.title()}: {count} événements") 
                        for impact, count in impact_counts.items()
                    ])
                ], width=6),
                dbc.Col([
                    html.H6("🌍 Répartition par Pays"),
                    dbc.ListGroup([
                        dbc.ListGroupItem(f"{country}: {count} événements") 
                        for country, count in country_counts.items()
                    ])
                ], width=6)
            ])
        ])
    
    def setup_callbacks(self, app):
        """Configurer les callbacks du module avec données réelles"""
        
        # [ANCIEN CALLBACK SUPPRIMÉ] 
        # Callback pour gérer les clics sur les cases de jour
        @app.callback(
            [Output('day-events-modal', 'is_open'),
             Output('day-events-title', 'children'),
             Output('day-events-content', 'children')],
            [Input({'type': 'calendar-day', 'date': ALL}, 'n_clicks'),
             Input('close-day-events', 'n_clicks')],
            [State('day-events-modal', 'is_open')],
            prevent_initial_call=True
        )
        def handle_day_click(day_clicks, close_clicks, is_open):
            """Gère les clics sur les cases de jour pour afficher tous les événements"""
            
            ctx = dash.callback_context
            
            if not ctx.triggered:
                return False, "", ""
            
            trigger_id = ctx.triggered[0]['prop_id']
            
            # Si clic sur fermer
            if 'close-day-events' in trigger_id:
                return False, "", ""
            
            # Si clic sur une case de jour
            if 'calendar-day' in trigger_id and any(day_clicks):
                import json
                trigger_data = json.loads(trigger_id.split('.')[0])
                clicked_date = trigger_data['date']
                
                try:
                    # Récupérer tous les événements
                    events = self.get_real_economic_events(
                        days_ahead=90,
                        countries=None,
                        impacts=None
                    )
                    
                    if not events:
                        events = self._get_fallback_events()
                    
                    # Filtrer par impact si nécessaire
                    if hasattr(self, 'current_impact_filter') and self.current_impact_filter != 'all':
                        events = [e for e in events if e.get('impact', '').lower() == self.current_impact_filter]
                    
                    # Filtrer les événements pour la date cliquée
                    day_events = []
                    clicked_datetime = datetime.strptime(clicked_date, '%Y-%m-%d')
                    
                    for event in events:
                        event_date = event.get('event_date')
                        if event_date:
                            if isinstance(event_date, str):
                                try:
                                    event_date = datetime.strptime(event_date[:10], '%Y-%m-%d')
                                except ValueError:
                                    continue
                            
                            if event_date.date() == clicked_datetime.date():
                                day_events.append(event)
                    
                    if not day_events:
                        return True, f"📅 {clicked_datetime.strftime('%A %d %B %Y')}", [
                            dbc.Alert("Aucun événement économique pour cette journée", color="info")
                        ]
                    
                    # Créer le titre
                    title = f"📅 {clicked_datetime.strftime('%A %d %B %Y')} - {len(day_events)} événement(s)"
                    
                    # Créer le contenu avec tous les événements
                    content = []
                    
                    # Grouper par pays pour une meilleure organisation
                    events_by_country = {}
                    for event in day_events:
                        country = event.get('country', 'Unknown')
                        if country not in events_by_country:
                            events_by_country[country] = []
                        events_by_country[country].append(event)
                    
                    for country, country_events in events_by_country.items():
                        # Drapeau et nom du pays
                        country_flags = {
                            'US': '🇺🇸 États-Unis', 'EU': '🇪🇺 Zone Euro', 'UK': '🇬🇧 Royaume-Uni',
                            'JP': '🇯🇵 Japon', 'CN': '🇨🇳 Chine', 'CA': '🇨🇦 Canada',
                            'AU': '🇦🇺 Australie', 'DE': '🇩🇪 Allemagne', 'FR': '🇫🇷 France'
                        }
                        country_name = country_flags.get(country, f"🌍 {country}")
                        
                        content.append(html.H5(country_name, className="mt-3 mb-2"))
                        
                        # Liste des événements pour ce pays
                        for event in country_events:
                            impact_colors = {
                                'critical': 'danger', 'high': 'warning',
                                'medium': 'info', 'moderate': 'info', 'low': 'success'
                            }
                            impact = event.get('impact', 'medium')
                            impact_color = impact_colors.get(impact, 'secondary')
                            
                            event_card = dbc.Card([
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.H6(event.get('title', 'Événement Économique'), className="mb-1"),
                                            html.P(event.get('description', 'Aucune description'), className="text-muted small")
                                        ], width=8),
                                        dbc.Col([
                                            dbc.Badge(impact.title(), color=impact_color, className="mb-1"),
                                            html.Br(),
                                            html.Small(f"⏰ {event.get('event_time', 'TBD')}", className="text-muted")
                                        ], width=4, className="text-end")
                                    ])
                                ])
                            ], className="mb-2")
                            
                            content.append(event_card)
                    
                    return True, title, content
                    
                except Exception as e:
                    print(f"❌ Erreur lors du clic sur jour: {e}")
                    return True, "❌ Erreur", [html.P("Impossible de charger les événements de cette journée")]
            
            return is_open, "", ""
        
        # Callback principal pour la gestion du calendrier
        @app.callback(
            [Output('calendar-content', 'children'),
             Output('calendar-current-month', 'children'),
             Output('btn-impact-critical', 'active'),
             Output('btn-impact-high', 'active'),
             Output('btn-impact-moderate', 'active'),
             Output('btn-impact-all', 'active')],
            [Input('btn-impact-critical', 'n_clicks'),
             Input('btn-impact-high', 'n_clicks'),
             Input('btn-impact-moderate', 'n_clicks'),
             Input('btn-impact-all', 'n_clicks'),
             Input('calendar-prev-month', 'n_clicks'),
             Input('calendar-next-month', 'n_clicks')],
            prevent_initial_call=True
        )
        def update_calendar_display(critical_clicks, high_clicks, moderate_clicks, all_clicks,
                                   prev_clicks, next_clicks):
            """Met à jour l'affichage du calendrier selon le filtre d'impact - VERSION SIMPLIFIÉE"""
            ctx = dash.callback_context
            
            if not ctx.triggered:
                # État initial : vue calendrier, tous les impacts
                return dash.no_update, dash.no_update, False, False, False, True
                
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            print(f"🔄 Callback déclenché par: {trigger_id}")
            
            # Gestion de la navigation temporelle
            if trigger_id == 'calendar-prev-month':
                self.current_date = self.current_date.replace(day=1)
                self.current_date = (self.current_date - timedelta(days=1)).replace(day=1)
            elif trigger_id == 'calendar-next-month':
                next_month = self.current_date.replace(day=28) + timedelta(days=4)
                self.current_date = next_month.replace(day=1)
            
            # Gestion des filtres d'impact
            impact_filter = 'all'  # défaut
            impact_buttons = [False, False, False, True]  # tous actif par défaut
            
            if trigger_id == 'btn-impact-critical':
                impact_filter = 'critical'
                impact_buttons = [True, False, False, False]
            elif trigger_id == 'btn-impact-high':
                impact_filter = 'high' 
                impact_buttons = [False, True, False, False]
            elif trigger_id == 'btn-impact-moderate':
                impact_filter = 'moderate'
                impact_buttons = [False, False, True, False]
            elif trigger_id == 'btn-impact-all':
                impact_filter = 'all'
                impact_buttons = [False, False, False, True]
            
            self.current_impact_filter = impact_filter
            
            # Récupérer TOUS les événements économiques
            print("📊 Récupération de TOUS les événements économiques...")
            events = self.get_real_economic_events(
                days_ahead=self.filter_period,
                countries=None,  # TOUS les pays
                impacts=None     # TOUS les impacts initialement
            )
            
            # Si pas d'événements API, utiliser fallback
            if not events:
                print("🔄 Utilisation des événements de fallback")
                events = self._get_fallback_events()
            
            # Filtrer par impact seulement si pas "tous"
            if impact_filter != 'all':
                print(f"🔍 Filtrage par impact: {impact_filter}")
                filtered_events = [e for e in events if e.get('impact', '').lower() == impact_filter]
                events = filtered_events
                print(f"📊 Événements après filtrage impact: {len(events)}")
            else:
                print(f"📊 TOUS les événements affichés: {len(events)}")
            
            # Générer toujours le contenu calendrier
            try:
                content = self.generate_calendar_view(events)
                
                # Titre du mois pour le calendrier
                month_title = f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
                
                print(f"✅ Contenu généré: {len(events)} événements, vue: calendrier, impact: {impact_filter}")
                
                return content, month_title, *impact_buttons
                
            except Exception as e:
                print(f"❌ Erreur génération contenu: {e}")
                error_content = html.Div([
                    dbc.Alert([
                        html.H5("⚠️ Erreur de chargement"),
                        html.P(f"Une erreur s'est produite: {str(e)}")
                    ], color="warning", className="text-center mt-4")
                ])
                return error_content, "Erreur", *impact_buttons
    
    def get_custom_css(self) -> str:
        """Retourner le CSS personnalisé pour le module"""
        
        return """
        /* Styles pour le calendrier économique */
        .calendar-grid {
            font-family: 'Inter', Arial, sans-serif;
        }
        
        /* Fix critique pour les dropdowns du calendrier */
        .calendar-dropdown-fix .Select__menu {
            z-index: 999999 !important;
            position: fixed !important;
        }
        
        .calendar-dropdown-fix .Select__menu-list {
            z-index: 999999 !important;
            position: relative !important;
        }
        
        .calendar-dropdown-fix .Select__control {
            border: 2px solid #dee2e6 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            z-index: 10 !important;
            position: relative !important;
        }
        
        .calendar-dropdown-fix .Select__control:hover {
            border-color: #007bff !important;
            box-shadow: 0 0 0 0.1rem rgba(0, 123, 255, 0.25) !important;
        }
        
        .calendar-dropdown-fix .Select__control--is-focused {
            border-color: #007bff !important;
            box-shadow: 0 0 0 0.1rem rgba(0, 123, 255, 0.25) !important;
        }
        
        /* Styles pour les filtres - Toujours visibles et au-dessus */
        .calendar-module .card {
            position: relative;
            z-index: 10;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .calendar-module .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        /* Dropdowns avec z-index élevé - Solution universelle */
        .calendar-module .Select-menu-outer,
        .calendar-module .Select-menu,
        .calendar-module div[class*="menu"],
        .calendar-module .Select__menu,
        .calendar-module .Select__menu-list,
        .calendar-module div[data-dash-is-loading],
        .Select-menu-outer,
        .Select__menu,
        .Select__menu-list {
            z-index: 999999 !important;
            position: fixed !important;
        }
        
        /* Force ABSOLUE pour tous les dropdowns Dash */
        div[id*="calendar"] .Select__menu,
        div[id*="calendar"] .Select__menu-list,
        div[id*="calendar"] div[class*="menu"],
        div[class*="Select__menu"],
        div[class*="__menu"] {
            z-index: 999999 !important;
            position: fixed !important;
            background: white !important;
            border: 1px solid #ccc !important;
            border-radius: 4px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
        
        /* Container des filtres */
        .calendar-filters-container {
            position: sticky;
            top: 0;
            z-index: 100;
            background: white;
            padding: 15px 0;
            margin-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Amélioration des cellules de calendrier */
        .calendar-day-cell {
            min-height: 100px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid #dee2e6 !important;
            background-color: #ffffff;
            position: relative;
            z-index: 1;
        }
        
        .calendar-day-cell:hover {
            background-color: #f8f9fa !important;
            border-color: #007bff !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .calendar-day-empty {
            background-color: #f8f9fa !important;
            color: #6c757d !important;
        }
        
        .calendar-day-with-events {
            background-color: #e3f2fd !important;
            border-color: #2196f3 !important;
        }
        
        /* Événements cliquables avec drapeaux plus grands */
        .event-indicator {
            font-size: 12px !important;
            font-weight: bold !important;
            padding: 4px 6px !important;
            margin: 2px !important;
            border-radius: 4px !important;
            transition: all 0.2s ease !important;
        }
        
        .clickable-event {
            cursor: pointer !important;
            transform: scale(1) !important;
            transition: all 0.2s ease !important;
        }
        
        .clickable-event:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
            z-index: 10 !important;
        }
        
        /* Styles pour les filtres */
        .events-filter-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            color: white;
        }
        
        /* Styles pour les événements par impact */
        .event-item-critical {
            border-left: 4px solid #dc3545 !important;
            background-color: #f8d7da !important;
        }
        
        .event-item-high {
            border-left: 4px solid #fd7e14 !important;
            background-color: #fff3cd !important;
        }
        
        .event-item-medium {
            border-left: 4px solid #0dcaf0 !important;
            background-color: #cff4fc !important;
        }
        
        .event-item-low {
            border-left: 4px solid #198754 !important;
            background-color: #d1e7dd !important;
        }
        
        /* Navigation du calendrier */
        .calendar-navigation {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
        }
        
        /* Badges d'impact */
        .badge-critical {
            background: linear-gradient(45deg, #ff4757, #ff3742) !important;
        }
        
        .badge-high {
            background: linear-gradient(45deg, #ffa502, #ff9f43) !important;
        }
        
        .badge-medium {
            background: linear-gradient(45deg, #3742fa, #2f3542) !important;
        }
        
        .badge-low {
            background: linear-gradient(45deg, #2ed573, #1dd1a1) !important;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .calendar-day-cell {
                min-height: 60px;
                font-size: 12px;
            }
            
            .event-indicator {
                font-size: 10px !important;
            }
        }
        
        /* Dark mode support */
        [data-bs-theme="dark"] .calendar-day-cell {
            background-color: #2d3748;
            border-color: #4a5568;
            color: #e2e8f0;
        }
        
        [data-bs-theme="dark"] .calendar-day-cell:hover {
            background-color: #4a5568 !important;
            border-color: #63b3ed !important;
        }
        """