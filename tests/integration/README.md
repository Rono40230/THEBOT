# Tests d'Intégration THEBOT

Ce répertoire contient les tests d'intégration pour THEBOT, vérifiant le fonctionnement intégré des composants et APIs externes.

## Structure des Tests

```
tests/integration/
├── conftest.py              # Configuration et fixtures communes
├── test_api_integration.py          # Tests APIs de données (Binance, CoinGecko, RSS)
├── test_economic_api_integration.py # Tests APIs économiques et calendrier
└── test_dashboard_ai_integration.py # Tests composants dashboard et IA
```

## Exécution des Tests

### Tous les tests d'intégration
```bash
pytest tests/integration/ -v
```

### Tests spécifiques
```bash
# Tests APIs de données
pytest tests/integration/test_api_integration.py -v

# Tests APIs économiques
pytest tests/integration/test_economic_api_integration.py -v

# Tests composants dashboard/IA
pytest tests/integration/test_dashboard_ai_integration.py -v
```

### Tests avec marqueurs
```bash
# Tests nécessitant le réseau (marqués automatiquement)
pytest tests/integration/ -m "network" -v

# Tests d'intégration seulement
pytest tests/integration/ -m "integration" -v

# Tests lents (si marqués)
pytest tests/integration/ -m "slow" -v
```

### Tests en parallèle
```bash
pytest tests/integration/ -n auto -v
```

## Types de Tests

### 1. Tests de Connectivité API
- Vérification que les APIs externes sont accessibles
- Gestion des erreurs réseau et timeouts
- Validation des réponses API

### 2. Tests de Gestion d'Erreurs
- Erreurs réseau (RequestException)
- Limites de taux API (429)
- Erreurs serveur (5xx)
- Données malformées

### 3. Tests de Fonctionnalités
- Récupération de données de marché
- Calculs d'indicateurs techniques
- Gestion des alertes de prix
- Analyse IA du marché

### 4. Tests de Performance
- Temps de réponse des APIs
- Gestion du cache
- Utilisation mémoire

## Fixtures Disponibles

### Données de Test
- `sample_market_data`: DataFrame pandas avec données OHLCV fictives
- `sample_crypto_symbols`: Liste de symboles crypto populaires
- `sample_price_alerts`: Alertes de prix fictives
- `sample_news_items`: Éléments de news fictifs
- `sample_economic_events`: Événements économiques fictifs

### Mocks API
- `mock_api_response`: Réponse API générique réussie
- `mock_binance_response`: Réponse spécifique Binance
- `mock_coingecko_response`: Réponse spécifique CoinGecko
- `mock_network_error`: Simule erreur réseau
- `mock_api_rate_limit`: Simule limite de taux
- `mock_api_server_error`: Simule erreur serveur

### Instances de Composants
- `real_data_manager`: Instance RealDataManager
- `alerts_manager`: Instance AlertsManager
- `intelligent_cache`: Instance du cache global

## Gestion des APIs Externes

### Clés API
Certaines APIs nécessitent des clés valides pour fonctionner. Les tests sont conçus pour :
- Passer si l'API est accessible et répond correctement
- Sauter (skip) si l'API nécessite une clé non configurée
- Gérer les erreurs API gracieusement

### Rate Limiting
Les tests respectent les limites de taux des APIs :
- Utilisation de mocks pour éviter les appels réels en développement
- Tests de gestion des erreurs 429 (rate limit)
- Délais entre les appels si nécessaire

## Debugging

### Logs Détaillés
```bash
pytest tests/integration/ -v -s --log-cli-level=INFO
```

### Tests Échoués Seulement
```bash
pytest tests/integration/ --lf -v
```

### Coverage
```bash
pytest tests/integration/ --cov=dash_modules --cov-report=html
```

## Maintenance

### Ajout de Nouveaux Tests
1. Créer un nouveau fichier `test_*.py` dans `tests/integration/`
2. Utiliser les fixtures existantes dans `conftest.py`
3. Ajouter des mocks si nécessaire pour les nouvelles APIs
4. Documenter les nouveaux tests dans ce README

### Mise à Jour des Fixtures
- Modifier `conftest.py` pour ajouter de nouvelles fixtures
- Tester que les fixtures fonctionnent avec tous les tests existants

### Gestion des Dépendances
- Les tests utilisent les vraies dépendances du projet
- Pas de dépendances supplémentaires pour les tests d'intégration
- Mocks intégrés pour éviter les appels réseau en développement

## Résultats Attendus

### Succès
- APIs accessibles répondent correctement
- Gestion d'erreurs fonctionne
- Composants s'intègrent correctement
- Cache et alertes fonctionnent

### Échecs Acceptables
- APIs indisponibles (réseau, maintenance) → tests skippés
- Clés API manquantes → tests skippés
- Rate limits → tests gèrent l'erreur

### Échecs à Corriger
- Erreurs de code dans les composants
- Problèmes de logique métier
- Exceptions non gérées
- Données incorrectes retournées

## Métriques de Qualité

- **Coverage minimum**: 80% des APIs et composants critiques
- **Temps d'exécution**: < 5 minutes pour tous les tests
- **Taux de succès**: > 90% (hors APIs externes)
- **Fiabilité**: Tests passent de manière déterministe