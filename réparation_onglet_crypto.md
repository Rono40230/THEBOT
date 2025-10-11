📋 PLAN COMPLET - RÉPARATION ONGLET CRYPTO
OBJECTIF : Onglet crypto 100% fonctionnel, conforme aux .clinerules, zéro erreur F12

🚨 PHASE 0 : SAUVEGARDE ET DIAGNOSTIC (15 min)
0.1 Sauvegarde complète
Créer branche backup-crypto-before-refactor
Sauvegarder état actuel fonctionnel
Documenter erreurs F12 actuelles (screenshots)
0.2 Audit des fichiers crypto existants
Lister TOUS les fichiers concernant crypto
Identifier TOUS les callbacks crypto existants
Cartographier les dépendances croisées
🏗️ PHASE 1 : CRÉATION FICHIER CALLBACKS CENTRALISÉ (30 min)
1.1 Créer dash_modules/tabs/crypto_callbacks.py
Structure modulaire selon .clinerules
Fonctions séparées par responsabilité
Documentation complète
Gestion d'erreur robuste
1.2 Architecture du fichier

# Point d'entrée uniquedef register_all_crypto_callbacks(app)# Callbacks par catégoriedef register_dropdown_callbacks(app)     # Search + timeframedef register_chart_callbacks(app)        # Graphiques principauxdef register_data_callbacks(app)         # Prix + données marchédef register_display_callbacks(app)      # Affichage UI
1.3 Validation
Fichier créé sans erreur d'import
Structure respecte .clinerules
Prêt à recevoir les callbacks migrés
🧹 PHASE 2 : NETTOYAGE INTÉGRAL MODULES CRYPTO (45 min)
2.1 Audit et nettoyage crypto_module.py
Extraire tous les callbacks vers crypto_callbacks.py
Supprimer enregistrements de modals redondants
Simplifier register_callbacks() → délégation unique
Nettoyer code mort et imports inutiles
2.2 Suppression crypto_module_simple.py
Fusionner fonctionnalités utiles dans crypto_module.py
Supprimer le fichier complètement
Mettre à jour les imports dans autres fichiers
2.3 Nettoyage callbacks modals
Vérifier que modals s'enregistrent UNE SEULE FOIS
Supprimer enregistrements crypto spécifiques redondants
S'assurer que modals restent fonctionnels pour autres onglets
2.4 Validation phase 2
Aucun callback crypto en double
Module crypto simplifié et propre
Imports tous fonctionnels
🚀 PHASE 3 : NETTOYAGE LAUNCHER (30 min)
3.1 Extraction code crypto du launcher
Supprimer tous les callbacks crypto inline
Supprimer le CSS crypto embarqué
Supprimer la logique métier crypto
Supprimer les fonctions de génération de données
3.2 Simplification enregistrement callbacks

# AVANT (50+ lignes de callbacks crypto)# Code complexe d'enregistrement multiple# APRÈS (3 lignes max)if 'crypto' in self.modules:    self.modules['crypto'].setup_callbacks(self.app)
3.3 Déplacement assets
CSS crypto → assets/crypto_styles.css
JavaScript crypto → assets/crypto_scripts.js (si nécessaire)
Données simulées → data/mock/crypto_data.py
3.4 Validation phase 3
Launcher réduit de 200+ lignes
Plus de code crypto dans le launcher
Application démarre toujours
🔧 PHASE 4 : MIGRATION ET IMPLÉMENTATION CALLBACKS (60 min)
4.1 Migration callbacks dropdowns
crypto-symbol-search : Recherche dynamique symboles
crypto-timeframe-selector : Sélection timeframe
Tests unitaires : Validation recherche BTC, ETH, etc.
4.2 Migration callbacks graphiques
crypto-main-chart : Graphique principal OHLC
crypto-rsi-chart : Graphique RSI (si existant)
crypto-volume-chart : Graphique volume (si existant)
Gestion d'erreur : Fallback si données indisponibles
4.3 Migration callbacks données
crypto-price-display : Affichage prix temps réel
Synchronisation stores : main-symbol-selected, market-data-store
WebSocket integration : Données temps réel
Cache intelligent : Éviter appels API redondants
4.4 Migration callbacks affichage
Synchronisation UI : Dropdowns ↔ stores
Indicateurs visuels : Loading, erreurs, succès
Responsive design : Adaptation mobile/desktop
4.5 Validation phase 4
Chaque callback testé individuellement
Zéro erreur F12
Dropdowns fonctionnels
Graphiques s'affichent
📊 PHASE 5 : CORRECTION PROBLÈMES STRUCTURAUX (45 min)
5.1 Architecture conforme .clinerules

dash_modules/tabs/crypto/├── __init__.py              # API publique├── crypto_module.py         # Module principal├── crypto_callbacks.py      # Callbacks centralisés└── crypto_config.py         # Configuration (nouveau)
5.2 Séparation des responsabilités
crypto_module.py : Layout + initialisation seulement
crypto_callbacks.py : Logique callbacks uniquement
crypto_config.py : Configuration Pydantic
Data providers : API Binance isolée
5.3 Gestion d'erreur robuste
Try/catch dans tous les callbacks
Logging approprié (pas de print())
Fallback quand API échoue
Timeout sur appels externes
Validation des données reçues
5.4 Performance
Caching des données Binance
Debouncing de la recherche
Lazy loading des graphiques
Optimisation mémoire
5.5 Validation phase 5
Architecture modulaire respectée
Performance acceptable (< 2s chargement)
Gestion d'erreur robuste
Code maintenable
✅ PHASE 6 : TESTS ET VALIDATION FINALE (30 min)
6.1 Tests fonctionnels
Recherche symbole : Taper "BTC" → résultats corrects
Sélection symbole : Clic → graphique se met à jour
Changement timeframe : 1h → 4h → données correctes
Prix temps réel : Mise à jour automatique
Modals : IA, alertes, indicateurs fonctionnent
6.2 Tests techniques
F12 console : Zéro erreur JavaScript
Network tab : Appels API optimisés
Performance : Temps de chargement < 2s
Responsive : Fonctionne mobile + desktop
6.3 Tests de régression
Autres onglets : News, Calendrier toujours fonctionnels
Modals globaux : API config, etc. toujours OK
Navigation : Changement d'onglet sans erreur
6.4 Documentation
README : Mettre à jour avec nouvelle architecture
Commentaires : Code bien documenté
Changelog : Documenter les modifications
🎯 LIVRABLES FINAUX
Code
✅ crypto_callbacks.py : Callbacks centralisés (100-150 lignes)
✅ crypto_module.py : Module simplifié (< 200 lignes)
✅ launch_dash_professional.py : Réduit de 200+ lignes
✅ Architecture conforme .clinerules
Fonctionnalités
✅ Dropdown recherche crypto fonctionnel
✅ Sélecteur timeframe fonctionnel
✅ Graphique principal OHLC
✅ Prix temps réel via WebSocket
✅ Zéro erreur F12
Qualité
✅ Code maintenable et lisible
✅ Gestion d'erreur robuste
✅ Performance optimisée
✅ Tests de non-régression OK
⏱️ PLANNING DÉTAILLÉ
Phase	Durée	Tâches	Validation
0	15 min	Sauvegarde + Audit	Backup créé
1	30 min	Création callbacks centralisés	Fichier structure OK
2	45 min	Nettoyage modules crypto	Code simplifié
3	30 min	Nettoyage launcher	Launcher allégé
4	60 min	Migration callbacks	Dropdowns fonctionnels
5	45 min	Corrections structurales	Architecture conforme
6	30 min	Tests + validation	Zéro erreur F12
TOTAL : 4h15 de travail concentré

🚨 POINTS DE CONTRÔLE CRITIQUES
Après chaque phase
 Application démarre sans erreur Python
 Aucune régression sur autres onglets
 F12 console sans nouvelles erreurs
 Sauvegarde état si validation OK
Critères d'arrêt
❌ Erreur Python au démarrage → STOP, rollback
❌ Autres onglets cassés → STOP, corriger d'abord
❌ Nouvelles erreurs F12 → STOP, investiguer
🎊 RÉSULTAT ATTENDU
AVANT : Onglet crypto cassé, erreurs F12, code illisible APRÈS : Onglet crypto parfaitement fonctionnel, code propre, architecture conforme .clinerules