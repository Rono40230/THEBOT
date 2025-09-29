#!/usr/bin/env python3
"""
THEBOT - Interface Native Simple
Version simplifiée sans PyQt6 pour tests
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np
import pandas as pd
from decimal import Decimal


class SimpleTHEBOTApp:
    """Application THEBOT native simplifiée"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 THEBOT - Application Native")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        self.create_ui()
        self.setup_calculators()
        
    def setup_calculators(self):
        """Configurer les calculateurs directement"""
        try:
            from thebot.indicators.basic.sma.config import SMAConfig
            from thebot.indicators.basic.sma.calculator import SMACalculator
            from thebot.indicators.basic.ema.config import EMAConfig  
            from thebot.indicators.basic.ema.calculator import EMACalculator
            from thebot.indicators.oscillators.rsi.config import RSIConfig
            from thebot.indicators.oscillators.rsi.calculator import RSICalculator
            from thebot.indicators.volatility.atr.config import ATRConfig
            from thebot.indicators.volatility.atr.calculator import ATRCalculator
            
            self.sma_calc = SMACalculator(SMAConfig(period=20))
            self.ema_calc = EMACalculator(EMAConfig(period=12))
            self.rsi_calc = RSICalculator(RSIConfig(period=14))
            self.atr_calc = ATRCalculator(ATRConfig(period=14))
            
            self.log("✅ Calculateurs initialisés avec succès")
            
        except Exception as e:
            self.log(f"❌ Erreur init calculateurs: {e}")
            
        # Données d'exemple  
        self.sample_prices = [Decimal(str(100 + np.random.randn() * 2 + i * 0.1)) for i in range(100)]
        
    def create_ui(self):
        """Créer l'interface utilisateur"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = tk.Label(main_frame, text="🤖 THEBOT v1.0 - Native App", 
                              font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='white')
        title_label.pack(pady=(0, 10))
        
        # Frame de contrôles
        controls_frame = ttk.LabelFrame(main_frame, text="📊 Indicateurs", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # SMA
        sma_frame = ttk.Frame(controls_frame)
        sma_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sma_frame, text="SMA Période:").pack(side=tk.LEFT, padx=(0, 5))
        self.sma_var = tk.IntVar(value=20)
        sma_spin = ttk.Spinbox(sma_frame, from_=1, to=200, width=10, textvariable=self.sma_var)
        sma_spin.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(sma_frame, text="Calculer SMA", command=self.calc_sma).pack(side=tk.LEFT)
        
        # EMA
        ema_frame = ttk.Frame(controls_frame)
        ema_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ema_frame, text="EMA Période:").pack(side=tk.LEFT, padx=(0, 5))
        self.ema_var = tk.IntVar(value=12)
        ema_spin = ttk.Spinbox(ema_frame, from_=1, to=200, width=10, textvariable=self.ema_var)
        ema_spin.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(ema_frame, text="Calculer EMA", command=self.calc_ema).pack(side=tk.LEFT)
        
        # RSI
        rsi_frame = ttk.Frame(controls_frame)
        rsi_frame.pack(fill=tk.X, pady=2)
        ttk.Label(rsi_frame, text="RSI Période:").pack(side=tk.LEFT, padx=(0, 5))
        self.rsi_var = tk.IntVar(value=14)
        rsi_spin = ttk.Spinbox(rsi_frame, from_=1, to=50, width=10, textvariable=self.rsi_var)
        rsi_spin.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(rsi_frame, text="Calculer RSI", command=self.calc_rsi).pack(side=tk.LEFT)
        
        # ATR
        atr_frame = ttk.Frame(controls_frame)
        atr_frame.pack(fill=tk.X, pady=2)
        ttk.Label(atr_frame, text="ATR Période:").pack(side=tk.LEFT, padx=(0, 5))
        self.atr_var = tk.IntVar(value=14)
        atr_spin = ttk.Spinbox(atr_frame, from_=1, to=50, width=10, textvariable=self.atr_var)
        atr_spin.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(atr_frame, text="Calculer ATR", command=self.calc_atr).pack(side=tk.LEFT)
        
        # Boutons d'action
        action_frame = ttk.Frame(controls_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(action_frame, text="🔄 Nouvelles Données", command=self.refresh_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🧪 Tests", command=self.run_tests).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🎯 Test Tous", command=self.test_all_indicators).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🧹 Clear", command=self.clear_log).pack(side=tk.LEFT)
        
        # Zone de résultats
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, bg='#1e1e1e', fg='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("🚀 THEBOT Application Native démarrée")
        self.log("📊 Architecture ultra-modulaire active")
        
    def log(self, message):
        """Ajouter un message au log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()
        
    def calc_sma(self):
        """Calculer SMA"""
        try:
            period = self.sma_var.get()
            self.log(f"🔄 Calcul SMA période {period}...")
            
            # Recréer avec nouvelle période
            from thebot.indicators.basic.sma.config import SMAConfig
            from thebot.indicators.basic.sma.calculator import SMACalculator
            calc = SMACalculator(SMAConfig(period=period))
            
            results = []
            for price in self.sample_prices[-50:]:  # Dernières 50 valeurs
                sma_val = calc.add_price(price)
                if sma_val is not None:
                    results.append(float(sma_val))
                    
            if results:
                avg = np.mean(results)
                self.log(f"✅ SMA({period}): {avg:.4f} | Points: {len(results)} | Dernier: {results[-1]:.4f}")
            else:
                self.log(f"❌ SMA({period}): Données insuffisantes")
                
        except Exception as e:
            self.log(f"❌ Erreur SMA: {str(e)}")
            
    def calc_ema(self):
        """Calculer EMA"""
        try:
            period = self.ema_var.get()
            self.log(f"🔄 Calcul EMA période {period}...")
            
            from thebot.indicators.basic.ema.config import EMAConfig
            from thebot.indicators.basic.ema.calculator import EMACalculator
            calc = EMACalculator(EMAConfig(period=period))
            
            results = []
            for price in self.sample_prices[-50:]:
                ema_val = calc.add_price(price)
                if ema_val is not None:
                    results.append(float(ema_val))
                    
            if results:
                trend = results[-1] - results[-10] if len(results) > 10 else 0
                self.log(f"✅ EMA({period}): {results[-1]:.4f} | Points: {len(results)} | Trend: {trend:.4f}")
            else:
                self.log(f"❌ EMA({period}): Données insuffisantes")
                
        except Exception as e:
            self.log(f"❌ Erreur EMA: {str(e)}")
            
    def calc_rsi(self):
        """Calculer RSI"""
        try:
            period = self.rsi_var.get()
            self.log(f"🔄 Calcul RSI période {period}...")
            
            from thebot.indicators.oscillators.rsi.config import RSIConfig
            from thebot.indicators.oscillators.rsi.calculator import RSICalculator
            calc = RSICalculator(RSIConfig(period=period))
            
            results = []
            for price in self.sample_prices[-50:]:
                rsi_val = calc.add_price(price)
                if rsi_val is not None:
                    results.append(float(rsi_val))
                    
            if results:
                current_rsi = results[-1]
                status = "🔴 Survente" if current_rsi < 30 else "🟢 Surachat" if current_rsi > 70 else "🔵 Neutre"
                self.log(f"✅ RSI({period}): {current_rsi:.2f} | {status} | Points: {len(results)}")
            else:
                self.log(f"❌ RSI({period}): Données insuffisantes")
                
        except Exception as e:
            self.log(f"❌ Erreur RSI: {str(e)}")
            
    def calc_atr(self):
        """Calculer ATR"""
        try:
            period = self.atr_var.get()
            self.log(f"🔄 Calcul ATR période {period}...")
            
            from thebot.indicators.volatility.atr.config import ATRConfig
            from thebot.indicators.volatility.atr.calculator import ATRCalculator
            from thebot.core.types import MarketData, TimeFrame
            import pandas as pd
            
            calc = ATRCalculator(ATRConfig(period=period))
            
            results = []
            # Simuler des données OHLC à partir des prix
            for i in range(len(self.sample_prices) - 1):
                price = float(self.sample_prices[i])
                next_price = float(self.sample_prices[i + 1])
                
                # Simuler High/Low basés sur le prix
                volatility = abs(next_price - price) + 0.5
                high = price + volatility * np.random.random()
                low = price - volatility * np.random.random()
                
                market_data = MarketData(
                    timestamp=pd.Timestamp.now(),
                    open=Decimal(str(price)),
                    high=Decimal(str(high)),
                    low=Decimal(str(low)),
                    close=self.sample_prices[i + 1],
                    volume=Decimal('1000'),
                    timeframe=TimeFrame.M1
                )
                
                atr_val = calc.calculate(market_data)
                if atr_val is not None:
                    results.append(float(atr_val))
                    
            if results:
                current_atr = results[-1]
                volatility_level = "📈 Élevée" if current_atr > 2.0 else "📊 Normale" if current_atr > 1.0 else "📉 Faible"
                self.log(f"✅ ATR({period}): {current_atr:.4f} | Volatilité: {volatility_level} | Points: {len(results)}")
            else:
                self.log(f"❌ ATR({period}): Données insuffisantes")
                
        except Exception as e:
            self.log(f"❌ Erreur ATR: {str(e)}")
            
    def refresh_data(self):
        """Générer de nouvelles données"""
        self.sample_prices = [Decimal(str(100 + np.random.randn() * 2 + i * 0.1)) for i in range(100)]
        self.log("🔄 Nouvelles données générées (100 points)")
        
    def run_tests(self):
        """Lancer les tests"""
        self.log("🧪 Lancement des tests unitaires...")
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/unit/indicators/', '-v'
            ], capture_output=True, text=True, cwd='/home/rono/THEBOT')
            
            if result.returncode == 0:
                self.log("✅ Tous les tests passent !")
            else:
                self.log(f"❌ Tests échoués: {result.returncode}")
        except Exception as e:
            self.log(f"❌ Erreur tests: {e}")
            
    def test_all_indicators(self):
        """Tester tous les indicateurs en une fois"""
        self.log("🎯 Test complet de tous les indicateurs...")
        self.log("-" * 40)
        
        try:
            # Test SMA
            self.calc_sma()
            
            # Test EMA  
            self.calc_ema()
            
            # Test RSI
            self.calc_rsi()
            
            # Test ATR
            self.calc_atr()
            
            self.log("-" * 40)
            self.log("🎉 Test complet terminé ! Tous les indicateurs testés.")
            
        except Exception as e:
            self.log(f"❌ Erreur test complet: {e}")
            
    def clear_log(self):
        """Nettoyer le log"""
        self.log_text.delete(1.0, tk.END)


def main():
    """Point d'entrée principal"""
    print("🚀 THEBOT - Application Native Simple")
    
    try:
        root = tk.Tk()
        app = SimpleTHEBOTApp(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == '__main__':
    main()