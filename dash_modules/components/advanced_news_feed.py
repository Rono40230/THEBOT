"""
Advanced News Feed - Phase 3 THEBOT
Interface avancée pour le feed RSS avec filtres et interactions
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
from urllib.parse import urlparse

class AdvancedNewsFeed:
    """
    Interface avancée pour les actualités RSS avec fonctionnalités étendues
    """
    
    def __init__(self):
        self.news_categories = {
            'all': {'label': 'Toutes', 'icon': '📰', 'color': 'primary'},
            'crypto': {'label': 'Crypto', 'icon': '₿', 'color': 'warning'},
            'economic': {'label': 'Économie', 'icon': '📊', 'color': 'info'},
            'market': {'label': 'Marchés', 'icon': '📈', 'color': 'success'},
            'forex': {'label': 'Forex', 'icon': '💱', 'color': 'secondary'},
            'general': {'label': 'Général', 'icon': '🌐', 'color': 'dark'}
        }
        
        self.news_sources = {
            'CoinDesk News': {'color': 'warning', 'reliability': 'high'},
            'CryptoNews Feed': {'color': 'info', 'reliability': 'medium'},
            'Bitcoin Magazine': {'color': 'warning', 'reliability': 'high'},
            'Decrypt News': {'color': 'primary', 'reliability': 'high'},
            'CoinTelegraph': {'color': 'success', 'reliability': 'medium'},
            'BBC Business': {'color': 'danger', 'reliability': 'high'},
            'The Economist': {'color': 'dark', 'reliability': 'high'},
            'Seeking Alpha': {'color': 'success', 'reliability': 'medium'},
            'Yahoo Finance': {'color': 'purple', 'reliability': 'medium'},
            'Investing.com': {'color': 'info', 'reliability': 'medium'},
            'CNN Business': {'color': 'danger', 'reliability': 'high'}
        }
        
        self.sort_options = [
            {'label': '🕒 Plus récent', 'value': 'newest'},
            {'label': '⏰ Plus ancien', 'value': 'oldest'},
            {'label': '📊 Par source', 'value': 'source'},
            {'label': '🏷️ Par catégorie', 'value': 'category'}
        ]
    
    def create_news_interface(self) -> html.Div:
        """Crée l'interface complète des actualités"""
        return html.Div([
            # En-tête avec contrôles
            self.create_news_header(),
            
            # Filtres avancés
            self.create_news_filters(),
            
            # Zone de contenu principal
            dbc.Row([
                # Colonne principale - Feed
                dbc.Col([
                    html.Div(
                        id="news-feed-main",
                        children=[
                            dbc.Spinner(
                                html.Div("Chargement des actualités..."),
                                color="primary"
                            )
                        ]
                    )
                ], width=8),
                
                # Sidebar - Stats et favoris
                dbc.Col([
                    self.create_news_sidebar()
                ], width=4)
            ]),
            
            # Modal pour article détaillé
            self.create_article_modal(),
            
            # Stores pour données
            dcc.Store(id='news-data-store'),
            dcc.Store(id='news-filters-store', data={
                'category': 'all',
                'source': 'all',
                'sort': 'newest',
                'search': '',
                'favorites_only': False
            }),
            dcc.Store(id='news-favorites-store', data=[]),
            
            # Interval pour auto-refresh
            dcc.Interval(
                id='news-refresh-interval',
                interval=60*1000,  # 1 minute
                n_intervals=0
            )
        ])
    
    def create_news_header(self) -> dbc.Container:
        """Crée l'en-tête des actualités"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3([
                        html.I(className="fas fa-newspaper me-2"),
                        "Actualités en Temps Réel"
                    ]),
                    html.P(
                        id="news-last-update",
                        children=f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}",
                        className="text-muted small"
                    )
                ], width=6),
                
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button(
                            [html.I(className="fas fa-sync"), " Actualiser"],
                            id="news-refresh-btn",
                            color="primary",
                            size="sm"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-star"), " Favoris"],
                            id="news-favorites-toggle",
                            color="warning",
                            size="sm",
                            outline=True
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-download"), " Export"],
                            id="news-export-btn",
                            color="success",
                            size="sm"
                        )
                    ])
                ], width=6, className="text-end")
            ])
        ], fluid=True, className="news-header mb-3")
    
    def create_news_filters(self) -> dbc.Card:
        """Crée les filtres pour les actualités"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    # Recherche
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id="news-search-input",
                                placeholder="🔍 Rechercher dans les actualités...",
                                debounce=True
                            ),
                            dbc.Button(
                                html.I(className="fas fa-times"),
                                id="news-search-clear",
                                color="outline-secondary"
                            )
                        ])
                    ], width=4),
                    
                    # Filtre catégorie
                    dbc.Col([
                        dbc.Select(
                            id="news-category-filter",
                            options=[
                                {
                                    "label": f"{info['icon']} {info['label']}", 
                                    "value": cat_id
                                }
                                for cat_id, info in self.news_categories.items()
                            ],
                            value="all"
                        )
                    ], width=2),
                    
                    # Filtre source
                    dbc.Col([
                        dbc.Select(
                            id="news-source-filter",
                            options=[{"label": "Toutes les sources", "value": "all"}],
                            value="all"
                        )
                    ], width=3),
                    
                    # Tri
                    dbc.Col([
                        dbc.Select(
                            id="news-sort-select",
                            options=self.sort_options,
                            value="newest"
                        )
                    ], width=2),
                    
                    # Options
                    dbc.Col([
                        dbc.Switch(
                            id="news-auto-refresh-switch",
                            label="Auto",
                            value=True
                        )
                    ], width=1)
                ])
            ])
        ], className="news-filters mb-3")
    
    def create_news_sidebar(self) -> html.Div:
        """Crée la sidebar avec stats et outils"""
        return html.Div([
            # Statistiques
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-chart-bar me-2"),
                        "Statistiques"
                    ])
                ]),
                dbc.CardBody([
                    html.Div(id="news-stats-content", children=[
                        dbc.Row([
                            dbc.Col([
                                html.H4("0", id="news-total-count", className="text-primary"),
                                html.Small("Total articles")
                            ], width=6),
                            dbc.Col([
                                html.H4("0", id="news-today-count", className="text-success"),
                                html.Small("Aujourd'hui")
                            ], width=6)
                        ])
                    ])
                ])
            ], className="mb-3"),
            
            # Sources actives
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-rss me-2"),
                        "Sources"
                    ])
                ]),
                dbc.CardBody([
                    html.Div(id="news-sources-list", children=[
                        html.P("Chargement...", className="text-muted")
                    ])
                ])
            ], className="mb-3"),
            
            # Favoris rapides
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-bookmark me-2"),
                        "Favoris"
                    ])
                ]),
                dbc.CardBody([
                    html.Div(id="news-favorites-list", children=[
                        html.P("Aucun favori", className="text-muted small text-center")
                    ])
                ])
            ])
        ])
    
    def create_article_modal(self) -> dbc.Modal:
        """Crée le modal pour afficher un article détaillé"""
        return dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle(id="article-modal-title")
            ]),
            dbc.ModalBody([
                # Métadonnées article
                html.Div(id="article-modal-meta", className="mb-3"),
                
                # Contenu article
                html.Div(id="article-modal-content"),
                
                # Actions
                html.Hr(),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-star"), " Ajouter aux favoris"],
                        id="article-add-favorite",
                        color="warning",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-share"), " Partager"],
                        id="article-share",
                        color="info",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-external-link-alt"), " Voir original"],
                        id="article-open-original",
                        color="primary",
                        size="sm",
                        target="_blank"
                    )
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "Fermer",
                    id="article-modal-close",
                    color="secondary"
                )
            ])
        ], id="article-modal", size="lg", scrollable=True)
    
    def format_news_articles(self, articles: List[Dict], filters: Dict) -> List[html.Div]:
        """Formate les articles pour l'affichage"""
        if not articles:
            return [
                html.Div([
                    html.I(className="fas fa-info-circle fa-3x text-muted mb-3"),
                    html.H5("Aucun article trouvé", className="text-muted"),
                    html.P("Essayez de modifier vos filtres ou d'actualiser.", className="text-muted")
                ], className="text-center py-5")
            ]
        
        formatted_articles = []
        
        for i, article in enumerate(articles):
            # Métadonnées
            source = article.get('rss_source_name', article.get('source', 'Source inconnue'))
            category = article.get('category', 'general')
            pub_date = article.get('published', article.get('date', 'Date inconnue'))
            
            # Formater la date
            try:
                if isinstance(pub_date, str):
                    # Tenter de parser différents formats de date
                    date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                else:
                    date_obj = pub_date
                
                time_ago = self.get_time_ago(date_obj)
            except:
                time_ago = "Date inconnue"
            
            # Badges
            source_info = self.news_sources.get(source, {'color': 'secondary', 'reliability': 'unknown'})
            category_info = self.news_categories.get(category, {'color': 'secondary', 'icon': '📄'})
            
            # Card article
            article_card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            # En-tête avec badges
                            html.Div([
                                dbc.Badge(
                                    [category_info['icon'], f" {category_info.get('label', category)}"],
                                    color=category_info['color'],
                                    className="me-2"
                                ),
                                dbc.Badge(
                                    source,
                                    color=source_info['color'],
                                    className="me-2"
                                ),
                                dbc.Badge(
                                    time_ago,
                                    color="light",
                                    text_color="dark"
                                )
                            ], className="mb-2"),
                            
                            # Titre
                            html.H5(
                                article.get('title', 'Titre non disponible'),
                                className="card-title article-title",
                                id={"type": "article-title", "index": i}
                            ),
                            
                            # Résumé
                            html.P(
                                self.truncate_text(article.get('summary', article.get('description', '')), 150),
                                className="card-text text-muted"
                            ),
                            
                            # Actions
                            dbc.ButtonGroup([
                                dbc.Button(
                                    "Lire plus",
                                    id={"type": "read-more-btn", "index": i},
                                    color="primary",
                                    size="sm"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-star"),
                                    id={"type": "favorite-btn", "index": i},
                                    color="warning",
                                    size="sm",
                                    outline=True
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-external-link-alt"),
                                    href=article.get('url', '#'),
                                    target="_blank",
                                    color="info",
                                    size="sm",
                                    outline=True
                                )
                            ], size="sm")
                        ], width=12)
                    ])
                ])
            ], className="news-article-card mb-3 hover-shadow")
            
            formatted_articles.append(article_card)
        
        return formatted_articles
    
    def get_time_ago(self, date_obj: datetime) -> str:
        """Calcule le temps écoulé depuis une date"""
        now = datetime.now(date_obj.tzinfo) if date_obj.tzinfo else datetime.now()
        diff = now - date_obj
        
        if diff.days > 0:
            return f"Il y a {diff.days}j"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"Il y a {hours}h"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"Il y a {minutes}min"
        else:
            return "À l'instant"
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Tronque un texte à une longueur maximale"""
        if not text:
            return "Aucun résumé disponible"
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length].rsplit(' ', 1)[0] + "..."
    
    def filter_articles(self, articles: List[Dict], filters: Dict) -> List[Dict]:
        """Filtre les articles selon les critères"""
        filtered = articles.copy()
        
        # Filtre par catégorie
        if filters.get('category') and filters['category'] != 'all':
            filtered = [a for a in filtered if a.get('category') == filters['category']]
        
        # Filtre par source
        if filters.get('source') and filters['source'] != 'all':
            filtered = [a for a in filtered 
                       if a.get('rss_source_name') == filters['source'] or 
                          a.get('source') == filters['source']]
        
        # Filtre par recherche
        if filters.get('search'):
            search_term = filters['search'].lower()
            filtered = [a for a in filtered 
                       if search_term in a.get('title', '').lower() or 
                          search_term in a.get('summary', '').lower()]
        
        # Filtre favoris uniquement
        if filters.get('favorites_only'):
            favorites = filters.get('favorites', [])
            filtered = [a for a in filtered if a.get('url') in favorites]
        
        # Tri
        sort_key = filters.get('sort', 'newest')
        if sort_key == 'newest':
            filtered.sort(key=lambda x: x.get('published', ''), reverse=True)
        elif sort_key == 'oldest':
            filtered.sort(key=lambda x: x.get('published', ''))
        elif sort_key == 'source':
            filtered.sort(key=lambda x: x.get('rss_source_name', x.get('source', '')))
        elif sort_key == 'category':
            filtered.sort(key=lambda x: x.get('category', ''))
        
        return filtered
    
    def get_news_statistics(self, articles: List[Dict]) -> Dict:
        """Calcule les statistiques des actualités"""
        if not articles:
            return {
                'total': 0,
                'today': 0,
                'by_category': {},
                'by_source': {},
                'latest_update': None
            }
        
        today = datetime.now().date()
        today_count = 0
        by_category = {}
        by_source = {}
        latest_update = None
        
        for article in articles:
            # Compter articles d'aujourd'hui
            pub_date = article.get('published', '')
            try:
                if isinstance(pub_date, str):
                    date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                else:
                    date_obj = pub_date
                
                if date_obj.date() == today:
                    today_count += 1
                
                if not latest_update or date_obj > latest_update:
                    latest_update = date_obj
            except:
                pass
            
            # Par catégorie
            category = article.get('category', 'general')
            by_category[category] = by_category.get(category, 0) + 1
            
            # Par source
            source = article.get('rss_source_name', article.get('source', 'Inconnu'))
            by_source[source] = by_source.get(source, 0) + 1
        
        return {
            'total': len(articles),
            'today': today_count,
            'by_category': by_category,
            'by_source': by_source,
            'latest_update': latest_update
        }

# Instance globale
advanced_news_feed = AdvancedNewsFeed()