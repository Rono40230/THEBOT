from src.thebot.core.logger import logger
"""
Callback Factory - Factory pour créer des callbacks standardisés
Facilite la création de callbacks avec patterns communs
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps

from dash import Input, Output, State

logger = logging.getLogger(__name__)


class CallbackFactory:
    """
    Factory pour créer des callbacks standardisés avec patterns communs.

    Fournit des méthodes pour créer rapidement des callbacks fréquemment utilisés :
    - Callbacks de mise à jour de données
    - Callbacks de visibilité d'éléments
    - Callbacks de validation de formulaires
    - Callbacks de chargement asynchrone
    """

    def __init__(self, app):
        self.app = app

    def create_data_update_callback(
        self,
        output_id: str,
        input_ids: List[str],
        update_function: Callable,
        store_id: Optional[str] = None,
        loading_id: Optional[str] = None
    ) -> Callable:
        """
        Crée un callback standard pour la mise à jour de données.

        Args:
            output_id: ID de l'élément de sortie
            input_ids: Liste des IDs d'entrée
            update_function: Fonction de mise à jour
            store_id: ID optionnel d'un store pour la persistance
            loading_id: ID optionnel d'un élément de chargement

        Returns:
            Fonction callback configurée
        """

        inputs = [Input(input_id, "value") for input_id in input_ids]
        outputs = [Output(output_id, "children")]

        if store_id:
            outputs.append(Output(store_id, "data"))
        if loading_id:
            outputs.append(Output(loading_id, "children"))

        def callback(*args):
            try:
                result = update_function(*args)

                if store_id and loading_id:
                    return result, args, None  # data, store, loading
                elif store_id:
                    return result, args  # data, store
                elif loading_id:
                    return result, None  # data, loading
                else:
                    return result  # data only

            except Exception as e:
                logger.error(f"Erreur dans callback data update: {e}")
                error_message = f"Erreur: {str(e)}"

                if store_id and loading_id:
                    return error_message, None, None
                elif store_id:
                    return error_message, None
                elif loading_id:
                    return error_message, None
                else:
                    return error_message

        # Enregistrer le callback
        self.app.callback(outputs, inputs)(callback)

        logger.debug(f"📝 Callback data update créé: {output_id}")
        return callback

    def create_visibility_toggle_callback(
        self,
        element_id: str,
        trigger_ids: List[str],
        visibility_function: Callable
    ) -> Callable:
        """
        Crée un callback pour basculer la visibilité d'un élément.

        Args:
            element_id: ID de l'élément à montrer/cacher
            trigger_ids: Liste des IDs qui déclenchent le changement
            visibility_function: Fonction qui retourne True/False pour la visibilité

        Returns:
            Fonction callback configurée
        """

        inputs = [Input(trigger_id, "n_clicks") for trigger_id in trigger_ids]
        output = Output(element_id, "style")

        def callback(*args):
            try:
                is_visible = visibility_function(*args)
                return {"display": "block"} if is_visible else {"display": "none"}
            except Exception as e:
                logger.error(f"Erreur dans callback visibility: {e}")
                return {"display": "none"}

        self.app.callback(output, inputs)(callback)

        logger.debug(f"📝 Callback visibility créé: {element_id}")
        return callback

    def create_form_validation_callback(
        self,
        form_id: str,
        input_ids: List[str],
        validation_function: Callable,
        submit_button_id: Optional[str] = None
    ) -> Callable:
        """
        Crée un callback de validation de formulaire.

        Args:
            form_id: ID du formulaire
            input_ids: Liste des IDs des champs à valider
            validation_function: Fonction de validation
            submit_button_id: ID optionnel du bouton de soumission

        Returns:
            Fonction callback configurée
        """

        inputs = [Input(input_id, "value") for input_id in input_ids]
        outputs = [Output(form_id, "children")]

        if submit_button_id:
            outputs.append(Output(submit_button_id, "disabled"))

        def callback(*args):
            try:
                is_valid, messages = validation_function(*args)

                # Créer affichage des messages de validation
                if messages:
                    validation_display = []
                    for msg in messages:
                        color = "success" if is_valid else "danger"
                        validation_display.append(
                            f"⚠️ {msg}"
                        )
                else:
                    validation_display = "✅ Formulaire valide" if is_valid else "❌ Erreurs de validation"

                if submit_button_id:
                    return validation_display, not is_valid
                else:
                    return validation_display

            except Exception as e:
                logger.error(f"Erreur dans callback validation: {e}")
                error_msg = f"Erreur de validation: {str(e)}"

                if submit_button_id:
                    return error_msg, True
                else:
                    return error_msg

        self.app.callback(outputs, inputs)(callback)

        logger.debug(f"📝 Callback validation créé: {form_id}")
        return callback

    def create_async_loading_callback(
        self,
        content_id: str,
        loading_id: str,
        trigger_ids: List[str],
        async_function: Callable,
        loading_message: str = "Chargement en cours..."
    ) -> Callable:
        """
        Crée un callback avec gestion du chargement asynchrone.

        Args:
            content_id: ID de l'élément de contenu
            loading_id: ID de l'élément de chargement
            trigger_ids: Liste des IDs qui déclenchent le chargement
            async_function: Fonction asynchrone à exécuter
            loading_message: Message affiché pendant le chargement

        Returns:
            Fonction callback configurée
        """

        inputs = [Input(trigger_id, "n_clicks") for trigger_id in trigger_ids]
        outputs = [
            Output(content_id, "children"),
            Output(loading_id, "children")
        ]

        def callback(*args):
            try:
                # Démarrer le chargement
                result = async_function(*args)
                return result, None  # content, hide loading

            except Exception as e:
                logger.error(f"Erreur dans callback async: {e}")
                error_msg = f"Erreur de chargement: {str(e)}"
                return error_msg, None

        self.app.callback(outputs, inputs)(callback)

        logger.debug(f"📝 Callback async créé: {content_id}")
