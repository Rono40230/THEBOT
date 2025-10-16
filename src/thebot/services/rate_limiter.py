"""
Système de limitation de taux pour THEBOT
Implémentation de sliding window counter pour la protection contre les abus
"""

import time
import threading
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta

from .error_handler import RateLimitError, ErrorSeverity


@dataclass
class RateLimitRule:
    """Règle de limitation de taux"""
    requests_per_window: int
    window_seconds: int
    burst_limit: Optional[int] = None
    cooldown_seconds: int = 0

    def __post_init__(self):
        if self.burst_limit is None:
            self.burst_limit = self.requests_per_window


@dataclass
class RequestRecord:
    """Enregistrement d'une requête"""
    timestamp: float
    client_id: str


class SlidingWindowCounter:
    """
    Compteur de fenêtre glissante
    Implémente un algorithme de sliding window pour le rate limiting
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
        self.lock = threading.RLock()

    def add_request(self, client_id: str) -> bool:
        """
        Ajoute une requête et vérifie si elle est autorisée

        Args:
            client_id: Identifiant du client

        Returns:
            True si la requête est autorisée, False sinon
        """
        with self.lock:
            current_time = time.time()

            # Nettoyer les anciennes requêtes
            self._cleanup_old_requests(current_time)

            # Compter les requêtes dans la fenêtre
            if len(self.requests) >= self.max_requests:
                return False

            # Ajouter la nouvelle requête
            self.requests.append(RequestRecord(current_time, client_id))
            return True

    def get_request_count(self, client_id: Optional[str] = None) -> int:
        """
        Retourne le nombre de requêtes dans la fenêtre actuelle

        Args:
            client_id: Filtrer par client (optionnel)

        Returns:
            Nombre de requêtes
        """
        with self.lock:
            current_time = time.time()
            self._cleanup_old_requests(current_time)

            if client_id:
                return sum(1 for req in self.requests if req.client_id == client_id)
            else:
                return len(self.requests)

    def _cleanup_old_requests(self, current_time: float):
        """Nettoie les requêtes expirées"""
        cutoff_time = current_time - self.window_seconds

        while self.requests and self.requests[0].timestamp < cutoff_time:
            self.requests.popleft()

    def get_remaining_time(self) -> float:
        """
        Retourne le temps restant avant la prochaine fenêtre

        Returns:
            Temps en secondes
        """
        with self.lock:
            if not self.requests:
                return 0.0

            current_time = time.time()
            oldest_request = self.requests[0].timestamp
            elapsed = current_time - oldest_request

            return max(0.0, self.window_seconds - elapsed)


class RateLimiter:
    """
    Limiteur de taux principal
    Gère plusieurs règles de limitation pour différents endpoints
    """

    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.counters: Dict[str, SlidingWindowCounter] = {}
        self.client_violations: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()

        # Règles par défaut
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Configure les règles par défaut"""
        default_rules = {
            'api_general': RateLimitRule(
                requests_per_window=100,
                window_seconds=60,  # 100 req/min
                burst_limit=120
            ),
            'api_data': RateLimitRule(
                requests_per_window=50,
                window_seconds=60,  # 50 req/min
                burst_limit=60
            ),
            'api_trading': RateLimitRule(
                requests_per_window=10,
                window_seconds=60,  # 10 req/min
                burst_limit=12
            ),
            'auth_login': RateLimitRule(
                requests_per_window=5,
                window_seconds=300,  # 5 req/5min
                burst_limit=3,
                cooldown_seconds=300
            ),
            'web_general': RateLimitRule(
                requests_per_window=1000,
                window_seconds=60,  # 1000 req/min
                burst_limit=1200
            ),
        }

        for rule_name, rule in default_rules.items():
            self.add_rule(rule_name, rule)

    def add_rule(self, rule_name: str, rule: RateLimitRule):
        """
        Ajoute une règle de limitation

        Args:
            rule_name: Nom de la règle
            rule: Configuration de la règle
        """
        with self.lock:
            self.rules[rule_name] = rule
            self.counters[rule_name] = SlidingWindowCounter(
                rule.requests_per_window,
                rule.window_seconds
            )

    def check_limit(self, rule_name: str, client_id: str,
                   endpoint: Optional[str] = None) -> Tuple[bool, Dict[str, Union[str, int, float]]]:
        """
        Vérifie si une requête est autorisée

        Args:
            rule_name: Nom de la règle à appliquer
            client_id: Identifiant du client
            endpoint: Endpoint demandé (pour le contexte)

        Returns:
            Tuple (autorisé, informations de limite)
        """
        with self.lock:
            if rule_name not in self.rules:
                # Utiliser la règle par défaut
                rule_name = 'api_general'

            rule = self.rules[rule_name]
            counter = self.counters[rule_name]

            # Vérifier les violations récentes
            if self._is_in_cooldown(client_id, rule):
                return False, self._get_limit_info(rule_name, client_id, False, rule.cooldown_seconds)

            # Vérifier la limite
            allowed = counter.add_request(client_id)

            if not allowed:
                # Enregistrer la violation
                self.client_violations[client_id].append(time.time())
                # Garder seulement les 10 dernières violations
                self.client_violations[client_id] = self.client_violations[client_id][-10:]

            return allowed, self._get_limit_info(rule_name, client_id, allowed)

    def _is_in_cooldown(self, client_id: str, rule: RateLimitRule) -> bool:
        """Vérifie si un client est en cooldown"""
        if rule.cooldown_seconds == 0:
            return False

        violations = self.client_violations[client_id]
        if not violations:
            return False

        # Vérifier si la dernière violation est récente
        last_violation = max(violations)
        time_since_violation = time.time() - last_violation

        return time_since_violation < rule.cooldown_seconds

    def _get_limit_info(self, rule_name: str, client_id: str,
                       allowed: bool, cooldown_remaining: int = 0) -> Dict[str, Union[str, int, float]]:
        """Génère les informations de limite pour la réponse"""
        rule = self.rules[rule_name]
        counter = self.counters[rule_name]

        info = {
            'rule': rule_name,
            'allowed': allowed,
            'current_requests': counter.get_request_count(client_id),
            'max_requests': rule.requests_per_window,
            'window_seconds': rule.window_seconds,
            'remaining_time': counter.get_remaining_time(),
            'burst_limit': rule.burst_limit,
        }

        if cooldown_remaining > 0:
            info['cooldown_remaining'] = cooldown_remaining

        if not allowed:
            info['retry_after'] = counter.get_remaining_time()

        return info

    def get_client_stats(self, client_id: str) -> Dict[str, Union[str, int, float]]:
        """
        Retourne les statistiques d'un client

        Args:
            client_id: Identifiant du client

        Returns:
            Statistiques du client
        """
        with self.lock:
            stats = {
                'client_id': client_id,
                'total_violations': len(self.client_violations[client_id]),
                'rules': {}
            }

            for rule_name, counter in self.counters.items():
                stats['rules'][rule_name] = {
                    'current_requests': counter.get_request_count(client_id),
                    'remaining_time': counter.get_remaining_time()
                }

            return stats

    def reset_client(self, client_id: str):
        """
        Remet à zéro les compteurs d'un client

        Args:
            client_id: Identifiant du client
        """
        with self.lock:
            # Supprimer les violations
            self.client_violations.pop(client_id, None)

            # Remettre à zéro les compteurs (difficile avec sliding window,
            # on laisse expirer naturellement)

    def get_global_stats(self) -> Dict[str, Union[str, int, float]]:
        """
        Retourne les statistiques globales

        Returns:
            Statistiques globales
        """
        with self.lock:
            stats = {
                'rules': {},
                'total_clients_with_violations': len(self.client_violations),
                'timestamp': datetime.now().isoformat()
            }

            for rule_name, counter in self.counters.items():
                stats['rules'][rule_name] = {
                    'total_requests': counter.get_request_count(),
                    'remaining_time': counter.get_remaining_time()
                }

            return stats


# Instance globale du limiteur de taux
rate_limiter = RateLimiter()


def rate_limit(rule_name: str = 'api_general', client_id_param: str = 'client_id'):
    """
    Décorateur pour appliquer la limitation de taux

    Args:
        rule_name: Nom de la règle à appliquer
        client_id_param: Nom du paramètre contenant l'ID client

    Returns:
        Fonction décorée
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extraire l'ID client des paramètres
            client_id = kwargs.get(client_id_param)
            if client_id is None:
                # Chercher dans les arguments positionnels (endpoint)
                if args and len(args) > 0:
                    client_id = str(args[0])
                else:
                    client_id = 'anonymous'

            # Vérifier la limite
            allowed, limit_info = rate_limiter.check_limit(rule_name, client_id, func.__name__)

            if not allowed:
                raise RateLimitError(
                    f"Limite de taux dépassée pour {rule_name}",
                    severity=ErrorSeverity.WARNING,
                    context={
                        'rule_name': rule_name,
                        'client_id': client_id,
                        'limit_info': limit_info
                    }
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator
