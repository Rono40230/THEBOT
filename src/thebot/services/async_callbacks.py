"""
Async Callback Wrappers - Adapter les callbacks Dash pour async/await
Responsable: Gérer les appels async dans l'environnement Dash
Architecture: Wrapper pattern
"""

import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine, List, Optional

from src.thebot.core.logger import logger


class AsyncCallbackWrapper:
    """
    Wrapper pour convertir des callbacks async en callbacks sync Dash
    Gère la boucle d'événements asyncio pour les callbacks
    """

    def __init__(self):
        """Initialiser le wrapper"""
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        logger.info("✅ AsyncCallbackWrapper initialized")

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        """
        Obtenir ou créer une boucle d'événements
        
        Returns:
            Event loop asyncio
        """
        try:
            loop = asyncio.get_running_loop()
            return loop
        except RuntimeError:
            # Pas de boucle active, en créer une
            try:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                return self._loop
            except Exception as e:
                logger.error(f"❌ Failed to create event loop: {e}")
                raise

    def run_async(self, coro: Coroutine) -> Any:
        """
        Exécuter une coroutine de manière synchrone
        
        Args:
            coro: Coroutine à exécuter
            
        Returns:
            Résultat de la coroutine
        """
        try:
            loop = self.get_event_loop()
            
            # Si on est déjà dans la boucle, ne pas utiliser run_until_complete
            if loop.is_running():
                # Créer une nouvelle boucle pour l'exécution
                new_loop = asyncio.new_event_loop()
                result = new_loop.run_until_complete(coro)
                new_loop.close()
                return result
            else:
                # Exécuter dans la boucle existante
                return loop.run_until_complete(coro)
                
        except Exception as e:
            logger.error(f"❌ Error running async callback: {e}")
            raise

    def async_callback(self, *args, **kwargs) -> Callable:
        """
        Décorateur pour convertir une fonction async en callback Dash
        
        Usage:
            @async_callback('output', 'input')
            async def my_callback(input_value):
                await asyncio.sleep(1)
                return result
        
        Args:
            *args: Arguments de callback Dash
            **kwargs: Keyword arguments de callback Dash
            
        Returns:
            Décorateur
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*callback_args, **callback_kwargs):
                try:
                    # Créer la coroutine
                    coro = func(*callback_args, **callback_kwargs)
                    
                    # Exécuter de manière synchrone
                    result = self.run_async(coro)
                    
                    logger.debug(f"✅ Async callback executed: {func.__name__}")
                    return result
                    
                except Exception as e:
                    logger.error(f"❌ Async callback error: {e}")
                    raise
            
            return wrapper
        
        return decorator

    def async_callback_context(
        self,
        output_spec: Any,
        input_specs: List[Any],
        prevent_initial_call: bool = False
    ) -> Callable:
        """
        Décorateur pour async callback avec contexte Dash complet
        
        Args:
            output_spec: Output specification
            input_specs: List of input specifications
            prevent_initial_call: Si True, ne pas appeler au démarrage
            
        Returns:
            Décorateur
        """
        def decorator(func: Callable) -> Callable:
            # Pour l'instant, c'est un wrapper simple
            # Dans une vraie implémentation, il faudrait intégrer avec @callback
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    coro = func(*args, **kwargs)
                    result = self.run_async(coro)
                    logger.debug(f"✅ Context async callback: {func.__name__}")
                    return result
                except Exception as e:
                    logger.error(f"❌ Context callback error: {e}")
                    raise
            
            return wrapper
        
        return decorator

    def close(self) -> None:
        """Fermer la boucle d'événements"""
        if self._loop and not self._loop.is_closed():
            self._loop.close()
            self._loop = None
            logger.info("✅ Event loop closed")


# Instance globale
async_callback_wrapper = AsyncCallbackWrapper()


def get_async_callback_wrapper() -> AsyncCallbackWrapper:
    """Obtenir l'instance du wrapper"""
    return async_callback_wrapper


def async_dash_callback(
    output_spec: Any,
    input_specs: List[Any],
    prevent_initial_call: bool = False
) -> Callable:
    """
    Décorateur helper pour async callbacks Dash
    
    Usage:
        @async_dash_callback(
            Output('output', 'children'),
            [Input('input', 'value')]
        )
        async def update_output(value):
            result = await expensive_async_operation(value)
            return result
    
    Args:
        output_spec: Output specification
        input_specs: Input specifications list
        prevent_initial_call: Skip initial call
        
    Returns:
        Décorateur
    """
    wrapper = get_async_callback_wrapper()
    return wrapper.async_callback_context(
        output_spec,
        input_specs,
        prevent_initial_call
    )
