"""
Order Blocks (Blocs d'Ordres) - Indicateur Smart Money
API unifiée pour l'analyse des zones institutionnelles
"""

# Configuration d'availability
ORDER_BLOCKS_AVAILABLE = True

from .config import (
    OrderBlockConfig,
    OrderBlockType,
    OrderBlockStatus, 
    OrderBlockStrength,
    create_style_configs
)

from .calculator import (
    OrderBlock,
    OrderBlockCalculator,
    analyze_market_structure,
    find_order_block_signals
)

from .plotter import (
    OrderBlockPlotter,
    create_order_blocks_overlay
)

# Version du module
__version__ = "1.0.0"

# Configurations par défaut pour chaque style de trading
DEFAULT_CONFIGS = create_style_configs()

# Classes principales exportées
__all__ = [
    # Availability
    'ORDER_BLOCKS_AVAILABLE',
    
    # Configuration
    'OrderBlockConfig',
    'OrderBlockType',
    'OrderBlockStatus',
    'OrderBlockStrength',
    'create_style_configs',
    'DEFAULT_CONFIGS',
    
    # Calcul et analyse
    'OrderBlock',
    'OrderBlockCalculator', 
    'analyze_market_structure',
    'find_order_block_signals',
    
    # Visualisation
    'OrderBlockPlotter',
    'create_order_blocks_overlay',
    
    # Fonctions utilitaires
    'create_order_blocks_indicator',
    'get_order_blocks_signals',
    'analyze_order_blocks'
]


def create_order_blocks_indicator(style: str = "day_trading", **kwargs):
    """
    Crée un indicateur Order Blocks complet avec la configuration du style spécifié
    
    Args:
        style: Style de trading ('scalping', 'day_trading', 'swing_trading', 'position_trading')
        **kwargs: Paramètres de configuration supplémentaires
    
    Returns:
        Tuple (calculator, plotter, config)
    """
    
    # Obtenir la configuration de base
    if style in DEFAULT_CONFIGS:
        config = DEFAULT_CONFIGS[style]
    else:
        config = DEFAULT_CONFIGS['day_trading']  # Fallback
    
    # Appliquer les paramètres personnalisés
    if kwargs:
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    # Créer les composants
    calculator = OrderBlockCalculator(config)
    plotter = OrderBlockPlotter(config)
    
    return calculator, plotter, config


def get_order_blocks_signals(data, style: str = "day_trading", **kwargs):
    """
    Analyse rapide pour obtenir les signaux Order Blocks actuels
    
    Args:
        data: DataFrame OHLCV
        style: Style de trading
        **kwargs: Paramètres supplémentaires
    
    Returns:
        Dictionnaire avec les signaux et statistiques
    """
    
    calculator, plotter, config = create_order_blocks_indicator(style, **kwargs)
    
    # Analyser les blocs
    blocks = calculator.analyze_blocks(data)
    
    # Obtenir les signaux de trading actuels
    current_price = data['close'].iloc[-1] if len(data) > 0 else 0
    signals = calculator.get_trading_signals(current_price)
    
    # Statistiques résumées
    stats = plotter.create_statistics_summary(blocks)
    
    return {
        'signals': signals,
        'blocks': blocks,
        'statistics': stats,
        'config': {
            'style': style,
            'impulse_threshold': config.min_impulse_strength,
            'min_volume_multiplier': config.volume_multiplier,
            'max_blocks_display': config.max_blocks_display
        }
    }


def analyze_order_blocks(data, style: str = "day_trading", create_chart: bool = False, **kwargs):
    """
    Analyse complète des Order Blocks avec visualisation optionnelle
    
    Args:
        data: DataFrame OHLCV
        style: Style de trading
        create_chart: Si True, génère un graphique d'analyse
        **kwargs: Paramètres supplémentaires
    
    Returns:
        Dictionnaire avec analyse complète et graphique optionnel
    """
    
    calculator, plotter, config = create_order_blocks_indicator(style, **kwargs)
    
    # Analyse des blocs
    blocks = calculator.analyze_blocks(data)
    
    # Signaux actuels
    current_price = data['close'].iloc[-1] if len(data) > 0 else 0
    signals = calculator.get_trading_signals(current_price)
    
    # Statistiques détaillées
    stats = plotter.create_statistics_summary(blocks)
    
    # Données d'overlay pour graphique principal
    overlay_data = create_order_blocks_overlay(data, config)
    
    result = {
        'signals': signals,
        'blocks': blocks,
        'statistics': stats,
        'overlay_data': overlay_data,
        'config_info': {
            'style': style,
            'parameters': {
                'impulse_threshold': config.min_impulse_strength,
                'min_volume_multiplier': config.volume_multiplier,
                'min_block_size': config.min_block_size_pct,
                'max_blocks': config.max_blocks_display,
                'expire_after': config.max_age_bars
            }
        }
    }
    
    # Graphique d'analyse optionnel
    if create_chart:
        result['analysis_chart'] = plotter.create_analysis_chart(blocks)
    
    return result


# Exemples d'utilisation pour la documentation
USAGE_EXAMPLES = {
    'basic': """
# Utilisation de base
import pandas as pd
from thebot.indicators.smart_money.order_blocks import get_order_blocks_signals

# Données OHLCV
data = pd.read_csv('your_data.csv')
data.set_index('timestamp', inplace=True)

# Obtenir les signaux
signals = get_order_blocks_signals(data, style='day_trading')
print(f"Blocs actifs: {signals['statistics']['active_blocks']}")
print(f"Signal actuel: {signals['signals']}")
""",
    
    'advanced': """
# Utilisation avancée avec configuration personnalisée
from thebot.indicators.smart_money.order_blocks import analyze_order_blocks

# Configuration personnalisée
analysis = analyze_order_blocks(
    data,
    style='swing_trading',
    create_chart=True,
    impulse_threshold=1.8,  # Plus strict
    min_volume_multiplier=1.8,  # Volume plus élevé requis
    max_blocks_display=15  # Plus de blocs affichés
)

# Accès aux résultats
blocks = analysis['blocks']
overlay = analysis['overlay_data']
chart = analysis['analysis_chart']
""",
    
    'integration': """
# Intégration dans un système de trading
from thebot.indicators.smart_money.order_blocks import create_order_blocks_indicator

calculator, plotter, config = create_order_blocks_indicator('scalping')

# Analyse continue
for new_data in data_stream:
    blocks = calculator.analyze_blocks(new_data)
    signals = calculator.get_trading_signals(new_data['close'].iloc[-1])
    
    if signals.get('buy_signal'):
        print("Signal d'achat détecté près d'un Order Block bullish!")
    elif signals.get('sell_signal'):
        print("Signal de vente détecté près d'un Order Block bearish!")
"""
}


# Configuration par défaut pour l'importation rapide
DEFAULT_CALCULATOR, DEFAULT_PLOTTER, DEFAULT_CONFIG = create_order_blocks_indicator()


# Fonction de test rapide
def quick_test():
    """Test rapide du module Order Blocks"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Générer des données de test
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=720, freq='H')
    np.random.seed(42)
    
    price = 100
    data = []
    
    for i, date in enumerate(dates):
        # Simuler un mouvement de prix réaliste
        change = np.random.normal(0, 0.5)
        if i > 0 and i % 100 == 0:  # Impulsions occasionnelles
            change += np.random.choice([-3, 3]) * np.random.random()
        
        price += change
        high = price + abs(np.random.normal(0, 0.3))
        low = price - abs(np.random.normal(0, 0.3))
        volume = np.random.randint(1000, 10000)
        
        data.append({
            'timestamp': date,
            'open': price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    # Test rapide
    print("🧪 Test Order Blocks...")
    
    try:
        result = get_order_blocks_signals(df, style='day_trading')
        print(f"✅ Blocs détectés: {len(result['blocks'])}")
        print(f"✅ Blocs actifs: {result['statistics']['active_blocks']}")
        print(f"✅ Score moyen: {result['statistics']['average_strength']}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    # Exécution du test si le module est lancé directement
    quick_test()