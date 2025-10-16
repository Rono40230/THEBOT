import os

modules = [
    ("crypto_news_module", "📰 Crypto News", "Actualités crypto et analyse sentiment"),
    ("economic_news_module", "�� Economic News", "Actualités économiques et indicateurs"),
    ("forex_module", "💱 Forex", "Trading devises internationales"),
    ("stocks_module", "📊 Stocks", "Analyse actions et marchés boursiers"),
    ("strategies_module", "🎯 Strategies", "Stratégies de trading automatisées")
]

template = '''"""
{module_name} - Migration Phase 2
Stub temporaire pour compatibilité
"""

import logging
from typing import Any, Dict, Optional

from dash import html
from src.thebot.core.base_module import BaseModule
from src.thebot.core.logger import logger


class {class_name}(BaseModule):
    """{description} - Stub Phase 2"""

    def __init__(self):
        super().__init__("{module_key}")
        logger.info("{icon} {class_name} initialisé (stub Phase 2)")

    def get_layout(self) -> html.Div:
        """Layout temporaire en cours de migration"""
        return html.Div([
            html.H3("{icon} {title}", style={{"color": "white"}}),
            html.P("{description} en cours de migration...",
                  style={{"color": "gray"}}),
            html.P("🔄 Phase 2 - Migration UI", style={{"color": "orange"}})
        ], style={{"padding": "20px"}})

    def get_status(self) -> Dict[str, Any]:
        """Statut du module"""
        return {{
            "name": "{module_key}",
            "status": "migrating",
            "phase": "2_ui_migration"
        }}


# Instance globale temporaire
{instance_name} = {class_name}()
'''

for module_name, icon_title, description in modules:
    class_name = module_name.replace('_', ' ').title().replace(' ', '')
    instance_name = module_name.lower()
    module_key = module_name.lower()
    
    content = template.format(
        module_name=module_name,
        class_name=class_name,
        description=description,
        icon=icon_title.split()[0],
        title=icon_title,
        module_key=module_key,
        instance_name=instance_name
    )
    
    with open(f"src/thebot/tabs/{module_name}.py", "w") as f:
        f.write(content)
    
    print(f"Créé: {module_name}.py")

print("Tous les stubs UI créés!")
