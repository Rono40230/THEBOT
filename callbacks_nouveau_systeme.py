"""
🔧 CALLBACKS NOUVEAU SYSTÈME MODULAIRE - IDs Officiels
=====================================================

Callbacks utilisant les vrais IDs du nouveau système : basic-* et advanced-*
"""

# Ajouter ces callbacks après la ligne "# FIN DU CALLBACK PRINCIPAL DÉSACTIVÉ" dans crypto_module.py

@app.callback(
    Output('crypto-main-chart', 'figure'),
    [Input('crypto-symbol-search', 'value'),
     Input('crypto-timeframe-selector', 'value'),
     # Nouveaux IDs du système modulaire - Indicateurs de base
     Input('basic-sma-enabled', 'value'),
     Input('basic-sma-period', 'value'),
     Input('basic-ema-enabled', 'value'),
     Input('basic-ema-period', 'value')]
)
def update_main_chart_new_system(symbol, timeframe, 
                               sma_enabled, sma_period,
                               ema_enabled, ema_period):
    """Met à jour le graphique principal avec le nouveau système modulaire"""
    try:
        if not symbol:
            return go.Figure().add_annotation(
                text="Aucun symbole sélectionné",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Charger les données
        data = self.load_market_data(symbol, timeframe)
        if data.empty:
            return go.Figure().add_annotation(
                text=f"Pas de données pour {symbol}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Créer un graphique de base avec chandelier
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name=symbol,
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ))
        
        # === INDICATEURS SELON CONFIGURATION NOUVEAU SYSTÈME ===
        
        # SMA si activé (utilise la configuration par défaut si les valeurs sont None)
        if sma_enabled or sma_enabled is None:  # Par défaut activé
            period = sma_period if sma_period else 20
            sma_values = data['close'].rolling(window=period).mean()
            fig.add_trace(go.Scatter(
                x=data.index, y=sma_values, mode='lines',
                name=f'SMA {period}', line=dict(color='#2196F3', width=2)
            ))
        
        # EMA si activé (utilise la configuration par défaut si les valeurs sont None)
        if ema_enabled or ema_enabled is None:  # Par défaut activé
            period = ema_period if ema_period else 12
            ema_values = data['close'].ewm(span=period).mean()
            fig.add_trace(go.Scatter(
                x=data.index, y=ema_values, mode='lines',
                name=f'EMA {period}', line=dict(color='#FF9800', width=2)
            ))
        
        # Configuration du layout
        fig.update_layout(
            title=f"{symbol} - {timeframe} (Nouveau Système Modulaire)",
            yaxis_title="Prix",
            template="plotly_dark",
            showlegend=True,
            height=500
        )
        
        fig.update_xaxes(rangeslider_visible=False)
        
        print(f"✅ Graphique principal mis à jour: {symbol} (nouveau système)")
        return fig
        
    except Exception as e:
        print(f"❌ Erreur graphique principal nouveau système: {e}")
        return go.Figure().add_annotation(
            text=f"Erreur: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )

@app.callback(
    [Output('crypto-rsi-chart', 'figure'),
     Output('crypto-atr-chart', 'figure'), 
     Output('crypto-macd-chart', 'figure')],
    [Input('crypto-symbol-search', 'value'),
     Input('crypto-timeframe-selector', 'value'),
     # Nouveaux IDs du système modulaire - Indicateurs de base
     Input('basic-rsi-enabled', 'value'),
     Input('basic-rsi-period', 'value'),
     Input('basic-atr-enabled', 'value'),
     Input('basic-atr-period', 'value'),
     Input('basic-macd-enabled', 'value')]
)
def update_secondary_charts_new_system(symbol, timeframe,
                                     rsi_enabled, rsi_period,
                                     atr_enabled, atr_period,
                                     macd_enabled):
    """Met à jour les graphiques secondaires avec le nouveau système modulaire"""
    try:
        if not symbol:
            empty_fig = go.Figure().add_annotation(
                text="Aucun symbole",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
            return empty_fig, empty_fig, empty_fig
        
        # Charger les données
        data = self.load_market_data(symbol, timeframe)
        if data.empty:
            empty_fig = go.Figure().add_annotation(
                text="Pas de données",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
            return empty_fig, empty_fig, empty_fig
        
        # === RSI avec logique complète ===
        if rsi_enabled or rsi_enabled is None:  # Par défaut activé
            period = rsi_period if rsi_period else 14
            # Calcul RSI direct
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi_values = 100 - (100 / (1 + rs))
            
            rsi_fig = go.Figure()
            rsi_fig.add_trace(go.Scatter(
                x=data.index, y=rsi_values, mode='lines',
                name=f'RSI {period}', line=dict(color='#9C27B0', width=2)
            ))
            
            # Zones de surachat/survente avec remplissage
            rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
            rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
            rsi_fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255, 0, 0, 0.1)", line_width=0)
            rsi_fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0, 255, 0, 0.1)", line_width=0)
            
            # Signaux de trading basiques
            oversold_signals = rsi_values < 30
            overbought_signals = rsi_values > 70
            
            # Marqueurs pour signaux
            if oversold_signals.any():
                rsi_fig.add_trace(go.Scatter(
                    x=data.index[oversold_signals],
                    y=rsi_values[oversold_signals],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='lime'),
                    name='Signal Achat',
                    showlegend=False
                ))
            
            if overbought_signals.any():
                rsi_fig.add_trace(go.Scatter(
                    x=data.index[overbought_signals],
                    y=rsi_values[overbought_signals],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='red'),
                    name='Signal Vente',
                    showlegend=False
                ))
            
            rsi_fig.update_layout(
                title=f"RSI {period} (Nouveau Système)", yaxis_title="RSI", 
                template="plotly_dark", height=200, showlegend=False,
                yaxis=dict(range=[0, 100])
            )
        else:
            rsi_fig = go.Figure().add_annotation(
                text="RSI désactivé", xref="paper", yref="paper", 
                x=0.5, y=0.5, showarrow=False
            )
            rsi_fig.update_layout(template="plotly_dark", height=200)
        
        # === ATR avec logique complète ===
        if atr_enabled or atr_enabled is None:  # Par défaut activé
            period = atr_period if atr_period else 14
            # Calcul ATR direct avec pandas
            import pandas as pd
            high_low = data['high'] - data['low']
            high_close = abs(data['high'] - data['close'].shift())
            low_close = abs(data['low'] - data['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr_values = true_range.rolling(window=period).mean()
            
            atr_fig = go.Figure()
            atr_fig.add_trace(go.Scatter(
                x=data.index, y=atr_values, mode='lines',
                name=f'ATR {period}', line=dict(color='#4CAF50', width=2)
            ))
            
            # Ligne de moyenne pour contexte
            atr_mean = atr_values.mean()
            atr_fig.add_hline(y=atr_mean, line_dash="dot", line_color="yellow", 
                            annotation_text=f"Moyenne: {atr_mean:.2f}")
            
            atr_fig.update_layout(
                title=f"ATR {period} (Nouveau Système)", yaxis_title="ATR",
                template="plotly_dark", height=200, showlegend=False
            )
        else:
            atr_fig = go.Figure().add_annotation(
                text="ATR désactivé", xref="paper", yref="paper", 
                x=0.5, y=0.5, showarrow=False
            )
            atr_fig.update_layout(template="plotly_dark", height=200)
        
        # === MACD avec logique complète ===
        if macd_enabled or macd_enabled is None:  # Par défaut activé
            # Calcul MACD direct
            ema_12 = data['close'].ewm(span=12).mean()
            ema_26 = data['close'].ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            macd_fig = go.Figure()
            
            # Ligne MACD
            macd_fig.add_trace(go.Scatter(
                x=data.index, y=macd_line, mode='lines',
                name='MACD', line=dict(color='#2196F3', width=2)
            ))
            
            # Ligne de signal
            macd_fig.add_trace(go.Scatter(
                x=data.index, y=signal_line, mode='lines',
                name='Signal', line=dict(color='#FF5722', width=1)
            ))
            
            # Histogramme avec couleurs conditionnelles
            colors = ['#00ff88' if val >= 0 else '#ff4444' for val in histogram]
            macd_fig.add_trace(go.Bar(
                x=data.index, y=histogram,
                name='Histogramme', marker_color=colors, opacity=0.7
            ))
            
            # Ligne zéro
            macd_fig.add_hline(y=0, line_dash="dash", line_color="white", line_width=1)
            
            # Signaux de croisement
            crossovers = []
            for i in range(1, len(macd_line)):
                if (macd_line.iloc[i] > signal_line.iloc[i] and 
                    macd_line.iloc[i-1] <= signal_line.iloc[i-1]):
                    crossovers.append((data.index[i], macd_line.iloc[i], 'bullish'))
                elif (macd_line.iloc[i] < signal_line.iloc[i] and 
                      macd_line.iloc[i-1] >= signal_line.iloc[i-1]):
                    crossovers.append((data.index[i], macd_line.iloc[i], 'bearish'))
            
            # Ajouter marqueurs pour croisements
            if crossovers:
                bullish_x = [x for x, y, t in crossovers if t == 'bullish']
                bullish_y = [y for x, y, t in crossovers if t == 'bullish']
                bearish_x = [x for x, y, t in crossovers if t == 'bearish']
                bearish_y = [y for x, y, t in crossovers if t == 'bearish']
                
                if bullish_x:
                    macd_fig.add_trace(go.Scatter(
                        x=bullish_x, y=bullish_y, mode='markers',
                        marker=dict(symbol='triangle-up', size=12, color='lime'),
                        name='Achat', showlegend=False
                    ))
                
                if bearish_x:
                    macd_fig.add_trace(go.Scatter(
                        x=bearish_x, y=bearish_y, mode='markers',
                        marker=dict(symbol='triangle-down', size=12, color='red'),
                        name='Vente', showlegend=False
                    ))
            
            macd_fig.update_layout(
                title="MACD (Nouveau Système)", yaxis_title="MACD",
                template="plotly_dark", height=200, showlegend=False
            )
        else:
            macd_fig = go.Figure().add_annotation(
                text="MACD désactivé", xref="paper", yref="paper", 
                x=0.5, y=0.5, showarrow=False
            )
            macd_fig.update_layout(template="plotly_dark", height=200)
        
        print(f"✅ Graphiques secondaires mis à jour: {symbol} (nouveau système)")
        return rsi_fig, atr_fig, macd_fig
        
    except Exception as e:
        print(f"❌ Erreur graphiques secondaires nouveau système: {e}")
        import traceback
        traceback.print_exc()
        empty_fig = go.Figure().add_annotation(
            text=f"Erreur: {str(e)}",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        empty_fig.update_layout(template="plotly_dark", height=200)
        return empty_fig, empty_fig, empty_fig