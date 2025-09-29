#!/usr/bin/env python3
"""
THEBOT - Interface PyQt6 Native
Fenêtre principale de l'application de trading
"""

import sys
from typing import Optional, List
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox,
    QGridLayout, QComboBox, QSpinBox, QDoubleSpinBox, QProgressBar,
    QStatusBar, QMenuBar, QToolBar, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

# Imports des modules THEBOT
from thebot.indicators.basic.sma import SMAIndicator
from thebot.indicators.basic.ema import EMAIndicator
from thebot.indicators.volatility.atr import ATRIndicator
from thebot.indicators.oscillators.rsi import RSIIndicator
from thebot.core.types import MarketData, TimeFrame


class ChartWidget(FigureCanvas):
    """Widget de graphique intégré"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Configuration du thème sombre
        self.fig.patch.set_facecolor('#2b2b2b')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e1e')
        
        # Style des axes
        self.axes.tick_params(colors='white')
        self.axes.xaxis.label.set_color('white')
        self.axes.yaxis.label.set_color('white')
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white')
        self.axes.spines['right'].set_color('white')
        self.axes.spines['left'].set_color('white')
        
        self.sample_data()
        
    def sample_data(self):
        """Données d'exemple"""
        x = np.linspace(0, 100, 100)
        y = np.random.randn(100).cumsum() + 100
        
        self.axes.clear()
        self.axes.set_facecolor('#1e1e1e')
        self.axes.plot(x, y, color='#00ff00', linewidth=2, label='Prix')
        self.axes.set_title('THEBOT - Graphique de Prix', color='white', fontsize=14)
        self.axes.set_xlabel('Temps', color='white')
        self.axes.set_ylabel('Prix', color='white')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)
        
        # Recolorer les éléments
        self.axes.tick_params(colors='white')
        for spine in self.axes.spines.values():
            spine.set_color('white')
            
        self.draw()
        
    def plot_indicator(self, data: pd.Series, name: str, color: str = '#ff6600'):
        """Afficher un indicateur"""
        self.axes.plot(data.index, data.values, color=color, linewidth=2, label=name)
        self.axes.legend()
        self.draw()


class IndicatorsPanel(QGroupBox):
    """Panneau de contrôle des indicateurs"""
    
    indicator_calculated = pyqtSignal(str, object)  # Signal pour les résultats
    
    def __init__(self, parent=None):
        super().__init__("📊 Indicateurs Techniques", parent)
        self.init_ui()
        self.init_indicators()
        
    def init_ui(self):
        layout = QGridLayout()
        
        # SMA Controls
        layout.addWidget(QLabel("🔸 SMA Période:"), 0, 0)
        self.sma_period = QSpinBox()
        self.sma_period.setRange(1, 200)
        self.sma_period.setValue(20)
        layout.addWidget(self.sma_period, 0, 1)
        
        self.sma_btn = QPushButton("Calculer SMA")
        self.sma_btn.clicked.connect(self.calculate_sma)
        layout.addWidget(self.sma_btn, 0, 2)
        
        # EMA Controls
        layout.addWidget(QLabel("🔸 EMA Période:"), 1, 0)
        self.ema_period = QSpinBox()
        self.ema_period.setRange(1, 200)
        self.ema_period.setValue(12)
        layout.addWidget(self.ema_period, 1, 1)
        
        self.ema_btn = QPushButton("Calculer EMA")
        self.ema_btn.clicked.connect(self.calculate_ema)
        layout.addWidget(self.ema_btn, 1, 2)
        
        # RSI Controls
        layout.addWidget(QLabel("🔸 RSI Période:"), 2, 0)
        self.rsi_period = QSpinBox()
        self.rsi_period.setRange(1, 50)
        self.rsi_period.setValue(14)
        layout.addWidget(self.rsi_period, 2, 1)
        
        self.rsi_btn = QPushButton("Calculer RSI")
        self.rsi_btn.clicked.connect(self.calculate_rsi)
        layout.addWidget(self.rsi_btn, 2, 2)
        
        # ATR Controls
        layout.addWidget(QLabel("🔸 ATR Période:"), 3, 0)
        self.atr_period = QSpinBox()
        self.atr_period.setRange(1, 50)
        self.atr_period.setValue(14)
        layout.addWidget(self.atr_period, 3, 1)
        
        self.atr_btn = QPushButton("Calculer ATR")
        self.atr_btn.clicked.connect(self.calculate_atr)
        layout.addWidget(self.atr_btn, 3, 2)
        
        # Résultats
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        layout.addWidget(QLabel("📋 Résultats:"), 4, 0, 1, 3)
        layout.addWidget(self.results_text, 5, 0, 1, 3)
        
        self.setLayout(layout)
        
    def init_indicators(self):
        """Initialiser les calculateurs d'indicateurs"""
        from thebot.indicators.basic.sma.config import SMAConfig
        from thebot.indicators.basic.ema.config import EMAConfig
        from thebot.indicators.volatility.atr.config import ATRConfig
        from thebot.indicators.oscillators.rsi.config import RSIConfig
        
        self.sma_calc = SMAIndicator(SMAConfig(period=20))
        self.ema_calc = EMAIndicator(EMAConfig(period=12))
        self.rsi_calc = RSIIndicator(RSIConfig(period=14))
        self.atr_calc = ATRIndicator(ATRConfig(period=14))
        
        # Données d'exemple
        self.sample_prices = [100 + np.random.randn() * 2 + i * 0.1 for i in range(100)]
        
    @pyqtSlot()
    def calculate_sma(self):
        """Calculer SMA"""
        try:
            period = self.sma_period.value()
            # Recréer le calculateur avec la nouvelle période
            from thebot.indicators.basic.sma.config import SMAConfig
            self.sma_calc = SMAIndicator(SMAConfig(period=period))
            
            results = []
            for price in self.sample_prices[-50:]:  # Dernières 50 valeurs
                result = self.sma_calc.calculate(price)
                if result.sma_value is not None:
                    results.append(result.sma_value)
                    
            if results:
                avg = np.mean(results)
                self.results_text.append(f"✅ SMA({period}): {avg:.4f} | Dernière valeur: {results[-1]:.4f}")
                self.indicator_calculated.emit("SMA", results)
            else:
                self.results_text.append(f"❌ SMA({period}): Données insuffisantes")
                
        except Exception as e:
            self.results_text.append(f"❌ Erreur SMA: {str(e)}")
            
    @pyqtSlot()
    def calculate_ema(self):
        """Calculer EMA"""
        try:
            period = self.ema_period.value()
            from thebot.indicators.basic.ema.config import EMAConfig
            self.ema_calc = EMAIndicator(EMAConfig(period=period))
            
            results = []
            for price in self.sample_prices[-50:]:
                result = self.ema_calc.calculate(price)
                if result.ema_value is not None:
                    results.append(result.ema_value)
                    
            if results:
                self.results_text.append(f"✅ EMA({period}): {results[-1]:.4f} | Trend: {results[-1] - results[-10] if len(results) > 10 else 0:.4f}")
                self.indicator_calculated.emit("EMA", results)
            else:
                self.results_text.append(f"❌ EMA({period}): Données insuffisantes")
                
        except Exception as e:
            self.results_text.append(f"❌ Erreur EMA: {str(e)}")
            
    @pyqtSlot()
    def calculate_rsi(self):
        """Calculer RSI"""
        try:
            period = self.rsi_period.value()
            from thebot.indicators.oscillators.rsi.config import RSIConfig
            self.rsi_calc = RSIIndicator(RSIConfig(period=period))
            
            results = []
            for price in self.sample_prices[-50:]:
                result = self.rsi_calc.calculate(price)
                if result.rsi_value is not None:
                    results.append(result.rsi_value)
                    
            if results:
                current_rsi = results[-1]
                status = "🔴 Survente" if current_rsi < 30 else "🟢 Surachat" if current_rsi > 70 else "🔵 Neutre"
                self.results_text.append(f"✅ RSI({period}): {current_rsi:.2f} | {status}")
                self.indicator_calculated.emit("RSI", results)
            else:
                self.results_text.append(f"❌ RSI({period}): Données insuffisantes")
                
        except Exception as e:
            self.results_text.append(f"❌ Erreur RSI: {str(e)}")
            
    @pyqtSlot()
    def calculate_atr(self):
        """Calculer ATR"""
        try:
            period = self.atr_period.value()
            # Simuler des données OHLC
            results = []
            for i in range(len(self.sample_prices) - 1):
                high = self.sample_prices[i] + abs(np.random.randn() * 0.5)
                low = self.sample_prices[i] - abs(np.random.randn() * 0.5)
                close = self.sample_prices[i+1]
                
                market_data = MarketData(
                    timestamp=pd.Timestamp.now(),
                    open=self.sample_prices[i],
                    high=high,
                    low=low,
                    close=close,
                    volume=1000,
                    timeframe=TimeFrame.M1
                )
                
                result = self.atr_calc.calculate(market_data)
                if result.atr_value is not None:
                    results.append(result.atr_value)
                    
            if results:
                current_atr = results[-1]
                volatility = "📈 Haute" if current_atr > 2 else "📊 Normale" if current_atr > 1 else "📉 Faible"
                self.results_text.append(f"✅ ATR({period}): {current_atr:.4f} | Volatilité: {volatility}")
                self.indicator_calculated.emit("ATR", results)
            else:
                self.results_text.append(f"❌ ATR({period}): Données insuffisantes")
                
        except Exception as e:
            self.results_text.append(f"❌ Erreur ATR: {str(e)}")


class MainWindow(QMainWindow):
    """Fenêtre principale THEBOT"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖 THEBOT - Analyse Technique Native")
        self.setGeometry(100, 100, 1400, 900)
        
        # Thème sombre
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #404040;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555;
                border-radius: 3px;
            }
        """)
        
        self.init_ui()
        self.init_menu()
        self.init_status()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout()
        
        # Splitter pour diviser la fenêtre
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panneau gauche - Contrôles
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Titre et informations
        title_label = QLabel("🤖 THEBOT v1.0")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title_label)
        
        info_label = QLabel("Plateforme d'analyse technique ultra-modulaire")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #888; font-style: italic;")
        left_layout.addWidget(info_label)
        
        # Panneau des indicateurs
        self.indicators_panel = IndicatorsPanel()
        self.indicators_panel.indicator_calculated.connect(self.on_indicator_calculated)
        left_layout.addWidget(self.indicators_panel)
        
        # Boutons d'action
        action_group = QGroupBox("⚡ Actions")
        action_layout = QVBoxLayout()
        
        refresh_btn = QPushButton("🔄 Actualiser Données")
        refresh_btn.clicked.connect(self.refresh_data)
        action_layout.addWidget(refresh_btn)
        
        reset_btn = QPushButton("🧹 Réinitialiser")
        reset_btn.clicked.connect(self.reset_all)
        action_layout.addWidget(reset_btn)
        
        test_btn = QPushButton("🧪 Tests Unitaires")
        test_btn.clicked.connect(self.run_tests)
        action_layout.addWidget(test_btn)
        
        action_group.setLayout(action_layout)
        left_layout.addWidget(action_group)
        
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(400)
        
        # Panneau droit - Graphiques
        self.chart_widget = ChartWidget()
        
        # Ajouter au splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.chart_widget)
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
    def init_menu(self):
        """Initialiser le menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu('📁 Fichier')
        
        exit_action = QAction('🚪 Quitter', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Aide
        help_menu = menubar.addMenu('❓ Aide')
        
        about_action = QAction('ℹ️ À propos', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def init_status(self):
        """Initialiser la barre de statut"""
        self.statusBar().showMessage("✅ THEBOT prêt - Application native PyQt6")
        
    @pyqtSlot(str, object)
    def on_indicator_calculated(self, name: str, data):
        """Quand un indicateur est calculé"""
        try:
            if len(data) > 0:
                # Mettre à jour le graphique
                self.chart_widget.sample_data()  # Redessiner le graphique de base
                
                # Ajouter l'indicateur
                x = range(len(data))
                color_map = {"SMA": "#00ff00", "EMA": "#ff6600", "RSI": "#ff00ff", "ATR": "#00ffff"}
                color = color_map.get(name, "#ffffff")
                
                self.chart_widget.axes.plot(x, data, color=color, linewidth=2, label=f'{name}', alpha=0.8)
                self.chart_widget.axes.legend()
                self.chart_widget.draw()
                
                self.statusBar().showMessage(f"✅ {name} calculé avec succès - {len(data)} points de données")
        except Exception as e:
            self.statusBar().showMessage(f"❌ Erreur affichage {name}: {str(e)}")
            
    @pyqtSlot()
    def refresh_data(self):
        """Actualiser les données"""
        self.chart_widget.sample_data()
        self.indicators_panel.results_text.append("🔄 Données actualisées")
        self.statusBar().showMessage("🔄 Données actualisées")
        
    @pyqtSlot()
    def reset_all(self):
        """Réinitialiser tout"""
        self.indicators_panel.results_text.clear()
        self.chart_widget.sample_data()
        self.statusBar().showMessage("🧹 Interface réinitialisée")
        
    @pyqtSlot()
    def run_tests(self):
        """Lancer les tests unitaires"""
        self.statusBar().showMessage("🧪 Lancement des tests...")
        # Lancer les tests en arrière-plan
        import subprocess
        import sys
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/unit/indicators/', '-v'
            ], capture_output=True, text=True, cwd='/home/rono/THEBOT')
            
            if result.returncode == 0:
                self.indicators_panel.results_text.append("✅ Tous les tests unitaires passent !")
                self.statusBar().showMessage("✅ Tests réussis")
            else:
                self.indicators_panel.results_text.append(f"❌ Échec des tests:\n{result.stdout}")
                self.statusBar().showMessage("❌ Tests échoués")
                
        except Exception as e:
            self.indicators_panel.results_text.append(f"❌ Erreur tests: {str(e)}")
            self.statusBar().showMessage("❌ Erreur lors des tests")
            
    def show_about(self):
        """Afficher les informations"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "À propos de THEBOT", 
                         "🤖 THEBOT v1.0\n\n"
                         "Plateforme d'analyse technique ultra-modulaire\n"
                         "Interface native PyQt6\n\n"
                         "Indicateurs supportés:\n"
                         "• SMA - Simple Moving Average\n"
                         "• EMA - Exponential Moving Average\n"
                         "• RSI - Relative Strength Index\n"
                         "• ATR - Average True Range\n\n"
                         "Architecture 100% native - Aucune dépendance navigateur")


def main():
    """Point d'entrée principal"""
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("THEBOT")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("THEBOT Analytics")
    
    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()
    
    # Démarrer la boucle d'événements
    sys.exit(app.exec())


if __name__ == '__main__':
    main()