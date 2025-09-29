#!/usr/bin/env python3
"""
THEBOT - Interface Ultra-Moderne avec CustomTkinter
Design moderne, thèmes dark/light, animations fluides
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkinter
from matplotlib.figure import Figure
import threading
from decimal import Decimal
from datetime import datetime, timedelta


class ModernTHEBOTApp:
    """Application THEBOT avec UI ultra-moderne"""
    
    def __init__(self):
        # Configuration CustomTkinter
        ctk.set_appearance_mode("dark")  # "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("🤖 THEBOT - Analyse Technique Moderne")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        
        # Variables
        self.is_running = False
        self.data_points = []
        self.results_history = {
            'sma': [], 'ema': [], 'rsi': [], 'atr': [],
            'timestamps': [], 'prices': []
        }
        
        self.create_modern_ui()
        self.setup_calculators()
        self.setup_real_time_updates()
        
    def create_modern_ui(self):
        """Créer l'interface moderne"""
        
        # ===== SIDEBAR (Panneau de contrôle) =====
        self.sidebar = ctk.CTkFrame(self.root, width=300, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.sidebar.pack_propagate(False)
        
        # Logo/Titre
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🤖 THEBOT",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.logo_label.pack(pady=(20, 10))
        
        self.subtitle = ctk.CTkLabel(
            self.sidebar, 
            text="Analyse Technique Avancée",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle.pack(pady=(0, 30))
        
        # ===== CONTRÔLES DES INDICATEURS =====
        self.create_indicator_controls()
        
        # ===== CONTRÔLES PRINCIPAUX =====
        self.create_main_controls()
        
        # ===== STATUS =====
        self.create_status_panel()
        
        # ===== ZONE PRINCIPALE (Graphiques) =====
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Onglets pour différents graphiques
        self.tabview = ctk.CTkTabview(self.main_frame, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Onglet Analyse Temps Réel
        self.tab_realtime = self.tabview.add("📈 Temps Réel")
        self.create_realtime_chart()
        
        # Onglet Indicateurs
        self.tab_indicators = self.tabview.add("📊 Indicateurs")
        self.create_indicators_chart()
        
        # Onglet Configuration
        self.tab_config = self.tabview.add("⚙️ Configuration")
        self.create_config_panel()
        
    def create_indicator_controls(self):
        """Panneau de contrôle des indicateurs"""
        
        # Titre section
        ctk.CTkLabel(
            self.sidebar, 
            text="Paramètres Indicateurs",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 15))
        
        # Frame pour les contrôles
        controls_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10)
        
        # SMA
        sma_frame = ctk.CTkFrame(controls_frame)
        sma_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(sma_frame, text="SMA Période:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.sma_slider = ctk.CTkSlider(sma_frame, from_=5, to=50, number_of_steps=45)
        self.sma_slider.pack(fill="x", padx=10, pady=5)
        self.sma_slider.set(20)
        
        self.sma_value_label = ctk.CTkLabel(sma_frame, text="20")
        self.sma_value_label.pack(pady=(0,10))
        self.sma_slider.configure(command=self.update_sma_label)
        
        # EMA
        ema_frame = ctk.CTkFrame(controls_frame)
        ema_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ema_frame, text="EMA Période:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.ema_slider = ctk.CTkSlider(ema_frame, from_=5, to=50, number_of_steps=45)
        self.ema_slider.pack(fill="x", padx=10, pady=5)
        self.ema_slider.set(12)
        
        self.ema_value_label = ctk.CTkLabel(ema_frame, text="12")
        self.ema_value_label.pack(pady=(0,10))
        self.ema_slider.configure(command=self.update_ema_label)
        
        # RSI
        rsi_frame = ctk.CTkFrame(controls_frame)
        rsi_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(rsi_frame, text="RSI Période:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.rsi_slider = ctk.CTkSlider(rsi_frame, from_=5, to=30, number_of_steps=25)
        self.rsi_slider.pack(fill="x", padx=10, pady=5)
        self.rsi_slider.set(14)
        
        self.rsi_value_label = ctk.CTkLabel(rsi_frame, text="14")
        self.rsi_value_label.pack(pady=(0,10))
        self.rsi_slider.configure(command=self.update_rsi_label)
        
        # ATR
        atr_frame = ctk.CTkFrame(controls_frame)
        atr_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(atr_frame, text="ATR Période:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.atr_slider = ctk.CTkSlider(atr_frame, from_=5, to=30, number_of_steps=25)
        self.atr_slider.pack(fill="x", padx=10, pady=5)
        self.atr_slider.set(14)
        
        self.atr_value_label = ctk.CTkLabel(atr_frame, text="14")
        self.atr_value_label.pack(pady=(0,10))
        self.atr_slider.configure(command=self.update_atr_label)
        
    def create_main_controls(self):
        """Contrôles principaux"""
        
        ctk.CTkLabel(
            self.sidebar, 
            text="Contrôles",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(30, 15))
        
        # Boutons avec icônes modernes
        self.start_btn = ctk.CTkButton(
            self.sidebar,
            text="▶️ Démarrer Analyse",
            command=self.start_analysis,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.start_btn.pack(fill="x", padx=10, pady=5)
        
        self.stop_btn = ctk.CTkButton(
            self.sidebar,
            text="⏹️ Arrêter",
            command=self.stop_analysis,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.stop_btn.pack(fill="x", padx=10, pady=5)
        
        self.reset_btn = ctk.CTkButton(
            self.sidebar,
            text="🔄 Reset",
            command=self.reset_data,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.reset_btn.pack(fill="x", padx=10, pady=5)
        
        # Switch thème
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="🌙 Mode Sombre",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12)
        )
        self.theme_switch.pack(pady=(20, 10))
        self.theme_switch.select()  # Dark par défaut
        
    def create_status_panel(self):
        """Panneau de statut en temps réel"""
        
        status_frame = ctk.CTkFrame(self.sidebar)
        status_frame.pack(fill="x", padx=10, pady=(20, 10), side="bottom")
        
        ctk.CTkLabel(
            status_frame,
            text="État Temps Réel",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Métriques en temps réel
        self.price_label = ctk.CTkLabel(status_frame, text="Prix: --", font=ctk.CTkFont(size=12))
        self.price_label.pack()
        
        self.sma_result_label = ctk.CTkLabel(status_frame, text="SMA: --", font=ctk.CTkFont(size=12))
        self.sma_result_label.pack()
        
        self.ema_result_label = ctk.CTkLabel(status_frame, text="EMA: --", font=ctk.CTkFont(size=12))
        self.ema_result_label.pack()
        
        self.rsi_result_label = ctk.CTkLabel(status_frame, text="RSI: --", font=ctk.CTkFont(size=12))
        self.rsi_result_label.pack()
        
        self.atr_result_label = ctk.CTkLabel(status_frame, text="ATR: --", font=ctk.CTkFont(size=12))
        self.atr_result_label.pack(pady=(0,10))
        
    def create_realtime_chart(self):
        """Graphique temps réel avec matplotlib"""
        
        # Figure matplotlib avec style moderne
        plt.style.use('dark_background')
        self.fig_realtime = Figure(figsize=(12, 8), facecolor='#212121')
        
        # Sous-graphiques
        self.ax_price = self.fig_realtime.add_subplot(211)
        self.ax_rsi = self.fig_realtime.add_subplot(212)
        
        # Configuration axes
        self.ax_price.set_title('Prix et Moyennes Mobiles', color='white', fontsize=14, weight='bold')
        self.ax_price.set_ylabel('Prix', color='white')
        self.ax_price.grid(True, alpha=0.3)
        
        self.ax_rsi.set_title('RSI (Relative Strength Index)', color='white', fontsize=12)
        self.ax_rsi.set_ylabel('RSI', color='white')
        self.ax_rsi.set_ylim(0, 100)
        self.ax_rsi.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Surachat')
        self.ax_rsi.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Survente')
        self.ax_rsi.grid(True, alpha=0.3)
        self.ax_rsi.legend()
        
        # Canvas
        self.canvas_realtime = FigureCanvasTkinter(self.fig_realtime, self.tab_realtime)
        self.canvas_realtime.pack(fill="both", expand=True)
        
    def create_indicators_chart(self):
        """Graphique dédié aux indicateurs"""
        
        self.fig_indicators = Figure(figsize=(12, 8), facecolor='#212121')
        
        # 2x2 subplots pour chaque indicateur
        self.ax_sma = self.fig_indicators.add_subplot(221)
        self.ax_ema = self.fig_indicators.add_subplot(222)
        self.ax_rsi_detail = self.fig_indicators.add_subplot(223)
        self.ax_atr = self.fig_indicators.add_subplot(224)
        
        # Configuration
        for ax, title in zip([self.ax_sma, self.ax_ema, self.ax_rsi_detail, self.ax_atr],
                           ['SMA Evolution', 'EMA Evolution', 'RSI Détaillé', 'ATR Volatilité']):
            ax.set_title(title, color='white', fontsize=10)
            ax.grid(True, alpha=0.3)
        
        self.fig_indicators.tight_layout()
        
        self.canvas_indicators = FigureCanvasTkinter(self.fig_indicators, self.tab_indicators)
        self.canvas_indicators.pack(fill="both", expand=True)
        
    def create_config_panel(self):
        """Panneau de configuration avancé"""
        
        config_scroll = ctk.CTkScrollableFrame(self.tab_config)
        config_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Section Données
        ctk.CTkLabel(config_scroll, text="Configuration des Données", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Simulation parameters
        data_frame = ctk.CTkFrame(config_scroll)
        data_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(data_frame, text="Fréquence de mise à jour (ms):", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=10)
        
        self.update_freq_slider = ctk.CTkSlider(data_frame, from_=100, to=2000, number_of_steps=19)
        self.update_freq_slider.pack(fill="x", padx=20)
        self.update_freq_slider.set(500)
        
        self.freq_label = ctk.CTkLabel(data_frame, text="500 ms")
        self.freq_label.pack(pady=(0,20))
        self.update_freq_slider.configure(command=self.update_freq_label)
        
        # Section Affichage
        ctk.CTkLabel(config_scroll, text="Options d'Affichage", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30,20))
        
        display_frame = ctk.CTkFrame(config_scroll)
        display_frame.pack(fill="x", pady=10)
        
        self.show_grid = ctk.CTkCheckBox(display_frame, text="Afficher la grille")
        self.show_grid.pack(anchor="w", padx=20, pady=10)
        self.show_grid.select()
        
        self.show_legend = ctk.CTkCheckBox(display_frame, text="Afficher les légendes")
        self.show_legend.pack(anchor="w", padx=20, pady=10)
        self.show_legend.select()
        
        self.animation_enabled = ctk.CTkCheckBox(display_frame, text="Animations fluides")
        self.animation_enabled.pack(anchor="w", padx=20, pady=(10,20))
        self.animation_enabled.select()
        
    def setup_calculators(self):
        """Initialiser les calculateurs"""
        try:
            from thebot.indicators.basic.sma.config import SMAConfig
            from thebot.indicators.basic.sma.calculator import SMACalculator
            
            # Commencer avec SMA simple pour test
            self.sma_calc = SMACalculator(SMAConfig(period=20))
            
            self.log_status("✅ Calculateurs initialisés")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur initialisation: {e}")
            
    def setup_real_time_updates(self):
        """Configuration des mises à jour temps réel"""
        self.update_timer = None
        
    # ===== CALLBACKS =====
    
    def update_sma_label(self, value):
        self.sma_value_label.configure(text=f"{int(value)}")
        
    def update_ema_label(self, value):
        self.ema_value_label.configure(text=f"{int(value)}")
        
    def update_rsi_label(self, value):
        self.rsi_value_label.configure(text=f"{int(value)}")
        
    def update_atr_label(self, value):
        self.atr_value_label.configure(text=f"{int(value)}")
        
    def update_freq_label(self, value):
        self.freq_label.configure(text=f"{int(value)} ms")
        
    def toggle_theme(self):
        """Basculer entre thème clair/sombre"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
    def start_analysis(self):
        """Démarrer l'analyse en temps réel"""
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.real_time_analysis()
        
    def stop_analysis(self):
        """Arrêter l'analyse"""
        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
    def reset_data(self):
        """Reset toutes les données"""
        self.results_history = {
            'sma': [], 'ema': [], 'rsi': [], 'atr': [],
            'timestamps': [], 'prices': []
        }
        self.clear_charts()
        self.log_status("🔄 Données réinitialisées")
        
    def real_time_analysis(self):
        """Simulation d'analyse temps réel"""
        if not self.is_running:
            return
            
        try:
            # Générer prix simulé
            base_price = 100 if not self.results_history['prices'] else self.results_history['prices'][-1]
            new_price = base_price + np.random.randn() * 0.5
            
            # Ajouter aux données
            self.results_history['prices'].append(new_price)
            self.results_history['timestamps'].append(datetime.now())
            
            # Calculer SMA (simple pour demo)
            if len(self.results_history['prices']) >= int(self.sma_slider.get()):
                period = int(self.sma_slider.get())
                sma_value = np.mean(self.results_history['prices'][-period:])
                self.results_history['sma'].append(sma_value)
            else:
                self.results_history['sma'].append(None)
                
            # Mettre à jour UI
            self.update_status_display()
            self.update_charts()
            
            # Programmer prochaine mise à jour
            freq = int(self.update_freq_slider.get())
            self.root.after(freq, self.real_time_analysis)
            
        except Exception as e:
            self.log_status(f"❌ Erreur: {e}")
            self.stop_analysis()
            
    def update_status_display(self):
        """Mettre à jour l'affichage du statut"""
        if self.results_history['prices']:
            current_price = self.results_history['prices'][-1]
            self.price_label.configure(text=f"Prix: {current_price:.4f}")
            
        if self.results_history['sma'] and self.results_history['sma'][-1]:
            sma_val = self.results_history['sma'][-1]
            self.sma_result_label.configure(text=f"SMA: {sma_val:.4f}")
            
    def update_charts(self):
        """Mettre à jour les graphiques"""
        if not self.results_history['prices']:
            return
            
        try:
            # Graphique temps réel - Prix
            self.ax_price.clear()
            self.ax_price.plot(self.results_history['prices'], 'b-', linewidth=2, label='Prix')
            
            # SMA si disponible
            sma_values = [v for v in self.results_history['sma'] if v is not None]
            if sma_values:
                start_idx = len(self.results_history['sma']) - len(sma_values)
                x_sma = list(range(start_idx, len(self.results_history['prices'])))
                self.ax_price.plot(x_sma, sma_values, 'r--', linewidth=2, label=f'SMA({int(self.sma_slider.get())})')
                
            self.ax_price.set_title('Prix et Moyennes Mobiles', color='white', fontsize=14, weight='bold')
            self.ax_price.legend()
            self.ax_price.grid(True, alpha=0.3)
            
            # RSI simulé
            self.ax_rsi.clear()
            if len(self.results_history['prices']) > 1:
                # RSI simulé simple
                rsi_sim = 50 + 30 * np.sin(len(self.results_history['prices']) * 0.1)
                rsi_values = [rsi_sim] * len(self.results_history['prices'])
                self.ax_rsi.plot(rsi_values, 'purple', linewidth=2)
                self.ax_rsi.axhline(y=70, color='r', linestyle='--', alpha=0.7)
                self.ax_rsi.axhline(y=30, color='g', linestyle='--', alpha=0.7)
                self.ax_rsi.set_ylim(0, 100)
                
            self.ax_rsi.set_title('RSI (Simulé)', color='white')
            self.ax_rsi.grid(True, alpha=0.3)
            
            self.canvas_realtime.draw()
            
        except Exception as e:
            print(f"Erreur mise à jour graphiques: {e}")
            
    def clear_charts(self):
        """Nettoyer les graphiques"""
        self.ax_price.clear()
        self.ax_rsi.clear()
        self.canvas_realtime.draw()
        
    def log_status(self, message):
        """Log de statut"""
        print(f"[THEBOT] {message}")
        
    def run(self):
        """Lancer l'application"""
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    print("🚀 Lancement THEBOT UI Moderne...")
    
    try:
        app = ModernTHEBOTApp()
        app.run()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        messagebox.showerror("Erreur Fatale", str(e))


if __name__ == "__main__":
    main()