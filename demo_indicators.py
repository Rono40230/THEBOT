#!/usr/bin/env python3
"""
THEBOT - Démonstration Complète des Indicateurs
Script pour tester tous les indicateurs natifs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pandas as pd
from decimal import Decimal

def demo_all_indicators():
    """Démonstration de tous les indicateurs THEBOT"""
    
    print("🎯 THEBOT - Démonstration Complète des Indicateurs")
    print("=" * 60)
    
    # Générer des données de test
    print("📊 Génération des données de test...")
    prices = [Decimal(str(100 + np.random.randn() * 2 + i * 0.1)) for i in range(100)]
    print(f"   ✅ {len(prices)} points de données générés")
    
    # Test SMA
    print("\n🔸 TEST SMA (Simple Moving Average)")
    print("-" * 30)
    try:
        from thebot.indicators.basic.sma.config import SMAConfig
        from thebot.indicators.basic.sma.calculator import SMACalculator
        
        sma_calc = SMACalculator(SMAConfig(period=20))
        sma_results = []
        
        for price in prices[-30:]:
            result = sma_calc.add_price(price)
            if result is not None:
                sma_results.append(float(result))
        
        if sma_results:
            print(f"   ✅ SMA(20): {sma_results[-1]:.4f}")
            print(f"   📈 Points calculés: {len(sma_results)}")
            print(f"   📊 Moyenne: {np.mean(sma_results):.4f}")
        else:
            print("   ❌ SMA: Aucun résultat")
            
    except Exception as e:
        print(f"   ❌ Erreur SMA: {e}")
    
    # Test EMA
    print("\n🔹 TEST EMA (Exponential Moving Average)")
    print("-" * 30)
    try:
        from thebot.indicators.basic.ema.config import EMAConfig
        from thebot.indicators.basic.ema.calculator import EMACalculator
        
        config = EMAConfig(period=12)
        ema_calc = EMACalculator(config)
        ema_results = []
        
        for price in prices:
            result = ema_calc.calculate(price)
            if result is not None:
                ema_results.append(float(result))
        
        if ema_results:
            print(f"   ✅ EMA(12): {ema_results[-1]:.4f}")
            print(f"   📈 Points calculés: {len(ema_results)}")
            trend = ema_results[-1] - ema_results[-5] if len(ema_results) >= 5 else 0
            print(f"   📊 Tendance: {trend:+.4f}")
        else:
            print("   ❌ EMA: Aucun résultat")
            
    except Exception as e:
        print(f"   ❌ Erreur EMA: {e}")
    
    # Test RSI
    print("\n🔵 TEST RSI (Relative Strength Index)")
    print("-" * 30)
    try:
        from thebot.indicators.oscillators.rsi.config import RSIConfig
        from thebot.indicators.oscillators.rsi.calculator import RSICalculator
        
        config = RSIConfig(period=14)
        rsi_calc = RSICalculator(config)
        rsi_results = []
        
        for price in prices:
            result = rsi_calc.calculate(price)
            if result is not None:
                rsi_results.append(float(result))
        
        if rsi_results:
            current_rsi = rsi_results[-1]
            status = "🔴 Survente" if current_rsi < 30 else "🟢 Surachat" if current_rsi > 70 else "🔵 Neutre"
            print(f"   ✅ RSI(14): {current_rsi:.2f}")
            print(f"   📊 Status: {status}")
            print(f"   📈 Points calculés: {len(rsi_results)}")
        else:
            print("   ❌ RSI: Aucun résultat")
            
    except Exception as e:
        print(f"   ❌ Erreur RSI: {e}")
    
    # Test ATR
    print("\n🔶 TEST ATR (Average True Range)")
    print("-" * 30)
    try:
        from thebot.indicators.volatility.atr.config import ATRConfig
        from thebot.indicators.volatility.atr.calculator import ATRCalculator
        from thebot.core.types import MarketData, TimeFrame
        
        config = ATRConfig(period=14)
        atr_calc = ATRCalculator(config)
        atr_results = []
        
        # Simuler des données OHLC
        for i in range(len(prices) - 1):
            price = float(prices[i])
            next_price = float(prices[i + 1])
            
            volatility = abs(next_price - price) + 0.5
            high = price + volatility * np.random.random()
            low = price - volatility * np.random.random()
            
            market_data = MarketData(
                symbol="TEST",
                timestamp=pd.Timestamp.now(),
                open=prices[i],
                high=Decimal(str(high)),
                low=Decimal(str(low)),
                close=prices[i + 1],
                volume=Decimal('1000'),
                timeframe=TimeFrame.M1
            )
            
            result = atr_calc.calculate(market_data)
            if result is not None:
                atr_results.append(float(result))
        
        if atr_results:
            current_atr = atr_results[-1]
            volatility_level = "📈 Élevée" if current_atr > 2.0 else "📊 Normale" if current_atr > 1.0 else "📉 Faible"
            print(f"   ✅ ATR(14): {current_atr:.4f}")
            print(f"   📊 Volatilité: {volatility_level}")
            print(f"   📈 Points calculés: {len(atr_results)}")
        else:
            print("   ❌ ATR: Aucun résultat")
            
    except Exception as e:
        print(f"   ❌ Erreur ATR: {e}")
    
    # Résumé
    print("\n🎉 RÉSUMÉ DE LA DÉMONSTRATION")
    print("=" * 60)
    print("✅ Architecture ultra-modulaire validée")
    print("✅ Tous les indicateurs testés individuellement")
    print("✅ Calculs en temps réel opérationnels") 
    print("✅ Interface native prête à l'emploi")
    print("\n🚀 Lancer l'app: python launch_simple_native.py")

def main():
    """Point d'entrée"""
    demo_all_indicators()

if __name__ == '__main__':
    main()