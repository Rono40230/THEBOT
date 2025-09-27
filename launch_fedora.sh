#!/bin/bash
# =============================================================================
# THEBOT - Script de Lancement pour Fedora Linux
# Plateforme d'Analyse Trading avec Architecture Ultra-Modulaire
# =============================================================================

set -e  # Arrêt sur erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.11"
THEBOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$THEBOT_DIR/venv_thebot"

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

print_header() {
    echo -e "${PURPLE}=============================================${NC}"
    echo -e "${CYAN}🤖 THEBOT - Trading Analysis Platform${NC}"
    echo -e "${CYAN}   Architecture Ultra-Modulaire${NC}"
    echo -e "${PURPLE}=============================================${NC}"
}

print_step() {
    echo -e "${BLUE}➤ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# VÉRIFICATIONS SYSTÈME
# =============================================================================

check_fedora() {
    print_step "Vérification de Fedora Linux..."
    if [ -f /etc/fedora-release ]; then
        local fedora_version=$(cat /etc/fedora-release)
        print_success "Système détecté: $fedora_version"
    else
        print_warning "Ce script est optimisé pour Fedora, mais continue..."
    fi
}

check_python() {
    print_step "Vérification de Python..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé !"
        echo -e "${CYAN}Installation avec: sudo dnf install python3 python3-pip python3-venv${NC}"
        exit 1
    fi
    
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local required_version=${PYTHON_MIN_VERSION}
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
        print_success "Python $python_version détecté (>= $required_version)"
    else
        print_error "Python $python_version détecté, mais >= $required_version requis !"
        exit 1
    fi
}

install_system_deps() {
    print_step "Installation des dépendances système Fedora..."
    
    local deps=(
        "python3-pip"
        "python3-venv" 
        "python3-devel"
        "gcc"
        "gcc-c++"
        "make"
        "git"
        "nodejs"
        "npm"
    )
    
    for dep in "${deps[@]}"; do
        if ! rpm -q "$dep" &> /dev/null; then
            print_step "Installation de $dep..."
            sudo dnf install -y "$dep" || print_warning "Impossible d'installer $dep"
        else
            print_success "$dep déjà installé"
        fi
    done
}

# =============================================================================
# ENVIRONNEMENT VIRTUEL
# =============================================================================

setup_venv() {
    print_step "Configuration de l'environnement virtuel..."
    
    if [ ! -d "$VENV_DIR" ]; then
        print_step "Création de l'environnement virtuel..."
        python3 -m venv "$VENV_DIR"
        print_success "Environnement virtuel créé dans $VENV_DIR"
    else
        print_success "Environnement virtuel existant trouvé"
    fi
    
    # Activation
    source "$VENV_DIR/bin/activate"
    
    # Mise à jour pip
    print_step "Mise à jour de pip..."
    pip install --upgrade pip setuptools wheel
}

install_python_deps() {
    print_step "Installation des dépendances Python..."
    
    # Installation depuis requirements.txt si disponible
    if [ -f "$THEBOT_DIR/requirements.txt" ]; then
        print_step "Installation depuis requirements.txt..."
        pip install -r "$THEBOT_DIR/requirements.txt"
    fi
    
    # Installation en mode développement
    if [ -f "$THEBOT_DIR/setup.py" ]; then
        print_step "Installation de THEBOT en mode développement..."
        pip install -e .
    fi
    
    # Dépendances Jupyter spécifiques
    print_step "Installation des extensions Jupyter..."
    pip install jupyterlab ipywidgets jupyter-widgets-base
    
    # Activation des extensions
    jupyter nbextension enable --py widgetsnbextension --sys-prefix 2>/dev/null || true
    jupyter labextension install @jupyter-widgets/jupyterlab-manager 2>/dev/null || true
}

# =============================================================================
# LANCEMENT DE L'APPLICATION
# =============================================================================

start_jupyter_dashboard() {
    print_step "Lancement du Dashboard Jupyter..."
    
    cd "$THEBOT_DIR"
    
    # Vérification du fichier dashboard
    if [ ! -f "jupyter_dashboard.ipynb" ]; then
        print_error "Dashboard jupyter_dashboard.ipynb non trouvé !"
        exit 1
    fi
    
    print_success "Dashboard trouvé : jupyter_dashboard.ipynb"
    print_step "Ouverture de Jupyter Lab..."
    
    # Configuration pour ouvrir automatiquement le navigateur
    export BROWSER="firefox"  # Ou "google-chrome" selon votre préférence
    
    # Lancement avec ouverture automatique
    echo -e "${CYAN}🚀 Lancement de THEBOT Dashboard...${NC}"
    echo -e "${CYAN}   URL: http://localhost:8888${NC}"
    echo -e "${CYAN}   Dashboard: jupyter_dashboard.ipynb${NC}"
    echo -e "${YELLOW}   Appuyez sur Ctrl+C pour arrêter${NC}"
    
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root 2>/dev/null &
    
    # Attendre que Jupyter démarre
    sleep 3
    
    # Ouvrir le navigateur sur le dashboard
    if command -v firefox &> /dev/null; then
        firefox "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
    elif command -v google-chrome &> /dev/null; then
        google-chrome "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
    else
        print_warning "Aucun navigateur détecté. Ouvrez manuellement: http://localhost:8888"
    fi
    
    # Attendre l'arrêt
    wait
}

run_tests() {
    print_step "Exécution des tests de validation..."
    
    cd "$THEBOT_DIR"
    
    if [ -d "tests" ]; then
        print_step "Tests des indicateurs..."
        python -m pytest tests/unit/indicators/ -v --tb=short
        print_success "Tous les tests passent ! Architecture ultra-modulaire validée."
    else
        print_warning "Dossier tests non trouvé, tests ignorés."
    fi
}

show_status() {
    print_step "État du système THEBOT..."
    
    echo -e "${CYAN}📊 Indicateurs disponibles:${NC}"
    echo -e "   ✅ SMA - Simple Moving Average"
    echo -e "   ✅ EMA - Exponential Moving Average  "
    echo -e "   ✅ ATR - Average True Range"
    echo -e "   ✅ RSI - Relative Strength Index"
    
    echo -e "${CYAN}🎯 Marchés supportés:${NC}"
    echo -e "   📈 BTCUSDT, ETHUSD (Crypto)"
    echo -e "   💱 EURUSD, GBPUSD (Forex)"
    
    echo -e "${CYAN}🖥️  Interface:${NC}"
    echo -e "   📊 Dashboard Jupyter interactif"
    echo -e "   📱 Widgets de configuration temps réel"
    echo -e "   📊 Graphiques Plotly dynamiques"
}

# =============================================================================
# MENU PRINCIPAL
# =============================================================================

show_menu() {
    echo ""
    echo -e "${CYAN}Que voulez-vous faire ?${NC}"
    echo "1) 🚀 Lancer THEBOT Dashboard (recommandé)"
    echo "2) 🔧 Installation complète + Lancement"
    echo "3) ✅ Tests de validation"
    echo "4) 📊 Voir l'état du système" 
    echo "5) 🛠️  Installation des dépendances seulement"
    echo "6) ❌ Quitter"
    echo ""
}

# =============================================================================
# SCRIPT PRINCIPAL
# =============================================================================

main() {
    clear
    print_header
    
    # Si argument direct
    case "${1:-}" in
        "install")
            check_fedora
            check_python
            install_system_deps
            setup_venv
            install_python_deps
            print_success "Installation terminée !"
            ;;
        "test")
            setup_venv
            run_tests
            ;;
        "start")
            setup_venv
            start_jupyter_dashboard
            ;;
        "status")
            show_status
            ;;
        *)
            # Menu interactif
            while true; do
                show_menu
                read -p "Votre choix [1-6]: " choice
                
                case $choice in
                    1)
                        print_step "Lancement rapide du Dashboard..."
                        setup_venv
                        start_jupyter_dashboard
                        break
                        ;;
                    2)
                        print_step "Installation complète..."
                        check_fedora
                        check_python
                        install_system_deps
                        setup_venv
                        install_python_deps
                        run_tests
                        start_jupyter_dashboard
                        break
                        ;;
                    3)
                        setup_venv
                        run_tests
                        ;;
                    4)
                        show_status
                        ;;
                    5)
                        check_fedora
                        check_python
                        install_system_deps
                        setup_venv
                        install_python_deps
                        print_success "Dépendances installées !"
                        ;;
                    6)
                        print_success "Au revoir ! 👋"
                        exit 0
                        ;;
                    *)
                        print_error "Choix invalide. Veuillez choisir 1-6."
                        ;;
                esac
                
                echo ""
                read -p "Appuyez sur Entrée pour continuer..."
                clear
                print_header
            done
            ;;
    esac
}

# Vérification des permissions
if [[ $EUID -eq 0 ]]; then
   print_warning "Ce script ne devrait pas être exécuté en root (sauf pour l'installation des dépendances système)"
fi

# Lancement
main "$@"