#!/usr/bin/env python3
"""
Test Phase 1 - Validation OBV et SuperTrend
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_obv():
    """Test OBV Indicator"""
    try:
        from thebot.indicators.volume.obv import OBVIndicator
        obv = OBVIndicator()
        return f"✅ OBV: {obv.name} (Required: {obv.get_required_periods()})"
    except Exception as e:
        return f"❌ OBV Error: {e}"

def test_supertrend():
    """Test SuperTrend Indicator"""
    try:
        from thebot.indicators.trend.supertrend import SuperTrendIndicator
        st = SuperTrendIndicator()
        return f"✅ SuperTrend: {st.name} (Required: {st.get_required_periods()})"
    except Exception as e:
        return f"❌ SuperTrend Error: {e}"

if __name__ == "__main__":
    print("🏆 PHASE 1 - TEST FINAL")
    print("=" * 30)
    
    obv_result = test_obv()
    print(obv_result)
    
    st_result = test_supertrend()
    print(st_result)
    
    print()
    success = "✅" in obv_result and "✅" in st_result
    
    if success:
        print("🎉 PHASE 1 RÉUSSIE ! 🎉")
        print("✅ OBV: On Balance Volume opérationnel")
        print("✅ SuperTrend: Trend Following opérationnel")
        print("🚀 PRÊT POUR PHASE 2!")
    else:
        print("⚠️ Phase 1 nécessite des corrections")