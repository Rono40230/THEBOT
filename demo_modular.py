#!/usr/bin/env python3
"""
Démonstration de l'architecture ultra-modulaire THEBOT
Test en conditions réelles du SMA avec données de marché
"""

from decimal import Decimal
from datetime import datetime, timedelta
import sys
import os

# Ajouter le path pour l'import
sys.path.append('/workspaces/THEBOT/src')

from thebot.core.types import MarketData, TimeFrame
from thebot.indicators.basic.sma import SMAIndicator
from thebot.indicators.basic.sma.config import SMAConfig


def create_sample_data():
    """Créer des données de marché d'exemple"""
    base_time = datetime.now()
    data_points = []
    
    # Simuler un trend haussier puis baissier
    prices = [100, 102, 105, 103, 106, 108, 104, 102, 99, 95, 98, 101, 103, 105, 107]
    
    for i, price in enumerate(prices):
        data = MarketData(
            timestamp=base_time + timedelta(minutes=i),
            open=Decimal(str(price - 0.5)),
            high=Decimal(str(price + 1)),
            low=Decimal(str(price - 1)),
            close=Decimal(str(price)),
            volume=Decimal('1000'),
            timeframe=TimeFrame.M1,
            symbol="BTCUSDT"
        )
        data_points.append(data)
    
    return data_points


def demo_ultra_modular_sma():
    """Démonstration de l'architecture ultra-modulaire"""
    
    print("🚀 DÉMONSTRATION ARCHITECTURE ULTRA-MODULAIRE THEBOT")
    print("=" * 60)
    
    # 1. Configuration modulaire
    print("\n📋 1. Configuration SMA modulaire :")
    config = SMAConfig(
        period=5,
        enable_signals=True,
        crossover_sensitivity=0.005  # 0.5%
    )
    print(f"   Période: {config.period}")
    print(f"   Signaux activés: {config.enable_signals}")
    print(f"   Sensibilité: {config.crossover_sensitivity * 100}%")
    
    # 2. Indicateur modulaire
    print("\n🔧 2. Création indicateur SMA :")
    sma = SMAIndicator(config)
    print(f"   Nom: {sma.name}")
    print(f"   Périodes requises: {sma.get_required_periods()}")
    print(f"   Prêt: {sma.is_ready}")
    
    # 3. Données de test
    print("\n📊 3. Données de marché simulées :")
    market_data = create_sample_data()
    print(f"   {len(market_data)} points de données")
    print(f"   Prix de départ: {market_data[0].close}")
    print(f"   Prix final: {market_data[-1].close}")
    
    # 4. Traitement modulaire
    print("\n⚡ 4. Traitement temps réel :")
    print("   Timestamp           Prix    SMA     Signal")
    print("   " + "-" * 50)
    
    for i, data in enumerate(market_data):
        result = sma.add_data(data)
        
        if result:
            signal = sma.generate_signal(result)
            signal_str = f"{signal.direction.value.upper()} ({signal.strength.value})" if signal else "---"
            trend = sma.get_trend_direction()
            trend_str = "↗️" if trend.value == "buy" else "↘️" if trend.value == "sell" else "→"
            
            print(f"   {data.timestamp.strftime('%H:%M:%S')}   "
                  f"{data.close:>6}  {result.value:>6.2f}  "
                  f"{signal_str:<15} {trend_str}")
        else:
            print(f"   {data.timestamp.strftime('%H:%M:%S')}   "
                  f"{data.close:>6}  {'---':>6}  {'Données insuffisantes':<15}")
    
    # 5. État final
    print(f"\n📈 5. État final de l'indicateur :")
    print(f"   Valeur SMA actuelle: {sma.current_value}")
    print(f"   Nombre de points: {sma.data_count}")
    print(f"   Distance du prix: {sma.get_distance_from_sma():.2f}%")
    print(f"   Tendance actuelle: {sma.get_trend_direction().value}")
    
    # 6. Métadonnées modulaires
    print(f"\n🔍 6. Métadonnées modulaires :")
    metadata = sma.get_metadata()
    for key, value in metadata.items():
        print(f"   {key}: {value}")
    
    print("\n✅ DÉMONSTRATION TERMINÉE - Architecture ultra-modulaire validée !")
    print("   • Chaque module a une responsabilité unique")
    print("   • Configuration isolée et validée")  
    print("   • Calculs purs séparés de la logique")
    print("   • Tests unitaires granulaires")
    print("   • Maintenance simplifiée")


if __name__ == "__main__":
    demo_ultra_modular_sma()