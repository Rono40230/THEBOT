#!/usr/bin/env python3
"""
THEBOT - Application Native Desktop
Interface de trading professionnelle avec PyQt6
"""

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

try:
    from PyQt6.QtChart import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
    from PyQt6.QtCore import QSize, Qt, QThread, QTimer, pyqtSignal
    from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPalette, QPixmap
    from PyQt6.QtWidgets import (
        QApplication,
        QComboBox,
        QDoubleSpinBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMenu,
        QMenuBar,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QSplitter,
        QStatusBar,
        QSystemTrayIcon,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Fallback vers Tkinter si PyQt6 pas disponible
if not PYQT_AVAILABLE:
    import tkinter as tk
    from tkinter import messagebox, ttk

    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTk
        from matplotlib.figure import Figure

        MATPLOTLIB_AVAILABLE = True
    except ImportError:
        MATPLOTLIB_AVAILABLE = False

# Imports des indicateurs THEBOT
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from thebot.indicators.basic.ema import EMAIndicator
from thebot.indicators.basic.sma import SMAIndicator
from thebot.indicators.oscillators.rsi import RSIIndicator
from thebot.indicators.volatility.atr import ATRIndicator


@dataclass
class MarketData:
    """Données de marché simulées"""

    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class MarketDataGenerator:
    """Générateur de données de marché simulées"""

    def __init__(self, symbol: str, base_price: float = 50000.0):
        self.symbol = symbol
        self.current_price = Decimal(str(base_price))
        self.current_time = datetime.now()

    def generate_next_candle(self) -> MarketData:
        """Génère la prochaine bougie"""
        import random

        # Mouvement aléatoire (-2% à +2%)
        change_pct = Decimal(str(random.uniform(-0.02, 0.02)))
        new_price = self.current_price * (1 + change_pct)

        # OHLC réaliste
        open_price = self.current_price
        close_price = new_price
        high_price = max(open_price, close_price) * Decimal("1.001")
        low_price = min(open_price, close_price) * Decimal("0.999")
        volume = Decimal(str(random.uniform(1000, 10000)))

        self.current_price = close_price
        self.current_time += timedelta(minutes=1)

        return MarketData(
            symbol=self.symbol,
            timestamp=self.current_time,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
        )


if PYQT_AVAILABLE:

    class THEBOTMainWindow(QMainWindow):
        """Fenêtre principale de l'application native THEBOT"""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("THEBOT - Trading Analysis Platform")
            self.setGeometry(100, 100, 1400, 900)

            # Données et indicateurs
            self.market_generators = {
                "BTCUSDT": MarketDataGenerator("BTCUSDT", 50000),
                "ETHUSD": MarketDataGenerator("ETHUSD", 3000),
                "EURUSD": MarketDataGenerator("EURUSD", 1.1),
                "GBPUSD": MarketDataGenerator("GBPUSD", 1.3),
            }

            self.price_history: Dict[str, List[MarketData]] = {
                symbol: [] for symbol in self.market_generators.keys()
            }

            self.indicators = {
                "SMA": SMAIndicator(),
                "EMA": EMAIndicator(),
                "ATR": ATRIndicator(),
                "RSI": RSIIndicator(),
            }

            self.setup_ui()
            self.setup_timer()
            self.setup_system_tray()

        def setup_ui(self):
            """Configuration de l'interface utilisateur"""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout principal
            main_layout = QHBoxLayout(central_widget)

            # Splitter principal
            main_splitter = QSplitter(Qt.Orientation.Horizontal)
            main_layout.addWidget(main_splitter)

            # Panel de contrôle gauche
            control_panel = self.create_control_panel()
            main_splitter.addWidget(control_panel)

            # Panel central avec onglets
            chart_panel = self.create_chart_panel()
            main_splitter.addWidget(chart_panel)

            # Panel indicateurs droite
            indicators_panel = self.create_indicators_panel()
            main_splitter.addWidget(indicators_panel)

            # Proportions
            main_splitter.setSizes([250, 800, 350])

            # Menu bar
            self.create_menu_bar()

            # Status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("THEBOT Ready - Ultra-Modular Architecture")

        def create_control_panel(self) -> QWidget:
            """Panel de contrôle des paramètres"""
            widget = QWidget()
            widget.setMaximumWidth(300)
            layout = QVBoxLayout(widget)

            # Sélection de marché
            market_group = QGroupBox("Marché")
            market_layout = QVBoxLayout(market_group)

            self.symbol_combo = QComboBox()
            self.symbol_combo.addItems(["BTCUSDT", "ETHUSD", "EURUSD", "GBPUSD"])
            self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
            market_layout.addWidget(self.symbol_combo)

            layout.addWidget(market_group)

            # Configuration SMA
            sma_group = QGroupBox("SMA - Simple Moving Average")
            sma_layout = QGridLayout(sma_group)

            sma_layout.addWidget(QLabel("Période:"), 0, 0)
            self.sma_period = QSpinBox()
            self.sma_period.setRange(5, 200)
            self.sma_period.setValue(20)
            sma_layout.addWidget(self.sma_period, 0, 1)

            layout.addWidget(sma_group)

            # Configuration EMA
            ema_group = QGroupBox("EMA - Exponential Moving Average")
            ema_layout = QGridLayout(ema_group)

            ema_layout.addWidget(QLabel("Période:"), 0, 0)
            self.ema_period = QSpinBox()
            self.ema_period.setRange(5, 200)
            self.ema_period.setValue(12)
            ema_layout.addWidget(self.ema_period, 0, 1)

            layout.addWidget(ema_group)

            # Configuration ATR
            atr_group = QGroupBox("ATR - Average True Range")
            atr_layout = QGridLayout(atr_group)

            atr_layout.addWidget(QLabel("Période:"), 0, 0)
            self.atr_period = QSpinBox()
            self.atr_period.setRange(5, 50)
            self.atr_period.setValue(14)
            atr_layout.addWidget(self.atr_period, 0, 1)

            layout.addWidget(atr_group)

            # Configuration RSI
            rsi_group = QGroupBox("RSI - Relative Strength Index")
            rsi_layout = QGridLayout(rsi_group)

            rsi_layout.addWidget(QLabel("Période:"), 0, 0)
            self.rsi_period = QSpinBox()
            self.rsi_period.setRange(5, 50)
            self.rsi_period.setValue(14)
            rsi_layout.addWidget(self.rsi_period, 0, 1)

            rsi_layout.addWidget(QLabel("Survente:"), 1, 0)
            self.rsi_oversold = QSpinBox()
            self.rsi_oversold.setRange(10, 40)
            self.rsi_oversold.setValue(30)
            rsi_layout.addWidget(self.rsi_oversold, 1, 1)

            rsi_layout.addWidget(QLabel("Surachat:"), 2, 0)
            self.rsi_overbought = QSpinBox()
            self.rsi_overbought.setRange(60, 90)
            self.rsi_overbought.setValue(70)
            rsi_layout.addWidget(self.rsi_overbought, 2, 1)

            layout.addWidget(rsi_group)

            # Boutons de contrôle
            controls_group = QGroupBox("Contrôles")
            controls_layout = QVBoxLayout(controls_group)

            self.start_btn = QPushButton("🚀 Démarrer")
            self.start_btn.clicked.connect(self.start_analysis)
            controls_layout.addWidget(self.start_btn)

            self.stop_btn = QPushButton("⏹️ Arrêter")
            self.stop_btn.clicked.connect(self.stop_analysis)
            self.stop_btn.setEnabled(False)
            controls_layout.addWidget(self.stop_btn)

            self.reset_btn = QPushButton("🔄 Reset")
            self.reset_btn.clicked.connect(self.reset_analysis)
            controls_layout.addWidget(self.reset_btn)

            layout.addWidget(controls_group)

            # Spacer
            layout.addStretch()

            return widget

        def create_chart_panel(self) -> QWidget:
            """Panel central avec graphiques"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Onglets pour différents graphiques
            self.chart_tabs = QTabWidget()

            # Onglet Prix
            price_tab = QWidget()
            price_layout = QVBoxLayout(price_tab)

            # Graphique des prix (placeholder)
            self.price_chart = QLabel("📊 Graphique des Prix\\n(Simulation temps réel)")
            self.price_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.price_chart.setStyleSheet(
                """
                QLabel {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-size: 14px;
                    padding: 20px;
                }
            """
            )
            self.price_chart.setMinimumHeight(300)
            price_layout.addWidget(self.price_chart)

            self.chart_tabs.addTab(price_tab, "Prix & MA")

            # Onglet RSI
            rsi_tab = QWidget()
            rsi_layout = QVBoxLayout(rsi_tab)

            self.rsi_chart = QLabel("📈 RSI Oscillateur\\n(0-100)")
            self.rsi_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rsi_chart.setStyleSheet(self.price_chart.styleSheet())
            self.rsi_chart.setMinimumHeight(200)
            rsi_layout.addWidget(self.rsi_chart)

            self.chart_tabs.addTab(rsi_tab, "RSI")

            # Onglet ATR
            atr_tab = QWidget()
            atr_layout = QVBoxLayout(atr_tab)

            self.atr_chart = QLabel("📊 ATR Volatilité")
            self.atr_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.atr_chart.setStyleSheet(self.price_chart.styleSheet())
            self.atr_chart.setMinimumHeight(200)
            atr_layout.addWidget(self.atr_chart)

            self.chart_tabs.addTab(atr_tab, "ATR")

            layout.addWidget(self.chart_tabs)

            return widget

        def create_indicators_panel(self) -> QWidget:
            """Panel des indicateurs et signaux"""
            widget = QWidget()
            widget.setMaximumWidth(400)
            layout = QVBoxLayout(widget)

            # Valeurs actuelles
            current_group = QGroupBox("Valeurs Actuelles")
            current_layout = QGridLayout(current_group)

            self.current_price_label = QLabel("Prix: --")
            self.current_sma_label = QLabel("SMA(20): --")
            self.current_ema_label = QLabel("EMA(12): --")
            self.current_atr_label = QLabel("ATR(14): --")
            self.current_rsi_label = QLabel("RSI(14): --")

            current_layout.addWidget(self.current_price_label, 0, 0)
            current_layout.addWidget(self.current_sma_label, 1, 0)
            current_layout.addWidget(self.current_ema_label, 2, 0)
            current_layout.addWidget(self.current_atr_label, 3, 0)
            current_layout.addWidget(self.current_rsi_label, 4, 0)

            layout.addWidget(current_group)

            # Signaux de trading
            signals_group = QGroupBox("Signaux de Trading")
            signals_layout = QVBoxLayout(signals_group)

            self.signals_text = QTextEdit()
            self.signals_text.setMaximumHeight(200)
            self.signals_text.setStyleSheet(
                """
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Courier New';
                    font-size: 11px;
                }
            """
            )
            signals_layout.addWidget(self.signals_text)

            layout.addWidget(signals_group)

            # Statistiques
            stats_group = QGroupBox("Statistiques")
            stats_layout = QVBoxLayout(stats_group)

            self.stats_text = QTextEdit()
            self.stats_text.setMaximumHeight(150)
            stats_layout.addWidget(self.stats_text)

            layout.addWidget(stats_group)

            return widget

        def create_menu_bar(self):
            """Création de la barre de menu"""
            menubar = self.menuBar()

            # Menu Fichier
            file_menu = menubar.addMenu("Fichier")

            export_action = QAction("Exporter Données", self)
            export_action.triggered.connect(self.export_data)
            file_menu.addAction(export_action)

            file_menu.addSeparator()

            quit_action = QAction("Quitter", self)
            quit_action.triggered.connect(self.close)
            file_menu.addAction(quit_action)

            # Menu Outils
            tools_menu = menubar.addMenu("Outils")

            test_indicators = QAction("Tester Indicateurs", self)
            test_indicators.triggered.connect(self.test_indicators)
            tools_menu.addAction(test_indicators)

            # Menu Aide
            help_menu = menubar.addMenu("Aide")

            about_action = QAction("À Propos", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

        def setup_timer(self):
            """Configuration du timer pour mise à jour temps réel"""
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_market_data)

        def setup_system_tray(self):
            """Configuration de l'icône dans la barre système"""
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon = QSystemTrayIcon(self)
                self.tray_icon.setIcon(
                    self.style().standardIcon(
                        self.style().StandardPixmap.SP_ComputerIcon
                    )
                )

                tray_menu = QMenu()
                show_action = tray_menu.addAction("Afficher")
                show_action.triggered.connect(self.show)
                tray_menu.addSeparator()
                quit_action = tray_menu.addAction("Quitter")
                quit_action.triggered.connect(self.close)

                self.tray_icon.setContextMenu(tray_menu)
                self.tray_icon.show()

        # Méthodes d'événements
        def start_analysis(self):
            """Démarrage de l'analyse temps réel"""
            self.update_timer.start(1000)  # 1 seconde
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_bar.showMessage("Analyse en cours...")
            self.add_signal("🚀 Analyse démarrée")

        def stop_analysis(self):
            """Arrêt de l'analyse"""
            self.update_timer.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_bar.showMessage("Analyse arrêtée")
            self.add_signal("⏹️ Analyse arrêtée")

        def reset_analysis(self):
            """Reset de l'analyse"""
            self.stop_analysis()

            # Reset des indicateurs
            for indicator in self.indicators.values():
                indicator.reset()

            # Reset des données
            for symbol in self.price_history:
                self.price_history[symbol].clear()

            self.signals_text.clear()
            self.stats_text.clear()
            self.add_signal("🔄 Données réinitialisées")

        def on_symbol_changed(self, symbol: str):
            """Changement de symbole"""
            self.add_signal(f"📊 Symbole changé: {symbol}")

        def update_market_data(self):
            """Mise à jour des données de marché"""
            current_symbol = self.symbol_combo.currentText()
            generator = self.market_generators[current_symbol]

            # Générer nouvelle donnée
            new_data = generator.generate_next_candle()
            self.price_history[current_symbol].append(new_data)

            # Limiter l'historique
            if len(self.price_history[current_symbol]) > 200:
                self.price_history[current_symbol] = self.price_history[current_symbol][
                    -200:
                ]

            # Mise à jour des indicateurs
            self.update_indicators(new_data)

            # Mise à jour de l'affichage
            self.update_display(new_data)

        def update_indicators(self, data: MarketData):
            """Mise à jour des indicateurs"""
            price = float(data.close)

            # SMA
            sma_config = self.indicators["SMA"].config
            sma_config.period = self.sma_period.value()
            sma_result = self.indicators["SMA"].add_price(data.close)

            # EMA
            ema_config = self.indicators["EMA"].config
            ema_config.period = self.ema_period.value()
            ema_result = self.indicators["EMA"].add_price(data.close)

            # ATR
            atr_config = self.indicators["ATR"].config
            atr_config.period = self.atr_period.value()
            atr_result = self.indicators["ATR"].add_ohlc(
                data.high, data.low, data.close
            )

            # RSI
            rsi_config = self.indicators["RSI"].config
            rsi_config.period = self.rsi_period.value()
            rsi_config.overbought_level = self.rsi_overbought.value()
            rsi_config.oversold_level = self.rsi_oversold.value()
            rsi_result = self.indicators["RSI"].add_price(data.close)

            # Vérification des signaux
            self.check_signals(data, sma_result, ema_result, atr_result, rsi_result)

        def update_display(self, data: MarketData):
            """Mise à jour de l'affichage"""
            # Labels des valeurs actuelles
            self.current_price_label.setText(f"Prix: {data.close:.2f}")

            # Récupération des dernières valeurs calculées
            sma_val = self.indicators["SMA"].get_current_value()
            ema_val = self.indicators["EMA"].get_current_value()
            atr_val = self.indicators["ATR"].get_current_value()
            rsi_val = self.indicators["RSI"].get_current_value()

            self.current_sma_label.setText(
                f"SMA({self.sma_period.value()}): {sma_val:.2f}"
                if sma_val
                else "SMA: --"
            )
            self.current_ema_label.setText(
                f"EMA({self.ema_period.value()}): {ema_val:.2f}"
                if ema_val
                else "EMA: --"
            )
            self.current_atr_label.setText(
                f"ATR({self.atr_period.value()}): {atr_val:.4f}"
                if atr_val
                else "ATR: --"
            )
            self.current_rsi_label.setText(
                f"RSI({self.rsi_period.value()}): {rsi_val:.1f}"
                if rsi_val
                else "RSI: --"
            )

        def check_signals(self, data, sma_result, ema_result, atr_result, rsi_result):
            """Vérification des signaux de trading"""
            signals = []

            # Signaux RSI
            if rsi_result and hasattr(rsi_result, "signal"):
                if rsi_result.signal == "OVERSOLD":
                    signals.append(
                        f"🟢 RSI Survente: {rsi_result.value:.1f} < {self.rsi_oversold.value()}"
                    )
                elif rsi_result.signal == "OVERBOUGHT":
                    signals.append(
                        f"🔴 RSI Surachat: {rsi_result.value:.1f} > {self.rsi_overbought.value()}"
                    )

            # Signaux croisement MA
            if sma_result and ema_result:
                sma_val = (
                    sma_result.value if hasattr(sma_result, "value") else sma_result
                )
                ema_val = (
                    ema_result.value if hasattr(ema_result, "value") else ema_result
                )

                if ema_val > sma_val * 1.001:  # EMA > SMA avec marge
                    signals.append(f"📈 EMA > SMA: Tendance haussière")
                elif ema_val < sma_val * 0.999:  # EMA < SMA avec marge
                    signals.append(f"📉 EMA < SMA: Tendance baissière")

            # ATR volatilité
            if atr_result and hasattr(atr_result, "volatility_percentile"):
                if atr_result.volatility_percentile > 80:
                    signals.append(
                        f"⚡ Forte volatilité: {atr_result.volatility_percentile:.0f}%"
                    )

            # Affichage des signaux
            for signal in signals:
                self.add_signal(signal)

        def add_signal(self, signal: str):
            """Ajout d'un signal au log"""
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_signal = f"[{timestamp}] {signal}"
            self.signals_text.append(full_signal)

            # Limiter le nombre de lignes
            document = self.signals_text.document()
            if document.blockCount() > 100:
                cursor = self.signals_text.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                cursor.select(cursor.SelectionType.BlockUnderCursor)
                cursor.deleteChar()

        def test_indicators(self):
            """Test des indicateurs"""
            try:
                # Test rapide de tous les indicateurs
                test_price = Decimal("50000.0")

                results = []
                for name, indicator in self.indicators.items():
                    try:
                        if name in ["SMA", "EMA", "RSI"]:
                            result = indicator.add_price(test_price)
                        else:  # ATR
                            result = indicator.add_ohlc(
                                test_price, test_price * Decimal("0.99"), test_price
                            )
                        results.append(f"✅ {name}: OK")
                    except Exception as e:
                        results.append(f"❌ {name}: {e}")

                self.add_signal(f"Tests: {', '.join(results)}")

            except Exception as e:
                self.add_signal(f"❌ Erreur tests: {e}")

        def export_data(self):
            """Export des données"""
            current_symbol = self.symbol_combo.currentText()
            data = self.price_history.get(current_symbol, [])

            if data:
                filename = f"thebot_export_{current_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                export_data = [
                    {
                        "timestamp": d.timestamp.isoformat(),
                        "open": float(d.open),
                        "high": float(d.high),
                        "low": float(d.low),
                        "close": float(d.close),
                        "volume": float(d.volume),
                    }
                    for d in data
                ]

                with open(filename, "w") as f:
                    json.dump(export_data, f, indent=2)

                self.add_signal(f"💾 Données exportées: {filename}")
            else:
                self.add_signal("⚠️ Aucune donnée à exporter")

        def show_about(self):
            """Affichage des informations"""
            from PyQt6.QtWidgets import QMessageBox

            msg = QMessageBox(self)
            msg.setWindowTitle("À Propos de THEBOT")
            msg.setText(
                """
<h3>THEBOT - Trading Analysis Platform</h3>
<p><b>Version:</b> 1.0.0</p>
<p><b>Architecture:</b> Ultra-Modulaire</p>
<p><b>Indicateurs:</b> SMA, EMA, ATR, RSI</p>
<p><b>Marchés:</b> Crypto & Forex</p>
<p><b>Interface:</b> Application Native PyQt6</p>
<br>
<p>🤖 Plateforme professionnelle d'analyse technique avec 61 tests validés</p>
            """
            )
            msg.exec()


def create_native_app():
    """Création de l'application native"""
    app = QApplication(sys.argv)
    app.setApplicationName("THEBOT")
    app.setApplicationVersion("1.0.0")

    # Style sombre optionnel
    app.setStyle("Fusion")

    # Palette sombre
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)

    window = THEBOTMainWindow()
    window.show()

    return app, window


# Version Tkinter fallback si PyQt6 non disponible
if not PYQT_AVAILABLE:
    # Version Tkinter fallback
    class THEBOTTkinterApp:
        """Version Tkinter si PyQt6 n'est pas disponible"""

        def __init__(self):
            self.root = tk.Tk()
            self.root.title("THEBOT - Trading Analysis Platform")
            self.root.geometry("1200x800")

            # Variables
            self.running = False
            self.setup_ui()

        def setup_ui(self):
            """Interface Tkinter simplifiée"""
            # Frame principal
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Titre
            title_label = ttk.Label(
                main_frame,
                text="THEBOT - Native Desktop App",
                font=("Arial", 16, "bold"),
            )
            title_label.pack(pady=10)

            # Message d'information
            info_text = ttk.Label(
                main_frame,
                text="""
🤖 Application Native THEBOT

Cette version utilise Tkinter (PyQt6 non disponible)
Pour une meilleure expérience, installez PyQt6:
pip install PyQt6

Indicateurs supportés: SMA, EMA, ATR, RSI
Architecture: Ultra-Modulaire validée
            """,
                justify="center",
            )
            info_text.pack(pady=20)

            # Boutons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=10)

            ttk.Button(
                button_frame, text="🚀 Version PyQt6", command=self.suggest_pyqt
            ).pack(side="left", padx=5)
            ttk.Button(
                button_frame, text="📊 Dashboard Jupyter", command=self.open_jupyter
            ).pack(side="left", padx=5)
            ttk.Button(button_frame, text="❌ Quitter", command=self.root.quit).pack(
                side="left", padx=5
            )

        def suggest_pyqt(self):
            messagebox.showinfo(
                "Installation PyQt6",
                "Pour installer PyQt6:\\n\\npip install PyQt6\\n\\nPuis relancez l'application.",
            )

        def open_jupyter(self):
            messagebox.showinfo(
                "Dashboard Jupyter",
                "Lancez le dashboard avec:\\n\\n./start.sh\\n\\nou\\n\\n./launch_fedora.sh",
            )

        def run(self):
            self.root.mainloop()


def create_tkinter_app():
    """Création de l'application Tkinter"""
    app = THEBOTTkinterApp()
    return app


if __name__ == "__main__":
    if PYQT_AVAILABLE:
        print("🚀 Lancement THEBOT avec PyQt6...")
        app, window = create_native_app()
        sys.exit(app.exec())
    else:
        print("⚠️  PyQt6 non disponible, utilisation de Tkinter...")
        print("Pour une meilleure expérience: pip install PyQt6")
        app = create_tkinter_app()
        app.run()
