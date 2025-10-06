# Suggestion de paramètres avancés pour FVG - Configuration manuelle

# === PARAMÈTRES DE DÉTECTION AVANCÉE ===

# 1. CRITÈRES DE FORMATION
confluence_zones: bool = True           # Détecter les zones de confluence (plusieurs gaps proches)
confluence_distance: float = 0.5       # Distance max (%) pour considérer confluence
multi_timeframe: bool = False          # Analyser plusieurs timeframes simultanément
timeframe_confirmation: list = []      # Liste des TF pour confirmation [15m, 1h, 4h]

# 2. VALIDATION SOPHISTIQUÉE
price_action_filter: bool = True       # Filtrer selon l'action de prix (doji, hammer, etc.)
volatility_threshold: float = 0.8      # Seuil de volatilité (ATR) pour validation
liquidity_sweep: bool = True           # Détecter les balayages de liquidité avant gap
structural_break: bool = True          # Confirmer avec cassure de structure

# 3. QUALITÉ DU GAP
gap_quality_score: bool = True         # Calculer score de qualité (0-100)
momentum_confirmation: bool = True     # Confirmer avec momentum (RSI, MACD)
order_flow_analysis: bool = False      # Analyser l'order flow (si données disponibles)
institutional_hours: bool = True       # Privilégier gaps créés aux heures institutionnelles

# === PARAMÈTRES DE GESTION TEMPORELLE ===

# 4. SESSIONS DE MARCHÉ
asian_session: bool = True             # Détecter gaps session asiatique
london_session: bool = True            # Détecter gaps session de Londres  
new_york_session: bool = True          # Détecter gaps session de New York
overlap_sessions: bool = True          # Privilégier gaps créés lors de chevauchements

# 5. ÉVÉNEMENTS DE MARCHÉ
news_filter: bool = True               # Éviter gaps créés par actualités
earnings_filter: bool = False          # Éviter gaps liés aux résultats d'entreprises
weekend_gaps: bool = False             # Inclure/exclure gaps de weekend
holiday_gaps: bool = False             # Inclure/exclure gaps de jours fériés

# === PARAMÈTRES DE VALIDATION TECHNIQUE ===

# 6. INDICATEURS TECHNIQUES
rsi_confirmation: bool = False         # Confirmer avec niveaux RSI
rsi_overbought: float = 70            # Seuil de surachat RSI
rsi_oversold: float = 30              # Seuil de survente RSI

macd_confirmation: bool = False        # Confirmer avec signal MACD
bollinger_confirmation: bool = False   # Confirmer avec Bollinger Bands

# 7. STRUCTURE DE MARCHÉ
support_resistance: bool = True        # Prioriser gaps près de S/R
fibonacci_levels: bool = True          # Prioriser gaps aux niveaux Fibonacci
pivot_points: bool = True              # Prioriser gaps aux pivots
trend_direction: bool = True           # Filtrer selon direction de tendance

# === PARAMÈTRES DE PERFORMANCE ===

# 8. GESTION DES RETESTS
retest_sensitivity: float = 0.1       # Sensibilité pour détecter retests (%)
max_retest_count: int = 3              # Nombre max de retests avant invalidation
retest_timeframe: int = 20             # Délai max pour premier retest (bougies)
partial_fill_tracking: bool = True    # Suivre remplissages partiels détaillés

# 9. FORCE ET SCORING
strength_algorithm: str = "advanced"    # "simple", "advanced", "ml"
volume_weight: float = 0.4             # Poids du volume dans le calcul de force
size_weight: float = 0.3               # Poids de la taille dans le calcul
age_weight: float = 0.2                # Poids de l'âge dans le calcul
retest_weight: float = 0.1             # Poids des retests dans le calcul

# === PARAMÈTRES D'AFFICHAGE AVANCÉ ===

# 10. VISUALISATION SOPHISTIQUÉE
gradient_fill: bool = False            # Remplissage dégradé selon la force
dynamic_opacity: bool = True           # Opacité dynamique selon l'âge
age_color_transition: bool = True      # Transition de couleur selon l'âge
strength_line_width: bool = True       # Épaisseur de ligne selon la force

# 11. LABELS ET INFORMATIONS
show_gap_id: bool = False              # Afficher ID unique du gap
show_creation_time: bool = True        # Afficher heure de création
show_volume_ratio: bool = True         # Afficher ratio de volume
show_retest_count: bool = True         # Afficher nombre de retests
show_distance_to_price: bool = True    # Afficher distance au prix actuel

# === PARAMÈTRES DE TRADING ===

# 12. SIGNAUX AUTOMATIQUES  
auto_alerts: bool = False              # Générer alertes automatiques
alert_distance: float = 0.2            # Distance (%) pour déclencher alerte
entry_signals: bool = False            # Générer signaux d'entrée
exit_signals: bool = False             # Générer signaux de sortie

# 13. GESTION DU RISQUE
stop_loss_ratio: float = 0.5           # Ratio SL par rapport à la taille du gap
take_profit_ratio: float = 2.0         # Ratio TP par rapport au SL
risk_reward_min: float = 1.5           # R/R minimum pour signaler une opportunité

# === PARAMÈTRES D'OPTIMISATION ===

# 14. PERFORMANCE
max_gaps_display: int = 50             # Nombre max de gaps affichés
historical_analysis: bool = False      # Analyser performance historique
backtest_mode: bool = False            # Mode backtest pour optimisation
cache_calculations: bool = True        # Mettre en cache les calculs lourds

# 15. FILTRES AVANCÉS
min_market_cap: float = 0              # Cap market minimum (pour cryptos)
min_daily_volume: float = 0            # Volume quotidien minimum
spread_filter: bool = False            # Filtrer selon le spread bid/ask
slippage_consideration: bool = False   # Considérer le slippage potentiel