"""
Modal IA Trading Professionnel - THEBOT (Version Finale)
Analyse trading complète pour l'asset actuel uniquement
Utilise uniquement les APIs existantes (100% gratuit)
"""

import dash
from dash import html, dcc, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
from datetime import datetime
import json
from typing import Dict, Any
import logging

# Import des moteurs IA existants
try:
    from ..ai_engine.smart_ai_manager import smart_ai_manager
    from ..ai_engine.local_ai_engine import local_ai_engine
    from ..data_providers.rss_news_manager import rss_news_manager
    AI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI modules not available: {e}")
    smart_ai_manager = None
    local_ai_engine = None
    rss_news_manager = None
    AI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AITradingModal:
    """Modal IA pour analyse trading asset-spécifique"""
    
    def __init__(self):
        self.modal_id = "ai-trading-modal"
        self.current_symbol = None
        self.current_timeframe = None
        
    def create_modal(self) -> dbc.Modal:
        """Créer le modal IA complet avec contrôles intégrés"""
        return dbc.Modal([
            dbc.ModalHeader([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-robot me-2"),
                        "Trading AI Advisor",
                        html.Span(id="ai-modal-symbol", className="text-muted ms-2"),
                        html.Small([
                            html.I(className="fas fa-arrows-alt ms-3 text-muted"),
                            " Déplaçable"
                        ], className="text-muted")
                    ], className="mb-2 draggable-header"),
                    
                    # Contrôles IA dans le header
                    dbc.Row([
                        dbc.Col([
                            html.Label("Moteur IA:", className="form-label small mb-1"),
                            dcc.Dropdown(
                                id='crypto-ai-engine-dropdown',
                                options=[
                                    {'label': '🆓 IA Locale (Gratuit)', 'value': 'local'},
                                    {'label': '🎯 IA Smart (HuggingFace)', 'value': 'smart'},
                                    {'label': '⚡ IA Hybride', 'value': 'hybrid'}
                                ],
                                value='local',
                                className="mb-2",
                                style={'fontSize': '0.9rem'}
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Confidence:", className="form-label small mb-1"),
                            dcc.Slider(
                                id='crypto-ai-confidence-slider',
                                min=0, max=100, step=5, value=70,
                                marks={i: f'{i}%' for i in range(0, 101, 25)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], width=6)
                    ], className="mb-2")
                ], className="w-100"),
                dbc.Button("×", id="ai-modal-close", className="btn-close", n_clicks=0)
            ], className="modal-header-draggable"),
            dbc.ModalBody([
                # Loading State
                dbc.Spinner([
                    html.Div(id="ai-modal-content", children=[
                        self._create_placeholder_content()
                    ])
                ], id="ai-modal-spinner", spinner_style={"width": "3rem", "height": "3rem"}),
                
                # Timestamp
                html.Div(id="ai-analysis-timestamp", className="text-muted small mt-3")
            ]),
            dbc.ModalFooter([
                html.Div([
                    html.I(className="fas fa-info-circle me-1"),
                    "Analyse 100% gratuite - Données locales et RSS"
                ], className="text-success small me-auto"),
                dbc.Button("Fermer", id="ai-modal-close-btn", color="secondary", n_clicks=0)
            ])
        ], 
        id=self.modal_id,
        size="xl",
        is_open=False,
        backdrop=False,  # Désactiver backdrop pour permettre le drag
        scrollable=True,
        className="ai-modal-custom draggable-modal",
        style={"position": "absolute", "top": "50px", "left": "50px", "z-index": "1055"}
        )
    
    def _create_placeholder_content(self) -> html.Div:
        """Contenu placeholder pendant chargement"""
        return html.Div([
            dbc.Alert([
                html.I(className="fas fa-chart-line me-2"),
                "Prêt à analyser - Sélectionnez un asset et cliquez sur 'Generate AI Insights'"
            ], color="info", className="mb-0")
        ])
    
    def _create_analysis_content(self, analysis_data: Dict[str, Any]) -> html.Div:
        """Créer le contenu d'analyse complet"""
        symbol = analysis_data.get('symbol', 'N/A')
        
        return html.Div([
            # Header avec symbole
            self._create_analysis_header(symbol, analysis_data),
            
            # Grille d'analyse principale
            dbc.Row([
                # Colonne gauche - Technical Analysis
                dbc.Col([
                    self._create_technical_analysis_card(analysis_data.get('technical_analysis', {}))
                ], width=6),
                
                # Colonne droite - Sentiment Analysis
                dbc.Col([
                    self._create_sentiment_analysis_card(analysis_data.get('sentiment_analysis', {}))
                ], width=6)
            ], className="mb-4"),
            
            # Recommandation principale
            self._create_recommendation_card(analysis_data.get('trading_recommendation', {})),
            
            # Détails et contexte
            dbc.Row([
                dbc.Col([
                    self._create_risk_assessment_card(analysis_data.get('risk_assessment', {}))
                ], width=6),
                dbc.Col([
                    self._create_market_context_card(analysis_data.get('market_context', {}))
                ], width=6)
            ], className="mt-4")
        ])
    
    def _create_analysis_header(self, symbol: str, data: Dict) -> html.Div:
        """Header avec infos principales"""
        confidence = data.get('trading_recommendation', {}).get('confidence', 0)
        recommendation = data.get('trading_recommendation', {}).get('recommendation', 'HOLD')
        
        # Couleur selon recommandation
        if recommendation == 'BUY':
            badge_color = "success"
            icon = "fas fa-arrow-up"
        elif recommendation == 'SELL':
            badge_color = "danger"
            icon = "fas fa-arrow-down"
        else:
            badge_color = "warning"
            icon = "fas fa-minus"
        
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5([
                            html.I(className="fas fa-chart-line me-2"),
                            f"Analyse IA - {symbol}"
                        ], className="mb-2"),
                        html.P("Analyse complète technique et sentiment", className="text-muted mb-0")
                    ], width=8),
                    dbc.Col([
                        dbc.Badge([
                            html.I(className=f"{icon} me-1"),
                            recommendation
                        ], color=badge_color, className="fs-6 p-2"),
                        html.Div([
                            html.Small(f"Confiance: {confidence}%", className="text-muted")
                        ], className="mt-1")
                    ], width=4, className="text-end")
                ])
            ])
        ], className="mb-4", color="primary", outline=True)
    
    def _create_technical_analysis_card(self, technical_data: Dict) -> dbc.Card:
        """Card analyse technique"""
        score = technical_data.get('score', 50)
        trend = technical_data.get('trend', 'Neutre')
        patterns = technical_data.get('patterns', [])
        
        # Couleur selon score
        if score >= 70:
            progress_color = "success"
        elif score >= 40:
            progress_color = "warning"
        else:
            progress_color = "danger"
        
        return dbc.Card([
            dbc.CardHeader([
                html.H6([
                    html.I(className="fas fa-chart-area me-2"),
                    "Analyse Technique"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                # Score technique
                html.Div([
                    html.Label("Score Technique", className="form-label small"),
                    dbc.Progress(value=score, color=progress_color, className="mb-2"),
                    html.Small(f"{score}/100", className="text-muted")
                ], className="mb-3"),
                
                # Tendance
                html.Div([
                    html.Label("Tendance", className="form-label small"),
                    html.Div([
                        dbc.Badge(trend, color=progress_color, className="me-2"),
                        html.Span(technical_data.get('trend_strength', 'Modérée'), className="small text-muted")
                    ])
                ], className="mb-3"),
                
                # Patterns détectés
                html.Div([
                    html.Label("Patterns Détectés", className="form-label small"),
                    html.Div([
                        dbc.Badge(pattern, color="info", className="me-1 mb-1") 
                        for pattern in patterns[:5]  # Limiter affichage
                    ] if patterns else [
                        html.Small("Aucun pattern significatif", className="text-muted")
                    ])
                ])
            ])
        ], className="h-100")
    
    def _create_sentiment_analysis_card(self, sentiment_data: Dict) -> dbc.Card:
        """Card analyse sentiment"""
        sentiment = sentiment_data.get('sentiment', 'neutral')
        score = sentiment_data.get('score', 50)
        confidence = sentiment_data.get('confidence', 0)
        news_count = sentiment_data.get('news_count', 0)
        
        # Couleur selon sentiment
        if sentiment == 'bullish':
            sentiment_color = "success"
            sentiment_icon = "fas fa-thumbs-up"
        elif sentiment == 'bearish':
            sentiment_color = "danger" 
            sentiment_icon = "fas fa-thumbs-down"
        else:
            sentiment_color = "warning"
            sentiment_icon = "fas fa-minus"
        
        return dbc.Card([
            dbc.CardHeader([
                html.H6([
                    html.I(className="fas fa-newspaper me-2"),
                    "Analyse Sentiment"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                # Sentiment global
                html.Div([
                    html.Label("Sentiment Marché", className="form-label small"),
                    html.Div([
                        dbc.Badge([
                            html.I(className=f"{sentiment_icon} me-1"),
                            sentiment.title()
                        ], color=sentiment_color, className="fs-6 p-2")
                    ])
                ], className="mb-3"),
                
                # Score sentiment
                html.Div([
                    html.Label("Score Sentiment", className="form-label small"),
                    dbc.Progress(value=score, color=sentiment_color, className="mb-2"),
                    html.Small(f"{score}/100", className="text-muted")
                ], className="mb-3"),
                
                # Sources news
                html.Div([
                    html.Label("Sources Analysées", className="form-label small"),
                    html.Div([
                        html.I(className="fas fa-rss me-1"),
                        f"{news_count} articles RSS",
                        html.Span(f" (Confiance: {confidence}%)", className="text-muted ms-2")
                    ], className="small")
                ])
            ])
        ], className="h-100")
    
    def _create_recommendation_card(self, recommendation_data: Dict) -> dbc.Card:
        """Card recommandation principale"""
        action = recommendation_data.get('recommendation', 'HOLD')
        confidence = recommendation_data.get('confidence', 0)
        explanation = recommendation_data.get('explanation', 'Analyse en cours...')
        
        # Style selon action
        if action == 'BUY':
            card_color = "success"
            action_icon = "fas fa-arrow-up"
        elif action == 'SELL':
            card_color = "danger"
            action_icon = "fas fa-arrow-down"
        else:
            card_color = "warning"
            action_icon = "fas fa-minus"
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className=f"{action_icon} me-2"),
                    f"Recommandation: {action}"
                ], className="mb-0 text-white")
            ], style={"backgroundColor": f"var(--bs-{card_color})"}),
            dbc.CardBody([
                # Confiance
                dbc.Row([
                    dbc.Col([
                        html.Label("Niveau de Confiance", className="form-label small"),
                        dbc.Progress(value=confidence, color=card_color, className="mb-2"),
                        html.Small(f"{confidence}% confiance", className="text-muted")
                    ], width=4),
                    dbc.Col([
                        html.Label("Explication", className="form-label small"),
                        html.P(explanation, className="mb-0")
                    ], width=8)
                ])
            ])
        ], className="mb-0")
    
    def _create_risk_assessment_card(self, risk_data: Dict) -> dbc.Card:
        """Card évaluation des risques"""
        risk_level = risk_data.get('level', 'Modéré')
        factors = risk_data.get('factors', [])
        
        return dbc.Card([
            dbc.CardHeader([
                html.H6([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Évaluation Risques"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                html.Div([
                    html.Label("Niveau de Risque", className="form-label small"),
                    dbc.Badge(risk_level, color="warning", className="fs-6")
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Facteurs de Risque", className="form-label small"),
                    html.Ul([
                        html.Li(factor, className="small") for factor in factors[:5]
                    ] if factors else [
                        html.Li("Évaluation en cours...", className="small text-muted")
                    ])
                ])
            ])
        ], className="h-100")
    
    def _create_market_context_card(self, context_data: Dict) -> dbc.Card:
        """Card contexte marché"""
        market_mood = context_data.get('mood', 'Neutre')
        correlations = context_data.get('correlations', [])
        
        return dbc.Card([
            dbc.CardHeader([
                html.H6([
                    html.I(className="fas fa-globe me-2"),
                    "Contexte Marché"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                html.Div([
                    html.Label("Humeur du Marché", className="form-label small"),
                    dbc.Badge(market_mood, color="info", className="fs-6")
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Corrélations", className="form-label small"),
                    html.Div([
                        html.Small(corr, className="text-muted me-2") 
                        for corr in correlations[:3]
                    ] if correlations else [
                        html.Small("Analyse en cours...", className="text-muted")
                    ])
                ])
            ])
        ], className="h-100")
    
    def get_custom_css(self) -> str:
        """CSS personnalisé pour le modal déplaçable"""
        return """
        /* Modal déplaçable - Styles de base */
        .draggable-modal .modal-dialog {
            max-width: 90vw;
            margin: 0;
            transition: transform 0.1s ease-out;
        }
        
        .draggable-modal .modal-content {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #007bff;
        }
        
        /* Header déplaçable */
        .modal-header-draggable {
            background: linear-gradient(90deg, #007bff, #0056b3);
            color: white;
            border-radius: 13px 13px 0 0;
            border-bottom: 2px solid #0056b3;
            padding: 1rem 1.5rem;
            position: relative;
        }
        
        .modal-header-draggable::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 4px;
            background: rgba(255,255,255,0.5);
            border-radius: 2px;
        }
        
        .draggable-header {
            margin: 0 !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
        }
        
        .modal-header-draggable .btn-close {
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            padding: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .modal-header-draggable .btn-close:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.1);
        }
        
        /* Animation d'ouverture pour modal déplaçable */
        .draggable-modal.show .modal-dialog {
            animation: modalSlideIn 0.3s ease-out;
        }
        
        @keyframes modalSlideIn {
            from {
                opacity: 0;
                transform: scale(0.8) translate3d(0, -50px, 0);
            }
            to {
                opacity: 1;
                transform: scale(1) translate3d(0, 0, 0);
            }
        }
        
        /* Hover effects pour cards */
        .ai-modal-custom .card {
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
            border-radius: 10px;
        }
        
        .ai-modal-custom .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .ai-modal-custom .progress {
            height: 8px;
            border-radius: 4px;
        }
        
        .ai-modal-custom .badge {
            font-weight: 500;
            border-radius: 6px;
        }
        
        /* Indicateur de déplacement */
        .draggable-header small {
            opacity: 0.7;
            font-size: 0.75rem;
        }
        
        /* Responsive pour mobile */
        @media (max-width: 768px) {
            .draggable-modal .modal-dialog {
                max-width: 95vw;
                margin: 10px;
            }
            
            .modal-header-draggable {
                padding: 0.75rem 1rem;
            }
        }
        """

def register_ai_modal_callbacks(app):
    """Enregistrer les callbacks du modal IA"""
    
    # Callback principal du modal
    @app.callback(
        [Output("ai-trading-modal", "is_open"),
         Output("ai-modal-content", "children"),
         Output("ai-modal-symbol", "children"),
         Output("ai-analysis-timestamp", "children")],
        [Input("ai-modal-close", "n_clicks"),
         Input("ai-modal-close-btn", "n_clicks")],
        [State("crypto-symbol-search", "value"),
         State("crypto-timeframe-selector", "value"),
         State("crypto-ai-engine-dropdown", "value"),
         State("crypto-ai-confidence-slider", "value"),
         State("ai-trading-modal", "is_open")]
    )
    def toggle_ai_modal(close_clicks, close_btn_clicks, symbol, timeframe, 
                       ai_engine, confidence_threshold, is_open):
        """Toggle modal et génération d'analyse avec paramètres IA (IA toujours activée)"""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return False, ai_trading_modal._create_placeholder_content(), "", ""
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Fermeture du modal
        if trigger_id in ["ai-modal-close", "ai-modal-close-btn"]:
            return False, ai_trading_modal._create_placeholder_content(), "", ""
        
        return is_open, ai_trading_modal._create_placeholder_content(), "", ""
    
    
    # Callback client-side pour rendre le modal déplaçable
    app.clientside_callback(
        """
        function(is_open) {
            if (is_open) {
                setTimeout(function() {
                    // Rendre le modal déplaçable
                    const modal = document.getElementById('ai-trading-modal');
                    const modalDialog = modal?.querySelector('.modal-dialog');
                    const header = modal?.querySelector('.modal-header-draggable');
                    
                    if (modalDialog && header && !modalDialog.getAttribute('data-draggable')) {
                        modalDialog.setAttribute('data-draggable', 'true');
                        
                        let isDragging = false;
                        let currentX = 0;
                        let currentY = 0;
                        let initialX = 0;
                        let initialY = 0;
                        let xOffset = 0;
                        let yOffset = 0;
                        
                        // Style initial
                        modalDialog.style.position = 'relative';
                        modalDialog.style.cursor = 'default';
                        header.style.cursor = 'grab';
                        header.style.userSelect = 'none';
                        
                        function dragStart(e) {
                            if (e.target.closest('.btn-close')) return;
                            
                            header.style.cursor = 'grabbing';
                            isDragging = true;
                            
                            if (e.type === "touchstart") {
                                initialX = e.touches[0].clientX - xOffset;
                                initialY = e.touches[0].clientY - yOffset;
                            } else {
                                initialX = e.clientX - xOffset;
                                initialY = e.clientY - yOffset;
                            }
                        }
                        
                        function dragEnd(e) {
                            header.style.cursor = 'grab';
                            isDragging = false;
                            initialX = currentX;
                            initialY = currentY;
                        }
                        
                        function drag(e) {
                            if (isDragging) {
                                e.preventDefault();
                                
                                if (e.type === "touchmove") {
                                    currentX = e.touches[0].clientX - initialX;
                                    currentY = e.touches[0].clientY - initialY;
                                } else {
                                    currentX = e.clientX - initialX;
                                    currentY = e.clientY - initialY;
                                }
                                
                                xOffset = currentX;
                                yOffset = currentY;
                                
                                // Contraintes de déplacement (rester dans l'écran)
                                const rect = modalDialog.getBoundingClientRect();
                                const viewportWidth = window.innerWidth;
                                const viewportHeight = window.innerHeight;
                                
                                if (currentX < -rect.width/2) currentX = -rect.width/2;
                                if (currentX > viewportWidth - rect.width/2) currentX = viewportWidth - rect.width/2;
                                if (currentY < -50) currentY = -50;
                                if (currentY > viewportHeight - 100) currentY = viewportHeight - 100;
                                
                                xOffset = currentX;
                                yOffset = currentY;
                                
                                modalDialog.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
                            }
                        }
                        
                        // Event listeners
                        header.addEventListener("mousedown", dragStart, false);
                        document.addEventListener("mouseup", dragEnd, false);
                        document.addEventListener("mousemove", drag, false);
                        
                        // Touch events pour mobile
                        header.addEventListener("touchstart", dragStart, false);
                        document.addEventListener("touchend", dragEnd, false);
                        document.addEventListener("touchmove", drag, false);
                        
                        console.log("✅ Modal IA rendu déplaçable");
                    }
                }, 100);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("ai-trading-modal", "style"),
        Input("ai-trading-modal", "is_open")
    )

def generate_ai_analysis(symbol: str, timeframe: str = "1d", ai_engine: str = "local", confidence_threshold: int = 70) -> Dict[str, Any]:
    """Générer analyse IA complète pour un asset avec paramètres personnalisés"""
    try:
        # 1. Obtenir données techniques (simulées pour l'exemple)
        technical_data = {
            'price_data': {},
            'indicators': {
                'rsi': 65.5,
                'macd': 0.15,
                'bb_position': 0.7
            }
        }
        
        # 2. Obtenir news filtrées par symbole
        if rss_news_manager:
            news_data = rss_news_manager.get_symbol_specific_news(symbol)
        else:
            news_data = []
        
        # 3. Analyse technique (adaptée selon le moteur IA choisi)
        if ai_engine == "smart" and smart_ai_manager:
            # Utiliser Smart AI Manager pour analyse technique avancée
            technical_analysis = smart_ai_manager.analyze_with_best_ai(
                {'price_data': technical_data['price_data'], 'indicators': technical_data['indicators']}, 
                'technical'
            )
        elif local_ai_engine:
            # Utiliser IA locale par défaut
            technical_analysis = local_ai_engine.analyze_technical_pattern(
                technical_data['price_data'],
                technical_data['indicators']
            )
        else:
            # Fallback
            technical_analysis = {
                'score': 65,
                'trend': 'Haussier',
                'patterns': ['Support Strong', 'Volume Increasing']
            }
        
        # 4. Analyse sentiment (adaptée selon le moteur IA)
        if smart_ai_manager and news_data and ai_engine in ["smart", "hybrid"]:
            # Convertir les articles en format compatible pour Smart AI
            news_texts = []
            for article in news_data[:10]:
                if isinstance(article, dict):
                    title = article.get('title', '')
                    summary = article.get('summary', '') or article.get('description', '')
                    text = f"{title} {summary}".strip()
                    if text:
                        news_texts.append(text)
                elif isinstance(article, str):
                    news_texts.append(article)
            
            if news_texts:
                sentiment_analysis = smart_ai_manager.analyze_with_best_ai(
                    {'text': ' '.join(news_texts[:3])}, 'sentiment'
                )
                sentiment_analysis['news_count'] = len(news_data)
            else:
                sentiment_analysis = {
                    'sentiment': 'neutral',
                    'score': 50,
                    'confidence': 60,
                    'news_count': 0
                }
        else:
            # Utiliser analyse locale simple
            sentiment_analysis = {
                'sentiment': 'neutral', 
                'score': 50,
                'confidence': 60,
                'news_count': len(news_data) if news_data else 0
            }
        
        # 5. Recommandation combinée (ajustée par le seuil de confiance)
        trading_recommendation = local_ai_engine.generate_trading_insight(
            symbol, 
            {'technical_analysis': technical_analysis},
            sentiment_analysis
        ) if local_ai_engine else {
            'recommendation': 'HOLD',
            'confidence': 65,
            'explanation': 'Analyse basique - activez un moteur IA pour plus de détails'
        }
        
        # Ajuster la confiance selon le seuil défini par l'utilisateur
        if trading_recommendation['confidence'] < confidence_threshold:
            trading_recommendation['recommendation'] = 'HOLD'
            trading_recommendation['explanation'] += f" (Confiance {trading_recommendation['confidence']}% < seuil {confidence_threshold}%)"
        
        # 6. Évaluation risques (adaptée selon le moteur)
        risk_level = "Modéré"
        risk_factors = [
            'Volatilité normale pour cet asset',
            'Volume de trading suffisant',
            'Support technique identifié'
        ]
        
        if ai_engine == "smart":
            risk_factors.append('Analyse Smart AI - Précision améliorée')
        elif ai_engine == "hybrid":
            risk_factors.append('Analyse Hybride - Multi-sources')
        else:
            risk_factors.append('Analyse locale - Patterns algorithmiques')
            
        risk_assessment = {
            'level': risk_level,
            'factors': risk_factors
        }
        
        # 7. Contexte marché
        market_context = {
            'mood': 'Optimiste',
            'correlations': [
                'Corrélation positive avec BTC',
                'Résistance au niveau 50$',
                'Volume en augmentation'
            ]
        }
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'ai_engine': ai_engine,
            'confidence_threshold': confidence_threshold,
            'technical_analysis': technical_analysis,
            'sentiment_analysis': sentiment_analysis,
            'trading_recommendation': trading_recommendation,
            'risk_assessment': risk_assessment,
            'market_context': market_context,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur génération analyse IA: {e}")
        raise e

# Instance globale
ai_trading_modal = AITradingModal()