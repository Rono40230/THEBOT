"""
Modal pour la configuration des indicateurs techniques
Architecture basée sur price_alerts_modal.py pour assurer la cohérence
"""

import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional
from dash_modules.core.style_trading import trading_style_manager


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
                dbc.Row([
                    dbc.Col([
                        dbc.ModalTitle("📊 Configuration des Indicateurs", className="text-primary fw-bold")
                    ], width=6),
                    dbc.Col([
                        html.Div([
                            dbc.Label([
                                "🎯 Style Trading",
                                html.I(className="fas fa-question-circle ms-1", 
                                       id="style-trading-tooltip",
                                       style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                            ], className="fw-bold small"),
                            dbc.Tooltip([
                                "🎯 Choisissez votre style de trading", html.Br(),
                                "⚡ Auto-configure tous les indicateurs", html.Br(),
                                "📊 Paramètres optimisés par style", html.Br(),
                                "🎯 Manuel = contrôle total"
                            ], target="style-trading-tooltip", placement="bottom"),
                            dbc.Select(
                                id="indicators-trading-style",
                                options=[
                                    {"label": style_info, "value": style_key}
                                    for style_key, style_info in trading_style_manager.get_style_list().items()
                                ],
                                value="day_trading",
                                size="sm",
                                className="mt-1"
                            )
                        ])
                    ], width=4),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-question-circle me-1"), "Aide"],
                            id="indicators-help-btn",
                            color="info",
                            size="sm",
                            outline=True,
                            className="float-end"
                        )
                    ], width=2, className="text-end")
                ])
            ], close_button=True),
            
            # Zone d'aide contextuelle
            dbc.Collapse([
                dbc.Alert([
                    html.H6(["💡 Guide Rapide des Styles de Trading"], className="alert-heading"),
                    dbc.Row([
                        dbc.Col([
                            html.Strong("⚡ Scalping (1-5min)"), html.Br(),
                            "• Paramètres ultra-réactifs", html.Br(),
                            "• RSI 7 périodes, seuils 75/25", html.Br(),
                            "• Pivots journaliers essentiels", html.Br(),
                            "• ATR×1.0 pour stops serrés"
                        ], width=3),
                        dbc.Col([
                            html.Strong("🌅 Day Trading (15min-4h)"), html.Br(),
                            "• Configuration équilibrée", html.Br(),
                            "• RSI 14, seuils classiques 70/30", html.Br(),
                            "• Support/Résistance force 3", html.Br(),
                            "• ATR×2.0 stop optimal"
                        ], width=3),
                        dbc.Col([
                            html.Strong("📈 Swing Trading (4h-1D)"), html.Br(),
                            "• Signaux de qualité", html.Br(),
                            "• RSI 21, seuils ajustés 65/35", html.Br(),
                            "• Fibonacci très utile", html.Br(),
                            "• ATR×3.0 pour tendances"
                        ], width=3),
                        dbc.Col([
                            html.Strong("🏔️ Position Trading (1D+)"), html.Br(),
                            "• Indicateurs très stables", html.Br(),
                            "• RSI 30, seuils larges 60/40", html.Br(),
                            "• Niveaux historiques majeurs", html.Br(),
                            "• ATR×4.0 stops larges"
                        ], width=3)
                    ], className="mb-2"),
                    html.Hr(),
                    html.H6("🎯 Conseils d'Utilisation"),
                    dbc.Row([
                        dbc.Col([
                            html.Strong("📊 Moyennes Mobiles:"), html.Br(),
                            "• SMA = Tendance générale", html.Br(),
                            "• EMA = Signaux précoces", html.Br(),
                            "• Croisement = Signal d'entrée"
                        ], width=4),
                        dbc.Col([
                            html.Strong("📏 Niveaux:"), html.Br(),
                            "• Support = Zone d'achat", html.Br(),
                            "• Résistance = Zone de vente", html.Br(),
                            "• Fibonacci 61.8% = niveau clé"
                        ], width=4),
                        dbc.Col([
                            html.Strong("📉 Oscillateurs:"), html.Br(),
                            "• RSI > 70 = Survente", html.Br(),
                            "• RSI < 30 = Sous-achat", html.Br(),
                            "• ATR = Taille des stops"
                        ], width=4)
                    ]),
                    html.Hr(),
                    html.H6("💼 Exemples Concrets"),
                    dbc.Row([
                        dbc.Col([
                            html.Strong("🥇 Exemple Bitcoin:"), html.Br(),
                            "• Prix: 65000$ → 50000$ → ?", html.Br(),
                            "• Fib 61.8%: Rebond vers 59300$", html.Br(),
                            "• Support: 48000$ (3 touches)", html.Br(),
                            "• RSI 25: Zone d'achat"
                        ], width=6),
                        dbc.Col([
                            html.Strong("⚡ Stratégie Scalping:"), html.Br(),
                            "• Timeframe: 5min", html.Br(),
                            "• Entrée: Pivot + RSI inverse", html.Br(),
                            "• Stop: ATR×1.0 = 100$ sur BTC", html.Br(),
                            "• Target: R1 ou S1 selon direction"
                        ], width=6)
                    ])
                ], color="info", className="mb-3")
            ], id="indicators-help-collapse", is_open=False),
            
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
                        "💡 Exemple: BTC à 50000$ rebondit 3 fois = support fort", html.Br(),
                        "💼 Stratégie: Acheter près support, vendre près résistance"
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
                        dbc.Label([
                            "Force minimale",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sr-strength-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔢 Nombre minimum de contacts sur le niveau", html.Br(),
                            "⚡ Force 2-3: Niveaux faibles (scalping/day trading)", html.Br(),
                            "💪 Force 4-5: Niveaux modérés (swing trading)", html.Br(),
                            "🏔️ Force 6+: Niveaux majeurs (position trading)", html.Br(),
                            "💡 Plus la force est élevée, plus le niveau est fiable"
                        ], target="sr-strength-tooltip", placement="top"),
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
                        dbc.Label([
                            "Période d'analyse",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sr-lookback-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Nombre de bougies analysées pour détecter les niveaux", html.Br(),
                            "⚡ 20-50: Niveaux récents (scalping/day trading)", html.Br(),
                            "📈 50-100: Équilibre récent/historique (swing)", html.Br(),
                            "🏔️ 100-200: Niveaux historiques majeurs (position)", html.Br(),
                            "⚠️ Plus la période est longue, moins il y a de niveaux"
                        ], target="sr-lookback-tooltip", placement="top"),
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
                ], className="mt-2"),
                html.Hr(className="my-3"),
                html.H6("🎨 Configuration Visuelle", className="fw-bold text-primary"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Couleur Support",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sr-support-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🟢 Couleur des lignes de support", html.Br(),
                            "💡 Convention: Vert pour support", html.Br(),
                            "🎨 Choisissez une couleur contrastante"
                        ], target="sr-support-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-sr-support-color",
                            type="color",
                            value="#27AE60",
                            size="sm"
                        )
                    ], width=3),
                    dbc.Col([
                        dbc.Label([
                            "Couleur Résistance",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sr-resistance-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔴 Couleur des lignes de résistance", html.Br(),
                            "💡 Convention: Rouge pour résistance", html.Br(),
                            "🎨 Différenciez du support"
                        ], target="sr-resistance-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-sr-resistance-color",
                            type="color",
                            value="#E74C3C",
                            size="sm"
                        )
                    ], width=3),
                    dbc.Col([
                        dbc.Label([
                            "Style de ligne",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sr-line-style-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📏 Type de trait pour les lignes", html.Br(),
                            "━ Continu: Niveaux confirmés", html.Br(),
                            "┅ Pointillé: Niveaux en formation", html.Br(),
                            "╌ Tirets: Niveaux historiques"
                        ], target="sr-line-style-tooltip", placement="top"),
                        dbc.Select(
                            id="indicators-sr-line-style",
                            options=[
                                {"label": "━ Continu", "value": "solid"},
                                {"label": "┅ Pointillé", "value": "dot"},
                                {"label": "╌ Tirets", "value": "dash"}
                            ],
                            value="solid",
                            size="sm"
                        )
                    ], width=3),
                    dbc.Col([
                        dbc.Label([
                            "Épaisseur",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="sr-line-width-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📏 Épaisseur des lignes en pixels", html.Br(),
                            "1-2px: Discret, nombreux niveaux", html.Br(),
                            "3-4px: Visible, niveaux importants", html.Br(),
                            "5px: Très visible, niveaux majeurs"
                        ], target="sr-line-width-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-sr-line-width",
                            type="number",
                            value=2,
                            min=1,
                            max=5,
                            step=1,
                            size="sm"
                        )
                    ], width=3)
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
                        dbc.Label([
                            "Points de swing",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="fib-swing-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Période pour détecter les points hauts/bas", html.Br(),
                            "⚡ 5-15: Swings récents (scalping/day trading)", html.Br(),
                            "📈 20-30: Swings équilibrés (swing trading)", html.Br(),
                            "🏔️ 40-100: Swings majeurs (position trading)", html.Br(),
                            "💡 Plus petit = plus de retracements détectés"
                        ], target="fib-swing-tooltip", placement="top"),
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
                        dbc.Label([
                            "Niveaux de Fibonacci",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="fib-levels-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🌀 Niveaux mathématiques de Fibonacci", html.Br(),
                            "📊 23.6%: Premier niveau de retracement", html.Br(),
                            "📈 38.2%: Retracement modéré", html.Br(),
                            "⚖️ 50%: Niveau psychologique (non-Fibonacci)", html.Br(),
                            "🎯 61.8%: Nombre d'or, niveau le plus important", html.Br(),
                            "📉 78.6%: Retracement profond avant invalidation"
                        ], target="fib-levels-tooltip", placement="top"),
                        html.Small("23.6%, 38.2%, 50%, 61.8%, 78.6%", className="text-muted d-block")
                    ], width=6)
                ], className="mt-2"),
                html.Hr(className="my-3"),
                html.H6("🎨 Configuration Visuelle", className="fw-bold text-primary"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Style de ligne",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="fib-line-style-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📏 Style des lignes de retracement", html.Br(),
                            "┅ Pointillé: Style classique pour Fibonacci", html.Br(),
                            "╌ Tirets: Moins intrusif", html.Br(),
                            "━ Continu: Plus visible"
                        ], target="fib-line-style-tooltip", placement="top"),
                        dbc.Select(
                            id="indicators-fibonacci-line-style",
                            options=[
                                {"label": "┅ Pointillé", "value": "dot"},
                                {"label": "╌ Tirets", "value": "dash"},
                                {"label": "━ Continu", "value": "solid"}
                            ],
                            value="dash",
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Épaisseur",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="fib-line-width-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📏 Épaisseur des lignes Fibonacci", html.Br(),
                            "1px: Discret, nombreux niveaux", html.Br(),
                            "2px: Standard, bonne visibilité", html.Br(),
                            "3px: Emphase sur niveaux importants"
                        ], target="fib-line-width-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-fibonacci-line-width",
                            type="number",
                            value=1,
                            min=1,
                            max=3,
                            step=1,
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Transparence zones",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="fib-transparency-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🎨 Transparence des zones entre niveaux", html.Br(),
                            "0%: Transparent (lignes seulement)", html.Br(),
                            "20%: Légèrement visible", html.Br(),
                            "50%: Bien visible sans masquer le prix"
                        ], target="fib-transparency-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-fibonacci-transparency",
                            type="range",
                            min=0,
                            max=50,
                            step=10,
                            value=20,
                            className="form-range"
                        )
                    ], width=4)
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
                        "⚖️ Calcul: Pivot = (Haut + Bas + Clôture d'hier) / 3", html.Br(),
                        "📊 R1, R2, R3: Résistances au-dessus du pivot", html.Br(),
                        "🛡️ S1, S2, S3: Supports en-dessous du pivot", html.Br(),
                        "⏰ Utilité: Trading intraday et day trading", html.Br(),
                        "💡 Exemple: BTC pivot à 50k, R1 à 52k, S1 à 48k", html.Br(),
                        "💼 Stratégie: Vendre R1-R3, acheter S1-S3, pivot = direction",
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
                        dbc.Label([
                            "Méthode de calcul",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="pivot-method-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "⚖️ Formule de calcul des points pivots", html.Br(),
                            "📊 Standard: (H+L+C)/3 - Méthode classique", html.Br(),
                            "🌀 Fibonacci: Utilise les ratios de Fibonacci", html.Br(),
                            "🎯 Camarilla: Formule plus complexe, niveaux serrés", html.Br(),
                            "💼 Standard recommandé pour débuter"
                        ], target="pivot-method-tooltip", placement="top"),
                        dbc.Select(
                            id="indicators-pivot-method",
                            options=[
                                {"label": "📊 Standard", "value": "standard"},
                                {"label": "🌀 Fibonacci", "value": "fibonacci"},
                                {"label": "🎯 Camarilla", "value": "camarilla"}
                            ],
                            value="standard",
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label([
                            "Période de calcul",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="pivot-period-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "⏰ Période utilisée pour calculer les pivots", html.Br(),
                            "🌅 Journalier: Pour day trading et scalping", html.Br(),
                            "📈 Hebdomadaire: Pour swing trading", html.Br(),
                            "🏔️ Mensuel: Pour position trading", html.Br(),
                            "💡 Pivots journaliers = les plus utilisés"
                        ], target="pivot-period-tooltip", placement="top"),
                        dbc.Select(
                            id="indicators-pivot-period",
                            options=[
                                {"label": "🌅 Journalier", "value": "daily"},
                                {"label": "📈 Hebdomadaire", "value": "weekly"},
                                {"label": "🏔️ Mensuel", "value": "monthly"}
                            ],
                            value="daily",
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2"),
                html.Hr(className="my-3"),
                html.H6("🎨 Configuration Visuelle", className="fw-bold text-primary"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Couleur Pivot",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="pivot-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "⚖️ Couleur du niveau pivot principal", html.Br(),
                            "💡 Niveau central le plus important", html.Br(),
                            "🎨 Violet/bleu souvent utilisé"
                        ], target="pivot-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-pivot-color",
                            type="color",
                            value="#8E44AD",
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Couleur Résistances",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="pivot-resistance-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🔴 Couleur des résistances R1, R2, R3", html.Br(),
                            "📊 Niveaux au-dessus du pivot", html.Br(),
                            "💡 Rouge dégradé du clair au foncé"
                        ], target="pivot-resistance-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-pivot-resistance-color",
                            type="color",
                            value="#E74C3C",
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Couleur Supports",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="pivot-support-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🟢 Couleur des supports S1, S2, S3", html.Br(),
                            "📊 Niveaux en-dessous du pivot", html.Br(),
                            "💡 Vert dégradé du clair au foncé"
                        ], target="pivot-support-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-pivot-support-color",
                            type="color",
                            value="#27AE60",
                            size="sm"
                        )
                    ], width=4)
                ], className="mt-2"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Style de ligne",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="pivot-line-style-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📏 Style des lignes de pivots", html.Br(),
                            "━ Continu: Pivot principal", html.Br(),
                            "┅ Pointillé: Supports/résistances", html.Br(),
                            "╌ Tirets: Style alternatif"
                        ], target="pivot-line-style-tooltip", placement="top"),
                        dbc.Select(
                            id="indicators-pivot-line-style",
                            options=[
                                {"label": "━ Continu", "value": "solid"},
                                {"label": "┅ Pointillé", "value": "dot"},
                                {"label": "╌ Tirets", "value": "dash"}
                            ],
                            value="solid",
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label([
                            "Épaisseur",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="pivot-line-width-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📏 Épaisseur des lignes de pivots", html.Br(),
                            "1-2px: Standard pour day trading", html.Br(),
                            "3px: Plus visible pour swing trading", html.Br(),
                            "💡 Pivot principal plus épais que S/R"
                        ], target="pivot-line-width-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-pivot-line-width",
                            type="number",
                            value=2,
                            min=1,
                            max=4,
                            step=1,
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
        """Section MACD (Moving Average Convergence Divergence)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "MACD (Moving Average Convergence Divergence)",
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
                    html.P("Oscillateur de momentum avec ligne de signal", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-macd-switch",
                        value=True,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "EMA Rapide",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="macd-fast-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "⚡ EMA rapide pour calcul MACD", html.Br(),
                            "📊 Standard: 12 périodes", html.Br(),
                            "🔄 Plus court = plus réactif", html.Br(),
                            "📈 Trading intraday: 8-10", html.Br(),
                            "📉 Swing trading: 12-15"
                        ], target="macd-fast-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-macd-fast",
                            type="number",
                            value=12,
                            min=5,
                            max=50,
                            step=1,
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "EMA Lente",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="macd-slow-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🐌 EMA lente pour calcul MACD", html.Br(),
                            "📊 Standard: 26 périodes", html.Br(),
                            "📈 Doit être > EMA rapide", html.Br(),
                            "🔄 Plus long = moins de bruit", html.Br(),
                            "⚖️ Équilibre signal/stabilité"
                        ], target="macd-slow-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-macd-slow",
                            type="number",
                            value=26,
                            min=10,
                            max=100,
                            step=1,
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Signal",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="macd-signal-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📏 EMA de la ligne MACD", html.Br(),
                            "📊 Standard: 9 périodes", html.Br(),
                            "🎯 Crossover = signaux trading", html.Br(),
                            "⚡ Plus court = signaux précoces", html.Br(),
                            "🔄 Plus long = signaux confirmés"
                        ], target="macd-signal-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-macd-signal",
                            type="number",
                            value=9,
                            min=3,
                            max=30,
                            step=1,
                            size="sm"
                        )
                    ], width=4)
                ], className="mt-2"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Couleur MACD",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="macd-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🎨 Couleur de la ligne MACD", html.Br(),
                            "📊 Ligne principale de l'oscillateur", html.Br(),
                            "💡 Choisir couleur contrastante"
                        ], target="macd-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-macd-color",
                            type="color",
                            value="#2196F3",
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Couleur Signal",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="macd-signal-color-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "🎨 Couleur de la ligne de signal", html.Br(),
                            "� EMA du MACD pour crossovers", html.Br(),
                            "⚡ Souvent rouge ou orange"
                        ], target="macd-signal-color-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-macd-signal-color",
                            type="color",
                            value="#FF5722",
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Histogramme",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="macd-histogram-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Afficher l'histogramme MACD", html.Br(),
                            "📈 Vert: MACD > Signal", html.Br(),
                            "📉 Rouge: MACD < Signal", html.Br(),
                            "🎯 Montre la force du momentum"
                        ], target="macd-histogram-tooltip", placement="top"),
                        dbc.Switch(
                            id="indicators-macd-histogram",
                            value=True,
                            className="mt-2"
                        )
                    ], width=4)
                ], className="mt-2")
            ], id="indicators-macd-collapse", is_open=True)
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
         Output("indicators-atr-multiplier", "value", allow_duplicate=True),
         Output("indicators-macd-switch", "value", allow_duplicate=True),
         Output("indicators-macd-fast", "value", allow_duplicate=True),
         Output("indicators-macd-slow", "value", allow_duplicate=True),
         Output("indicators-macd-signal", "value", allow_duplicate=True),
         Output("indicators-macd-color", "value", allow_duplicate=True),
         Output("indicators-macd-signal-color", "value", allow_duplicate=True),
         Output("indicators-macd-histogram", "value", allow_duplicate=True)],
        [Input("indicators-reset-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def reset_indicators_config(reset_clicks):
        """Réinitialiser tous les indicateurs aux valeurs par défaut"""
        if reset_clicks:
            # Valeurs par défaut correspondant au crypto_module
            return (True, 20, True, 12, False, 3, False, 20, False, "standard", False, 14, 70, 30, False, 14, 2.0,
                   True, 12, 26, 9, "#2196F3", "#FF5722", True)  # MACD par défaut
        return (dash.no_update,) * 23  # Ajuster le nombre pour inclure MACD

    # Callback pour l'application automatique des styles de trading
    @app.callback(
        [Output("indicators-sma-switch", "value", allow_duplicate=True),
         Output("indicators-sma-period", "value", allow_duplicate=True),
         Output("indicators-sma-color", "value", allow_duplicate=True),
         Output("indicators-ema-switch", "value", allow_duplicate=True),
         Output("indicators-ema-period", "value", allow_duplicate=True),
         Output("indicators-ema-color", "value", allow_duplicate=True),
         Output("indicators-sr-switch", "value", allow_duplicate=True),
         Output("indicators-sr-strength", "value", allow_duplicate=True),
         Output("indicators-sr-lookback", "value", allow_duplicate=True),
         Output("indicators-sr-support-color", "value", allow_duplicate=True),
         Output("indicators-sr-resistance-color", "value", allow_duplicate=True),
         Output("indicators-sr-line-style", "value", allow_duplicate=True),
         Output("indicators-sr-line-width", "value", allow_duplicate=True),
         Output("indicators-fibonacci-switch", "value", allow_duplicate=True),
         Output("indicators-fibonacci-swing", "value", allow_duplicate=True),
         Output("indicators-fibonacci-line-style", "value", allow_duplicate=True),
         Output("indicators-fibonacci-line-width", "value", allow_duplicate=True),
         Output("indicators-fibonacci-transparency", "value", allow_duplicate=True),
         Output("indicators-pivot-switch", "value", allow_duplicate=True),
         Output("indicators-pivot-method", "value", allow_duplicate=True),
         Output("indicators-pivot-period", "value", allow_duplicate=True),
         Output("indicators-pivot-color", "value", allow_duplicate=True),
         Output("indicators-pivot-resistance-color", "value", allow_duplicate=True),
         Output("indicators-pivot-support-color", "value", allow_duplicate=True),
         Output("indicators-pivot-line-style", "value", allow_duplicate=True),
         Output("indicators-pivot-line-width", "value", allow_duplicate=True),
         Output("indicators-rsi-switch", "value", allow_duplicate=True),
         Output("indicators-rsi-period", "value", allow_duplicate=True),
         Output("indicators-rsi-overbought", "value", allow_duplicate=True),
         Output("indicators-rsi-oversold", "value", allow_duplicate=True),
         Output("indicators-atr-switch", "value", allow_duplicate=True),
         Output("indicators-atr-period", "value", allow_duplicate=True),
         Output("indicators-atr-multiplier", "value", allow_duplicate=True),
         Output("indicators-macd-switch", "value", allow_duplicate=True),
         Output("indicators-macd-fast", "value", allow_duplicate=True),
         Output("indicators-macd-slow", "value", allow_duplicate=True),
         Output("indicators-macd-signal", "value", allow_duplicate=True),
         Output("indicators-macd-color", "value", allow_duplicate=True),
         Output("indicators-macd-signal-color", "value", allow_duplicate=True),
         Output("indicators-macd-histogram", "value", allow_duplicate=True)],
        [Input("indicators-trading-style", "value")],
        prevent_initial_call=True
    )
    def apply_trading_style(selected_style):
        """Applique automatiquement les paramètres selon le style de trading choisi"""
        if not selected_style or selected_style == "manuel":
            # Style manuel - ne change rien
            return tuple([dash.no_update] * 40)  # Ajusté pour inclure MACD (7 paramètres)
        
        try:
            # Récupère la configuration pour ce style
            config = trading_style_manager.get_style_config(selected_style)
            
            # SMA
            sma_config = config.get('sma', {})
            sma_enabled = sma_config.enabled
            sma_period = sma_config.parameters.get('period', 20)
            sma_color = sma_config.parameters.get('color', '#2E86C1')
            
            # EMA  
            ema_config = config.get('ema', {})
            ema_enabled = ema_config.enabled
            ema_period = ema_config.parameters.get('period', 12)
            ema_color = ema_config.parameters.get('color', '#E74C3C')
            
            # Support/Resistance
            sr_config = config.get('support_resistance', {})
            sr_enabled = sr_config.enabled
            sr_strength = sr_config.parameters.get('strength', 3)
            sr_lookback = sr_config.parameters.get('lookback', 50)
            sr_support_color = sr_config.visual.get('support_color', '#27AE60')
            sr_resistance_color = sr_config.visual.get('resistance_color', '#E74C3C')
            sr_line_style = sr_config.visual.get('line_style', 'solid')
            sr_line_width = sr_config.visual.get('line_width', 2)
            
            # Fibonacci
            fib_config = config.get('fibonacci', {})
            fib_enabled = fib_config.enabled
            fib_swing = fib_config.parameters.get('swing_points', 20)
            fib_line_style = fib_config.visual.get('line_style', 'dash')
            fib_line_width = fib_config.visual.get('line_width', 1)
            fib_transparency = 20  # Valeur par défaut
            
            # Pivot Points
            pivot_config = config.get('pivot_points', {})
            pivot_enabled = pivot_config.enabled
            pivot_method = pivot_config.parameters.get('method', 'standard')
            pivot_period = pivot_config.parameters.get('period', 'daily')
            pivot_color = pivot_config.visual.get('pivot_color', '#8E44AD')
            pivot_resistance_color = pivot_config.visual.get('resistance_colors', ['#E74C3C'])[0]
            pivot_support_color = pivot_config.visual.get('support_colors', ['#27AE60'])[0]
            pivot_line_style = pivot_config.visual.get('line_style', 'solid')
            pivot_line_width = pivot_config.visual.get('line_width', 2)
            
            # RSI
            rsi_config = config.get('rsi', {})
            rsi_enabled = rsi_config.enabled
            rsi_period = rsi_config.parameters.get('period', 14)
            rsi_overbought = rsi_config.parameters.get('overbought', 70)
            rsi_oversold = rsi_config.parameters.get('oversold', 30)
            
            # ATR
            atr_config = config.get('atr', {})
            atr_enabled = atr_config.enabled
            atr_period = atr_config.parameters.get('period', 14)
            atr_multiplier = atr_config.parameters.get('multiplier', 2.0)
            
            # MACD
            macd_config = config.get('macd', {})
            macd_enabled = macd_config.enabled
            macd_fast = macd_config.parameters.get('fast', 12)
            macd_slow = macd_config.parameters.get('slow', 26)
            macd_signal = macd_config.parameters.get('signal', 9)
            macd_color = macd_config.visual.get('macd_color', '#2196F3')
            macd_signal_color = macd_config.visual.get('signal_color', '#FF5722')
            macd_histogram = macd_config.visual.get('histogram', True)
            
            return (
                sma_enabled, sma_period, sma_color,
                ema_enabled, ema_period, ema_color,
                sr_enabled, sr_strength, sr_lookback, sr_support_color, sr_resistance_color, sr_line_style, sr_line_width,
                fib_enabled, fib_swing, fib_line_style, fib_line_width, fib_transparency,
                pivot_enabled, pivot_method, pivot_period, pivot_color, pivot_resistance_color, pivot_support_color, pivot_line_style, pivot_line_width,
                rsi_enabled, rsi_period, rsi_overbought, rsi_oversold,
                atr_enabled, atr_period, atr_multiplier,
                macd_enabled, macd_fast, macd_slow, macd_signal, macd_color, macd_signal_color, macd_histogram
            )
            
        except Exception as e:
            print(f"Erreur lors de l'application du style {selected_style}: {e}")
            # En cas d'erreur, retourne les valeurs par défaut day trading
            return (
                True, 20, '#2E86C1',  # SMA
                True, 12, '#E74C3C',  # EMA  
                True, 3, 50, '#27AE60', '#E74C3C', 'solid', 2,  # Support/Resistance
                True, 20, 'dash', 1, 20,  # Fibonacci
                True, 'standard', 'daily', '#8E44AD', '#E74C3C', '#27AE60', 'solid', 2,  # Pivot
                True, 14, 70, 30,  # RSI
                True, 14, 2.0,  # ATR
                True, 12, 26, 9, '#2196F3', '#FF5722', True  # MACD
            )
    
    # Callback pour le bouton d'aide
    @app.callback(
        Output("indicators-help-collapse", "is_open"),
        [Input("indicators-help-btn", "n_clicks")],
        [State("indicators-help-collapse", "is_open")],
        prevent_initial_call=True
    )
    def toggle_help(n_clicks, is_open):
        """Afficher/masquer l'aide contextuelle"""
        if n_clicks:
            return not is_open
        return is_open
# Store pour sauvegarder la configuration des indicateurs
indicators_store = dcc.Store(id='indicators-config-store', data=indicators_modal.indicators_config)