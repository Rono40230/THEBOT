"""
Phase 5.2 - Callbacks d'intégration des indicateurs
Connexion des composants UI aux services Phase 5.1
Phase 5.3 - Real-time data integration
"""

from typing import Dict, Any, List, Optional
import json
from decimal import Decimal
import pandas as pd
from dash import callback, Input, Output, State, ctx, ALL, dcc
import dash_bootstrap_components as dbc
from dash import html, dash_table

from src.thebot.core.logger import logger
from src.thebot.services.indicator_integration import get_integration_factory
from src.thebot.services.real_time_updates import get_subscriber, get_signal_aggregator
from src.thebot.services.async_callbacks import get_async_wrapper
from src.thebot.services.data_stream import get_data_stream
from src.thebot.core.types import TimeFrame, SignalDirection


# Singletons for services
_factory = None
_subscriber = None
_aggregator = None
_wrapper = None


def _get_services():
    """Initialiser les services de manière lazy"""
    global _factory, _subscriber, _aggregator, _wrapper
    
    if _factory is None:
        try:
            _factory = get_integration_factory()
            _subscriber = get_subscriber()
            _aggregator = get_signal_aggregator()
            _wrapper = get_async_wrapper()
            logger.info("✅ Services Phase 5.1 initialisés dans callbacks")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation services: {e}")
            raise
    
    return _factory, _subscriber, _aggregator, _wrapper


@callback(
    Output("indicator-params", "children"),
    Input("indicator-selector", "value"),
    prevent_initial_call=False
)
def update_indicator_params(selected_indicator: str) -> List[dbc.Row]:
    """
    Mettre à jour les paramètres d'indicateur
    
    Args:
        selected_indicator: Valeur sélectionnée (format: NAME_category)
        
    Returns:
        Liste des champs de paramètres
    """
    if not selected_indicator:
        return []
    
    try:
        factory, _, _, _ = _get_services()
        
        # Extraire le nom de l'indicateur
        indicator_name = selected_indicator.split("_")[0]
        
        # Paramètres par défaut pour chaque indicateur
        default_params = {
            "SMA": {"period": 20},
            "EMA": {"period": 20},
            "RSI": {"period": 14},
            "ATR": {"period": 14},
            "MACD": {"fast": 12, "slow": 26, "signal": 9},
            "SuperTrend": {"multiplier": 3.0, "period": 10},
            "Squeeze": {"momentum_length": 20, "bb_length": 20},
            "Breakout": {"lookback": 20},
            "Volume Profile": {"bins": 20},
            "OBV": {},
            "FairValueGaps": {"lookback": 20},
        }
        
        params = default_params.get(indicator_name, {})
        
        # Créer des champs de saisie
        param_fields = []
        for param_name, default_value in params.items():
            param_fields.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Input(
                            id={"type": "indicator-param", "index": param_name},
                            type="number",
                            placeholder=f"{param_name}",
                            value=default_value,
                            className="form-control-sm"
                        )
                    ], lg=6),
                    dbc.Col([
                        html.Label(param_name, className="form-label small")
                    ], lg=6),
                ], className="mb-2")
            )
        
        return param_fields
        
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour paramètres: {e}")
        return [html.Div(f"Erreur: {str(e)}", className="alert alert-danger")]


@callback(
    Output("indicator-chart", "figure"),
    Input("indicator-selector", "value"),
    Input("timeframe-selector", "value"),
    State({"type": "indicator-param", "index": ALL}, "value"),
    prevent_initial_call=True
)
def update_indicator_chart(
    selected_indicator: str,
    timeframe: str,
    param_values: List[Any]
) -> Dict[str, Any]:
    """
    Mettre à jour le chart de l'indicateur
    
    Args:
        selected_indicator: Indicateur sélectionné
        timeframe: Timeframe sélectionné
        param_values: Valeurs des paramètres
        
    Returns:
        Figure Plotly
    """
    if not selected_indicator:
        return {
            "data": [],
            "layout": {"title": "Sélectionnez un indicateur"}
        }
    
    try:
        factory, _, _, wrapper = _get_services()
        
        # Extraire le nom et la catégorie
        parts = selected_indicator.split("_")
        indicator_name = parts[0]
        category = parts[1] if len(parts) > 1 else "basic"
        
        # Mapper timeframe
        timeframe_map = {
            "1m": TimeFrame.M1,
            "5m": TimeFrame.M5,
            "15m": TimeFrame.M15,
            "1h": TimeFrame.H1,
            "4h": TimeFrame.H4,
            "1d": TimeFrame.D1,
        }
        tf = timeframe_map.get(timeframe, TimeFrame.H1)
        
        # Construire les paramètres
        params = _build_indicator_params(indicator_name, param_values)
        
        # Calculer l'indicateur
        result = factory.calculate_indicator(
            indicator_name=indicator_name,
            symbol="BTCUSDT",
            timeframe=tf,
            **params
        )
        
        if not result or not hasattr(result, 'chart_data') or not result.chart_data:
            logger.warning(f"Pas de données pour {indicator_name}")
            return {
                "data": [],
                "layout": {"title": f"Aucune donnée pour {indicator_name}"}
            }
        
        # Extraire la figure du plotter
        figure = result.chart_data
        
        return figure
        
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour chart: {e}")
        return {
            "data": [],
            "layout": {"title": f"Erreur: {str(e)}", "xaxis": {}, "yaxis": {}}
        }


@callback(
    Output("comparison-table", "children"),
    Input("comparison-indicators", "value"),
    Input("timeframe-selector", "value"),
    prevent_initial_call=True
)
def update_comparison_table(
    selected_indicators: List[str],
    timeframe: str
) -> html.Div:
    """
    Mettre à jour le tableau de comparaison
    
    Args:
        selected_indicators: Liste des indicateurs sélectionnés
        timeframe: Timeframe sélectionné
        
    Returns:
        Div avec tableau HTML
    """
    if not selected_indicators:
        return html.Div("Sélectionnez au moins un indicateur", 
                       className="text-muted")
    
    try:
        factory, _, _, _ = _get_services()
        
        # Mapper timeframe
        timeframe_map = {
            "1m": TimeFrame.M1,
            "5m": TimeFrame.M5,
            "15m": TimeFrame.M15,
            "1h": TimeFrame.H1,
            "4h": TimeFrame.H4,
            "1d": TimeFrame.D1,
        }
        tf = timeframe_map.get(timeframe, TimeFrame.H1)
        
        # Collecter les données pour comparaison
        comparison_data = []
        
        for indicator_sel in selected_indicators:
            parts = indicator_sel.split("_")
            indicator_name = parts[0]
            
            try:
                result = factory.calculate_indicator(
                    indicator_name=indicator_name,
                    symbol="BTCUSDT",
                    timeframe=tf,
                )
                
                if result and result.statistics:
                    comparison_data.append({
                        "Indicateur": indicator_name,
                        "Valeur Actuelle": f"{result.statistics.get('current_value', 'N/A')}",
                        "Min": f"{result.statistics.get('min', 'N/A')}",
                        "Max": f"{result.statistics.get('max', 'N/A')}",
                        "Moyenne": f"{result.statistics.get('mean', 'N/A')}",
                    })
            except Exception as e:
                logger.warning(f"Erreur calcul {indicator_name}: {e}")
                continue
        
        if not comparison_data:
            return html.Div("Erreur: Aucune donnée de comparaison",
                           className="alert alert-warning")
        
        # Créer le tableau
        table = dash_table.DataTable(
            data=comparison_data,
            columns=[{"name": col, "id": col} for col in comparison_data[0].keys()],
            style_cell={"textAlign": "center", "padding": "10px"},
            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(248, 248, 248)"
                }
            ]
        )
        
        return html.Div(table)
        
    except Exception as e:
        logger.error(f"❌ Erreur tableau comparaison: {e}")
        return html.Div(f"Erreur: {str(e)}", className="alert alert-danger")


@callback(
    Output("metric-current-value", "children"),
    Output("metric-change", "children"),
    Output("metric-signals-today", "children"),
    Output("metric-last-update", "children"),
    Input("indicator-selector", "value"),
    Input("timeframe-selector", "value"),
    prevent_initial_call=True
)
def update_metrics(
    selected_indicator: str,
    timeframe: str
) -> tuple:
    """
    Mettre à jour les métriques d'indicateur
    
    Args:
        selected_indicator: Indicateur sélectionné
        timeframe: Timeframe sélectionné
        
    Returns:
        Tuple de (valeur_actuelle, changement, signaux_today, derniere_maj)
    """
    if not selected_indicator:
        return "N/A", "N/A", "0", "N/A"
    
    try:
        factory, _, aggregator, _ = _get_services()
        
        parts = selected_indicator.split("_")
        indicator_name = parts[0]
        
        timeframe_map = {
            "1m": TimeFrame.M1,
            "5m": TimeFrame.M5,
            "15m": TimeFrame.M15,
            "1h": TimeFrame.H1,
            "4h": TimeFrame.H4,
            "1d": TimeFrame.D1,
        }
        tf = timeframe_map.get(timeframe, TimeFrame.H1)
        
        # Calculer l'indicateur
        result = factory.calculate_indicator(
            indicator_name=indicator_name,
            symbol="BTCUSDT",
            timeframe=tf,
        )
        
        if not result:
            return "N/A", "N/A", "0", "N/A"
        
        # Extraire les métriques
        current_value = "N/A"
        if result.statistics:
            current_value = f"{result.statistics.get('current_value', 'N/A')}"
        
        # Changement (exemple: dernière vs avant-dernière)
        change = "N/A"
        if result.statistics and 'change' in result.statistics:
            val = result.statistics['change']
            change = f"{val:+.2f}" if isinstance(val, (int, float)) else val
        
        # Signaux d'aujourd'hui
        signals_today = "0"
        if result.signals:
            signals_today = str(len(result.signals))
        
        # Dernière mise à jour
        last_update = "Maintenant"
        
        return current_value, change, signals_today, last_update
        
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour métriques: {e}")
        return "Erreur", "Erreur", "0", "Erreur"


@callback(
    Output("stat-signals-up", "children"),
    Output("stat-signals-down", "children"),
    Output("stat-ratio", "children"),
    Output("stat-strength", "children"),
    Input("indicator-selector", "value"),
    prevent_initial_call=True
)
def update_statistics(selected_indicator: str) -> tuple:
    """
    Mettre à jour les statistiques des signaux
    
    Args:
        selected_indicator: Indicateur sélectionné
        
    Returns:
        Tuple de (signaux_up, signaux_down, ratio, puissance)
    """
    if not selected_indicator:
        return "0", "0", "0%", "0.0"
    
    try:
        _, _, aggregator, _ = _get_services()
        
        # Obtenir les statistiques
        stats = aggregator.get_signal_statistics()
        
        if not stats:
            return "0", "0", "0%", "0.0"
        
        signals_up = stats.get('up_count', 0)
        signals_down = stats.get('down_count', 0)
        total = signals_up + signals_down
        
        ratio = f"{(signals_up / total * 100):.1f}%" if total > 0 else "0%"
        strength = f"{stats.get('average_strength', 0.0):.2f}"
        
        return str(signals_up), str(signals_down), ratio, strength
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques: {e}")
        return "0", "0", "0%", "0.0"


@callback(
    Output("signals-modal", "is_open"),
    Output("signals-content", "children"),
    Input("indicator-selector", "value"),
    State("signals-modal", "is_open"),
    prevent_initial_call=True
)
def update_signals_modal(
    selected_indicator: str,
    is_open: bool
) -> tuple:
    """
    Mettre à jour le modal des signaux
    
    Args:
        selected_indicator: Indicateur sélectionné
        is_open: État du modal
        
    Returns:
        Tuple de (is_open, contenu)
    """
    if not selected_indicator:
        return False, html.P("Sélectionnez un indicateur", className="text-muted")
    
    try:
        factory, _, _, _ = _get_services()
        
        parts = selected_indicator.split("_")
        indicator_name = parts[0]
        
        # Calculer l'indicateur pour obtenir les signaux
        result = factory.calculate_indicator(
            indicator_name=indicator_name,
            symbol="BTCUSDT",
            timeframe=TimeFrame.H1,
        )
        
        if not result or not result.signals:
            return True, html.P("Aucun signal pour le moment", 
                              className="text-muted")
        
        # Créer la liste des signaux
        signal_items = []
        for signal in result.signals:
            direction = signal.direction.value if hasattr(signal.direction, 'value') else str(signal.direction)
            badge_color = "success" if direction == "UP" else "danger"
            
            signal_items.append(
                dbc.Alert([
                    html.H6(f"{indicator_name} - {direction}", 
                            className=f"text-{badge_color}"),
                    html.Small(f"Force: {signal.strength:.2f}"),
                    html.Br(),
                    html.Small(f"Timestamp: {signal.timestamp}"),
                ], color=badge_color, dismissable=True)
            )
        
        return True, signal_items
        
    except Exception as e:
        logger.error(f"❌ Erreur modal signaux: {e}")
        return True, html.Div(f"Erreur: {str(e)}", className="alert alert-danger")


def _build_indicator_params(
    indicator_name: str,
    param_values: List[Any]
) -> Dict[str, Any]:
    """
    Construire les paramètres d'indicateur
    
    Args:
        indicator_name: Nom de l'indicateur
        param_values: Valeurs des paramètres
        
    Returns:
        Dictionnaire des paramètres
    """
    params = {}
    
    param_names = {
        "SMA": ["period"],
        "EMA": ["period"],
        "RSI": ["period"],
        "ATR": ["period"],
        "MACD": ["fast", "slow", "signal"],
        "SuperTrend": ["multiplier", "period"],
        "Squeeze": ["momentum_length", "bb_length"],
        "Breakout": ["lookback"],
        "Volume Profile": ["bins"],
        "OBV": [],
        "FairValueGaps": ["lookback"],
    }
    
    names = param_names.get(indicator_name, [])
    for i, name in enumerate(names):
        if i < len(param_values):
            params[name] = param_values[i]
    
    return params


# Phase 5.3 - Real-time data integration callbacks

@callback(
    Output("realtime-data-store", "data"),
    Input("realtime-update-interval", "n_intervals"),
    prevent_initial_call=True
)
def update_realtime_data(n_intervals: int) -> Dict[str, Any]:
    """
    Periodic callback for real-time data updates
    Triggered every 100ms by dcc.Interval component
    
    Args:
        n_intervals: Number of intervals triggered
        
    Returns:
        Dictionary with real-time data
    """
    try:
        stream = get_data_stream()
        
        # Get current status
        status = stream.get_status()
        
        # Collect symbol data
        data_dict = {}
        for symbol, data in stream.get_all_data().items():
            data_dict[symbol] = {
                "price": str(data.latest_price),
                "bid": str(data.bid),
                "ask": str(data.ask),
                "volume": str(data.volume),
                "last_update": data.last_update.isoformat() if data.last_update else None,
            }
        
        return {
            "timestamp": pd.Timestamp.now().isoformat(),
            "running": status.get("running", False),
            "symbols": data_dict,
            "intervals": n_intervals,
        }
    
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour real-time: {e}")
        return {"error": str(e), "timestamp": pd.Timestamp.now().isoformat()}


@callback(
    Output("metric-current-value", "children"),
    Output("metric-change", "children"),
    Output("metric-signals-today", "children"),
    Output("metric-last-update", "children"),
    Input("realtime-data-store", "data"),  # Trigger on real-time updates
    State("indicator-selector", "value"),
    State("timeframe-selector", "value"),
    prevent_initial_call=True
)
def update_metrics_realtime(
    realtime_data: Dict[str, Any],
    selected_indicator: str,
    timeframe: str
) -> tuple:
    """
    Update metrics from real-time data stream
    
    Args:
        realtime_data: Real-time data from periodic update
        selected_indicator: Indicateur sélectionné
        timeframe: Timeframe sélectionné
        
    Returns:
        Tuple de (valeur_actuelle, changement, signaux_today, derniere_maj)
    """
    if not selected_indicator or not realtime_data:
        return "N/A", "N/A", "0", "N/A"
    
    try:
        factory, _, aggregator, _ = _get_services()
        
        parts = selected_indicator.split("_")
        indicator_name = parts[0]
        
        timeframe_map = {
            "1m": TimeFrame.M1,
            "5m": TimeFrame.M5,
            "15m": TimeFrame.M15,
            "1h": TimeFrame.H1,
            "4h": TimeFrame.H4,
            "1d": TimeFrame.D1,
        }
        tf = timeframe_map.get(timeframe, TimeFrame.H1)
        
        # Calculer l'indicateur avec données actualisées
        result = factory.calculate_indicator(
            indicator_name=indicator_name,
            symbol="BTCUSDT",
            timeframe=tf,
        )
        
        if not result:
            return "N/A", "N/A", "0", "N/A"
        
        # Extraire les métriques
        current_value = "N/A"
        if result.statistics:
            current_value = f"{result.statistics.get('current_value', 'N/A')}"
        
        # Changement
        change = "N/A"
        if result.statistics and 'change' in result.statistics:
            val = result.statistics['change']
            change = f"{val:+.2f}" if isinstance(val, (int, float)) else val
        
        # Signaux d'aujourd'hui
        signals_today = "0"
        if result.signals:
            signals_today = str(len(result.signals))
        
        # Dernière mise à jour
        last_update = realtime_data.get("timestamp", "N/A")
        if last_update and last_update != "N/A":
            last_update = "À jour ✅"
        
        return current_value, change, signals_today, last_update
    
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour métriques real-time: {e}")
        return "Erreur", "Erreur", "0", "Erreur"


def create_realtime_components() -> List:
    """
    Create real-time update components
    Should be added to app layout
    
    Returns:
        List of Dash components for real-time updates
    """
    return [
        # Hidden store for real-time data
        dcc.Store(id="realtime-data-store", data={}),
        
        # Interval for periodic updates (100ms)
        dcc.Interval(
            id="realtime-update-interval",
            interval=100,  # 100ms updates
            n_intervals=0,
            disabled=False,
        ),
    ]


logger.info("✅ Phase 5.2 Callbacks loaded (with Phase 5.3 real-time integration)")

