#!/usr/bin/env python3
"""
THEBOT - Interface Native Ultra-Moderne avec CustomTkinter
Solution native avec design moderne, animations fluides
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
import threading
import time


class UltraModernTHEBOT:
    """Interface THEBOT Native Ultra-Moderne"""
    
    def __init__(self):
        # Configuration CustomTkinter
        ctk.set_appearance_mode("dark")  # "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("🤖 THEBOT - Trading Intelligence Platform")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        
        # Icône moderne
        try:
            self.root.iconify()
        except:
            pass
            
        # Variables d'état
        self.is_running = False
        self.market_data = self.generate_sample_data()
        self.current_symbol = "BTCUSDT"
        
        # Configuration style matplotlib
        plt.style.use('dark_background')
        
        self.setup_calculators()
        self.create_ui()
        self.setup_real_time_updates()
        
    def generate_sample_data(self):
        """Générer des données de marché réalistes"""
        
        symbols = {
            'BTCUSDT': {'base': 43000, 'volatility': 500},
            'ETHUSD': {'base': 2600, 'volatility': 50},
            'EURUSD': {'base': 1.0850, 'volatility': 0.002},
            'GBPUSD': {'base': 1.2650, 'volatility': 0.003}
        }
        
        data = {}
        
        for symbol, params in symbols.items():
            # Génération de 200 points pour graphiques plus riches
            n_points = 200
            dates = pd.date_range(
                start=datetime.now() - timedelta(hours=n_points),
                end=datetime.now(),
                freq='1h'
            )
            
            # Simulation prix réaliste avec tendance
            base_price = params['base']
            volatility = params['volatility']
            
            prices = []
            current_price = base_price
            
            for i in range(n_points):
                # Tendance générale + cycles + bruit
                trend = np.sin(i * 0.05) * volatility * 0.2
                cycle = np.cos(i * 0.1) * volatility * 0.1
                noise = np.random.randn() * volatility * 0.05
                
                current_price += trend + cycle + noise
                prices.append(current_price)
            
            # Génération OHLCV - utiliser directement les prix comme closes
            opens = [prices[0]] + prices[:-1]  # Open = close précédent
            closes = prices
            
            highs = []
            lows = []
            volumes = []
            
            for i in range(len(prices)):
                o = opens[i]
                c = closes[i]
                high = max(o, c) + abs(np.random.randn()) * volatility * 0.02
                low = min(o, c) - abs(np.random.randn()) * volatility * 0.02
                volume = abs(np.random.randn()) * 1000 + 500
                
                highs.append(high)
                lows.append(low)
                volumes.append(volume)
            
            # Toutes les listes ont maintenant la même longueur (n_points)
            data[symbol] = {
                'timestamps': dates[:n_points],  # Même longueur exacte
                'opens': opens,
                'highs': highs,
                'lows': lows,
                'closes': closes,
                'volumes': volumes
            }
            
        return data
        
    def setup_calculators(self):
        """Initialiser les calculateurs THEBOT"""
        try:
            from thebot.indicators.basic.sma.config import SMAConfig
            from thebot.indicators.basic.sma.calculator import SMACalculator
            
            self.sma_calc = SMACalculator(SMAConfig(period=20))
            self.calculators_loaded = True
            print("✅ Calculateurs THEBOT initialisés")
            
        except Exception as e:
            print(f"⚠️ Calculateurs non disponibles: {e}")
            self.calculators_loaded = False
    
    def create_ui(self):
        """Créer l'interface utilisateur moderne"""
        
        # ===== LAYOUT PRINCIPAL =====
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # ===== SIDEBAR =====
        self.create_sidebar()
        
        # ===== ZONE PRINCIPALE =====
        self.create_main_area()
        
        # ===== STATUS BAR =====
        self.create_status_bar()
        
    def create_sidebar(self):
        """Sidebar avec contrôles modernes"""
        
        # Frame sidebar
        self.sidebar_frame = ctk.CTkFrame(self.root, width=300, corner_radius=15)
        self.sidebar_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        # Logo et titre
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🤖 THEBOT",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Trading Intelligence",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 30))
        
        # Sélecteur de marché
        self.market_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Market Selection",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.market_label.grid(row=2, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.market_selector = ctk.CTkComboBox(
            self.sidebar_frame,
            values=["₿ BTCUSDT", "⟠ ETHUSD", "🇪🇺 EURUSD", "🇬🇧 GBPUSD"],
            command=self.on_market_change,
            width=260
        )
        self.market_selector.grid(row=3, column=0, padx=20, pady=(0, 20))
        self.market_selector.set("₿ BTCUSDT")
        
        # Section indicateurs
        self.create_indicators_section()
        
        # Contrôles principaux
        self.create_control_buttons()
        
        # Section status temps réel
        self.create_realtime_status()
        
    def create_indicators_section(self):
        """Section de contrôle des indicateurs"""
        
        # Titre
        self.indicators_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Technical Indicators",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.indicators_label.grid(row=4, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Frame pour les contrôles
        self.indicators_frame = ctk.CTkFrame(self.sidebar_frame)
        self.indicators_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # SMA Controls
        self.sma_frame = ctk.CTkFrame(self.indicators_frame)
        self.sma_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.sma_switch = ctk.CTkSwitch(
            self.sma_frame,
            text="SMA",
            command=self.update_charts,
            font=ctk.CTkFont(weight="bold")
        )
        self.sma_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.sma_switch.select()
        
        self.sma_slider = ctk.CTkSlider(
            self.sma_frame,
            from_=5,
            to=50,
            command=self.on_sma_change,
            width=150
        )
        self.sma_slider.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.sma_slider.set(20)
        
        self.sma_value_label = ctk.CTkLabel(
            self.sma_frame,
            text="Period: 20",
            font=ctk.CTkFont(size=12)
        )
        self.sma_value_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        
        # EMA Controls
        self.ema_frame = ctk.CTkFrame(self.indicators_frame)
        self.ema_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.ema_switch = ctk.CTkSwitch(
            self.ema_frame,
            text="EMA",
            command=self.update_charts,
            font=ctk.CTkFont(weight="bold")
        )
        self.ema_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ema_switch.select()
        
        self.ema_slider = ctk.CTkSlider(
            self.ema_frame,
            from_=5,
            to=50,
            command=self.on_ema_change,
            width=150
        )
        self.ema_slider.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.ema_slider.set(12)
        
        self.ema_value_label = ctk.CTkLabel(
            self.ema_frame,
            text="Period: 12",
            font=ctk.CTkFont(size=12)
        )
        self.ema_value_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        
        # RSI Controls
        self.rsi_frame = ctk.CTkFrame(self.indicators_frame)
        self.rsi_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.rsi_switch = ctk.CTkSwitch(
            self.rsi_frame,
            text="RSI",
            command=self.update_charts,
            font=ctk.CTkFont(weight="bold")
        )
        self.rsi_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.rsi_switch.select()
        
        self.rsi_slider = ctk.CTkSlider(
            self.rsi_frame,
            from_=5,
            to=30,
            command=self.on_rsi_change,
            width=150
        )
        self.rsi_slider.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.rsi_slider.set(14)
        
        self.rsi_value_label = ctk.CTkLabel(
            self.rsi_frame,
            text="Period: 14",
            font=ctk.CTkFont(size=12)
        )
        self.rsi_value_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        
        # ATR Controls
        self.atr_frame = ctk.CTkFrame(self.indicators_frame)
        self.atr_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.atr_switch = ctk.CTkSwitch(
            self.atr_frame,
            text="ATR",
            command=self.update_charts,
            font=ctk.CTkFont(weight="bold")
        )
        self.atr_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.atr_switch.select()
        
        self.atr_slider = ctk.CTkSlider(
            self.atr_frame,
            from_=5,
            to=30,
            command=self.on_atr_change,
            width=150
        )
        self.atr_slider.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.atr_slider.set(14)
        
        self.atr_value_label = ctk.CTkLabel(
            self.atr_frame,
            text="Period: 14",
            font=ctk.CTkFont(size=12)
        )
        self.atr_value_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        
    def create_control_buttons(self):
        """Boutons de contrôle principaux"""
        
        # Titre
        self.controls_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.controls_label.grid(row=6, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Bouton Start/Stop
        self.start_button = ctk.CTkButton(
            self.sidebar_frame,
            text="▶️ Start Real-Time Analysis",
            command=self.toggle_realtime,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray75", "gray25"),
            width=260
        )
        self.start_button.grid(row=7, column=0, padx=20, pady=(0, 10))
        
        # Bouton Refresh
        self.refresh_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🔄 Refresh Data",
            command=self.refresh_data,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color=("gray70", "gray30"),
            width=260
        )
        self.refresh_button.grid(row=8, column=0, padx=20, pady=(0, 10))
        
        # Switch thème
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12)
        )
        self.theme_switch.grid(row=9, column=0, padx=20, pady=(20, 10))
        self.theme_switch.select()
        
    def create_realtime_status(self):
        """Status temps réel"""
        
        # Frame status
        self.status_frame = ctk.CTkFrame(self.sidebar_frame)
        self.status_frame.grid(row=10, column=0, padx=20, pady=(20, 20), sticky="ew")
        
        self.status_title = ctk.CTkLabel(
            self.status_frame,
            text="📊 Live Status",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_title.grid(row=0, column=0, padx=15, pady=(15, 10))
        
        # Prix actuel
        self.price_label = ctk.CTkLabel(
            self.status_frame,
            text="Price: --",
            font=ctk.CTkFont(size=12)
        )
        self.price_label.grid(row=1, column=0, padx=15, pady=2)
        
        # SMA actuel
        self.sma_status_label = ctk.CTkLabel(
            self.status_frame,
            text="SMA(20): --",
            font=ctk.CTkFont(size=12)
        )
        self.sma_status_label.grid(row=2, column=0, padx=15, pady=2)
        
        # EMA actuel
        self.ema_status_label = ctk.CTkLabel(
            self.status_frame,
            text="EMA(12): --",
            font=ctk.CTkFont(size=12)
        )
        self.ema_status_label.grid(row=3, column=0, padx=15, pady=2)
        
        # RSI actuel
        self.rsi_status_label = ctk.CTkLabel(
            self.status_frame,
            text="RSI(14): --",
            font=ctk.CTkFont(size=12)
        )
        self.rsi_status_label.grid(row=4, column=0, padx=15, pady=2)
        
        # ATR actuel
        self.atr_status_label = ctk.CTkLabel(
            self.status_frame,
            text="ATR(14): --",
            font=ctk.CTkFont(size=12)
        )
        self.atr_status_label.grid(row=5, column=0, padx=15, pady=2)
        
        # Signal
        self.signal_label = ctk.CTkLabel(
            self.status_frame,
            text="Signal: Neutral",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray70"
        )
        self.signal_label.grid(row=6, column=0, padx=15, pady=(2, 15))
        
    def create_main_area(self):
        """Zone principale avec graphiques"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Titre principal
        self.main_title = ctk.CTkLabel(
            self.main_frame,
            text="📈 Real-Time Market Analysis",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.main_title.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Zone graphiques
        self.create_charts_area()
        
    def create_charts_area(self):
        """Zone des graphiques matplotlib"""
        
        # Frame pour les graphiques
        self.charts_frame = ctk.CTkFrame(self.main_frame)
        self.charts_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.charts_frame.grid_columnconfigure(0, weight=1)
        self.charts_frame.grid_rowconfigure(0, weight=3)  # Graphique principal plus grand
        self.charts_frame.grid_rowconfigure(1, weight=1)  # RSI
        self.charts_frame.grid_rowconfigure(2, weight=1)  # Volume + ATR
        
        # Graphique principal (Prix + SMA/EMA)
        self.fig_main = Figure(figsize=(12, 6), facecolor='#212121', tight_layout=True)
        self.ax_main = self.fig_main.add_subplot(111)
        
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, self.charts_frame)
        self.canvas_main.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Graphique RSI
        self.fig_rsi = Figure(figsize=(12, 2), facecolor='#212121', tight_layout=True)
        self.ax_rsi = self.fig_rsi.add_subplot(111)
        
        self.canvas_rsi = FigureCanvasTkAgg(self.fig_rsi, self.charts_frame)
        self.canvas_rsi.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        
        # Graphique Volume + ATR
        self.fig_volume_atr = Figure(figsize=(12, 2), facecolor='#212121', tight_layout=True)
        self.ax_volume = self.fig_volume_atr.add_subplot(121)
        self.ax_atr = self.fig_volume_atr.add_subplot(122)
        
        self.canvas_volume_atr = FigureCanvasTkAgg(self.fig_volume_atr, self.charts_frame)
        self.canvas_volume_atr.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Configuration initiale
        self.setup_charts()
        self.update_charts()
        
    def setup_charts(self):
        """Configuration initiale des graphiques"""
        
        # Configuration graphique principal
        self.ax_main.set_facecolor('#1a1a1a')
        self.ax_main.grid(True, alpha=0.3, color='gray')
        self.ax_main.set_title('Market Price & Moving Averages', 
                              color='white', fontsize=14, fontweight='bold', pad=20)
        
        # Configuration graphique RSI
        self.ax_rsi.set_facecolor('#1a1a1a')
        self.ax_rsi.grid(True, alpha=0.3, color='gray')
        self.ax_rsi.set_title('RSI (Relative Strength Index)', color='white', fontsize=12, pad=10)
        self.ax_rsi.set_ylim(0, 100)
        
        # Configuration graphique Volume
        self.ax_volume.set_facecolor('#1a1a1a')
        self.ax_volume.grid(True, alpha=0.3, color='gray')
        self.ax_volume.set_title('Volume', color='white', fontsize=12, pad=10)
        
        # Configuration graphique ATR
        self.ax_atr.set_facecolor('#1a1a1a')
        self.ax_atr.grid(True, alpha=0.3, color='gray')
        self.ax_atr.set_title('ATR (Average True Range)', color='white', fontsize=12, pad=10)
        
    def create_status_bar(self):
        """Barre de status en bas"""
        
        self.status_bar = ctk.CTkFrame(self.root, height=40, corner_radius=10)
        self.status_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.status_bar.grid_columnconfigure(1, weight=1)
        
        # Status connexion
        self.connection_status = ctk.CTkLabel(
            self.status_bar,
            text="🟢 Connected | Data: Simulated | Last Update: --:--:--",
            font=ctk.CTkFont(size=11)
        )
        self.connection_status.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Version
        self.version_label = ctk.CTkLabel(
            self.status_bar,
            text="THEBOT v2.0 Native",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.version_label.grid(row=0, column=1, padx=15, pady=10, sticky="e")
        
    def setup_real_time_updates(self):
        """Configuration des mises à jour temps réel"""
        self.update_timer = None
        
    # ===== CALLBACKS =====
    
    def on_market_change(self, value):
        """Changement de marché"""
        symbol_map = {
            "₿ BTCUSDT": "BTCUSDT",
            "⟠ ETHUSD": "ETHUSD", 
            "🇪🇺 EURUSD": "EURUSD",
            "🇬🇧 GBPUSD": "GBPUSD"
        }
        self.current_symbol = symbol_map.get(value, "BTCUSDT")
        self.update_charts()
        
    def on_sma_change(self, value):
        """Changement période SMA"""
        period = int(value)
        self.sma_value_label.configure(text=f"Period: {period}")
        self.update_charts()
        
    def on_ema_change(self, value):
        """Changement période EMA"""
        period = int(value)
        self.ema_value_label.configure(text=f"Period: {period}")
        self.update_charts()
        
    def on_rsi_change(self, value):
        """Changement période RSI"""
        period = int(value)
        self.rsi_value_label.configure(text=f"Period: {period}")
        self.update_charts()
        
    def on_atr_change(self, value):
        """Changement période ATR"""
        period = int(value)
        self.atr_value_label.configure(text=f"Period: {period}")
        self.update_charts()
        
    def toggle_theme(self):
        """Basculer le thème"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
    def toggle_realtime(self):
        """Toggle temps réel"""
        if not self.is_running:
            self.start_realtime()
        else:
            self.stop_realtime()
            
    def start_realtime(self):
        """Démarrer mise à jour temps réel"""
        self.is_running = True
        self.start_button.configure(
            text="⏹️ Stop Real-Time",
            fg_color=("red", "darkred")
        )
        self.realtime_loop()
        
    def stop_realtime(self):
        """Arrêter temps réel"""
        self.is_running = False
        self.start_button.configure(
            text="▶️ Start Real-Time Analysis",
            fg_color=("gray75", "gray25")
        )
        
    def realtime_loop(self):
        """Boucle de mise à jour temps réel"""
        if self.is_running:
            # Simuler nouveaux prix
            self.simulate_new_data()
            self.update_charts()
            self.update_realtime_status()
            
            # Programmer prochaine mise à jour
            self.root.after(2000, self.realtime_loop)
            
    def simulate_new_data(self):
        """Simuler de nouvelles données"""
        if self.current_symbol not in self.market_data:
            return
            
        data = self.market_data[self.current_symbol]
        
        # Ajouter un nouveau point
        last_close = data['closes'][-1]
        new_close = last_close + np.random.randn() * (last_close * 0.001)
        
        new_time = data['timestamps'][-1] + timedelta(minutes=1)
        new_open = last_close
        new_high = max(new_open, new_close) + abs(np.random.randn()) * (new_close * 0.002)
        new_low = min(new_open, new_close) - abs(np.random.randn()) * (new_close * 0.002)
        new_volume = abs(np.random.randn()) * 1000 + 500
        
        # Ajouter et limiter historique
        data['timestamps'] = list(data['timestamps']) + [new_time]
        data['opens'] = list(data['opens']) + [new_open]
        data['highs'] = list(data['highs']) + [new_high]
        data['lows'] = list(data['lows']) + [new_low]
        data['closes'] = list(data['closes']) + [new_close]
        data['volumes'] = list(data['volumes']) + [new_volume]
        
        # Garder seulement les 200 derniers points
        for key in ['timestamps', 'opens', 'highs', 'lows', 'closes', 'volumes']:
            data[key] = data[key][-200:]
    
    def calculate_rsi(self, prices, period=14):
        """Calculer RSI"""
        if len(prices) < period:
            return [50] * len(prices)
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calcul RSI
        avg_gains = pd.Series(gains).rolling(window=period).mean()
        avg_losses = pd.Series(losses).rolling(window=period).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        # Remplir les valeurs NaN au début
        rsi = rsi.fillna(50)
        
        return [50] + rsi.tolist()  # Ajouter valeur initiale
        
    def calculate_atr(self, highs, lows, closes, period=14):
        """Calculer ATR"""
        if len(highs) < period or len(lows) < period or len(closes) < period:
            return [1.0] * len(highs)
            
        # True Range calculation
        tr_list = []
        for i in range(1, len(highs)):
            h = highs[i]
            l = lows[i]
            c_prev = closes[i-1]
            
            tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
            tr_list.append(tr)
            
        # ATR calculation
        atr_values = pd.Series(tr_list).rolling(window=period).mean()
        atr_values = atr_values.fillna(1.0)
        
        return [1.0] + atr_values.tolist()  # Ajouter valeur initiale
            
    def refresh_data(self):
        """Rafraîchir les données"""
        self.market_data = self.generate_sample_data()
        self.update_charts()
        
    def update_charts(self):
        """Mettre à jour les graphiques"""
        if self.current_symbol not in self.market_data:
            return
            
        data = self.market_data[self.current_symbol]
        
        # Nettoyer graphiques
        self.ax_main.clear()
        self.ax_rsi.clear()
        self.ax_volume.clear()
        self.ax_atr.clear()
        
        # Données
        timestamps = data['timestamps']
        closes = data['closes']
        highs = data['highs']
        lows = data['lows']
        volumes = data['volumes']
        
        # === GRAPHIQUE PRINCIPAL - PRIX ===
        self.ax_main.plot(timestamps, closes, 'cyan', linewidth=2, label='Price')
        
        # SMA si activé
        if self.sma_switch.get():
            sma_period = int(self.sma_slider.get())
            if len(closes) >= sma_period:
                sma_values = pd.Series(closes).rolling(window=sma_period).mean()
                self.ax_main.plot(timestamps, sma_values, 'orange', linewidth=2, label=f'SMA({sma_period})')
        
        # EMA si activé
        if self.ema_switch.get():
            ema_period = int(self.ema_slider.get())
            if len(closes) >= ema_period:
                ema_values = pd.Series(closes).ewm(span=ema_period).mean()
                self.ax_main.plot(timestamps, ema_values, 'lime', linewidth=2, label=f'EMA({ema_period})')
        
        # Configuration graphique principal
        self.ax_main.set_facecolor('#1a1a1a')
        self.ax_main.grid(True, alpha=0.3, color='gray')
        self.ax_main.set_title(f'{self.current_symbol} - Price & Moving Averages', 
                              color='white', fontsize=14, fontweight='bold', pad=20)
        self.ax_main.legend(loc='upper left')
        self.ax_main.tick_params(colors='white')
        self.ax_main.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax_main.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        
        # === GRAPHIQUE RSI ===
        if self.rsi_switch.get():
            rsi_period = int(self.rsi_slider.get())
            rsi_values = self.calculate_rsi(closes, rsi_period)
            
            self.ax_rsi.plot(timestamps, rsi_values, 'purple', linewidth=2, label=f'RSI({rsi_period})')
            
            # Zones de surachat/survente
            self.ax_rsi.axhline(y=70, color='red', linestyle='--', alpha=0.7)
            self.ax_rsi.axhline(y=30, color='green', linestyle='--', alpha=0.7)
            self.ax_rsi.fill_between(timestamps, 70, 100, alpha=0.1, color='red')
            self.ax_rsi.fill_between(timestamps, 0, 30, alpha=0.1, color='green')
        
        self.ax_rsi.set_facecolor('#1a1a1a')
        self.ax_rsi.grid(True, alpha=0.3, color='gray')
        self.ax_rsi.set_title('RSI (Relative Strength Index)', color='white', fontsize=12, pad=10)
        self.ax_rsi.set_ylim(0, 100)
        self.ax_rsi.tick_params(colors='white')
        self.ax_rsi.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # === GRAPHIQUE VOLUME ===
        self.ax_volume.bar(timestamps, volumes, color='steelblue', alpha=0.7, width=0.02)
        self.ax_volume.set_facecolor('#1a1a1a')
        self.ax_volume.grid(True, alpha=0.3, color='gray')
        self.ax_volume.set_title('Volume', color='white', fontsize=12, pad=10)
        self.ax_volume.tick_params(colors='white')
        self.ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # === GRAPHIQUE ATR ===
        if self.atr_switch.get():
            atr_period = int(self.atr_slider.get())
            atr_values = self.calculate_atr(highs, lows, closes, atr_period)
            
            self.ax_atr.plot(timestamps, atr_values, 'red', linewidth=2, label=f'ATR({atr_period})')
            self.ax_atr.fill_between(timestamps, atr_values, alpha=0.2, color='red')
        
        self.ax_atr.set_facecolor('#1a1a1a')
        self.ax_atr.grid(True, alpha=0.3, color='gray')
        self.ax_atr.set_title('ATR (Volatility)', color='white', fontsize=12, pad=10)
        self.ax_atr.tick_params(colors='white')
        self.ax_atr.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # Refresh canvas
        self.canvas_main.draw()
        self.canvas_rsi.draw()
        self.canvas_volume_atr.draw()
        
    def update_realtime_status(self):
        """Mettre à jour le status temps réel"""
        if self.current_symbol not in self.market_data:
            return
            
        data = self.market_data[self.current_symbol]
        
        # Prix actuel
        current_price = data['closes'][-1]
        self.price_label.configure(text=f"Price: {current_price:.4f}")
        
        # SMA
        if self.sma_switch.get():
            sma_period = int(self.sma_slider.get())
            if len(data['closes']) >= sma_period:
                sma_value = pd.Series(data['closes']).rolling(window=sma_period).mean().iloc[-1]
                self.sma_status_label.configure(text=f"SMA({sma_period}): {sma_value:.4f}")
        
        # EMA
        if self.ema_switch.get():
            ema_period = int(self.ema_slider.get())
            if len(data['closes']) >= ema_period:
                ema_value = pd.Series(data['closes']).ewm(span=ema_period).mean().iloc[-1]
                self.ema_status_label.configure(text=f"EMA({ema_period}): {ema_value:.4f}")
        
        # RSI
        if self.rsi_switch.get():
            rsi_period = int(self.rsi_slider.get())
            rsi_values = self.calculate_rsi(data['closes'], rsi_period)
            if rsi_values:
                current_rsi = rsi_values[-1]
                rsi_status = "🔴 Overbought" if current_rsi > 70 else "🟢 Oversold" if current_rsi < 30 else "🟡 Neutral"
                self.rsi_status_label.configure(text=f"RSI({rsi_period}): {current_rsi:.1f} {rsi_status}")
        
        # ATR
        if self.atr_switch.get():
            atr_period = int(self.atr_slider.get())
            atr_values = self.calculate_atr(data['highs'], data['lows'], data['closes'], atr_period)
            if atr_values:
                current_atr = atr_values[-1]
                volatility_level = "📈 High" if current_atr > np.mean(atr_values) * 1.5 else "📊 Normal"
                self.atr_status_label.configure(text=f"ATR({atr_period}): {current_atr:.4f} {volatility_level}")
        
        # Signal avancé basé sur plusieurs indicateurs
        self.update_advanced_signal(data)
        
        # Status de connexion
        current_time = datetime.now().strftime("%H:%M:%S")
        self.connection_status.configure(
            text=f"🟢 Live Data | {self.current_symbol} | Last Update: {current_time}"
        )
        
    def update_advanced_signal(self, data):
        """Signal avancé basé sur SMA, EMA et RSI"""
        if len(data['closes']) < 20:
            return
            
        current_price = data['closes'][-1]
        signals = []
        
        # Signal SMA
        if self.sma_switch.get():
            sma_period = int(self.sma_slider.get())
            sma_value = pd.Series(data['closes']).rolling(window=sma_period).mean().iloc[-1]
            if current_price > sma_value * 1.002:
                signals.append('BULL')
            elif current_price < sma_value * 0.998:
                signals.append('BEAR')
        
        # Signal RSI
        if self.rsi_switch.get():
            rsi_period = int(self.rsi_slider.get())
            rsi_values = self.calculate_rsi(data['closes'], rsi_period)
            if rsi_values:
                current_rsi = rsi_values[-1]
                if current_rsi < 30:
                    signals.append('BULL')  # Oversold = potential buy
                elif current_rsi > 70:
                    signals.append('BEAR')  # Overbought = potential sell
        
        # Déterminer signal global
        bull_count = signals.count('BULL')
        bear_count = signals.count('BEAR')
        
        if bull_count > bear_count:
            self.signal_label.configure(text="Signal: 🚀 STRONG BULLISH", text_color="lime")
        elif bear_count > bull_count:
            self.signal_label.configure(text="Signal: 🔻 STRONG BEARISH", text_color="red")
        elif bull_count > 0 or bear_count > 0:
            self.signal_label.configure(text="Signal: ⚡ MIXED SIGNALS", text_color="orange")
        else:
            self.signal_label.configure(text="Signal: 🟡 NEUTRAL", text_color="gray70")
        
    def run(self):
        """Lancer l'application"""
        print("""
🚀 THEBOT Native Ultra-Moderne Starting...

✨ Interface Native CustomTkinter
📊 Real-time market analysis
🎨 Modern dark theme with animations
📈 Interactive charts with matplotlib
⚡ Live data simulation

🎯 Ready for professional trading!
        """)
        
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    try:
        app = UltraModernTHEBOT()
        app.run()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        messagebox.showerror("Erreur Fatale", str(e))


if __name__ == "__main__":
    main()