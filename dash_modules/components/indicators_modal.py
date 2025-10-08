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
            },
            
            # Momentum Indicators (Phase 2)
            'squeeze_momentum': {
                'enabled': False,
                'bb_period': 20,
                'bb_deviation': 2.0,
                'kc_period': 20,
                'kc_atr_period': 10,
                'kc_multiplier': 1.5,
                'momentum_period': 12,
                'momentum_ma_period': 6,
                'squeeze_alert': True,
                'momentum_alert': True,
                'min_squeeze_bars': 3,
                'trading_style': 'day_trading'
            },
            'candle_patterns': {
                'enabled': False,
                'doji_threshold': 0.1,
                'hammer_ratio': 2.0,
                'body_size_min': 0.02,
                'engulfing_body_ratio': 1.0,
                'engulfing_volume_confirm': True,
                'show_labels': True,
                'show_stats': True,
                'max_patterns': 8,
                'trading_style': 'day_trading'
            },
            'breakout_detector': {
                'enabled': False,
                'sr_period': 20,
                'sr_strength': 2,
                'price_precision': 4,
                'volume_threshold': 0.5,
                'volume_ma_period': 10,
                'breakout_threshold': 0.03,
                'confirmation_bars': 2,
                'max_age_levels': 50,
                'trading_style': 'day_trading'
            },
            
            # Volume Analysis (Phase 4)
            'volume_profile': {
                'enabled': False,
                'profile_type': 'session',
                'bins_count': 100,
                'lookback_periods': 100,
                'value_area_percent': 70.0,
                'poc_sensitivity': 1.0,
                'high_volume_threshold': 80.0,
                'low_volume_threshold': 20.0,
                'support_resistance_strength': 1.0,
                'show_poc': True,
                'show_value_area': True,
                'show_high_volume_nodes': True,
                'show_low_volume_nodes': False,
                'show_volume_histogram': True,
                'enable_poc_alerts': True,
                'enable_value_area_alerts': True,
                'poc_proximity_percent': 0.5,
                'value_area_break_alert': True,
                'histogram_opacity': 60,
                'value_area_opacity': 20,
                'trading_style': 'day_trading'
            },
            
            # Smart Money Analysis
            'fair_value_gaps': {
                'enabled': False,
                'gap_threshold': 0.1,
                'volume_confirmation': True,
                'max_gap_age': 50,
                'min_gap_size': 0.05,
                'trading_style': 'day_trading',
                'show_gap_labels': True,
                'gap_opacity': 30,
                # Paramètres avancés
                'volume_multiplier': 1.5,
                'immediate_fill_threshold': 0.3,
                'confluence_detection': True,
                'confluence_distance': 0.5,
                'structural_break_confirmation': False,
                'price_action_filter': False,
                'retest_sensitivity': 0.1,
                'max_retest_count': 3,
                'session_filter': True,
                'news_filter': False,
                'weekend_gaps': True,
                'dynamic_opacity': True,
                'strength_line_width': True,
                'show_distance_to_price': True,
                'max_gaps_display': 20,
                'auto_alerts': False,
                'alert_distance': 0.2,
                'rsi_confirmation': False,
                'fibonacci_levels': True
            },
            'order_blocks': {
                'enabled': False,
                'trading_style': 'day_trading',
                # Paramètres de base
                'lookback_period': 20,
                'min_volume_ratio': 1.5,
                'strength_threshold': 0.6,
                'impulse_threshold': 1.5,
                'min_block_size': 0.2,
                'max_block_age': 100,
                # Détection avancée
                'volume_confirmation': True,
                'structure_validation': True,
                'imbalance_detection': True,
                'retest_validation': True,
                'session_filter': False,
                'trend_alignment': False,
                # Visualisation
                'show_labels': True,
                'show_strength': True,
                'show_retest_count': True,
                'bullish_color': '#2E8B57',
                'bearish_color': '#DC143C',
                'opacity_active': 30,
                'opacity_tested': 20,
                'max_blocks_display': 15,
                # Signaux et alertes
                'signal_generation': True,
                'proximity_alerts': False,
                'alert_distance': 0.1,
                'confluence_with_fvg': False,
                'fibonacci_confluence': False
            },
            'liquidity_zones': {
                'enabled': False,
                'zone_strength': 3,
                'time_sensitivity': 'medium',
                'volume_confirmation': True
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
                        ], width=3),
                        dbc.Col([
                            html.Strong("📏 Niveaux:"), html.Br(),
                            "• Support = Zone d'achat", html.Br(),
                            "• Résistance = Zone de vente", html.Br(),
                            "• Fibonacci 61.8% = niveau clé"
                        ], width=3),
                        dbc.Col([
                            html.Strong("📉 Oscillateurs:"), html.Br(),
                            "• RSI > 70 = Survente", html.Br(),
                            "• RSI < 30 = Sous-achat", html.Br(),
                            "• ATR = Taille des stops"
                        ], width=3),
                        dbc.Col([
                            html.Strong("🧠 Smart Money:"), html.Br(),
                            "• FVG = Zones magnétiques", html.Br(),
                            "• Order Blocks = Niveaux institutionnels", html.Br(),
                            "• Liquidity = Hunt & Reversal"
                        ], width=3)
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
                        ], width=4),
                        dbc.Col([
                            html.Strong("⚡ Stratégie Scalping:"), html.Br(),
                            "• Timeframe: 5min", html.Br(),
                            "• Entrée: Pivot + RSI inverse", html.Br(),
                            "• Stop: ATR×1.0 = 100$ sur BTC", html.Br(),
                            "• Target: R1 ou S1 selon direction"
                        ], width=4),
                        dbc.Col([
                            html.Strong("🧠 Smart Money Setup:"), html.Br(),
                            "• FVG à 63500$ non comblé", html.Br(),
                            "• Order Block: 62000-62500$", html.Br(),
                            "• Liquidity Hunt: Stops à 61800$", html.Br(),
                            "• Entrée: Retest FVG + volume"
                        ], width=4)
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
                    ]),
                    
                    # Onglet Momentum (Nouveaux indicateurs Phase 2) - TEMPORAIREMENT DÉSACTIVÉ
                    # dbc.Tab(label="⚡ Momentum", tab_id="momentum", children=[
                    #     html.Div([
                    #         self._create_squeeze_momentum_section(),
                    #         html.Hr(),
                    #         self._create_candle_patterns_section(),
                    #         html.Hr(),
                    #         self._create_breakout_detector_section()
                    #     ], className="p-3")
                    # ]),
                    
                    # Onglet Smart Money Analysis
                    dbc.Tab(label="🧠 Smart Money", tab_id="smart-money", children=[
                        html.Div([
                            self._create_fvg_section(),
                            html.Hr(),
                            self._create_order_blocks_section(),
                            html.Hr(),
                            self._create_liquidity_zones_section()
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
    
    def _create_fvg_section(self) -> html.Div:
        """Section Fair Value Gaps (FVG) - Smart Money Analysis"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Fair Value Gaps (FVG)",
                        html.I(className="fas fa-brain ms-2", 
                               id="fvg-tooltip-target",
                               style={"color": "#6f42c1", "cursor": "pointer"})
                    ], className="fw-bold text-primary"),
                    dbc.Tooltip([
                        html.Strong("🧠 Fair Value Gaps - Zones d'Inefficience"), html.Br(),
                        "📊 Concept: Zones de prix non comblées révélant l'activité institutionnelle", html.Br(),
                        "🎯 Formation: 3 bougies consécutives créant un gap de prix", html.Br(),
                        "💼 Smart Money: Les institutions laissent ces gaps lors d'entrées massives", html.Br(),
                        "📈 Usage: Zones de support/résistance futures très fiables", html.Br(),
                        "🔄 Magnétisme: Le prix retourne souvent combler ces zones", html.Br(),
                        "⚡ Signaux: Retests = opportunités d'entrée de qualité"
                    ], target="fvg-tooltip-target", placement="right"),
                    html.P("Zones de prix non comblées révélant l'activité institutionnelle", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-fvg-switch",
                        value=True,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                # Onglets pour organiser les paramètres FVG
                dbc.Tabs([
                    
                    # Onglet Configuration de Base
                    dbc.Tab(label="⚙️ Base", tab_id="fvg-base", children=[
                        html.Div([
                            self._create_fvg_base_params()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Détection Avancée
                    dbc.Tab(label="� Détection", tab_id="fvg-detection", children=[
                        html.Div([
                            self._create_fvg_detection_params()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Visualisation
                    dbc.Tab(label="🎨 Visuel", tab_id="fvg-visual", children=[
                        html.Div([
                            self._create_fvg_visual_params()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Signaux & Alertes
                    dbc.Tab(label="� Signaux", tab_id="fvg-signals", children=[
                        html.Div([
                            self._create_fvg_signals_params()
                        ], className="p-3")
                    ])
                    
                ], id="fvg-tabs", active_tab="fvg-base", className="mt-3")
            ], id="indicators-fvg-collapse", is_open=True)
        ])
    
    def _create_order_blocks_section(self) -> html.Div:
        """Section Order Blocks - Smart Money Analysis"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "📦 Order Blocks",
                        html.I(className="fas fa-layer-group ms-2", 
                               id="ob-tooltip-target",
                               style={"color": "#e83e8c", "cursor": "pointer"})
                    ], className="fw-bold text-primary"),
                    dbc.Tooltip([
                        html.Strong("📦 Order Blocks - Zones d'Ordres Institutionnels"), html.Br(),
                        "💼 Concept: Zones où les institutions placent leurs gros ordres", html.Br(),
                        "📊 Formation: Dernière bougie avant mouvement impulsif", html.Br(),
                        "🎯 Smart Money: Révèle les niveaux d'entrée des institutions", html.Br(),
                        "📈 Usage: Support/Résistance de très haute qualité", html.Br(),
                        "🔄 Retest: Opportunités d'entrée dans le sens des institutions", html.Br(),
                        "⚡ Fiabilité: Très élevée pour les retournements"
                    ], target="ob-tooltip-target", placement="right"),
                    html.P("Zones d'accumulation/distribution institutionnelle", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-ob-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                # Onglets pour organiser les paramètres Order Blocks
                dbc.Tabs([
                    
                    # Onglet Configuration de Base
                    dbc.Tab(label="⚙️ Base", tab_id="ob-base", children=[
                        html.Div([
                            self._create_ob_base_params()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Détection Avancée
                    dbc.Tab(label="🔍 Détection", tab_id="ob-detection", children=[
                        html.Div([
                            self._create_ob_detection_params()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Visualisation
                    dbc.Tab(label="🎨 Visuel", tab_id="ob-visual", children=[
                        html.Div([
                            self._create_ob_visual_params()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Signaux & Alertes
                    dbc.Tab(label="🔔 Signaux", tab_id="ob-signals", children=[
                        html.Div([
                            self._create_ob_signals_params()
                        ], className="p-3")
                    ])
                    
                ], id="ob-tabs", active_tab="ob-base", className="mt-3")
            ], id="indicators-ob-collapse", is_open=True)
        ])
    
    def _create_liquidity_zones_section(self) -> html.Div:
        """Section Liquidity Zones - Smart Money Analysis"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Liquidity Zones",
                        html.I(className="fas fa-water ms-2", 
                               id="lz-tooltip-target",
                               style={"color": "#20c997", "cursor": "pointer"})
                    ], className="fw-bold text-primary"),
                    dbc.Tooltip([
                        html.Strong("💧 Liquidity Zones - Zones de Liquidité"), html.Br(),
                        "💼 Concept: Zones où les institutions collectent la liquidité", html.Br(),
                        "📊 Formation: Accumulation d'ordres d'achat/vente", html.Br(),
                        "🎯 Smart Money: Les gros acteurs ont besoin de liquidité", html.Br(),
                        "📈 Usage: Niveaux de retournement probable", html.Br(),
                        "🔄 Hunt: Les institutions 'chassent' les stops dans ces zones", html.Br(),
                        "⚡ Reversal: Zones de retournement très efficaces"
                    ], target="lz-tooltip-target", placement="right"),
                    html.P("Zones de collecte de liquidité institutionnelle", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-lz-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label([
                            "Force Zone",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="lz-strength-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "💪 Nombre de touches pour valider une zone", html.Br(),
                            "📊 2: Zones testées au minimum", html.Br(),
                            "🎯 3: Zones bien établies (recommandé)", html.Br(),
                            "⭐ 4+: Zones très fortes et fiables"
                        ], target="lz-strength-tooltip", placement="top"),
                        dbc.Input(
                            id="indicators-lz-zone-strength",
                            type="number",
                            value=3,
                            min=2,
                            max=10,
                            step=1,
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Sensibilité Temps",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="lz-time-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "⏰ Sensibilité temporelle pour les zones", html.Br(),
                            "⚡ High: Zones récentes prioritaires", html.Br(),
                            "📊 Medium: Équilibre récent/historique", html.Br(),
                            "🎯 Low: Toutes les zones historiques"
                        ], target="lz-time-tooltip", placement="top"),
                        dbc.Select(
                            id="indicators-lz-time-sensitivity",
                            options=[
                                {"label": "⚡ High", "value": "high"},
                                {"label": "📊 Medium", "value": "medium"},
                                {"label": "🎯 Low", "value": "low"}
                            ],
                            value="medium",
                            size="sm"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label([
                            "Confirmation Volume",
                            html.I(className="fas fa-question-circle ms-1", 
                                   id="lz-volume-tooltip",
                                   style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                        ], className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Valider avec analyse de volume", html.Br(),
                            "💼 Smart Money: Volume confirme l'activité", html.Br(),
                            "✅ Recommandé: Évite les fausses zones", html.Br(),
                            "🎯 Qualité supérieure des signaux"
                        ], target="lz-volume-tooltip", placement="top"),
                        dbc.Switch(
                            id="indicators-lz-volume-confirmation",
                            value=True,
                            className="mt-2"
                        )
                    ], width=4)
                ], className="mt-2")
            ], id="indicators-lz-collapse", is_open=False)
        ])
    
    def _create_fvg_base_params(self) -> html.Div:
        """Paramètres de base pour FVG"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "Seuil du Gap (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-threshold-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📏 Taille minimale du gap pour validation", html.Br(),
                        "⚡ Scalping: 0.05% - gaps très fins", html.Br(),
                        "🌅 Day Trading: 0.1% - équilibre qualité/quantité", html.Br(),
                        "📈 Swing: 0.2% - gaps significatifs seulement", html.Br(),
                        "🏔️ Position: 0.5% - gaps majeurs uniquement"
                    ], target="fvg-threshold-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-threshold",
                        type="number",
                        value=0.1,
                        min=0.01,
                        max=2.0,
                        step=0.01,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label([
                        "Taille Minimale (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-min-size-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📐 Taille absolue minimale du gap", html.Br(),
                        "🎯 Évite les micro-gaps non significatifs", html.Br(),
                        "⚡ Scalping: 0.02% minimum", html.Br(),
                        "📊 Standard: 0.05% minimum"
                    ], target="fvg-min-size-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-min-gap-size",
                        type="number",
                        value=0.05,
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label([
                        "Âge Maximum",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-age-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "⏰ Durée de vie maximale d'un gap", html.Br(),
                        "🕐 En nombre de bougies", html.Br(),
                        "⚡ Court terme: 20-30 bougies", html.Br(),
                        "📊 Moyen terme: 50-100 bougies", html.Br(),
                        "🎯 Long terme: 200+ bougies"
                    ], target="fvg-age-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-max-age",
                        type="number",
                        value=50,
                        min=10,
                        max=500,
                        step=5,
                        size="sm"
                    )
                ], width=4)
            ], className="mt-2"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "Confirmation Volume",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-volume-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📊 Valider les gaps avec le volume", html.Br(),
                        "💼 Smart Money: Volume élevé = institutions", html.Br(),
                        "✅ Recommandé: Filtre les faux gaps", html.Br(),
                        "🎯 Qualité > Quantité des signaux"
                    ], target="fvg-volume-tooltip", placement="top"),
                    dbc.Switch(
                        id="indicators-fvg-volume-confirmation",
                        value=True,
                        className="mt-2"
                    )
                ], width=6)
            ], className="mt-3")
        ])
    
    def _create_fvg_detection_params(self) -> html.Div:
        """Paramètres de détection avancée pour FVG"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "Multiplicateur Volume",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-vol-multi-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📊 Volume requis vs moyenne pour validation", html.Br(),
                        "💼 1.2x: Légèrement au-dessus moyenne", html.Br(),
                        "🎯 1.5x: Volume significatif (recommandé)", html.Br(),
                        "💥 2.0x+: Volume exceptionnel, très fiable"
                    ], target="fvg-vol-multi-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-volume-multiplier",
                        type="number",
                        value=1.5,
                        min=1.0,
                        max=5.0,
                        step=0.1,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label([
                        "Seuil Remplissage (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-fill-threshold-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "⚡ % de remplissage immédiat accepté", html.Br(),
                        "🎯 30%: Standard - gaps partiellement touchés OK", html.Br(),
                        "🔒 10%: Strict - gaps presque intacts seulement", html.Br(),
                        "🆓 50%: Tolérant - accepte remplissages partiels"
                    ], target="fvg-fill-threshold-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-immediate-fill-threshold",
                        type="number",
                        value=30,
                        min=5,
                        max=80,
                        step=5,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label([
                        "Distance Confluence (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-confluence-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🎯 Distance max pour grouper les gaps", html.Br(),
                        "📊 0.5%: Détecte zones de confluence", html.Br(),
                        "💪 Confluence = niveau plus fort", html.Br(),
                        "⚡ Gaps proches = activité institutionnelle"
                    ], target="fvg-confluence-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-confluence-distance",
                        type="number",
                        value=0.5,
                        min=0.1,
                        max=2.0,
                        step=0.1,
                        size="sm"
                    )
                ], width=4)
            ], className="mt-2"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "Sensibilité Retest (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-retest-sens-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🎯 Sensibilité pour détecter retests", html.Br(),
                        "📊 0.1%: Standard - retests précis", html.Br(),
                        "⚡ 0.05%: Très sensible - tous retests", html.Br(),
                        "🎯 0.2%: Moins sensible - retests significatifs"
                    ], target="fvg-retest-sens-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-retest-sensitivity",
                        type="number",
                        value=0.1,
                        min=0.01,
                        max=0.5,
                        step=0.01,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label([
                        "Max Retests",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-max-retest-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🔄 Nombre max de retests avant invalidation", html.Br(),
                        "📊 3: Standard - gaps normalement testés", html.Br(),
                        "⚡ 5: Scalping - gaps très actifs", html.Br(),
                        "🎯 1: Position - gaps rarement retestés"
                    ], target="fvg-max-retest-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-max-retest-count",
                        type="number",
                        value=3,
                        min=1,
                        max=10,
                        step=1,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Détection Confluence", className="fw-bold"),
                        dbc.Switch(
                            id="indicators-fvg-confluence-detection",
                            value=True,
                            className="mt-2"
                        )
                    ]),
                    html.Div([
                        dbc.Label("Cassure Structure", className="fw-bold mt-2"),
                        dbc.Switch(
                            id="indicators-fvg-structural-break-confirmation",
                            value=False,
                            className="mt-1"
                        )
                    ])
                ], width=4)
            ], className="mt-3")
        ])
    
    def _create_fvg_visual_params(self) -> html.Div:
        """Paramètres visuels pour FVG"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "Opacité (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-opacity-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🎨 Transparence des zones FVG", html.Br(),
                        "👁️ 30%: Subtil, ne gêne pas la lecture", html.Br(),
                        "📊 50%: Visible mais transparent", html.Br(),
                        "🎯 70%: Très visible pour analyse"
                    ], target="fvg-opacity-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-opacity",
                        type="number",
                        value=30,
                        min=10,
                        max=80,
                        step=5,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label([
                        "Max Gaps Affichés",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-max-display-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📊 Limite d'affichage pour performance", html.Br(),
                        "⚡ 15: Scalping - gaps récents", html.Br(),
                        "📊 20: Day Trading - équilibre", html.Br(),
                        "🎯 25+: Swing/Position - historique long"
                    ], target="fvg-max-display-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-max-gaps-display",
                        type="number",
                        value=20,
                        min=5,
                        max=50,
                        step=5,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Afficher Labels", className="fw-bold"),
                        dbc.Switch(
                            id="indicators-fvg-show-labels",
                            value=True,
                            className="mt-2"
                        )
                    ]),
                    html.Div([
                        dbc.Label("Distance au Prix", className="fw-bold mt-2"),
                        dbc.Switch(
                            id="indicators-fvg-show-distance-to-price",
                            value=True,
                            className="mt-1"
                        )
                    ])
                ], width=4)
            ], className="mt-2"),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Label("Opacité Dynamique", className="fw-bold"),
                        dbc.Tooltip([
                            "🎨 Opacité variable selon l'âge du gap", html.Br(),
                            "👴 Plus vieux = plus transparent", html.Br(),
                            "👶 Plus récent = plus opaque", html.Br(),
                            "💡 Améliore la lisibilité visuelle"
                        ], target="indicators-fvg-dynamic-opacity", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-dynamic-opacity",
                            value=True,
                            className="mt-2"
                        )
                    ])
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Épaisseur selon Force", className="fw-bold"),
                        dbc.Tooltip([
                            "📏 Épaisseur de ligne selon force du gap", html.Br(),
                            "💪 Plus fort = ligne plus épaisse", html.Br(),
                            "📊 Identification visuelle rapide", html.Br(),
                            "🎯 Met en évidence les gaps importants"
                        ], target="indicators-fvg-strength-line-width", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-strength-line-width",
                            value=True,
                            className="mt-2"
                        )
                    ])
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Niveaux Fibonacci", className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Prioriser gaps aux niveaux Fibonacci", html.Br(),
                            "🎯 38.2%, 50%, 61.8% = niveaux clés", html.Br(),
                            "💪 Confluence Fib + FVG = très fort", html.Br(),
                            "✨ Signaux de qualité supérieure"
                        ], target="indicators-fvg-fibonacci-levels", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-fibonacci-levels",
                            value=True,
                            className="mt-2"
                        )
                    ])
                ], width=4)
            ], className="mt-3")
        ])
    
    def _create_fvg_signals_params(self) -> html.Div:
        """Paramètres signaux et alertes pour FVG"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "Distance Alerte (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="fvg-alert-distance-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🔔 Distance pour déclencher alerte", html.Br(),
                        "⚡ 0.1%: Alertes très proches", html.Br(),
                        "📊 0.2%: Standard - bon équilibre", html.Br(),
                        "🎯 0.5%: Alertes anticipées"
                    ], target="fvg-alert-distance-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-fvg-alert-distance",
                        type="number",
                        value=0.2,
                        min=0.05,
                        max=1.0,
                        step=0.05,
                        size="sm"
                    )
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Alertes Automatiques", className="fw-bold"),
                        dbc.Tooltip([
                            "🔔 Générer alertes automatiques", html.Br(),
                            "⚡ Notification quand prix approche gap", html.Br(),
                            "🎯 Opportunités de trading en temps réel", html.Br(),
                            "💡 Seulement pour gaps forts"
                        ], target="indicators-fvg-auto-alerts", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-auto-alerts",
                            value=False,
                            className="mt-2"
                        )
                    ])
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Confirmation RSI", className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Confirmer avec niveaux RSI", html.Br(),
                            "🎯 RSI survente + FVG bullish = signal fort", html.Br(),
                            "📈 RSI surachat + FVG bearish = signal fort", html.Br(),
                            "💡 Améliore qualité des signaux"
                        ], target="indicators-fvg-rsi-confirmation", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-rsi-confirmation",
                            value=False,
                            className="mt-2"
                        )
                    ])
                ], width=4)
            ], className="mt-2"),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Label("Filtrage Sessions", className="fw-bold"),
                        dbc.Tooltip([
                            "🕐 Filtrer selon sessions de marché", html.Br(),
                            "🌅 Londres/New York = plus volatiles", html.Br(),
                            "📊 Gaps pendant chevauchements = forts", html.Br(),
                            "💼 Activité institutionnelle concentrée"
                        ], target="indicators-fvg-session-filter", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-session-filter",
                            value=True,
                            className="mt-2"
                        )
                    ])
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Filtrage Actualités", className="fw-bold"),
                        dbc.Tooltip([
                            "📰 Éviter gaps créés par actualités", html.Br(),
                            "⚡ News = mouvements non institutionnels", html.Br(),
                            "🎯 Focus sur gaps de structure pure", html.Br(),
                            "💡 Améliore fiabilité des signaux"
                        ], target="indicators-fvg-news-filter", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-news-filter",
                            value=False,
                            className="mt-2"
                        )
                    ])
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Label("Gaps Weekend", className="fw-bold"),
                        dbc.Tooltip([
                            "📅 Inclure gaps de weekend", html.Br(),
                            "🕐 Crypto: Marché 24/7, gaps valides", html.Br(),
                            "📊 Forex: Gaps dimanche soir importants", html.Br(),
                            "⚡ Peut créer opportunités uniques"
                        ], target="indicators-fvg-weekend-gaps", placement="top"),
                        dbc.Switch(
                            id="indicators-fvg-weekend-gaps",
                            value=True,
                            className="mt-2"
                        )
                    ])
                ], width=4)
            ], className="mt-3")
        ])
    
    # ========================================
    # METHODS POUR ORDER BLOCKS TABS
    # ========================================
    
    def _create_ob_base_params(self) -> html.Div:
        """Paramètres de base Order Blocks"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "📊 Période Lookback",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-lookback-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "👀 Nombre de bougies à analyser", html.Br(),
                        "⚡ Court: 10-15 pour signaux récents", html.Br(),
                        "📊 Standard: 20-30 équilibre qualité/réactivité", html.Br(),
                        "🎯 Long: 50+ pour niveaux historiques"
                    ], target="ob-lookback-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-lookback",
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
                        "🔊 Ratio Volume Min",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-volume-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📊 Volume minimum vs moyenne pour validation", html.Br(),
                        "💼 1.2x: Légèrement au-dessus", html.Br(),
                        "📈 1.5x: Volume significatif (recommandé)", html.Br(),
                        "🚀 2.0x+: Volume institutionnel fort"
                    ], target="ob-volume-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-volume-ratio",
                        type="number",
                        value=1.5,
                        min=1.0,
                        max=5.0,
                        step=0.1,
                        size="sm"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "💪 Seuil de Force",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-strength-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "💪 Score minimum pour valider un bloc", html.Br(),
                        "🎯 0.3-0.5: Blocs faibles mais nombreux", html.Br(),
                        "📊 0.6-0.7: Équilibre qualité/quantité", html.Br(),
                        "🏆 0.8+: Seulement blocs très forts"
                    ], target="ob-strength-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-strength",
                        type="number",
                        value=0.6,
                        min=0.1,
                        max=1.0,
                        step=0.1,
                        size="sm"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label([
                        "⚡ Seuil Impulsion",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-impulse-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "⚡ Force minimum du mouvement impulsif", html.Br(),
                        "📈 1.2x: Mouvements légers", html.Br(),
                        "🚀 1.5x: Impulsions significatives", html.Br(),
                        "💥 2.0x+: Breakouts puissants seulement"
                    ], target="ob-impulse-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-impulse",
                        type="number",
                        value=1.5,
                        min=1.0,
                        max=3.0,
                        step=0.1,
                        size="sm"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "📏 Taille Min. Bloc (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-minsize-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📏 Taille minimum du bloc en % du prix", html.Br(),
                        "🔍 0.1%: Tous les micro-blocs", html.Br(),
                        "📊 0.2%: Blocs significatifs", html.Br(),
                        "🎯 0.5%+: Seulement gros blocs"
                    ], target="ob-minsize-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-min-size",
                        type="number",
                        value=0.2,
                        min=0.05,
                        max=2.0,
                        step=0.05,
                        size="sm"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label([
                        "⏰ Âge Max (bougies)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-maxage-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "⏰ Combien de temps un bloc reste actif", html.Br(),
                        "⚡ 50: Blocs récents seulement", html.Br(),
                        "📊 100: Durée standard", html.Br(),
                        "🏛️ 200+: Niveaux historiques"
                    ], target="ob-maxage-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-max-age",
                        type="number",
                        value=100,
                        min=20,
                        max=500,
                        step=10,
                        size="sm"
                    )
                ], width=6)
            ])
        ])
    
    def _create_ob_detection_params(self) -> html.Div:
        """Paramètres de détection avancée Order Blocks"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("🔍 Validations Avancées", className="text-info fw-bold mb-3")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "Confirmation Volume",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-vol-conf-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📊 Valide le volume au moment de formation", html.Br(),
                        "✅ Activé: Blocs avec volume significatif", html.Br(),
                        "❌ Désactivé: Tous blocs structurels"
                    ], target="ob-vol-conf-tooltip", placement="top"),
                    dbc.Switch(
                        id="indicators-ob-volume-conf",
                        value=True,
                        className="mt-1"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label([
                        "Validation Structure",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-struct-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🏗️ Vérifie la structure de marché", html.Br(),
                        "✅ Activé: Blocs dans tendance cohérente", html.Br(),
                        "❌ Désactivé: Tous blocs valides"
                    ], target="ob-struct-tooltip", placement="top"),
                    dbc.Switch(
                        id="indicators-ob-structure-val",
                        value=True,
                        className="mt-1"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Détection Imbalances", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-imbalance",
                        value=True,
                        className="mt-1"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Validation Retest", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-retest",
                        value=True,
                        className="mt-1"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Filtre Session", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-session",
                        value=False,
                        className="mt-1"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Alignement Tendance", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-trend",
                        value=False,
                        className="mt-1"
                    )
                ], width=6)
            ])
        ])
    
    def _create_ob_visual_params(self) -> html.Div:
        """Paramètres de visualisation Order Blocks"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("🎨 Affichage", className="text-info fw-bold mb-3")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("🏷️ Afficher Labels", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-show-labels",
                        value=True,
                        className="mt-1"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("💪 Afficher Force", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-show-strength",
                        value=True,
                        className="mt-1"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "🟢 Couleur Bullish",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-bull-color-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🟢 Couleur des Order Blocks haussiers", html.Br(),
                        "💡 Choisissez une couleur facilement visible"
                    ], target="ob-bull-color-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-bullish-color",
                        type="color",
                        value="#2E8B57",
                        size="sm",
                        className="mt-1"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label([
                        "🔴 Couleur Bearish",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-bear-color-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "🔴 Couleur des Order Blocks baissiers", html.Br(),
                        "💡 Contraste avec couleur bullish"
                    ], target="ob-bear-color-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-bearish-color",
                        type="color",
                        value="#DC143C",
                        size="sm",
                        className="mt-1"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "👁️ Opacité (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-opacity-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "👁️ Transparence des zones Order Blocks", html.Br(),
                        "🔅 10-20%: Très discret", html.Br(),
                        "📊 30-40%: Bien visible", html.Br(),
                        "🔆 50%+: Très visible"
                    ], target="ob-opacity-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-opacity",
                        type="number",
                        value=30,
                        min=10,
                        max=80,
                        step=5,
                        size="sm"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label([
                        "📊 Max Blocs Affichés",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-maxdisp-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📊 Nombre maximum de blocs à afficher", html.Br(),
                        "⚡ 5-10: Graphique épuré", html.Br(),
                        "📈 15-20: Vue complète", html.Br(),
                        "🔥 25+: Analyse détaillée"
                    ], target="ob-maxdisp-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-max-display",
                        type="number",
                        value=15,
                        min=5,
                        max=50,
                        step=5,
                        size="sm"
                    )
                ], width=6)
            ])
        ])
    
    def _create_ob_signals_params(self) -> html.Div:
        """Paramètres de signaux et alertes Order Blocks"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("🔔 Signaux & Alertes", className="text-info fw-bold mb-3")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("📈 Génération Signaux", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-signals",
                        value=True,
                        className="mt-1"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("🚨 Alertes Proximité", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-alerts",
                        value=False,
                        className="mt-1"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label([
                        "📏 Distance Alerte (%)",
                        html.I(className="fas fa-question-circle ms-1", 
                               id="ob-alert-dist-tooltip",
                               style={"color": "#6c757d", "cursor": "help", "fontSize": "0.8rem"})
                    ], className="fw-bold"),
                    dbc.Tooltip([
                        "📏 Distance du prix pour déclencher alerte", html.Br(),
                        "🎯 0.05%: Très proche", html.Br(),
                        "📊 0.1%: Distance standard", html.Br(),
                        "📈 0.2%+: Anticipation large"
                    ], target="ob-alert-dist-tooltip", placement="top"),
                    dbc.Input(
                        id="indicators-ob-alert-distance",
                        type="number",
                        value=0.1,
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        size="sm"
                    )
                ], width=6),
                dbc.Col([
                    html.P("", className="invisible")  # Spacer
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("🎯 Confluence avec FVG", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-confluence-fvg",
                        value=False,
                        className="mt-1"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("📐 Confluence Fibonacci", className="fw-bold"),
                    dbc.Switch(
                        id="indicators-ob-confluence-fib",
                        value=False,
                        className="mt-1"
                    )
                ], width=6)
            ], className="mb-3"),
            
            html.Hr(),
            
            dbc.Alert([
                html.H6("💡 Conseils Order Blocks", className="fw-bold mb-2"),
                html.P([
                    "🎯 ", html.Strong("Zones de retournement"), ": Order Blocks marquent où les institutions ont placé leurs ordres"
                ], className="mb-1"),
                html.P([
                    "📊 ", html.Strong("Confluence"), ": Combinez avec FVG et Fibonacci pour des signaux plus forts"
                ], className="mb-1"),
                html.P([
                    "⚡ ", html.Strong("Retest"), ": Attendez le retour du prix sur le bloc pour une entrée"
                ], className="mb-0")
            ], color="info", className="mt-3")
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
    
    # Callbacks individuels pour les collapses (pas de boucle pour éviter le problème de closure)
    
    @app.callback(
        Output("indicators-sma-collapse", "is_open"),
        [Input("indicators-sma-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_sma_collapse(enabled):
        """Toggle SMA collapse"""
        return enabled
    
    @app.callback(
        Output("indicators-ema-collapse", "is_open"),
        [Input("indicators-ema-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_ema_collapse(enabled):
        """Toggle EMA collapse"""
        return enabled
    
    @app.callback(
        Output("indicators-sr-collapse", "is_open"),
        [Input("indicators-sr-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_sr_collapse(enabled):
        """Toggle Support/Résistance collapse"""
        print(f"🔍 DEBUG SR COLLAPSE: enabled={enabled}, returning={enabled}")
        return enabled
    
    @app.callback(
        Output("indicators-fibonacci-collapse", "is_open"),
        [Input("indicators-fibonacci-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_fibonacci_collapse(enabled):
        """Toggle Fibonacci collapse"""
        print(f"🔍 DEBUG FIBONACCI COLLAPSE: enabled={enabled}, returning={enabled}")
        return enabled
    
    @app.callback(
        Output("indicators-pivot-collapse", "is_open"),
        [Input("indicators-pivot-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_pivot_collapse(enabled):
        """Toggle Points Pivots collapse"""
        print(f"🔍 DEBUG PIVOT COLLAPSE: enabled={enabled}, returning={enabled}")
        return enabled
    
    @app.callback(
        Output("indicators-rsi-collapse", "is_open"),
        [Input("indicators-rsi-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_rsi_collapse(enabled):
        """Toggle RSI collapse"""
        return enabled
    
    @app.callback(
        Output("indicators-atr-collapse", "is_open"),
        [Input("indicators-atr-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_atr_collapse(enabled):
        """Toggle ATR collapse"""
        return enabled
    
    @app.callback(
        Output("indicators-fvg-collapse", "is_open"),
        [Input("indicators-fvg-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_fvg_collapse(enabled):
        """Toggle FVG collapse"""
        return enabled
    
    @app.callback(
        Output("indicators-ob-collapse", "is_open"),
        [Input("indicators-ob-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_ob_collapse(enabled):
        """Toggle Order Blocks collapse"""
        return enabled
    
    # Nouveaux callbacks pour les indicateurs Momentum (Phase 3)
    @app.callback(
        Output("indicators-squeeze-momentum-collapse", "is_open"),
        [Input("indicators-squeeze-momentum-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_squeeze_momentum_collapse(enabled):
        """Toggle Squeeze Momentum collapse"""
        return enabled
    
    @app.callback(
        Output("indicators-candle-patterns-collapse", "is_open"),
        [Input("indicators-candle-patterns-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_candle_patterns_collapse(enabled):
        """Toggle Candle Patterns collapse"""
        return enabled
    
    @app.callback(
        Output("indicators-breakout-detector-collapse", "is_open"),
        [Input("indicators-breakout-detector-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_breakout_detector_collapse(enabled):
        """Toggle Breakout Detector collapse"""
        return enabled
    
    # Callback toggle Volume Profile (Phase 4)
    @app.callback(
        Output("indicators-volume-profile-collapse", "is_open"),
        [Input("indicators-volume-profile-switch", "value")],
        prevent_initial_call=True
    )
    def toggle_volume_profile_collapse(enabled):
        """Toggle Volume Profile collapse"""
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
         Input("indicators-atr-multiplier", "value"),
         # Nouveaux indicateurs Momentum (Phase 3)
         Input("indicators-squeeze-momentum-switch", "value"),
         Input("indicators-squeeze-period", "value"),
         Input("indicators-squeeze-sensitivity", "value"),
         Input("indicators-candle-patterns-switch", "value"),
         Input("indicators-doji-threshold", "value"),
         Input("indicators-hammer-ratio", "value"),
         Input("indicators-pattern-volume-confirm", "value"),
         Input("indicators-pattern-labels", "value"),
         Input("indicators-breakout-detector-switch", "value"),
         Input("indicators-breakout-strength", "value"),
         Input("indicators-breakout-volume-threshold", "value"),
         Input("indicators-breakout-threshold", "value"),
         Input("indicators-breakout-confirmation", "value"),
         # Volume Profile (Phase 4)
         Input("indicators-volume-profile-switch", "value"),
         Input("indicators-volume-bins", "value"),
         Input("indicators-volume-lookback", "value"),
         Input("indicators-value-area-percent", "value"),
         Input("indicators-poc-sensitivity", "value"),
         Input("indicators-show-poc", "value"),
         Input("indicators-show-value-area", "value"),
         Input("indicators-show-histogram", "value"),
         Input("indicators-show-hvn", "value"),
         Input("indicators-hvn-threshold", "value"),
         Input("indicators-poc-alerts", "value"),
         Input("indicators-poc-proximity", "value"),
         Input("indicators-va-alerts", "value"),
         Input("indicators-histogram-opacity", "value")],
        prevent_initial_call=True
    )
    def store_indicators_config(sma_enabled, sma_period, ema_enabled, ema_period,
                               sr_enabled, sr_strength, fib_enabled, fib_swing, 
                               pivot_enabled, pivot_method, rsi_enabled, rsi_period, 
                               rsi_overbought, rsi_oversold, atr_enabled, atr_period, atr_multiplier,
                               # Nouveaux indicateurs Momentum
                               squeeze_enabled, squeeze_period, squeeze_sensitivity,
                               candle_enabled, doji_threshold, hammer_ratio, pattern_volume_confirm, pattern_labels,
                               breakout_enabled, breakout_strength, breakout_volume_threshold, breakout_threshold, breakout_confirmation,
                               # Volume Profile (Phase 4)
                               volume_profile_enabled, volume_bins, volume_lookback, value_area_percent, poc_sensitivity,
                               show_poc, show_value_area, show_histogram, show_hvn, hvn_threshold,
                               poc_alerts, poc_proximity, va_alerts, histogram_opacity):
        """Stocker la configuration des indicateurs pour persistance"""
        return {
            'sma': {'enabled': sma_enabled, 'period': sma_period},
            'ema': {'enabled': ema_enabled, 'period': ema_period},
            'sr': {'enabled': sr_enabled, 'strength': sr_strength},
            'fibonacci': {'enabled': fib_enabled, 'swing': fib_swing},
            'pivot': {'enabled': pivot_enabled, 'method': pivot_method},
            'rsi': {'enabled': rsi_enabled, 'period': rsi_period, 'overbought': rsi_overbought, 'oversold': rsi_oversold},
            'atr': {'enabled': atr_enabled, 'period': atr_period, 'multiplier': atr_multiplier},
            # Nouveaux indicateurs
            'squeeze_momentum': {
                'enabled': squeeze_enabled, 
                'period': squeeze_period, 
                'sensitivity': squeeze_sensitivity
            },
            'candle_patterns': {
                'enabled': candle_enabled,
                'doji_threshold': doji_threshold,
                'hammer_ratio': hammer_ratio,
                'volume_confirm': pattern_volume_confirm,
                'show_labels': pattern_labels
            },
            'breakout_detector': {
                'enabled': breakout_enabled,
                'strength': breakout_strength,
                'volume_threshold': breakout_volume_threshold,
                'threshold': breakout_threshold,
                'confirmation': breakout_confirmation
            },
            # Volume Profile (Phase 4)
            'volume_profile': {
                'enabled': volume_profile_enabled,
                'bins_count': volume_bins,
                'lookback_periods': volume_lookback,
                'value_area_percent': value_area_percent,
                'poc_sensitivity': poc_sensitivity,
                'show_poc': show_poc,
                'show_value_area': show_value_area,
                'show_histogram': show_histogram,
                'show_hvn': show_hvn,
                'hvn_threshold': hvn_threshold,
                'poc_alerts': poc_alerts,
                'poc_proximity': poc_proximity,
                'va_alerts': va_alerts,
                'histogram_opacity': histogram_opacity
            }
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
         Output("indicators-macd-histogram", "value", allow_duplicate=True),
         # Fair Value Gaps - paramètres principaux synchronisés avec styles
         Output("indicators-fvg-switch", "value", allow_duplicate=True),
         Output("indicators-fvg-min-gap-size", "value", allow_duplicate=True),
         Output("indicators-fvg-volume-confirmation", "value", allow_duplicate=True),
         Output("indicators-fvg-threshold", "value", allow_duplicate=True),
         Output("indicators-fvg-max-age", "value", allow_duplicate=True),
         Output("indicators-fvg-show-labels", "value", allow_duplicate=True),
         Output("indicators-fvg-opacity", "value", allow_duplicate=True),
         Output("indicators-fvg-max-gaps-display", "value", allow_duplicate=True),
         # Order Blocks - paramètres principaux synchronisés avec styles
         Output("indicators-ob-switch", "value", allow_duplicate=True),
         Output("indicators-ob-lookback", "value", allow_duplicate=True),
         Output("indicators-ob-volume-ratio", "value", allow_duplicate=True),
         Output("indicators-ob-strength", "value", allow_duplicate=True),
         Output("indicators-ob-impulse", "value", allow_duplicate=True),
         Output("indicators-ob-min-size", "value", allow_duplicate=True),
         Output("indicators-ob-max-age", "value", allow_duplicate=True),
         Output("indicators-ob-volume-conf", "value", allow_duplicate=True),
         Output("indicators-ob-structure-val", "value", allow_duplicate=True),
         Output("indicators-ob-show-labels", "value", allow_duplicate=True),
         Output("indicators-ob-show-strength", "value", allow_duplicate=True),
         Output("indicators-ob-bullish-color", "value", allow_duplicate=True),
         Output("indicators-ob-bearish-color", "value", allow_duplicate=True),
         Output("indicators-ob-opacity", "value", allow_duplicate=True),
         Output("indicators-ob-max-display", "value", allow_duplicate=True)],
        [Input("indicators-trading-style", "value")],
        prevent_initial_call=True
    )
    def apply_trading_style(selected_style):
        """Applique automatiquement les paramètres selon le style de trading choisi"""
        if not selected_style or selected_style == "manuel":
            # Style manuel - ne change rien
            return tuple([dash.no_update] * 63)  # Ajusté pour inclure MACD (7) + FVG (8) + OB (15) = 40 + 8 + 15 = 63
        
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
            
            # Fair Value Gaps
            fvg_config = config.get('fvg', {})
            fvg_enabled = fvg_config.enabled
            fvg_min_gap_size = fvg_config.parameters.get('min_gap_size', 0.002)
            fvg_volume_confirmation = fvg_config.parameters.get('volume_confirmation', True)
            fvg_overlap_threshold = fvg_config.parameters.get('overlap_threshold', 0.7)
            fvg_max_distance = fvg_config.parameters.get('max_distance', 100)
            fvg_show_labels = fvg_config.parameters.get('show_labels', True)
            fvg_zones_opacity = fvg_config.parameters.get('zones_opacity', 0.2)
            fvg_max_zones = fvg_config.parameters.get('max_zones', 15)
            
            # Order Blocks
            ob_config = config.get('order_blocks', {})
            ob_enabled = ob_config.enabled
            ob_lookback = ob_config.parameters.get('lookback_period', 20)
            ob_volume_ratio = ob_config.parameters.get('min_body_size', 0.002) * 1000  # Convertir en pourcentage
            ob_strength = ob_config.parameters.get('strong_threshold', 0.7)
            ob_impulse = ob_config.parameters.get('min_impulse_strength', 0.5) * 100  # Convertir en pourcentage
            ob_min_size = ob_config.parameters.get('min_body_size', 0.002) * 100  # Convertir en pourcentage
            ob_max_age = ob_config.parameters.get('max_age_bars', 100)
            ob_volume_conf = ob_config.parameters.get('volume_confirmation', True)
            ob_structure_val = ob_config.parameters.get('volume_confirmation', True)  # Utiliser même paramètre
            ob_show_labels = ob_config.parameters.get('show_labels', True)
            ob_show_strength = ob_config.parameters.get('show_retests', True)  # Utiliser retests pour strength
            ob_bullish_color = ob_config.visual.get('bullish_color', '#2E8B57')
            ob_bearish_color = ob_config.visual.get('bearish_color', '#DC143C')
            ob_opacity = int(ob_config.parameters.get('opacity_active', 0.3) * 100)  # Convertir en pourcentage
            ob_max_display = ob_config.parameters.get('max_age_bars', 100) // 5  # Approximation

            return (
                sma_enabled, sma_period, sma_color,
                ema_enabled, ema_period, ema_color,
                sr_enabled, sr_strength, sr_lookback, sr_support_color, sr_resistance_color, sr_line_style, sr_line_width,
                fib_enabled, fib_swing, fib_line_style, fib_line_width, fib_transparency,
                pivot_enabled, pivot_method, pivot_period, pivot_color, pivot_resistance_color, pivot_support_color, pivot_line_style, pivot_line_width,
                rsi_enabled, rsi_period, rsi_overbought, rsi_oversold,
                atr_enabled, atr_period, atr_multiplier,
                macd_enabled, macd_fast, macd_slow, macd_signal, macd_color, macd_signal_color, macd_histogram,
                fvg_enabled, fvg_min_gap_size, fvg_volume_confirmation, fvg_overlap_threshold, fvg_max_distance, fvg_show_labels, fvg_zones_opacity, fvg_max_zones,
                ob_enabled, ob_lookback, ob_volume_ratio, ob_strength, ob_impulse, ob_min_size, ob_max_age, ob_volume_conf, ob_structure_val, ob_show_labels, ob_show_strength, ob_bullish_color, ob_bearish_color, ob_opacity, ob_max_display
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
                True, 12, 26, 9, '#2196F3', '#FF5722', True,  # MACD
                True, 0.002, True, 0.7, 100, True, 0.2, 15,  # FVG (Day Trading defaults)
                True, 20, 1.5, 0.6, 1.5, 0.2, 100, True, True, True, True, '#2E8B57', '#DC143C', 30, 15  # Order Blocks
            )

    # Callback de synchronisation automatique des paramètres Order Blocks selon le style
    @app.callback(
        [Output('indicators-ob-lookback', 'value'),
         Output('indicators-ob-strength', 'value'),
         Output('indicators-ob-opacity', 'value')],
        [Input('indicators-trading-style', 'value')],
        prevent_initial_call=True
    )
    def sync_order_blocks_with_style(trading_style):
        """Synchronise automatiquement les paramètres Order Blocks avec le style sélectionné"""
        if not trading_style:
            return dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Récupérer la configuration du style pour Order Blocks
            style_config = trading_style_manager.get_style_config(trading_style)
            ob_indicator_config = style_config.get('order_blocks')
            
            if ob_indicator_config and hasattr(ob_indicator_config, 'parameters'):
                params = ob_indicator_config.parameters
                
                # Mettre à jour les contrôles avec les paramètres du style
                lookback = params.get('lookback_period', 20)
                strength = params.get('strong_threshold', 0.7)
                opacity = int(params.get('opacity_active', 0.3) * 100)  # Convertir en pourcentage
                
                print(f"🔄 Sync Order Blocks avec style {trading_style}: lookback={lookback}, strength={strength}, opacity={opacity}")
                
                return lookback, strength, opacity
            
        except Exception as e:
            print(f"❌ Erreur synchronisation Order Blocks: {e}")
        
        return dash.no_update, dash.no_update, dash.no_update

    # Callback de synchronisation automatique FVG selon le style
    @app.callback(
        [Output('indicators-fvg-threshold', 'value'),
         Output('indicators-fvg-max-age', 'value'),
         Output('indicators-fvg-opacity', 'value')],
        [Input('indicators-trading-style', 'value')],
        prevent_initial_call=True
    )
    def sync_fvg_with_style(trading_style):
        """Synchronise automatiquement les paramètres FVG avec le style sélectionné"""
        if not trading_style:
            return dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Récupérer la configuration du style pour FVG
            style_config = trading_style_manager.get_style_config(trading_style)
            fvg_indicator_config = style_config.get('fair_value_gaps')
            
            if fvg_indicator_config and hasattr(fvg_indicator_config, 'parameters'):
                params = fvg_indicator_config.parameters
                
                # Mettre à jour les contrôles avec les paramètres du style
                threshold = params.get('gap_threshold', 0.1)
                max_age = params.get('max_gap_age', 50)
                opacity = int(params.get('gap_opacity', 0.3) * 100)  # Convertir en pourcentage
                
                print(f"🔄 Sync FVG avec style {trading_style}: threshold={threshold}, max_age={max_age}, opacity={opacity}")
                
                return threshold, max_age, opacity
            
        except Exception as e:
            print(f"❌ Erreur synchronisation FVG: {e}")
        
        return dash.no_update, dash.no_update, dash.no_update

    # =================================================================
    # NOUVELLES SECTIONS MOMENTUM - PHASE 3
    # =================================================================
    
    def _create_squeeze_momentum_section(self) -> html.Div:
        """Section Squeeze Momentum - Détection Compression/Expansion"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Squeeze Momentum",
                        html.I(className="fas fa-compress-arrows-alt ms-2", 
                               id="squeeze-momentum-tooltip-target",
                               style={"color": "#ff9800", "cursor": "pointer"})
                    ], className="fw-bold text-warning"),
                    dbc.Tooltip([
                        html.Strong("⚡ Squeeze Momentum - Compression/Expansion"), html.Br(),
                        "📊 Concept: Détecte les phases de compression et d'expansion du marché", html.Br(),
                        "🎯 Squeeze: Bollinger Bands à l'intérieur des Keltner Channels", html.Br(),
                        "💥 Release: Breakout avec forte expansion de volatilité", html.Br(),
                        "📈 Momentum: Direction de l'explosion (haussier/baissier)", html.Br(),
                        "⚡ Trading: Anticiper les mouvements explosifs après compression"
                    ], target="squeeze-momentum-tooltip-target", placement="right"),
                    html.P("Détecte compression/expansion pour anticiper les breakouts", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-squeeze-momentum-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        html.Label("Période BB/KC", className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Période pour Bollinger Bands et Keltner Channels", html.Br(),
                            "⚡ Court: Signaux fréquents", html.Br(),
                            "🎯 Long: Signaux de qualité"
                        ], target="squeeze-period-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="squeeze-period-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-squeeze-period",
                            min=5, max=50, step=1, value=20,
                            marks={5: '5', 20: '20', 50: '50'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Sensibilité Momentum", className="fw-bold"),
                        dbc.Tooltip([
                            "⚡ Sensibilité détection momentum", html.Br(),
                            "🔥 Faible: Plus de signaux", html.Br(),
                            "🎯 Élevé: Signaux sélectifs"
                        ], target="squeeze-sensitivity-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="squeeze-sensitivity-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-squeeze-sensitivity",
                            min=1, max=10, step=1, value=5,
                            marks={1: '1', 5: '5', 10: '10'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-squeeze-momentum-collapse", is_open=False)
        ])
    
    def _create_candle_patterns_section(self) -> html.Div:
        """Section Candle Patterns - Détection Patterns de Bougies"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Candle Patterns",
                        html.I(className="fas fa-chart-bar ms-2", 
                               id="candle-patterns-tooltip-target",
                               style={"color": "#4caf50", "cursor": "pointer"})
                    ], className="fw-bold text-success"),
                    dbc.Tooltip([
                        html.Strong("🕯️ Candle Patterns - Psychologie du Marché"), html.Br(),
                        "📊 Doji: Indécision, potentiel retournement", html.Br(),
                        "🔨 Hammer: Rejet baissier, signal haussier", html.Br(),
                        "💪 Engulfing: Absorption complète, signal fort", html.Br(),
                        "🎯 Usage: Confirmation des zones de retournement", html.Br(),
                        "⚡ Trading: Entrées sur retests de patterns validés"
                    ], target="candle-patterns-tooltip-target", placement="right"),
                    html.P("Détecte Doji, Hammer, Engulfing pour signaux de retournement", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-candle-patterns-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        html.Label("Sensibilité Doji", className="fw-bold"),
                        dbc.Tooltip([
                            "🕯️ Taille max du corps pour Doji", html.Br(),
                            "⚡ Faible: Dojis stricts", html.Br(),
                            "🎯 Élevé: Plus de détections"
                        ], target="doji-sensitivity-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="doji-sensitivity-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-doji-threshold",
                            min=0.05, max=0.3, step=0.05, value=0.1,
                            marks={0.05: '5%', 0.1: '10%', 0.3: '30%'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Ratio Hammer", className="fw-bold"),
                        dbc.Tooltip([
                            "🔨 Ratio mèche/corps pour Hammer", html.Br(),
                            "⚡ Faible: Hammers larges", html.Br(),
                            "🎯 Élevé: Hammers stricts"
                        ], target="hammer-ratio-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="hammer-ratio-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-hammer-ratio",
                            min=1.5, max=4.0, step=0.5, value=2.0,
                            marks={1.5: '1.5x', 2.0: '2x', 4.0: '4x'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6)
                ], className="mt-2"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Confirmation Volume", className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Confirmer patterns avec volume", html.Br(),
                            "✅ Activé: Patterns plus fiables", html.Br(),
                            "⚡ Désactivé: Plus de signaux"
                        ], target="pattern-volume-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="pattern-volume-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dbc.Switch(
                            id="indicators-pattern-volume-confirm",
                            value=True,
                            className="mt-2"
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Afficher Labels", className="fw-bold"),
                        dbc.Tooltip([
                            "🏷️ Afficher noms des patterns", html.Br(),
                            "✅ Utile pour apprentissage", html.Br(),
                            "❌ Peut encombrer le graphique"
                        ], target="pattern-labels-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="pattern-labels-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dbc.Switch(
                            id="indicators-pattern-labels",
                            value=True,
                            className="mt-2"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-candle-patterns-collapse", is_open=False)
        ])
    
    def _create_breakout_detector_section(self) -> html.Div:
        """Section Breakout Detector - Détection Cassures de Niveaux"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Breakout Detector",
                        html.I(className="fas fa-rocket ms-2", 
                               id="breakout-detector-tooltip-target",
                               style={"color": "#ff5722", "cursor": "pointer"})
                    ], className="fw-bold text-danger"),
                    dbc.Tooltip([
                        html.Strong("🚀 Breakout Detector - Cassures Explosives"), html.Br(),
                        "📊 Concept: Détecte cassures de supports/résistances clés", html.Br(),
                        "💥 Volume: Confirmation par explosion de volume", html.Br(),
                        "🎯 Direction: Breakout haussier ou baissier", html.Br(),
                        "📈 Momentum: Force de la cassure", html.Br(),
                        "⚡ Trading: Entrées sur retests post-breakout"
                    ], target="breakout-detector-tooltip-target", placement="right"),
                    html.P("Détecte cassures explosives avec confirmation volume", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-breakout-detector-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        html.Label("Force S/R", className="fw-bold"),
                        dbc.Tooltip([
                            "💪 Force minimale Support/Résistance", html.Br(),
                            "⚡ Faible: Plus de niveaux", html.Br(),
                            "🎯 Élevé: Niveaux majeurs seulement"
                        ], target="breakout-strength-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="breakout-strength-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-breakout-strength",
                            min=1, max=5, step=1, value=2,
                            marks={1: '1', 2: '2', 5: '5'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Seuil Volume", className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Volume min vs moyenne pour confirmer", html.Br(),
                            "⚡ Faible: Moins strict", html.Br(),
                            "🔥 Élevé: Volume explosif requis"
                        ], target="breakout-volume-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="breakout-volume-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-breakout-volume-threshold",
                            min=0.2, max=2.0, step=0.1, value=0.5,
                            marks={0.2: '0.2x', 0.5: '0.5x', 2.0: '2x'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6)
                ], className="mt-2"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Seuil Breakout %", className="fw-bold"),
                        dbc.Tooltip([
                            "💥 % minimum de cassure du niveau", html.Br(),
                            "⚡ Faible: Breakouts sensibles", html.Br(),
                            "🎯 Élevé: Breakouts confirmés"
                        ], target="breakout-threshold-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="breakout-threshold-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-breakout-threshold",
                            min=0.01, max=0.1, step=0.01, value=0.03,
                            marks={0.01: '1%', 0.03: '3%', 0.1: '10%'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Barres Confirmation", className="fw-bold"),
                        dbc.Tooltip([
                            "📊 Nombre de barres pour confirmer", html.Br(),
                            "⚡ 1: Confirmation rapide", html.Br(),
                            "🎯 5: Confirmation solide"
                        ], target="breakout-confirmation-tooltip", placement="top"),
                        html.I(className="fas fa-info-circle ms-1", id="breakout-confirmation-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                        dcc.Slider(
                            id="indicators-breakout-confirmation",
                            min=1, max=5, step=1, value=2,
                            marks={1: '1', 2: '2', 5: '5'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-breakout-detector-collapse", is_open=False)
        ])

    # =================================================================
    # CALLBACKS SYNCHRONISATION NOUVEAUX INDICATEURS - PHASE 3
    # =================================================================
    
    # Callback de synchronisation automatique Squeeze Momentum selon le style
    @app.callback(
        [Output('indicators-squeeze-period', 'value'),
         Output('indicators-squeeze-sensitivity', 'value')],
        [Input('indicators-trading-style', 'value')],
        prevent_initial_call=True
    )
    def sync_squeeze_momentum_with_style(trading_style):
        """Synchronise automatiquement les paramètres Squeeze Momentum avec le style sélectionné"""
        if not trading_style:
            return dash.no_update, dash.no_update
        
        try:
            # Récupérer la configuration du style pour Squeeze Momentum
            style_config = trading_style_manager.get_style_config(trading_style)
            squeeze_config = style_config.get('squeeze_momentum')
            
            if squeeze_config and hasattr(squeeze_config, 'parameters'):
                params = squeeze_config.parameters
                
                # Mettre à jour les contrôles avec les paramètres du style
                period = params.get('bb_period', 20)
                sensitivity = params.get('momentum_period', 12) // 2  # Convertir en sensibilité 1-10
                
                print(f"🔄 Sync Squeeze Momentum avec style {trading_style}: period={period}, sensitivity={sensitivity}")
                
                return period, sensitivity
            
        except Exception as e:
            print(f"❌ Erreur synchronisation Squeeze Momentum: {e}")
        
        return dash.no_update, dash.no_update
    
    # Callback de synchronisation automatique Candle Patterns selon le style
    @app.callback(
        [Output('indicators-doji-threshold', 'value'),
         Output('indicators-hammer-ratio', 'value'),
         Output('indicators-pattern-volume-confirm', 'value'),
         Output('indicators-pattern-labels', 'value')],
        [Input('indicators-trading-style', 'value')],
        prevent_initial_call=True
    )
    def sync_candle_patterns_with_style(trading_style):
        """Synchronise automatiquement les paramètres Candle Patterns avec le style sélectionné"""
        if not trading_style:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Récupérer la configuration du style pour Candle Patterns
            style_config = trading_style_manager.get_style_config(trading_style)
            patterns_config = style_config.get('candle_patterns')
            
            if patterns_config and hasattr(patterns_config, 'parameters'):
                params = patterns_config.parameters
                
                # Mettre à jour les contrôles avec les paramètres du style
                doji_threshold = params.get('doji_threshold', 0.1)
                hammer_ratio = params.get('hammer_ratio', 2.0)
                volume_confirm = params.get('engulfing_volume_confirm', True)
                show_labels = params.get('show_labels', True)
                
                print(f"🔄 Sync Candle Patterns avec style {trading_style}: doji={doji_threshold}, hammer={hammer_ratio}, volume={volume_confirm}, labels={show_labels}")
                
                return doji_threshold, hammer_ratio, volume_confirm, show_labels
            
        except Exception as e:
            print(f"❌ Erreur synchronisation Candle Patterns: {e}")
        
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Callback de synchronisation automatique Breakout Detector selon le style
    @app.callback(
        [Output('indicators-breakout-strength', 'value'),
         Output('indicators-breakout-volume-threshold', 'value'),
         Output('indicators-breakout-threshold', 'value'),
         Output('indicators-breakout-confirmation', 'value')],
        [Input('indicators-trading-style', 'value')],
        prevent_initial_call=True
    )
    def sync_breakout_detector_with_style(trading_style):
        """Synchronise automatiquement les paramètres Breakout Detector avec le style sélectionné"""
        if not trading_style:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Récupérer la configuration du style pour Breakout Detector
            style_config = trading_style_manager.get_style_config(trading_style)
            breakout_config = style_config.get('breakout_detector')
            
            if breakout_config and hasattr(breakout_config, 'parameters'):
                params = breakout_config.parameters
                
                # Mettre à jour les contrôles avec les paramètres du style
                strength = params.get('sr_strength', 2)
                volume_threshold = params.get('volume_threshold', 0.5)
                breakout_threshold = params.get('breakout_threshold', 0.03)
                confirmation = params.get('confirmation_bars', 2)
                
                print(f"🔄 Sync Breakout Detector avec style {trading_style}: strength={strength}, volume={volume_threshold}, threshold={breakout_threshold}, confirmation={confirmation}")
                
                return strength, volume_threshold, breakout_threshold, confirmation
            
        except Exception as e:
            print(f"❌ Erreur synchronisation Breakout Detector: {e}")
        
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # =================================================================
    # SECTION VOLUME PROFILE - PHASE 4
    # =================================================================
    
    def _create_volume_profile_section(self) -> html.Div:
        """Section Volume Profile + POC - Analyse Distribution Volume"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        "Volume Profile + POC",
                        html.I(className="fas fa-chart-area ms-2", 
                               id="volume-profile-tooltip-target",
                               style={"color": "#ff6b35", "cursor": "pointer"})
                    ], className="fw-bold text-warning"),
                    dbc.Tooltip([
                        html.Strong("📊 Volume Profile - Distribution du Volume par Prix"), html.Br(),
                        "🎯 POC: Point of Control = prix avec le plus gros volume", html.Br(),
                        "💹 Value Area: Zone contenant 70% du volume total", html.Br(),
                        "🔥 HVN: High Volume Nodes = supports/résistances forts", html.Br(),
                        "💴 Histogramme: Visualisation horizontale du volume", html.Br(),
                        "⚡ Trading: POC = zones de retournement, Value Area = limites clés"
                    ], target="volume-profile-tooltip-target", placement="right"),
                    html.P("Analyse distribution volume avec POC et Value Area", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-volume-profile-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Tabs([
                    
                    # Onglet Configuration de Base
                    dbc.Tab(label="⚙️ Base", tab_id="volume-profile-base", children=[
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Nombre de Niveaux", className="fw-bold"),
                                    dbc.Tooltip([
                                        "📊 Niveaux de prix pour histogramme", html.Br(),
                                        "⚡ Peu: Plus lisible, moins précis", html.Br(),
                                        "🎯 Beaucoup: Plus précis, plus dense"
                                    ], target="volume-bins-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="volume-bins-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dcc.Slider(
                                        id="indicators-volume-bins",
                                        min=25, max=200, step=25, value=100,
                                        marks={25: '25', 100: '100', 200: '200'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Période d'Analyse", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🕰️ Nombre de bougies à analyser", html.Br(),
                                        "⚡ Court: Profil réactif, récent", html.Br(),
                                        "🎯 Long: Profil stable, historique"
                                    ], target="volume-lookback-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="volume-lookback-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dcc.Slider(
                                        id="indicators-volume-lookback",
                                        min=50, max=500, step=50, value=100,
                                        marks={50: '50', 100: '100', 500: '500'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ], className="mt-2"),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Value Area %", className="fw-bold"),
                                    dbc.Tooltip([
                                        "💹 % du volume pour Value Area", html.Br(),
                                        "📈 Standard: 70% (norme institutionnelle)", html.Br(),
                                        "⚡ Plus bas: Zone plus étroite", html.Br(),
                                        "🎯 Plus haut: Zone plus large"
                                    ], target="value-area-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="value-area-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dcc.Slider(
                                        id="indicators-value-area-percent",
                                        min=50, max=90, step=5, value=70,
                                        marks={50: '50%', 70: '70%', 90: '90%'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Sensibilité POC", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🎯 Sensibilité détection POC", html.Br(),
                                        "⚡ Faible: POC plus stable", html.Br(),
                                        "🔥 Élevé: POC plus réactif"
                                    ], target="poc-sensitivity-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="poc-sensitivity-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dcc.Slider(
                                        id="indicators-poc-sensitivity",
                                        min=0.5, max=2.0, step=0.1, value=1.0,
                                        marks={0.5: '0.5x', 1.0: '1x', 2.0: '2x'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ], className="mt-2")
                        ], className="p-3")
                    ]),
                    
                    # Onglet Visualisation
                    dbc.Tab(label="🎨 Affichage", tab_id="volume-profile-display", children=[
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Afficher POC", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🎯 Point of Control (prix max volume)", html.Br(),
                                        "✅ Ligne horizontale orange", html.Br(),
                                        "💹 Zone de retournement importante"
                                    ], target="show-poc-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="show-poc-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dbc.Switch(
                                        id="indicators-show-poc",
                                        value=True,
                                        className="mt-2"
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Afficher Value Area", className="fw-bold"),
                                    dbc.Tooltip([
                                        "💹 Zone 70% du volume", html.Br(),
                                        "✅ Zone colorée bleu-vert", html.Br(),
                                        "💴 Limites clés du marché"
                                    ], target="show-value-area-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="show-value-area-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dbc.Switch(
                                        id="indicators-show-value-area",
                                        value=True,
                                        className="mt-2"
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Histogramme Volume", className="fw-bold"),
                                    dbc.Tooltip([
                                        "📊 Barres horizontales volume", html.Br(),
                                        "✅ Visualisation distribution", html.Br(),
                                        "🔥 Intensité par niveau prix"
                                    ], target="show-histogram-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="show-histogram-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dbc.Switch(
                                        id="indicators-show-histogram",
                                        value=True,
                                        className="mt-2"
                                    )
                                ], width=4)
                            ], className="mt-2"),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("High Volume Nodes", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🔥 Niveaux à fort volume", html.Br(),
                                        "✅ Supports/Résistances forts", html.Br(),
                                        "💴 Zones de consolidation"
                                    ], target="show-hvn-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="show-hvn-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dbc.Switch(
                                        id="indicators-show-hvn",
                                        value=True,
                                        className="mt-2"
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Seuil HVN %", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🔥 % volume pour être HVN", html.Br(),
                                        "⚡ Faible: Plus de HVN", html.Br(),
                                        "🎯 Élevé: Seulement majeurs"
                                    ], target="hvn-threshold-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="hvn-threshold-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dcc.Slider(
                                        id="indicators-hvn-threshold",
                                        min=60, max=95, step=5, value=80,
                                        marks={60: '60%', 80: '80%', 95: '95%'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ], className="mt-2")
                        ], className="p-3")
                    ]),
                    
                    # Onglet Alertes
                    dbc.Tab(label="🔔 Alertes", tab_id="volume-profile-alerts", children=[
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Alertes POC", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🔔 Alerte approche POC", html.Br(),
                                        "✅ Signal retournement potentiel", html.Br(),
                                        "🎯 Zone de trading importante"
                                    ], target="poc-alerts-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="poc-alerts-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dbc.Switch(
                                        id="indicators-poc-alerts",
                                        value=True,
                                        className="mt-2"
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Distance POC %", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🎯 % distance pour alerte POC", html.Br(),
                                        "⚡ Faible: Alertes plus fréquentes", html.Br(),
                                        "🔥 Élevé: Seulement très proche"
                                    ], target="poc-distance-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="poc-distance-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dcc.Slider(
                                        id="indicators-poc-proximity",
                                        min=0.1, max=2.0, step=0.1, value=0.5,
                                        marks={0.1: '0.1%', 0.5: '0.5%', 2.0: '2%'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ], className="mt-2"),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Alertes Value Area", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🔔 Alerte cassure Value Area", html.Br(),
                                        "✅ Signal mouvement important", html.Br(),
                                        "💥 Breakout hors zone principale"
                                    ], target="va-alerts-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="va-alerts-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dbc.Switch(
                                        id="indicators-va-alerts",
                                        value=True,
                                        className="mt-2"
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Opacité Histogramme", className="fw-bold"),
                                    dbc.Tooltip([
                                        "🎨 Transparence histogramme", html.Br(),
                                        "⚡ Faible: Discret, fond", html.Br(),
                                        "🔥 Élevé: Très visible"
                                    ], target="histogram-opacity-tooltip", placement="top"),
                                    html.I(className="fas fa-info-circle ms-1", id="histogram-opacity-tooltip", style={"font-size": "0.8rem", "color": "#6c757d"}),
                                    dcc.Slider(
                                        id="indicators-histogram-opacity",
                                        min=20, max=100, step=10, value=60,
                                        marks={20: '20%', 60: '60%', 100: '100%'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ], className="mt-2")
                        ], className="p-3")
                    ])
                    
                ], id="volume-profile-tabs", active_tab="volume-profile-base")
            ], id="indicators-volume-profile-collapse", is_open=False)
        ])
    
    # Callback de synchronisation automatique Volume Profile selon le style
    @app.callback(
        [Output('indicators-volume-bins', 'value'),
         Output('indicators-volume-lookback', 'value'),
         Output('indicators-value-area-percent', 'value'),
         Output('indicators-poc-sensitivity', 'value'),
         Output('indicators-hvn-threshold', 'value'),
         Output('indicators-histogram-opacity', 'value')],
        [Input('indicators-trading-style', 'value')],
        prevent_initial_call=True
    )
    def sync_volume_profile_with_style(trading_style):
        """Synchronise automatiquement les paramètres Volume Profile avec le style sélectionné"""
        if not trading_style:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Récupérer la configuration du style pour Volume Profile
            style_config = trading_style_manager.get_style_config(trading_style)
            vp_config = style_config.get('volume_profile')
            
            if vp_config and hasattr(vp_config, 'parameters'):
                params = vp_config.parameters
                
                # Mettre à jour les contrôles avec les paramètres du style
                bins_count = params.get('bins_count', 100)
                lookback_periods = params.get('lookback_periods', 100)
                value_area_percent = params.get('value_area_percent', 70.0)
                poc_sensitivity = params.get('poc_sensitivity', 1.0)
                hvn_threshold = params.get('high_volume_threshold', 80.0)
                histogram_opacity = int(params.get('histogram_opacity', 0.6) * 100)  # Convertir en %
                
                print(f"🔄 Sync Volume Profile avec style {trading_style}: bins={bins_count}, lookback={lookback_periods}, VA={value_area_percent}%, POC={poc_sensitivity}, HVN={hvn_threshold}%, opacity={histogram_opacity}%")
                
                return bins_count, lookback_periods, value_area_percent, poc_sensitivity, hvn_threshold, histogram_opacity
            
        except Exception as e:
            print(f"❌ Erreur synchronisation Volume Profile: {e}")
        
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Store pour sauvegarder la configuration des indicateurs
indicators_store = dcc.Store(id='indicators-config-store', data=indicators_modal.indicators_config)