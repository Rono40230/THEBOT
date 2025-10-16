from src.thebot.core.logger import logger
#!/usr/bin/env python3
"""
Script de validation de la configuration THEBOT
Vérifie que tous les secrets et paramètres requis sont configurés
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent))

from dash_modules.core.secrets_manager import secrets_manager
from dash_modules.core.error_handler import ErrorSeverity


def validate_configuration():
    """Valide la configuration complète"""
    logger.info("🔍 Validation de la configuration THEBOT...")
    logger.info("=" * 50)
    
    # Utiliser le gestionnaire de secrets pour valider
    report = secrets_manager.validate_configuration()
    
    # Afficher les résultats
    if report['valid']:
        logger.info("✅ Configuration valide")
    else:
        logger.info("❌ Configuration invalide")
        logger.info("\nSecrets requis manquants:")
        for secret in report['missing_required']:
            logger.info(f"  - {secret}")
    
    if report['warnings']:
        logger.info("\n⚠️  Avertissements:")
        for warning in report['warnings']:
            logger.info(f"  - {warning}")
    
    if report['recommendations']:
        logger.info("\n💡 Recommandations:")
        for rec in report['recommendations']:
            logger.info(f"  - {rec}")
    
    # Afficher les secrets configurés (masqués)
    logger.info("\n🔐 Secrets configurés:")
    secrets_info = secrets_manager.get_all_secrets_info()
    if secrets_info:
        for key, masked_value in secrets_info.items():
            logger.info(f"  - {key}: {masked_value}")
    else:
        logger.info("  Aucun secret configuré")
    
    logger.info("\n" + "=" * 50)
    
    # Vérifier la présence du fichier .env
    env_file = Path('.env')
    if env_file.exists():
        logger.info("✅ Fichier .env trouvé")
    else:
        logger.info("⚠️  Fichier .env non trouvé (utilise les variables d'environnement système)")
    
    return report['valid']


def check_database_connection():
    """Vérifie la connexion à la base de données"""
    logger.info("\n🔌 Test de connexion à la base de données...")
    
    try:
        db_config = secrets_manager.get_database_config()
        logger.info(f"URL: {secrets_manager.mask_secret(db_config['url'])}")
        
        # Ici on pourrait ajouter un vrai test de connexion
        # Pour l'instant, on vérifie juste que l'URL est définie
        if db_config['url']:
            logger.info("✅ Configuration base de données OK")
            return True
        else:
            logger.info("❌ URL de base de données manquante")
            return False
            
    except Exception as e:
        logger.info(f"❌ Erreur base de données: {e}")
        return False


def check_api_keys():
    """Vérifie les clés API disponibles"""
    logger.info("\n🔑 Vérification des clés API...")
    
    providers = ['binance', 'coingecko', 'twelve_data', 'alpha_vantage', 'finnhub', 'fmp']
    available_providers = []
    
    for provider in providers:
        keys = secrets_manager.get_api_keys(provider)
        if keys:
            available_providers.append(provider)
            logger.info(f"✅ {provider}: {len(keys)} clé(s) configurée(s)")
        else:
            logger.info(f"❌ {provider}: aucune clé configurée")
    
    if available_providers:
        logger.info(f"\n📊 {len(available_providers)}/{len(providers)} providers API disponibles")
    else:
        logger.info("\n⚠️  Aucune clé API configurée - fonctionnalités limitées")
    
    return len(available_providers) > 0


def main():
    """Fonction principale"""
    logger.info("🚀 Validation de configuration THEBOT Phase 3")
    logger.info("Phase 3: Qualité et Sécurité")
    logger.info()
    
    # Validation générale
    config_valid = validate_configuration()
    
    # Tests spécifiques
    db_ok = check_database_connection()
    api_ok = check_api_keys()
    
    logger.info("\n" + "=" * 50)
    logger.info("📋 RAPPORT FINAL")
    logger.info("=" * 50)
    
    all_checks = [
        ("Configuration générale", config_valid),
        ("Base de données", db_ok),
        ("Clés API", api_ok),
    ]
    
    for check_name, status in all_checks:
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {check_name}: {'OK' if status else 'ÉCHEC'}")
    
    overall_success = all(check[1] for check in all_checks)
    
    if overall_success:
        logger.info("\n🎉 Toutes les vérifications passées ! Phase 3 prête.")
        return 0
    else:
        logger.info("\n⚠️  Certaines vérifications ont échoué. Vérifiez la configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
