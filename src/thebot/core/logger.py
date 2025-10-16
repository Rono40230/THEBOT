"""
Logger centralisé THEBOT
Configuration de logging structuré pour toute l'application
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Configuration du logger principal
logger = logging.getLogger('thebot')
logger.setLevel(logging.INFO)

# Handler console avec format simple pour développement
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(levelname)s - %(message)s'
)
console_handler.setFormatter(console_formatter)

# Éviter les logs dupliqués
if not logger.handlers:
    logger.addHandler(console_handler)

# Logger pour les erreurs
error_logger = logging.getLogger('thebot.error')
error_logger.setLevel(logging.ERROR)

# Logger pour le debugging
debug_logger = logging.getLogger('thebot.debug')
debug_logger.setLevel(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger configuré pour un module spécifique

    Args:
        name: Nom du module (ex: 'indicators.sma')

    Returns:
        Logger configuré
    """
    return logging.getLogger(f'thebot.{name}')


def setup_file_logging(log_file: Optional[str] = None) -> None:
    """
    Configure le logging vers un fichier pour la production

    Args:
        log_file: Chemin du fichier de log (optionnel)
    """
    if log_file is None:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        log_file_path: str = str(log_dir / 'thebot.log')
    else:
        log_file_path = str(log_file)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)


# Configuration par défaut pour les scripts
if __name__ == '__main__':
    logger.info("Logger THEBOT initialisé")