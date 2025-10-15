"""
Theme Constants - Palette de couleurs et thèmes THEBOT
Centralisation de tous les styles et couleurs utilisés dans l'application
"""

# 🎨 PALETTE DE COULEURS PRINCIPALE
class ThemeColors:
    """Palette de couleurs principale de THEBOT"""

    # Couleurs primaires
    PRIMARY = "#007bff"
    SECONDARY = "#6c757d"
    SUCCESS = "#28a745"
    INFO = "#17a2b8"
    WARNING = "#ffc107"
    DANGER = "#dc3545"
    LIGHT = "#f8f9fa"
    DARK = "#343a40"

    # Couleurs trading/financières
    BULLISH = "#00d4aa"      # Vert pour les hausses
    BEARISH = "#ff6b6b"      # Rouge pour les baisses
    NEUTRAL = "#ffd93d"      # Jaune pour RSI/stable

    # Couleurs sentiment
    POSITIVE = "#28a745"     # Vert positif
    NEGATIVE = "#dc3545"     # Rouge négatif
    NEUTRAL_SENTIMENT = "#ffc107"  # Jaune neutre

    # Couleurs spéciales
    ACCENT = "#6f42c1"       # Violet accent
    HIGHLIGHT = "#e83e8c"    # Rose highlight

# 📊 COULEURS POUR LES GRAPHIQUES
class ChartColors:
    """Couleurs standardisées pour les graphiques Plotly"""

    # Lignes principales
    PRICE_LINE = "#ffffff"   # Blanc pour les prix
    VOLUME_BAR = "#6c757d"   # Gris pour le volume

    # Indicateurs techniques
    RSI_LINE = ThemeColors.NEUTRAL
    MACD_LINE = ThemeColors.BULLISH
    MACD_SIGNAL = ThemeColors.BEARISH
    MACD_HISTOGRAM = ThemeColors.NEUTRAL

    # Bandes Bollinger
    BB_UPPER = ThemeColors.DANGER
    BB_LOWER = ThemeColors.SUCCESS
    BB_MIDDLE = ThemeColors.INFO

    # Moyennes mobiles
    MA_FAST = ThemeColors.BULLISH    # MA courte (bleu-vert)
    MA_MEDIUM = ThemeColors.WARNING  # MA moyenne (jaune)
    MA_SLOW = ThemeColors.BEARISH    # MA longue (rouge)

# 🎯 COULEURS POUR LES COMPOSANTS UI
class UIColors:
    """Couleurs pour les composants d'interface utilisateur"""

    # Arrière-plans
    BG_DARK = "#212529"      # Fond sombre principal
    BG_LIGHT = "#f8f9fa"     # Fond clair
    BG_CARD = "#343a40"      # Fond des cartes
    BG_MODAL = "rgba(0,0,0,0.8)"  # Fond modal

    # Textes
    TEXT_LIGHT = "#ffffff"   # Texte blanc
    TEXT_DARK = "#212529"    # Texte sombre
    TEXT_MUTED = "#6c757d"   # Texte atténué
    TEXT_SUCCESS = ThemeColors.SUCCESS
    TEXT_DANGER = ThemeColors.DANGER
    TEXT_WARNING = ThemeColors.WARNING
    TEXT_INFO = ThemeColors.INFO

    # Bordures
    BORDER_LIGHT = "#495057"
    BORDER_DARK = "#dee2e6"

# 📱 THÈMES RESPONSIVE
class ResponsiveBreakpoints:
    """Points de rupture pour le design responsive"""

    XS = 576   # Extra small devices (phones < 576px)
    SM = 768   # Small devices (tablets >= 576px)
    MD = 992   # Medium devices (desktops >= 768px)
    LG = 1200  # Large devices (desktops >= 992px)
    XL = 1400  # Extra large devices (large desktops >= 1200px)

# 🎨 CLASSES CSS STANDARDISÉES
class CSSClasses:
    """Classes CSS standardisées pour cohérence"""

    # Layout
    FULL_WIDTH = "w-100"
    HALF_WIDTH = "w-50"
    TEXT_CENTER = "text-center"
    TEXT_END = "text-end"

    # Espacement
    MARGIN_BOTTOM_2 = "mb-2"
    MARGIN_BOTTOM_3 = "mb-3"
    MARGIN_BOTTOM_4 = "mb-4"
    PADDING_2 = "p-2"
    PADDING_3 = "p-3"

    # Couleurs Bootstrap standardisées
    BG_SUCCESS = "bg-success"
    BG_DANGER = "bg-danger"
    BG_WARNING = "bg-warning"
    BG_INFO = "bg-info"
    BG_LIGHT = "bg-light"
    BG_DARK = "bg-dark"

    TEXT_SUCCESS = "text-success"
    TEXT_DANGER = "text-danger"
    TEXT_WARNING = "text-warning"
    TEXT_INFO = "text-info"
    TEXT_MUTED = "text-muted"

    # Boutons
    BTN_SUCCESS = "btn btn-success"
    BTN_DANGER = "btn btn-danger"
    BTN_WARNING = "btn btn-warning"
    BTN_INFO = "btn btn-info"
    BTN_SECONDARY = "btn btn-secondary"

# 📊 CONSTANTES POUR LES GRAPHIQUES
class ChartConstants:
    """Constantes pour la configuration des graphiques"""

    # Dimensions
    DEFAULT_HEIGHT = 400
    MOBILE_HEIGHT = 300

    # Polices
    FONT_FAMILY = "Arial, sans-serif"
    TITLE_FONT_SIZE = 16
    AXIS_FONT_SIZE = 12

    # Marges
    MARGIN_L = 40
    MARGIN_R = 40
    MARGIN_T = 40
    MARGIN_B = 40

# 🚨 COULEURS POUR LES ALERTES ET NOTIFICATIONS
class AlertColors:
    """Couleurs pour les alertes et notifications"""

    # Niveaux d'alerte
    CRITICAL = ThemeColors.DANGER
    HIGH = "#ff6b35"      # Orange-rouge
    MEDIUM = ThemeColors.WARNING
    LOW = ThemeColors.INFO
    INFO = ThemeColors.PRIMARY

    # États
    ACTIVE = ThemeColors.SUCCESS
    INACTIVE = ThemeColors.SECONDARY
    TRIGGERED = ThemeColors.DANGER

# 🌙 THÈME DARK MODE (extension future)
class DarkTheme:
    """Configuration pour le thème sombre"""

    BACKGROUND = "#1a1a1a"
    SURFACE = "#2d2d2d"
    PRIMARY_TEXT = "#ffffff"
    SECONDARY_TEXT = "#b0b0b0"
    BORDER = "#404040"
    ACCENT = ThemeColors.ACCENT</content>
<parameter name="filePath">/home/rono/THEBOT/dash_modules/core/theme_constants.py