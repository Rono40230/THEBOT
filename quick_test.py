#!/usr/bin/env python3
"""
THEBOT - Test Simple des Indicateurs
Version simplifiée pour validation rapide
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pandas as pd
from decimal import Decimal

def quick_test():
    """Test rapide de tous les indicateurs"""
    
    print("🎯 THEBOT - Test Rapide des Indicateurs")
    print("=" * 50)
    
    # Données simple
    prices = [Decimal(str(100 + i * 0.5 + np.random.randn() * 0.1)) for i in range(30)]
    print(f"📊 Test avec {len(prices)} prix générés")
    
    # Test SMA simple
    print("\n🔸 SMA(10)")
    try:
        sma_sum = sum(prices[-10:])
        sma_result = sma_sum / 10
        print(f"   ✅ Valeur: {float(sma_result):.4f}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test avec calculateurs réels
    print("\n🧪 Test avec calculateurs THEBOT:")
    
    # SMA Calculator
    try:
        from thebot.indicators.basic.sma.config import SMAConfig
        from thebot.indicators.basic.sma.calculator import SMACalculator
        from thebot.core.types import MarketData, TimeFrame
        
        calc = SMACalculator(SMAConfig(period=5))
        
        for i, price in enumerate(prices[-10:]):
            market_data = MarketData(
                symbol="TEST",
                timestamp=pd.Timestamp.now(),
                open=price,
                high=price * Decimal('1.001'),
                low=price * Decimal('0.999'),
                close=price,
                volume=Decimal('1000'),
                timeframe=TimeFrame.M1
            )
            result = calc.add_data_point(market_data)
            if result and i == len(prices[-10:]) - 1:  # Dernier point
                print(f"   ✅ SMA Calculator: {float(result.value):.4f}")
    except Exception as e:
        print(f"   ❌ SMA Calculator: {e}")
    
    print("\n🎉 Test rapide terminé !")
    print("🚀 App native: python launch_simple_native.py")

if __name__ == '__main__':
    quick_test()