"""
Modal pour la configuration des indicateurs techniques
Architecture basée sur price_alerts_modal.py pour assurer la cohérence
"""

import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional


class IndicatorsModal:
    """Modal pour configurer tous les indicateurs techniques"""
    
    def __init__(self):
        self.modal_id = "indicators-modal"
        self.indicators_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut des indicateurs"""
        return {
            # Moyennes mobiles
            'sma': {
                'enabled': True,
                'period': 20,
                'color': '#2E86C1'
            },
            'ema': {
                'enabled': True, 
                'period': 12,
                'color': '#E74C3C'
            },
            
            # Niveaux structurels
            'support_resistance': {
                'enabled': False,
                'strength': 3,
                'lookback': 50
            },
            'fibonacci': {
                'enabled': False,
                'swing_points': 20,
                'levels': [0.236, 0.382, 0.5, 0.618, 0.786]
            },
            'pivot_points': {
                'enabled': False,
                'method': 'standard',
                'period': 'daily'
            },
            
            # Oscillateurs
            'rsi': {
                'enabled': True,
                'period': 14,
                'overbought': 70,
                'oversold': 30
            },
            'atr': {
                'enabled': True,
                'period': 14,
                'multiplier': 2.0
            },
            'macd': {
                'enabled': False,
                'fast': 12,
                'slow': 26,
                'signal': 9
            }
        }
    
    def create_modal(self) -> dbc.Modal:
        """Créer la modal des indicateurs"""
        return dbc.Modal([
            dbc.ModalHeader([
                html.H4([
                    html.I(className="fas fa-chart-line me-2"),
                    "Configuration des Indicateurs Techniques"
                ], className="mb-0")
            ]),
            
            dbc.ModalBody([
                # Onglets pour organiser les indicateurs
                dbc.Tabs([
                    
                    # Onglet Moyennes Mobiles
                    dbc.Tab(label="📈 Moyennes Mobiles", tab_id="moving-averages", children=[
                        html.Div([
                            self._create_sma_section(),
                            html.Hr(),
                            self._create_ema_section()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Niveaux Structurels
                    dbc.Tab(label="📊 Niveaux", tab_id="levels", children=[
                        html.Div([
                            self._create_sr_section(),
                            html.Hr(),
                            self._create_fibonacci_section(),
                            html.Hr(),
                            self._create_pivot_section()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Oscillateurs
                    dbc.Tab(label="📉 Oscillateurs", tab_id="oscillators", children=[
                        html.Div([
                            self._create_rsi_section(),
                            html.Hr(),
                            self._create_atr_section(),
                            html.Hr(),
                            self._create_macd_section()
                        ], className="p-3")
                    ])
                    
                ], id="indicators-tabs", active_tab="moving-averages")
            ]),
            
            dbc.ModalFooter([
                html.Div([
                    html.I(className="fas fa-bolt text-success me-2"),
                    html.Small("Mise à jour instantanée activée", className="text-success")
                ], className="me-auto"),
                dbc.Button(
                    "Réinitialiser",
                    id="indicators-reset-btn",
                    color="secondary",
                    outline=True,
                    className="me-2"
                ),
                dbc.Button(
                    "Fermer",
                    id="indicators-close-btn",
                    color="primary"
                )
            ])
            
        ], id=self.modal_id, size="lg", is_open=False, backdrop=True, scrollable=True)
    
    def _create_sma_section(self) -> html.Div:
        """Section SMA (Simple Moving Average)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Simple Moving Average (SMA)",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="sma-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("SMA - Moyenne Mobile Simple"), html.Br(),
                        "📊 Calcule la moyenne des prix sur une période donnée", html.Br(),
                        "🎯 Utilité: Identifier la tendance générale", html.Br(),
                        "📈 Signal: Prix > SMA = tendance haussière", html.Br(),
                        "📉 Signal: Prix < SMA = tendance baissière", html.Br(),
                        "⚖️ Avantage: Lisse les fluctuations du marché"
                    ], target="sma-tooltip-target", placement="right"),
                    html.P("Moyenne mobile simple pour identifier les tendances", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-sma-switch",
                        value=True,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Période",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sma-period-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔢 Nombre de périodes pour le calcul", html.Br(),
                            "📊 Période courte (5-10): Plus réactive, plus de signaux", html.Br(),
                            "📈 Période moyenne (20-50): Équilibre signal/bruit", html.Br(),
                            "📉 Période longue (100-200): Tendance de fond, moins de bruit", html.Br(),
                            "⚖️ Valeur standard: 20 périodes"
                        ], target="sma-period-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-sma-period",
                            type="number",
                            value=20,
                            min=1,
                            max=200,
                            step=1,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label([
                            "Couleur",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sma-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🎨 Couleur d'affichage de la ligne SMA", html.Br(),
                            "📊 Choisissez une couleur contrastante", html.Br(),
                            "💡 Évitez les couleurs trop proches des chandeliers"
                        ], target="sma-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-sma-color",
                            type="color",
                            value="#2E86C1",
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-sma-collapse", is_open=True)
        ])
    
    def _create_ema_section(self) -> html.Div:
        """Section EMA (Exponential Moving Average)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Exponential Moving Average (EMA)",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="ema-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("EMA - Moyenne Mobile Exponentielle"), html.Br(),
                        "📊 Donne plus de poids aux prix récents", html.Br(),
                        "🎯 Utilité: Réaction plus rapide aux changements", html.Br(),
                        "⚡ Avantage: Plus réactive que la SMA", html.Br(),
                        "📈 Trading: Signaux plus précoces", html.Br(),
                        "🔄 Période courte = plus de signaux mais plus de bruit"
                    ], target="ema-tooltip-target", placement="right"),
                    html.P("Moyenne mobile exponentielle, plus réactive aux changements récents", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-ema-switch",
                        value=True,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Période",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="ema-period-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔢 Nombre de périodes pour l'EMA", html.Br(),
                            "⚡ EMA courte (5-12): Très réactive, nombreux signaux", html.Br(),
                            "📈 EMA moyenne (20-50): Bon compromis réactivité/stabilité", html.Br(),
                            "📉 EMA longue (100-200): Tendance principale", html.Br(),
                            "💼 Trading: EMA 12 et 26 (MACD), EMA 20 et 50 (crossover)"
                        ], target="ema-period-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-ema-period",
                            type="number",
                            value=12,
                            min=1,
                            max=200,
                            step=1,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label([
                            "Couleur",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="ema-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🎨 Couleur d'affichage de la ligne EMA", html.Br(),
                            "📊 Différenciez de la SMA avec une couleur distincte", html.Br(),
                            "💡 Rouge/orange pour EMA, bleu pour SMA (convention)"
                        ], target="ema-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-ema-color",
                            type="color",
                            value="#E74C3C",
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-ema-collapse", is_open=True)
        ])
    
    def _create_sr_section(self) -> html.Div:
        """Section Support/Résistance"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Support et Résistance",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="sr-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("Support & Résistance"), html.Br(),
                        "🛡️ Support: Niveau où le prix rebondit vers le haut", html.Br(),
                        "⚔️ Résistance: Niveau où le prix rebondit vers le bas", html.Br(),
                        "📊 Utilité: Points d'entrée/sortie stratégiques", html.Br(),
                        "🎯 Force: Plus de contacts = niveau plus fort", html.Br(),
                        "💡 Trading: Acheter près du support, vendre près de la résistance"
                    ], target="sr-tooltip-target", placement="right"),
                    html.P("Niveaux de prix clés basés sur l'historique", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-sr-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Force minimale", className="fw-bold"),
                        dbc.Input(
                            id="indicators-sr-strength",
                            type="number",
                            value=3,
                            min=1,
                            max=10,
                            step=1,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Période d'analyse", className="fw-bold"),
                        dbc.Input(
                            id="indicators-sr-lookback",
                            type="number",
                            value=50,
                            min=10,
                            max=200,
                            step=10,
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-sr-collapse", is_open=False)
        ])
    
    def _create_fibonacci_section(self) -> html.Div:
        """Section Fibonacci"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Retracements de Fibonacci",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="fib-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("Fibonacci - Retracements"), html.Br(),
                        "🌀 Basé sur la séquence mathématique de Fibonacci", html.Br(),
                        "📏 Niveaux: 23.6%, 38.2%, 50%, 61.8%, 78.6%", html.Br(),
                        "🎯 Utilité: Prédire les niveaux de retracement", html.Br(),
                        "📈 61.8% = Niveau d'or (golden ratio)", html.Br(),
                        "💼 Trading: Zones de rebond potentiel"
                    ], target="fib-tooltip-target", placement="right"),
                    html.P("Niveaux de retracement basés sur la séquence de Fibonacci", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-fibonacci-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Points de swing", className="fw-bold"),
                        dbc.Input(
                            id="indicators-fibonacci-swing",
                            type="number",
                            value=20,
                            min=5,
                            max=100,
                            step=5,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Niveaux", className="fw-bold"),
                        html.Small("23.6%, 38.2%, 50%, 61.8%, 78.6%", className="text-muted d-block")
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-fibonacci-collapse", is_open=False)
        ])
    
    def _create_pivot_section(self) -> html.Div:
        """Section Points Pivots"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Points Pivots",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="pivot-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("Points Pivots - Niveaux Intraday"), html.Br(),
                        "⚖️ Calculés: (Haut + Bas + Clôture) / 3", html.Br(),
                        "📊 R1, R2, R3: Résistances au-dessus du pivot", html.Br(),
                        "🛡️ S1, S2, S3: Supports en-dessous du pivot", html.Br(),
                        "⏰ Utilité: Trading intraday et day trading", html.Br(),
                        "🎯 Très populaire chez les traders professionnels"
                    ], target="pivot-tooltip-target", placement="right"),
                    html.P("Niveaux calculés à partir des prix de la session précédente", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-pivot-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Méthode", className="fw-bold"),
                        dbc.Select(
                            id="indicators-pivot-method",
                            options=[
                                {"label": "Standard", "value": "standard"},
                                {"label": "Fibonacci", "value": "fibonacci"},
                                {"label": "Camarilla", "value": "camarilla"}
                            ],
                            value="standard",
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Période", className="fw-bold"),
                        dbc.Select(
                            id="indicators-pivot-period",
                            options=[
                                {"label": "Journalier", "value": "daily"},
                                {"label": "Hebdomadaire", "value": "weekly"},
                                {"label": "Mensuel", "value": "monthly"}
                            ],
                            value="daily",
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-pivot-collapse", is_open=False)
        ])
    
    def _create_rsi_section(self) -> html.Div:
        """Section RSI (Relative Strength Index)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "RSI (Relative Strength Index)",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="rsi-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("RSI - Oscillateur de Force Relative"), html.Br(),
                        "📊 Mesure: Vitesse et amplitude des changements de prix", html.Br(),
                        "📈 Échelle: 0 à 100", html.Br(),
                        "🟢 > 70: Zone de survente (vendre)", html.Br(),
                        "🔴 < 30: Zone de sous-achat (acheter)", html.Br(),
                        "⏰ Période standard: 14 sessions", html.Br(),
                        "🎯 Très fiable pour détecter les retournements"
                    ], target="rsi-tooltip-target", placement="right"),
                    html.P("Oscillateur de momentum (14 périodes par défaut)", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-rsi-switch",
                        value=True,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Période",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="rsi-period-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔢 Nombre de périodes pour calculer le RSI", html.Br(),
                            "⚡ RSI court (7-10): Très sensible, plus de signaux", html.Br(),
                            "🎯 RSI standard (14): Équilibre optimal", html.Br(),
                            "📉 RSI long (21-25): Moins de faux signaux", html.Br(),
                            "💼 Wilder a créé le RSI avec 14 périodes"
                        ], target="rsi-period-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-rsi-period",
                            type="number",
                            value=14,
                            min=2,
                            max=50,
                            step=1,
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Survente",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="rsi-overbought-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🟢 Niveau de survente (signal de vente)", html.Br(),
                            "📊 RSI > 70: Marché possiblement survendu", html.Br(),
                            "📉 Signal: Considérer une vente ou attendre correction", html.Br(),
                            "⚠️ Attention: En tendance forte, RSI peut rester > 70", html.Br(),
                            "🎯 Ajustement: 80 pour marchés très volatils"
                        ], target="rsi-overbought-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-rsi-overbought",
                            type="number",
                            value=70,
                            min=50,
                            max=90,
                            step=5,
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Sous-achat",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="rsi-oversold-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔴 Niveau de sous-achat (signal d'achat)", html.Br(),
                            "📊 RSI < 30: Marché possiblement sous-acheté", html.Br(),
                            "📈 Signal: Opportunité d'achat potentielle", html.Br(),
                            "⚠️ Attention: En tendance baisse, RSI peut rester < 30", html.Br(),
                            "🎯 Ajustement: 20 pour marchés très volatils"
                        ], target="rsi-oversold-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-rsi-oversold",
                            type="number",
                            value=30,
                            min=10,
                            max=50,
                            step=5,
                            size="sm"
                        )
                    ], width=4)
                ], className="mt-2")
            ], id="indicators-rsi-collapse", is_open=True)
        ])

    def _create_atr_section(self) -> html.Div:
        """Section ATR (Average True Range)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "ATR (Average True Range)",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="atr-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("ATR - Moyenne de la Vraie Amplitude"), html.Br(),
                        "📊 Mesure: Volatilité moyenne du marché", html.Br(),
                        "📈 Utilité: Définir stops et objectifs", html.Br(),
                        "🎯 Plus l'ATR est élevé = plus volatil", html.Br(),
                        "⚡ Trading: Ajuster taille positions selon volatilité", html.Br(),
                        "📉 Période standard: 14 sessions", html.Br(),
                        "🔢 Multiplier: Pour calculer stops (ATR x 2)"
                    ], target="atr-tooltip-target", placement="right"),
                    html.P("Indicateur de volatilité pour ajuster le risk management", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-atr-switch",
                        value=True,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Période",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="atr-period-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔢 Nombre de périodes pour calculer l'ATR", html.Br(),
                            "📊 ATR court (7-10): Volatité à court terme", html.Br(),
                            "🎯 ATR standard (14): Équilibre optimal", html.Br(),
                            "📉 ATR long (20-30): Volatité de fond", html.Br(),
                            "💼 Utile pour: Position sizing, stop loss, take profit"
                        ], target="atr-period-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-atr-period",
                            type="number",
                            value=14,
                            min=5,
                            max=50,
                            step=1,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label([
                            "Multiplier (Stop Loss)",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="atr-multiplier-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔢 Multiplicateur pour le stop loss basé sur l'ATR", html.Br(),
                            "🛡️ Stop Loss = Prix d'entrée ± (ATR × Multiplier)", html.Br(),
                            "📊 1.0-1.5: Stop serré (day trading)", html.Br(),
                            "🎯 2.0-2.5: Équilibre risque/profit", html.Br(),
                            "📉 3.0+: Stop large (swing trading)", html.Br(),
                            "💼 Plus le multiplier est élevé, moins de faux signaux"
                        ], target="atr-multiplier-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-atr-multiplier",
                            type="number",
                            value=2.0,
                            min=0.5,
                            max=5.0,
                            step=0.5,
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-atr-collapse", is_open=True)
        ])
    
    def _create_macd_section(self) -> html.Div:
        """Section MACD (pour futures extensions)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "MACD",
                        html.I(className="fas fa-info-circle ms-2", 
                               id="macd-tooltip-target",
                               style={"color": "#17a2b8", "cursor": "pointer"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        html.Strong("MACD - Convergence/Divergence des Moyennes"), html.Br(),
                        "📊 Calcul: EMA(12) - EMA(26)", html.Br(),
                        "📏 Ligne de signal: EMA(9) du MACD", html.Br(),
                        "📈 Crossover positif: Signal d'achat", html.Br(),
                        "📉 Crossover négatif: Signal de vente", html.Br(),
                        "📊 Histogramme: MACD - Signal", html.Br(),
                        "🎯 Excellent pour détecter les changements de tendance"
                    ], target="macd-tooltip-target", placement="right"),
                    html.P("Moving Average Convergence Divergence", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-macd-switch",
                        value=False,
                        disabled=True,  # Désactivé pour l'instant
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            html.Small("🚧 Fonctionnalité en développement", className="text-warning")
        ])
    
    def get_custom_css(self) -> str:
        """CSS personnalisé pour la modal des indicateurs"""
        return """
        /* Modal Indicateurs */
        #indicators-modal .modal-dialog {
            max-width: 800px;
        }
        
        #indicators-modal .modal-body {
            max-height: 70vh;
            overflow-y: auto;
        }
        
        /* Onglets */
        #indicators-tabs .nav-link {
            border: none;
            border-bottom: 2px solid transparent;
            background: none !important;
            color: #6c757d !important;
            font-weight: 500;
        }
        
        #indicators-tabs .nav-link.active {
            border-bottom-color: #007bff !important;
            color: #007bff !important;
            background: none !important;
        }
        
        /* Sections d'indicateurs */
        .indicators-section {
            border: 1px solid #e9ecef;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #f8f9fa;
        }
        
        /* Switches */
        .form-switch .form-check-input {
            width: 3rem;
            height: 1.5rem;
        }
        
        /* Collapse animations */
        .collapse {
            transition: height 0.3s ease;
        }
        
        /* Inputs couleur */
        input[type="color"] {
            border: 1px solid #ced4da;
            border-radius: 0.375rem;
            width: 100%;
            height: 38px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            #indicators-modal .modal-dialog {
                max-width: 95%;
                margin: 1rem auto;
            }
        }
        """


# Instance globale
indicators_modal = IndicatorsModal()


def register_indicators_modal_callbacks(app):
    """Enregistrer les callbacks pour la modal des indicateurs"""
    
    # Callback pour ouvrir/fermer la modal
    @app.callback(
        Output("indicators-modal", "is_open"),
        [Input("manage-indicators-btn", "n_clicks"),
         Input("indicators-close-btn", "n_clicks")],
        [State("indicators-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_indicators_modal(open_clicks, close_clicks, is_open):
        """Gérer l'ouverture/fermeture de la modal"""
        ctx = callback_context
        if not ctx.triggered:
            return False
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "manage-indicators-btn":
            return True
        elif button_id == "indicators-close-btn":
            return False
        
        return is_open
    
    # Callbacks pour les collapses des sections
    collapse_callbacks = [
        ("indicators-sma-switch", "indicators-sma-collapse"),
        ("indicators-ema-switch", "indicators-ema-collapse"),
        ("indicators-sr-switch", "indicators-sr-collapse"),
        ("indicators-fibonacci-switch", "indicators-fibonacci-collapse"),
        ("indicators-pivot-switch", "indicators-pivot-collapse"),
        ("indicators-rsi-switch", "indicators-rsi-collapse"),
        ("indicators-atr-switch", "indicators-atr-collapse")
    ]
    
    for switch_id, collapse_id in collapse_callbacks:
        @app.callback(
            Output(collapse_id, "is_open"),
            [Input(switch_id, "value")],
            prevent_initial_call=True
        )
        def toggle_collapse(enabled):
            """Ouvrir/fermer la section quand l'indicateur est activé/désactivé"""
            return enabled
    
    # Callback principal pour synchronisation INSTANTANÉE avec le graphique
    # Note: Cette version ne renvoie rien car les IDs crypto-xxx n'existent plus
    # La synchronisation se fait directement via les inputs du callback du graphique
    @app.callback(
        Output('indicators-config-store', 'data'),
        [Input("indicators-sma-switch", "value"),
         Input("indicators-sma-period", "value"),
         Input("indicators-ema-switch", "value"),
         Input("indicators-ema-period", "value"),
         Input("indicators-sr-switch", "value"),
         Input("indicators-sr-strength", "value"),
         Input("indicators-fibonacci-switch", "value"),
         Input("indicators-fibonacci-swing", "value"),
         Input("indicators-pivot-switch", "value"),
         Input("indicators-pivot-method", "value"),
         Input("indicators-rsi-switch", "value"),
         Input("indicators-rsi-period", "value"),
         Input("indicators-rsi-overbought", "value"),
         Input("indicators-rsi-oversold", "value"),
         Input("indicators-atr-switch", "value"),
         Input("indicators-atr-period", "value"),
         Input("indicators-atr-multiplier", "value")],
        prevent_initial_call=True
    )
    def store_indicators_config(sma_enabled, sma_period, ema_enabled, ema_period,
                               sr_enabled, sr_strength, fib_enabled, fib_swing, 
                               pivot_enabled, pivot_method, rsi_enabled, rsi_period, 
                               rsi_overbought, rsi_oversold, atr_enabled, atr_period, atr_multiplier):
        """Stocker la configuration des indicateurs pour persistance"""
        return {
            'sma': {'enabled': sma_enabled, 'period': sma_period},
            'ema': {'enabled': ema_enabled, 'period': ema_period},
            'sr': {'enabled': sr_enabled, 'strength': sr_strength},
            'fibonacci': {'enabled': fib_enabled, 'swing': fib_swing},
            'pivot': {'enabled': pivot_enabled, 'method': pivot_method},
            'rsi': {'enabled': rsi_enabled, 'period': rsi_period, 'overbought': rsi_overbought, 'oversold': rsi_oversold},
            'atr': {'enabled': atr_enabled, 'period': atr_period, 'multiplier': atr_multiplier}
        }

    # Callback pour réinitialiser les indicateurs
    @app.callback(
        [Output("indicators-sma-switch", "value", allow_duplicate=True),
         Output("indicators-sma-period", "value", allow_duplicate=True),
         Output("indicators-ema-switch", "value", allow_duplicate=True),
         Output("indicators-ema-period", "value", allow_duplicate=True),
         Output("indicators-sr-switch", "value", allow_duplicate=True),
         Output("indicators-sr-strength", "value", allow_duplicate=True),
         Output("indicators-fibonacci-switch", "value", allow_duplicate=True),
         Output("indicators-fibonacci-swing", "value", allow_duplicate=True),
         Output("indicators-pivot-switch", "value", allow_duplicate=True),
         Output("indicators-pivot-method", "value", allow_duplicate=True),
         Output("indicators-rsi-switch", "value", allow_duplicate=True),
         Output("indicators-rsi-period", "value", allow_duplicate=True),
         Output("indicators-rsi-overbought", "value", allow_duplicate=True),
         Output("indicators-rsi-oversold", "value", allow_duplicate=True),
         Output("indicators-atr-switch", "value", allow_duplicate=True),
         Output("indicators-atr-period", "value", allow_duplicate=True),
         Output("indicators-atr-multiplier", "value", allow_duplicate=True)],
        [Input("indicators-reset-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def reset_indicators_config(reset_clicks):
        """Réinitialiser tous les indicateurs aux valeurs par défaut"""
        if reset_clicks:
            # Valeurs par défaut correspondant au crypto_module
            return True, 20, True, 12, False, 3, False, 20, False, "standard", False, 14, 70, 30, False, 14, 2.0
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Store pour sauvegarder la configuration des indicateurs
indicators_store = dcc.Store(id='indicators-config-store', data=indicators_modal.indicators_config)