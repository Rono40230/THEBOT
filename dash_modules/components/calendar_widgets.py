"""
Composants UI pour le calendrier d'annonces économiques
Widgets réutilisables pour la sélection et affichage des événements
"""

import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import calendar
import pandas as pd

from ..data_providers.economic_events_config import economic_events_config, EventImpact, EventCategory

class EventsSelectionWidget:
    """Widget de sélection des événements à suivre"""
    
    def __init__(self):
        self.events_config = economic_events_config
    
    def create_selection_panel(self) -> dbc.Card:
        """Créer le panel de sélection des événements"""
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="fas fa-filter me-2"),
                    "Sélection des Annonces à Suivre"
                ], className="mb-0 text-primary")
            ]),
            dbc.CardBody([
                
                # Filtres rapides par impact
                html.Div([
                    html.H6("Filtres Rapides", className="text-muted mb-2"),
                    dbc.ButtonGroup([
                        dbc.Button("🔴 Critiques", id="filter-critical", size="sm", outline=True, color="danger"),
                        dbc.Button("🟠 Élevé", id="filter-high", size="sm", outline=True, color="warning"),
                        dbc.Button("🟡 Moyen", id="filter-medium", size="sm", outline=True, color="info"),
                        dbc.Button("🟢 Faible", id="filter-low", size="sm", outline=True, color="success"),
                        dbc.Button("🌍 Tous", id="filter-all", size="sm", outline=True, color="primary"),
                    ], className="mb-3")
                ]),
                
                # Filtres par pays
                html.Div([
                    html.H6("Filtres par Pays", className="text-muted mb-2"),
                    dcc.Dropdown(
                        id="country-filter",
                        options=[
                            {'label': f"{flag} {country}", 'value': country}
                            for country, flag in self.events_config.country_flags.items()
                        ],
                        value=["US", "EU", "UK"],
                        multi=True,
                        placeholder="Sélectionner les pays...",
                        className="mb-3"
                    )
                ]),
                
                # Filtres par catégorie
                html.Div([
                    html.H6("Filtres par Catégorie", className="text-muted mb-2"),
                    dcc.Dropdown(
                        id="category-filter",
                        options=[
                            {'label': self._get_category_label(cat), 'value': cat.value}
                            for cat in EventCategory
                        ],
                        value=["monetary_policy", "inflation", "employment"],
                        multi=True,
                        placeholder="Sélectionner les catégories...",
                        className="mb-3"
                    )
                ]),
                
                # Liste de sélection détaillée
                html.Div([
                    html.H6("Sélection Détaillée", className="text-muted mb-2"),
                    html.Div(id="events-selection-list")
                ])
            ])
        ], className="mb-3")
    
    def _get_category_label(self, category: EventCategory) -> str:
        """Obtenir le label d'affichage pour une catégorie"""
        labels = {
            EventCategory.EMPLOYMENT: "👥 Emploi",
            EventCategory.MONETARY_POLICY: "🏦 Politique Monétaire",
            EventCategory.INFLATION: "📈 Inflation",
            EventCategory.ECONOMIC_ACTIVITY: "🏭 Activité Économique",
            EventCategory.CONSUMPTION: "🛒 Consommation",
            EventCategory.GEOPOLITICAL: "🏛️ Géopolitique",
            EventCategory.CRYPTO_REGULATORY: "💎 Crypto/Régulation",
            EventCategory.CORPORATE: "🏢 Entreprises",
            EventCategory.COMMODITIES: "🛢️ Matières Premières"
        }
        return labels.get(category, category.value.title())
    
    def create_events_checklist(self, filtered_events: List = None) -> html.Div:
        """Créer la liste à cocher des événements"""
        
        events = filtered_events or self.events_config.get_enabled_events()
        
        # Grouper par pays et impact
        events_by_country = {}
        for event in events:
            if event.country not in events_by_country:
                events_by_country[event.country] = {
                    'critical': [],
                    'high': [],
                    'medium': [],
                    'low': []
                }
            events_by_country[event.country][event.impact.value].append(event)
        
        country_sections = []
        
        for country, events_by_impact in events_by_country.items():
            flag = self.events_config.country_flags.get(country, "🌍")
            
            # Section pays
            country_events = []
            
            for impact_level in ['critical', 'high', 'medium', 'low']:
                events_list = events_by_impact[impact_level]
                if not events_list:
                    continue
                
                impact_color = {
                    'critical': 'danger',
                    'high': 'warning', 
                    'medium': 'info',
                    'low': 'success'
                }[impact_level]
                
                impact_icon = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡', 
                    'low': '🟢'
                }[impact_level]
                
                # Événements de ce niveau d'impact
                event_items = []
                for event in events_list:
                    event_items.append(
                        dbc.ListGroupItem([
                            dbc.Checkbox(
                                id={'type': 'event-checkbox', 'index': event.id},
                                value=event.enabled,
                                className="me-2"
                            ),
                            html.Span([
                                html.Strong(event.name, className="me-2"),
                                dbc.Badge(
                                    event.frequency.value.title(), 
                                    color="secondary", 
                                    className="me-2"
                                ),
                                html.Small(event.description, className="text-muted")
                            ])
                        ], className="d-flex align-items-start")
                    )
                
                if event_items:
                    country_events.append(
                        html.Div([
                            html.H6([
                                impact_icon,
                                f" Impact {impact_level.title()}"
                            ], className=f"text-{impact_color} mb-2"),
                            dbc.ListGroup(event_items, className="mb-3")
                        ])
                    )
            
            if country_events:
                country_sections.append(
                    dbc.Accordion([
                        dbc.AccordionItem(
                            country_events,
                            title=f"{flag} {country}",
                            item_id=f"country-{country}"
                        )
                    ], start_collapsed=False, className="mb-3")
                )
        
        return html.Div(country_sections)

class CalendarWidget:
    """Widget de calendrier interactif"""
    
    def __init__(self):
        pass
    
    def create_calendar_view(self, month: int = None, year: int = None) -> html.Div:
        """Créer la vue calendrier mensuel"""
        
        now = datetime.now()
        month = month or now.month
        year = year or now.year
        
        return html.Div([
            # Navigation calendrier
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("◀", id="prev-month", size="sm", outline=True),
                        dbc.Button(
                            f"{calendar.month_name[month]} {year}",
                            id="current-month-year",
                            disabled=True,
                            className="text-center"
                        ),
                        dbc.Button("▶", id="next-month", size="sm", outline=True),
                    ], className="w-100")
                ], width=6),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("📅 Mois", id="view-month", size="sm", active=True),
                        dbc.Button("📋 Liste", id="view-list", size="sm"),
                        dbc.Button("📊 Analyse", id="view-analysis", size="sm"),
                    ], className="w-100")
                ], width=6)
            ], className="mb-3"),
            
            # Zone d'affichage du calendrier
            html.Div(id="calendar-display-area")
        ])
    
    def create_month_grid(self, calendar_data: Dict) -> html.Div:
        """Créer la grille mensuelle du calendrier"""
        
        month = calendar_data['month']
        year = calendar_data['year']
        events_by_day = calendar_data['events_by_day']
        
        # Créer le calendrier
        cal = calendar.monthcalendar(year, month)
        
        # En-têtes jours de la semaine
        weekdays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        header_row = dbc.Row([
            dbc.Col(html.Div(day, className="text-center fw-bold text-muted"), width=True)
            for day in weekdays
        ], className="mb-2")
        
        # Lignes du calendrier
        calendar_rows = []
        for week in cal:
            week_cols = []
            for day in week:
                if day == 0:
                    # Jour vide
                    week_cols.append(
                        dbc.Col(html.Div(), width=True, className="calendar-day-empty")
                    )
                else:
                    # Jour avec événements potentiels
                    day_events = events_by_day.get(day, [])
                    day_cell = self._create_calendar_day_cell(day, day_events)
                    week_cols.append(
                        dbc.Col(day_cell, width=True, className="calendar-day")
                    )
            
            calendar_rows.append(dbc.Row(week_cols, className="mb-1"))
        
        return html.Div([
            header_row,
            *calendar_rows
        ], className="calendar-grid")
    
    def _create_calendar_day_cell(self, day: int, events: List[Dict]) -> html.Div:
        """Créer une cellule de jour du calendrier"""
        
        # Indicateurs d'événements
        event_indicators = []
        
        # Compter par impact
        impact_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for event in events:
            impact_counts[event['impact']] += 1
        
        # Créer les indicateurs visuels
        for impact, count in impact_counts.items():
            if count > 0:
                color = {
                    'critical': '#dc3545',
                    'high': '#fd7e14',
                    'medium': '#0dcaf0',
                    'low': '#198754'
                }[impact]
                
                event_indicators.append(
                    html.Div(
                        str(count),
                        className="event-indicator",
                        style={
                            'backgroundColor': color,
                            'color': 'white',
                            'borderRadius': '50%',
                            'width': '20px',
                            'height': '20px',
                            'fontSize': '10px',
                            'textAlign': 'center',
                            'lineHeight': '20px',
                            'display': 'inline-block',
                            'margin': '1px'
                        }
                    )
                )
        
        # Déterminer la classe CSS du jour
        today = datetime.now().date()
        day_date = datetime.now().replace(day=day).date()
        
        day_class = "calendar-day-cell p-2 border rounded"
        if day_date == today:
            day_class += " bg-primary text-white"
        elif events:
            day_class += " bg-light border-primary"
        
        return html.Div([
            html.Div(str(day), className="fw-bold mb-1"),
            html.Div(event_indicators, className="event-indicators")
        ], className=day_class, id={'type': 'calendar-day', 'index': day})

class EventsListWidget:
    """Widget de liste des événements"""
    
    def __init__(self):
        pass
    
    def create_events_table(self, events: List[Dict]) -> dash_table.DataTable:
        """Créer le tableau des événements"""
        
        if not events:
            return html.Div([
                dbc.Alert("Aucun événement trouvé pour les critères sélectionnés", color="info")
            ])
        
        # Préparer les données
        table_data = []
        for event in events:
            row = {
                'flag': event['flag'],
                'datetime': event['datetime'].strftime('%d/%m %H:%M'),
                'name': event['name'],
                'impact': event['impact'],
                'previous': event.get('previous_value', '-'),
                'forecast': event.get('forecast_value', '-'),
                'actual': event.get('actual_value', '-'),
                'status': event['status']
            }
            table_data.append(row)
        
        return dash_table.DataTable(
            data=table_data,
            columns=[
                {'name': '', 'id': 'flag', 'type': 'text'},
                {'name': 'Date/Heure', 'id': 'datetime', 'type': 'text'},
                {'name': 'Événement', 'id': 'name', 'type': 'text'},
                {'name': 'Impact', 'id': 'impact', 'type': 'text'},
                {'name': 'Précédent', 'id': 'previous', 'type': 'text'},
                {'name': 'Prévision', 'id': 'forecast', 'type': 'text'},
                {'name': 'Réel', 'id': 'actual', 'type': 'text'},
                {'name': 'Statut', 'id': 'status', 'type': 'text'}
            ],
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{impact} = critical'},
                    'backgroundColor': '#fee2e2',
                    'color': '#dc2626'
                },
                {
                    'if': {'filter_query': '{impact} = high'},
                    'backgroundColor': '#fef3c7',
                    'color': '#d97706'
                },
                {
                    'if': {'filter_query': '{status} = upcoming'},
                    'fontWeight': 'bold'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            sort_action="native",
            filter_action="native",
            page_size=15,
            id="events-table"
        )
    
    def create_events_timeline(self, events: List[Dict]) -> dcc.Graph:
        """Créer la timeline des événements"""
        
        if not events:
            return html.Div()
        
        # Préparer les données pour le graphique
        df = pd.DataFrame(events)
        
        # Créer le graphique timeline
        fig = go.Figure()
        
        # Couleurs par impact
        impact_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#0dcaf0',
            'low': '#198754'
        }
        
        for impact in ['critical', 'high', 'medium', 'low']:
            impact_events = df[df['impact'] == impact]
            if not impact_events.empty:
                fig.add_trace(go.Scatter(
                    x=impact_events['datetime'],
                    y=[impact] * len(impact_events),
                    mode='markers',
                    marker=dict(
                        size=12,
                        color=impact_colors[impact],
                        symbol='circle'
                    ),
                    text=impact_events['name'],
                    hovertemplate="<b>%{text}</b><br>%{x}<extra></extra>",
                    name=impact.title(),
                    showlegend=True
                ))
        
        fig.update_layout(
            title="Timeline des Événements",
            xaxis_title="Date",
            yaxis_title="Impact",
            template="plotly_dark",
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return dcc.Graph(figure=fig, id="events-timeline")

class AnalyticsWidget:
    """Widget d'analyse des événements"""
    
    def __init__(self):
        pass
    
    def create_impact_analysis(self, events: List[Dict]) -> html.Div:
        """Créer l'analyse d'impact des événements"""
        
        if not events:
            return html.Div()
        
        # Analyse par impact
        df = pd.DataFrame(events)
        
        # Graphique en secteurs par impact
        impact_counts = df['impact'].value_counts()
        
        impact_pie = go.Figure(data=[go.Pie(
            labels=impact_counts.index,
            values=impact_counts.values,
            marker_colors=['#dc3545', '#fd7e14', '#0dcaf0', '#198754']
        )])
        
        impact_pie.update_layout(
            title="Répartition par Impact",
            template="plotly_dark",
            height=250,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        # Graphique par pays
        country_counts = df['country'].value_counts()
        
        country_bar = go.Figure(data=[go.Bar(
            x=country_counts.index,
            y=country_counts.values,
            marker_color='#0dcaf0'
        )])
        
        country_bar.update_layout(
            title="Événements par Pays",
            template="plotly_dark",
            height=250,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return dbc.Row([
            dbc.Col([
                dcc.Graph(figure=impact_pie)
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=country_bar)
            ], width=6)
        ])
    
    def create_statistics_cards(self, events: List[Dict], calendar_data: Dict = None) -> html.Div:
        """Créer les cartes de statistiques"""
        
        total_events = len(events)
        critical_events = len([e for e in events if e['impact'] == 'critical'])
        upcoming_events = len([e for e in events if e['status'] == 'upcoming'])
        
        # Calcul des prochaines 24h
        now = datetime.now()
        next_24h = now + timedelta(hours=24)
        next_24h_events = len([
            e for e in events 
            if e['status'] == 'upcoming' and now <= e['datetime'] <= next_24h
        ])
        
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(total_events), className="text-primary"),
                        html.P("Total Événements", className="mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(critical_events), className="text-danger"),
                        html.P("Impact Critique", className="mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(upcoming_events), className="text-warning"),
                        html.P("À Venir", className="mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(next_24h_events), className="text-success"),
                        html.P("Prochaines 24h", className="mb-0")
                    ])
                ])
            ], width=3)
        ], className="mb-3")

# Instances des widgets
events_selection_widget = EventsSelectionWidget()
calendar_widget = CalendarWidget()
events_list_widget = EventsListWidget()
analytics_widget = AnalyticsWidget()