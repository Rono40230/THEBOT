"""
🎛️ BASE CONTROLS - Factory de Contrôles Unifiés
===============================================

Factory pour créer tous les types de contrôles (Input/Slider) avec
format unifié et callbacks standardisés.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Dict, Any, Union, List, Optional


class ControlsFactory:
    """Factory pour créer tous les types de contrôles standardisés"""
    
    @staticmethod
    def create_numeric_input(
        control_id: str,
        label: str,
        value: Union[int, float],
        min_value: Union[int, float],
        max_value: Union[int, float],
        step: Union[int, float] = 1,
        input_group_text: str = "",
        help_text: str = "",
        size: str = "sm"
    ) -> dbc.Row:
        """
        Créer un Input numérique standardisé
        
        Args:
            control_id: ID unique du contrôle
            label: Libellé du contrôle
            value: Valeur par défaut
            min_value: Valeur minimum
            max_value: Valeur maximum
            step: Pas d'incrémentation
            input_group_text: Texte à afficher dans l'InputGroup
            help_text: Texte d'aide (tooltip)
            size: Taille du contrôle (sm, md, lg)
        """
        input_component = dbc.Input(
            id=control_id,
            type="number",
            value=value,
            min=min_value,
            max=max_value,
            step=step,
            size=size,
            className="text-center",
            style={
                "backgroundColor": "#2d3748",
                "borderColor": "#4a5568",
                "color": "#e2e8f0"
            }
        )
        
        # Ajouter InputGroup si texte spécifié
        if input_group_text:
            input_with_text = dbc.InputGroup([
                input_component,
                dbc.InputGroupText(
                    input_group_text,
                    style={
                        "backgroundColor": "#4a5568",
                        "borderColor": "#4a5568",
                        "color": "#e2e8f0",
                        "fontSize": "0.8rem"
                    }
                )
            ], size=size)
        else:
            input_with_text = input_component
        
        # Label avec tooltip si help_text
        if help_text:
            label_component = html.Div([
                dbc.Label(label, size=size, className="text-light mb-1"),
                dbc.Tooltip(help_text, target=f"{control_id}-label", placement="top")
            ], id=f"{control_id}-label")
        else:
            label_component = dbc.Label(label, size=size, className="text-light mb-1")
        
        return dbc.Row([
            dbc.Col([
                label_component,
                input_with_text
            ], width=12)
        ], className="mb-2")
    
    @staticmethod
    def create_slider_control(
        control_id: str,
        label: str,
        value: Union[int, float],
        min_value: Union[int, float],
        max_value: Union[int, float],
        step: Union[int, float] = 1,
        marks: Optional[Dict] = None,
        help_text: str = "",
        show_value: bool = True
    ) -> dbc.Row:
        """
        Créer un Slider standardisé
        
        Args:
            control_id: ID unique du contrôle
            label: Libellé du contrôle
            value: Valeur par défaut
            min_value: Valeur minimum
            max_value: Valeur maximum
            step: Pas d'incrémentation
            marks: Marqueurs sur le slider
            help_text: Texte d'aide
            show_value: Afficher la valeur actuelle
        """
        # Créer les marqueurs par défaut si non spécifiés
        if marks is None:
            marks = {
                min_value: str(min_value),
                max_value: str(max_value)
            }
            # Ajouter marqueur médian si range > 20
            if max_value - min_value > 20:
                mid_value = (min_value + max_value) // 2
                marks[mid_value] = str(mid_value)
        
        slider_component = dcc.Slider(
            id=control_id,
            min=min_value,
            max=max_value,
            step=step,
            value=value,
            marks=marks,
            className="custom-slider",
            tooltip={
                "placement": "bottom",
                "always_visible": False
            }
        )
        
        # Label avec valeur actuelle
        if show_value:
            label_text = f"{label}: {value}"
        else:
            label_text = label
            
        if help_text:
            label_component = html.Div([
                dbc.Label(label_text, size="sm", className="text-light mb-1"),
                dbc.Tooltip(help_text, target=f"{control_id}-label", placement="top")
            ], id=f"{control_id}-label")
        else:
            label_component = dbc.Label(label_text, size="sm", className="text-light mb-1")
        
        return dbc.Row([
            dbc.Col([
                label_component,
                html.Div(slider_component, className="px-2")
            ], width=12)
        ], className="mb-3")
    
    @staticmethod
    def create_switch_control(
        control_id: str,
        label: str,
        value: bool = True,
        help_text: str = ""
    ) -> dbc.Row:
        """Créer un Switch standardisé"""
        switch_component = dbc.Switch(
            id=control_id,
            value=value,
            className="custom-switch"
        )
        
        if help_text:
            label_component = html.Div([
                dbc.Label(label, size="sm", className="text-light"),
                dbc.Tooltip(help_text, target=f"{control_id}-label", placement="top")
            ], id=f"{control_id}-label")
        else:
            label_component = dbc.Label(label, size="sm", className="text-light")
        
        return dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([switch_component], width="auto"),
                    dbc.Col([label_component], width="auto")
                ], align="center", className="g-2")
            ], width=12)
        ], className="mb-2")
    
    @staticmethod
    def create_dropdown_control(
        control_id: str,
        label: str,
        options: List[Dict[str, str]],
        value: str,
        help_text: str = ""
    ) -> dbc.Row:
        """Créer un Dropdown standardisé"""
        dropdown_component = dcc.Dropdown(
            id=control_id,
            options=options,
            value=value,
            className="custom-dropdown",
            style={
                "backgroundColor": "#2d3748",
                "color": "#e2e8f0"
            }
        )
        
        if help_text:
            label_component = html.Div([
                dbc.Label(label, size="sm", className="text-light mb-1"),
                dbc.Tooltip(help_text, target=f"{control_id}-label", placement="top")
            ], id=f"{control_id}-label")
        else:
            label_component = dbc.Label(label, size="sm", className="text-light mb-1")
        
        return dbc.Row([
            dbc.Col([
                label_component,
                dropdown_component
            ], width=12)
        ], className="mb-2")
    
    @staticmethod
    def create_color_picker(
        control_id: str,
        label: str,
        value: str = "#2196F3",
        help_text: str = ""
    ) -> dbc.Row:
        """Créer un Color Picker standardisé"""
        color_input = dbc.Input(
            id=control_id,
            type="color",
            value=value,
            style={"width": "50px", "height": "30px", "padding": "2px"}
        )
        
        if help_text:
            label_component = html.Div([
                dbc.Label(label, size="sm", className="text-light mb-1"),
                dbc.Tooltip(help_text, target=f"{control_id}-label", placement="top")
            ], id=f"{control_id}-label")
        else:
            label_component = dbc.Label(label, size="sm", className="text-light mb-1")
        
        return dbc.Row([
            dbc.Col([
                label_component,
                color_input
            ], width=12)
        ], className="mb-2")
    
    @staticmethod
    def create_section_header(title: str, description: str = "") -> html.Div:
        """Créer un header de section standardisé"""
        header_content = [
            html.H6(title, className="text-primary mb-1 fw-bold")
        ]
        
        if description:
            header_content.append(
                html.P(description, className="text-muted small mb-2")
            )
        
        return html.Div(
            header_content,
            className="border-bottom border-secondary pb-2 mb-3"
        )
    
    @staticmethod
    def create_collapsible_section(
        section_id: str,
        title: str,
        content: List,
        is_open: bool = False,
        switch_control_id: Optional[str] = None
    ) -> html.Div:
        """Créer une section collapsible standardisée"""
        # Header avec switch optionnel
        if switch_control_id:
            header_content = dbc.Row([
                dbc.Col([
                    html.H6(title, className="text-light mb-0")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id=switch_control_id,
                        value=is_open,
                        className="float-end"
                    )
                ], width=4)
            ], className="align-items-center")
        else:
            header_content = html.H6(title, className="text-light mb-0")
        
        return html.Div([
            dbc.Button(
                header_content,
                id=f"{section_id}-toggle",
                color="dark",
                outline=True,
                className="w-100 text-start",
                n_clicks=0
            ),
            dbc.Collapse(
                dbc.Card(
                    dbc.CardBody(content, className="p-3"),
                    className="border-0"
                ),
                id=section_id,
                is_open=is_open
            )
        ], className="mb-3")


# Style CSS pour les contrôles personnalisés
CUSTOM_CONTROLS_CSS = """
.custom-slider .rc-slider-track {
    background-color: #4299e1 !important;
}

.custom-slider .rc-slider-handle {
    border-color: #4299e1 !important;
}

.custom-slider .rc-slider-handle:hover {
    border-color: #3182ce !important;
}

.custom-switch .form-check-input:checked {
    background-color: #4299e1 !important;
    border-color: #4299e1 !important;
}

.custom-dropdown .Select-control {
    background-color: #2d3748 !important;
    border-color: #4a5568 !important;
}

.custom-dropdown .Select-menu-outer {
    background-color: #2d3748 !important;
}

.custom-dropdown .Select-option {
    background-color: #2d3748 !important;
    color: #e2e8f0 !important;
}

.custom-dropdown .Select-option:hover {
    background-color: #4a5568 !important;
}
"""